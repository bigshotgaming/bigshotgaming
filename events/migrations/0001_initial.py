# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models
from django.conf import settings
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('ipn', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('uuid', models.CharField(default=events.models.make_uuid, max_length=36, serialize=False, editable=False, primary_key=True)),
                ('activated', models.BooleanField()),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('activated_time', models.DateTimeField(null=True, blank=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Event Name')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('participant_limit', models.IntegerField()),
                ('description', models.CharField(max_length=100)),
                ('is_active', models.BooleanField()),
                ('registration_enabled', models.BooleanField()),
                ('prepay_price', models.DecimalField(max_digits=4, decimal_places=2)),
                ('atd_price', models.DecimalField(verbose_name=b'At-the-Door price', max_digits=4, decimal_places=2)),
                ('waiver', models.FileField(upload_to=b'events/waivers/', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signup_time', models.DateTimeField(auto_now_add=True)),
                ('checked_in', models.BooleanField(default=False)),
                ('checkin_time', models.DateTimeField(null=True, blank=True)),
                ('coupon', models.OneToOneField(null=True, blank=True, to='events.Coupon')),
                ('event', models.ForeignKey(to='events.Event')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=150)),
                ('city', models.CharField(max_length=30)),
                ('state', localflavor.us.models.USStateField(max_length=2, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('zipcode', models.CharField(max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Waiver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('pname', models.CharField(max_length=255, null=True, blank=True)),
                ('minor', models.BooleanField()),
                ('minor_age', models.IntegerField(max_length=2, null=True, blank=True)),
                ('signed_on', models.DateTimeField(auto_now_add=True)),
                ('part', models.ForeignKey(to='events.Participant')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='venue',
            field=models.ForeignKey(to='events.Venue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coupon',
            name='event',
            field=models.ForeignKey(to='events.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coupon',
            name='transaction',
            field=models.ForeignKey(blank=True, editable=False, to='ipn.PayPalIPN', null=True),
            preserve_default=True,
        ),
    ]
