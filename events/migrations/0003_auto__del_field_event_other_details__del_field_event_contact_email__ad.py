# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Event.other_details'
        db.delete_column('events_event', 'other_details')

        # Deleting field 'Event.contact_email'
        db.delete_column('events_event', 'contact_email')

        # Adding field 'Event.is_active'
        db.add_column('events_event', 'is_active', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Removing M2M table for field participants on 'Event'
        db.delete_table('events_event_participants')

        # Changing field 'Event.description'
        db.alter_column('events_event', 'description', self.gf('django.db.models.fields.CharField')(max_length=100))


    def backwards(self, orm):
        
        # Adding field 'Event.other_details'
        db.add_column('events_event', 'other_details', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'Event.contact_email'
        db.add_column('events_event', 'contact_email', self.gf('django.db.models.fields.EmailField')(default='', max_length=75), keep_default=False)

        # Deleting field 'Event.is_active'
        db.delete_column('events_event', 'is_active')

        # Adding M2M table for field participants on 'Event'
        db.create_table('events_event_participants', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm['events.event'], null=False)),
            ('attendee', models.ForeignKey(orm['attendeereg.attendee'], null=False))
        ))
        db.create_unique('events_event_participants', ['event_id', 'attendee_id'])

        # Changing field 'Event.description'
        db.alter_column('events_event', 'description', self.gf('django.db.models.fields.TextField')())


    models = {
        'events.event': {
            'Meta': {'object_name': 'Event'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'participant_limit': ('django.db.models.fields.IntegerField', [], {}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.Venue']"})
        },
        'events.venue': {
            'Meta': {'object_name': 'Venue'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['events']
