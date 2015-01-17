# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sponsorship', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prize',
            name='raffle_prize',
            field=models.BooleanField(default=False, verbose_name=b'Raffle Prize?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='featured_sponsor',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
