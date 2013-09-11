# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Coupon'
        db.delete_table(u'events_coupon')

        # Adding model 'Ticket'
        db.create_table(u'events_ticket', (
            ('uuid', self.gf('django.db.models.fields.CharField')(default='da0047fb-0f06-4321-b90e-85aa1d154f15', max_length=36, primary_key=True)),
            ('tickettype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.TicketType'])),
            ('transaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Transaction'], null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'events', ['Ticket'])

        # Adding model 'TicketType'
        db.create_table(u'events_tickettype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('max_available', self.gf('django.db.models.fields.IntegerField')()),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
        ))
        db.send_create_signal(u'events', ['TicketType'])

        # Adding model 'Transaction'
        db.create_table(u'events_transaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'events', ['Transaction'])

        # Deleting field 'Participant.coupon'
        db.delete_column(u'events_participant', 'coupon_id')

        # Adding field 'Participant.ticket'
        db.add_column(u'events_participant', 'ticket',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Ticket'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Event.atd_price'
        db.delete_column(u'events_event', 'atd_price')

        # Deleting field 'Event.participant_limit'
        db.delete_column(u'events_event', 'participant_limit')

        # Deleting field 'Event.prepay_price'
        db.delete_column(u'events_event', 'prepay_price')

        # Adding field 'Event.reg_enabled'
        db.add_column(u'events_event', 'reg_enabled',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'Event.description'
        db.alter_column(u'events_event', 'description', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):
        # Adding model 'Coupon'
        db.create_table(u'events_coupon', (
            ('uuid', self.gf('django.db.models.fields.CharField')(default='6feb12cb-8dda-476a-8d71-46b8bcc9b0e2', max_length=36, primary_key=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('transaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ipn.PayPalIPN'], null=True, blank=True)),
            ('activated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('activated_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.Event'])),
        ))
        db.send_create_signal('events', ['Coupon'])

        # Deleting model 'Ticket'
        db.delete_table(u'events_ticket')

        # Deleting model 'TicketType'
        db.delete_table(u'events_tickettype')

        # Deleting model 'Transaction'
        db.delete_table(u'events_transaction')

        # Adding field 'Participant.coupon'
        db.add_column(u'events_participant', 'coupon',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['events.Coupon'], unique=True, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Participant.ticket'
        db.delete_column(u'events_participant', 'ticket_id')

        # Adding field 'Event.atd_price'
        db.add_column(u'events_event', 'atd_price',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=2),
                      keep_default=False)

        # Adding field 'Event.participant_limit'
        db.add_column(u'events_event', 'participant_limit',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Event.prepay_price'
        db.add_column(u'events_event', 'prepay_price',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=2),
                      keep_default=False)

        # Deleting field 'Event.reg_enabled'
        db.delete_column(u'events_event', 'reg_enabled')


        # Changing field 'Event.description'
        db.alter_column(u'events_event', 'description', self.gf('django.db.models.fields.CharField')(max_length=100))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'events.event': {
            'Meta': {'object_name': 'Event'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'reg_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'venue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Venue']"}),
            'waiver': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'events.participant': {
            'Meta': {'object_name': 'Participant'},
            'checked_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'checkin_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signup_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Ticket']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'events.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'notes': ('django.db.models.fields.TextField', [], {}),
            'tickettype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.TicketType']"}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Transaction']", 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'3135d5c3-eda0-4a45-91ad-aa4381c78fbf'", 'max_length': '36', 'primary_key': 'True'})
        },
        u'events.tickettype': {
            'Meta': {'object_name': 'TicketType'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_available': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'})
        },
        u'events.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'events.venue': {
            'Meta': {'object_name': 'Venue'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'events.waiver': {
            'Meta': {'object_name': 'Waiver'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minor_age': ('django.db.models.fields.IntegerField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Participant']"}),
            'pname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'signed_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['events']