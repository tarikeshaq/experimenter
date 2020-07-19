# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-05 20:15
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import timezone
import experimenter.experiments.models


class Migration(migrations.Migration):

    dependencies = [("experiments", "0003_auto_20171120_2205")]

    operations = [
        migrations.AddField(
            model_name="experiment",
            name="enrollment_dashboard_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="experiment",
            name="total_users",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="experimentchangelog",
            name="changed_on",
            field=models.DateTimeField(default=timezone.now),
        ),
    ]
