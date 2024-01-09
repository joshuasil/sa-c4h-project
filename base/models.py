from django.db import models
from django.utils.timezone import now
from django.db.models.functions import Now
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings
import vonage
from django.http import HttpResponse, JsonResponse
client = vonage.Client(key=settings.VONAGE_KEY, secret=settings.VONAGE_SECRET)
import time
from django.db import transaction
import hashlib
from .send_message_vonage import *
from .aws_kms_functions import *

welcome_message = settings.WELCOME_MESSAGE
welcome_message_es = settings.WELCOME_MESSAGE_ES
class Arm(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (self.name)


class PhoneNumber(models.Model):
    # Define a regular expression pattern for an 11-digit number
    phone_number_validator = RegexValidator(
        regex=r'^\d{11}$',  # Matches exactly 11 digits
        message="Phone number must be exactly 11 digits long.",
        code="invalid_phone_number"
    )
    arm = models.ForeignKey(Arm, on_delete=models.SET_DEFAULT, default=1,
                            help_text="Select the arm to which this number belongs. If the arm you wish to select doesn't exist, please create it first.")
    phone_number = models.TextField(unique=True, blank=False,
                                    # validators=[phone_number_validator],
                                    help_text="Enter the 11 digit phone number in the format 1234567890 (no spaces or dashes).")
    phone_number_key = models.BinaryField()
    phone_number_hash = models.CharField(max_length=64, unique=True, blank=True, null=True)
    name = models.TextField(blank=True, null=True,
                            help_text="Enter a first name for this number.")
    name_key = models.BinaryField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    opted_in = models.BooleanField(default=False)
    welcome_sent = models.BooleanField(default=False)
    final_pilot_message_sent = models.BooleanField(default=False)
    sub_group = models.BooleanField(default=False)
    language = models.CharField(max_length=2, blank=True, null=True, default="")
    pre_survey = models.URLField(blank=True, null=True)
    post_survey = models.URLField(blank=True, null=True)
    

    def __str__(self):
        return f"PhoneNumber object (id: {self.id})"
    
    def clean(self):
        super().clean()
        if self.phone_number:
            # Validate if the phone number is a mobile number using Vonage Number Insight API
            try:
                insight_json = client.number_insight.get_standard_number_insight(number=self.phone_number)

                if insight_json['current_carrier']['network_type'] == 'mobile':
                    # The API call was successful, and the number is a mobile number
                    pass
                else:
                    # The API call was not successful, or the number is not a mobile number
                    raise ValidationError("Invalid phone number. It must be a mobile number.")
            except Exception as e:
                raise ValidationError("Error validating phone number.Please check if this is a mobile number.")
    
    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        # Generate the hash for the current phone number
        current_phone_number_hash = hashlib.sha256(self.phone_number.encode()).hexdigest()

        # Query for any other instances with the same phone number hash
        existing = self.__class__.objects.filter(phone_number_hash=current_phone_number_hash)

        if self.pk:  # Exclude the current instance if it's an update
            existing = existing.exclude(pk=self.pk)

        if existing.exists():
            raise ValidationError({
                'phone_number': ValidationError(
                    'Phone number already exists.',
                    code='unique',
                ),
            })
        
    @transaction.atomic
    def save(self, *args, **kwargs):

        if self.phone_number:
            self.phone_number_hash = hashlib.sha256(self.phone_number.encode()).hexdigest()
            self.phone_number, self.phone_number_key = encrypt_data(self.phone_number)
        if self.name:
            self.name, self.name_key = encrypt_data(self.name)
        super().save(*args, **kwargs)


        # Check if opted_in has been changed to True
        if self.pk is not None:
            orig = PhoneNumber.objects.get(pk=self.pk)
            if self.opted_in and not self.welcome_sent:
                if self.language == "es":
                    message = welcome_message_es
                else:
                    message = welcome_message
                success = retry_send_message_vonage(message, self, "sending welcome message", max_retries=3, retry_delay=5)
                TextMessage.objects.create(phone_number=self, message=message, route="sending welcome message")
                time.sleep(5)
                if self.pre_survey:
                    message = self.pre_survey
                    success = retry_send_message_vonage(message, self, "sending pre survey link", max_retries=3, retry_delay=5)
                    TextMessage.objects.create(phone_number=self, message=message, route="sending pre survey link")
                if success:
                    self.welcome_sent = True

        super().save(*args, **kwargs)



class Topic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, blank=False)
    name_es = models.CharField(max_length=100, unique=True, blank=True, null=True)
    description = models.TextField(blank=False, null=False)
    image = models.ImageField(upload_to='images', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return (self.name)


class ScheduledMessage(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    weekday = models.IntegerField(blank=False, null=False)
    message = models.TextField(blank=False, null=True)
    message_es = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    picklist = models.TextField(blank=True, null=True)

    def __str__(self):
        return (self.message)
    
class ScheduledMessageControl(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    weekday = models.IntegerField(blank=False, null=False)
    message = models.TextField(blank=False, null=True)
    message_es = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (self.message)


class TextMessage(models.Model):
    phone_number = models.ForeignKey(PhoneNumber,on_delete=models.SET_NULL, null=True)
    message = models.TextField(blank=False, null=True)
    route = models.CharField(max_length=100, blank=False, null=False)
    messageuuid = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (self.message)
    



class WeeklyTopic(models.Model):
    week_number = models.PositiveIntegerField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    phone_number = models.ForeignKey(
        PhoneNumber, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        # Define the composite primary key
        constraints = [
            models.UniqueConstraint(fields=['week_number', 'phone_number'], name='weekly_topic_pk')
        ]

    def __str__(self):
        return f"Week {self.week_number}: {self.topic.name} - {self.phone_number}"

class TopicGoal(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    goal = models.TextField(blank=False, null=True)
    goal_es = models.TextField(blank=True, null=True)
    goal_dict = models.TextField(blank=True, null=True)
    goal_feedback = models.TextField(blank=False, null=True)
    goal_feedback_es = models.TextField(blank=True, null=True)
    goal_feedback_dict = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (self.goal)
    
class MessageTracker(models.Model):
    phone_number = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE)
    week_no = models.PositiveIntegerField()
    sent_topic_selection_message = models.BooleanField(default=False)
    sent_goal_message = models.BooleanField(default=False)
    sent_info_message_1 = models.BooleanField(default=False)
    sent_info_message_2 = models.BooleanField(default=False)
    sent_info_message_3 = models.BooleanField(default=False)
    sent_info_message_4 = models.BooleanField(default=False)
    sent_info_message_5 = models.BooleanField(default=False)
    sent_goal_feedback_message = models.BooleanField(default=False)
    set_goal = models.TextField(blank=False, null=True, default="No goal set")
    goal_feedback = models.TextField(blank=False, null=True, default="No feedback")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"MessageTracker - Phone Number: {self.phone_number}, Week No: {self.week_no}"


class Picklist(models.Model):
    phone_number = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE)
    context = models.TextField(blank=True, null=True)
    picklist = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=2, blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=PhoneNumber)
def create_message_trackers(sender, instance, created, **kwargs):
    if created and instance.arm.name == "test":
        for week_no in range(1, int(settings.TOTAL_TOPICS)+1):  
            MessageTracker.objects.create(phone_number=instance, week_no=week_no)
