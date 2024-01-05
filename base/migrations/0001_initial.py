# Generated by Django 4.2.7 on 2023-11-22 21:28

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Arm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(help_text='Enter the 11 digit phone number in the format 1234567890 (no spaces or dashes).', max_length=11, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_phone_number', message='Phone number must be exactly 11 digits long.', regex='^\\d{11}$')])),
                ('name', models.CharField(blank=True, help_text='Enter a first name for this number.', max_length=100, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('welcome_sent', models.BooleanField(default=False)),
                ('language', models.CharField(blank=True, default='', max_length=2, null=True)),
                ('arm', models.ForeignKey(default=1, help_text="Select the arm to which this number belongs. If the arm you wish to select doesn't exist, please create it first.", on_delete=django.db.models.deletion.SET_DEFAULT, to='base.arm')),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('name_es', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='images')),
                ('url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WeeklyTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_number', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phone_number', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.phonenumber')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.topic')),
            ],
        ),
        migrations.CreateModel(
            name='TopicGoal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goal', models.TextField(null=True)),
                ('goal_es', models.TextField(blank=True, null=True)),
                ('goal_dict', models.TextField(blank=True, null=True)),
                ('goal_feedback', models.TextField(null=True)),
                ('goal_feedback_es', models.TextField(blank=True, null=True)),
                ('goal_feedback_dict', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.topic')),
            ],
        ),
        migrations.CreateModel(
            name='TextMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(null=True)),
                ('route', models.CharField(max_length=100)),
                ('messageuuid', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phone_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.phonenumber')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledMessageControl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.IntegerField()),
                ('message', models.TextField(null=True)),
                ('message_es', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.topic')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.IntegerField()),
                ('message', models.TextField(null=True)),
                ('message_es', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('picklist', models.TextField(blank=True, null=True)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.topic')),
            ],
        ),
        migrations.CreateModel(
            name='Picklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('context', models.TextField(blank=True, null=True)),
                ('picklist', models.TextField(blank=True, null=True)),
                ('language', models.CharField(blank=True, default='', max_length=2, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phone_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.phonenumber')),
            ],
        ),
        migrations.CreateModel(
            name='MessageTracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_no', models.PositiveIntegerField()),
                ('sent_topic_selection_message', models.BooleanField(default=False)),
                ('sent_goal_message', models.BooleanField(default=False)),
                ('sent_info_message_2', models.BooleanField(default=False)),
                ('sent_info_message_4', models.BooleanField(default=False)),
                ('sent_goal_feedback_message', models.BooleanField(default=False)),
                ('set_goal', models.TextField(default='No goal set', null=True)),
                ('goal_feedback', models.TextField(default='No feedback', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phone_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.phonenumber')),
            ],
        ),
        migrations.AddConstraint(
            model_name='weeklytopic',
            constraint=models.UniqueConstraint(fields=('week_number', 'phone_number'), name='weekly_topic_pk'),
        ),
    ]