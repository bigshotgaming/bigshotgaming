# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20150117_0017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='activated',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='is_active',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='registration_enabled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='waiver',
            name='minor',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
