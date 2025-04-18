# Generated by Django 5.1.6 on 2025-03-18 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0008_application_application_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='application_status',
            field=models.CharField(choices=[('Approved for interview', 'Approved for interview'), ('Scheduled interview', 'Scheduled interview'), ('Interview passed', 'Interview passed'), ('Rejected', 'Rejected'), ('Accepted', 'Accepted'), ('Waiting list', 'Waiting list'), ('Draft', 'Application in progress'), ('Submitted', 'Submitted')], default='Draft', max_length=40),
        ),
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(choices=[('Draft', 'Draft'), ('Submitted', 'Submitted')], default='Draft', max_length=20),
        ),
    ]
