# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coupon',
            old_name='transaction',
            new_name='paypal_transaction',
        ),
        migrations.AddField(
            model_name='coupon',
            name='stripe_transaction',
            field=models.CharField(max_length=128, null=True, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
