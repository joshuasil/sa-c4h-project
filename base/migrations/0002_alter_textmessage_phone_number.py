# Generated by Django 4.2.7 on 2023-12-05 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='textmessage',
            name='phone_number',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.phonenumber'),
        ),
    ]
