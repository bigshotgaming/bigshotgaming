# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('platform', models.CharField(max_length=1, choices=[(b'P', b'PC'), (b'C', b'Console')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('password', models.CharField(max_length=10)),
                ('members', models.ManyToManyField(to='events.Participant', blank=True)),
                ('owner', models.ForeignKey(related_name='owned_by', to='events.Participant')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('team_size', models.IntegerField()),
                ('max_teams', models.IntegerField()),
                ('rules', models.TextField(null=True, blank=True)),
                ('html_rules', models.TextField(null=True, blank=True)),
                ('style', models.CharField(max_length=1, choices=[(b'S', b'Single Elimination'), (b'D', b'Double Elimination'), (b'R', b'Round Robin'), (b'W', b'Swiss')])),
                ('slugified_name', models.SlugField(max_length=80, editable=False)),
                ('is_active', models.BooleanField(default=True)),
                ('has_started', models.BooleanField()),
                ('automated', models.BooleanField(help_text=b'Will periodically check to see if the tournament has been updated to send participants emails.')),
                ('automated_data', models.TextField(null=True, blank=True)),
                ('event', models.ForeignKey(to='events.Event')),
                ('game', models.ForeignKey(to='tournaments.Game')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='team',
            name='tournament',
            field=models.ForeignKey(to='tournaments.Tournament'),
            preserve_default=True,
        ),
    ]
