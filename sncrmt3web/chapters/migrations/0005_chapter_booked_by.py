# Generated by Django 5.1.6 on 2025-03-01 09:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chapters', '0004_chapterbooking_delete_chapterbookings'),
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='booked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='booked_chapters', to='userprofile.userprofile'),
        ),
    ]
