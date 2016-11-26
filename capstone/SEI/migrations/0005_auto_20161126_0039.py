# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-26 05:39
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('SEI', '0004_auto_20161118_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chargestring',
            name='charge',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='employee',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='employeeavailability',
            name='is_available',
            field=models.BooleanField(default=1),
        ),
        migrations.AlterField(
            model_name='profile',
            name='permission_description',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_role',
            field=models.CharField(choices=[('ADMIN', 'Administrator'), ('NM', 'NormalUser'), ('ITADMIN', 'ITAdministrator')], default='NM', max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='business_manager',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
