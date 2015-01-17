# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='automated',
            field=models.BooleanField(default=False, help_text=b'Will periodically check to see if the tournament has been updated to send participants emails.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tournament',
            name='has_started',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
