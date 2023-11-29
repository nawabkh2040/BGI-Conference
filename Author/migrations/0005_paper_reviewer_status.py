# Generated by Django 4.1.7 on 2023-11-29 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0004_reviewerprofile_is_mail_verify'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='reviewer_status',
            field=models.CharField(choices=[('approved', 'Approved'), ('partially_approved', 'Partially Approved'), ('pending', 'Pending'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]
