# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-10 19:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SEI', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmonth',
            name='project_date',
            field=models.DateField(),
        ),
    ]
