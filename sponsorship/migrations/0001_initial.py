# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EventSponsor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'n', max_length=1, choices=[(b'c', b'Confirmed'), (b'd', b'Denied'), (b'p', b'Pending Confirmation'), (b't', b'Contacted'), (b'r', b'Follow-Up Required'), (b'f', b'Followed-Up'), (b'n', b'Not Contacted'), (b'e', b'Dead Contact')])),
                ('event', models.ForeignKey(to='events.Event')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Prize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Prize Name')),
                ('description', models.TextField(blank=True)),
                ('raffle_prize', models.BooleanField(verbose_name=b'Raffle Prize?')),
                ('eventsponsor', models.ForeignKey(verbose_name=b'Sponsor/Event', to='sponsorship.EventSponsor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Sponsor Name')),
                ('contact_name', models.CharField(max_length=50, blank=True)),
                ('contact_email', models.EmailField(max_length=75, blank=True)),
                ('contact_phone', localflavor.us.models.PhoneNumberField(max_length=20, blank=True)),
                ('notes', models.TextField(blank=True)),
                ('contact_form_url', models.URLField(verbose_name=b'Contact Form URL', blank=True)),
                ('banner_url', models.URLField(verbose_name=b'Banner URL', blank=True)),
                ('banner', models.ImageField(upload_to=b'sponsor/banners/', blank=True)),
                ('featured_sponsor', models.BooleanField()),
                ('featured_banner', models.ImageField(upload_to=b'sponsor/featured/', blank=True)),
                ('event', models.ManyToManyField(to='events.Event', through='sponsorship.EventSponsor')),
                ('lan_rep', models.ForeignKey(verbose_name=b'LAN Representative', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='eventsponsor',
            name='sponsor',
            field=models.ForeignKey(to='sponsorship.Sponsor'),
            preserve_default=True,
        ),
    ]
