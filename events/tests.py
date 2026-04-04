import test_mocks  # noqa: F401 – installs third-party stubs before Django loads

import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from events.models import Event, Venue, Participant, Coupon, Waiver, activate_coupon
from events.forms import RegisterForm, WaiverForm


def make_venue():
    return Venue.objects.create(
        name='Test Venue',
        address='123 Main St',
        city='Detroit',
        state='MI',
        zipcode='48201',
    )


def make_event(venue=None, is_active=True):
    if venue is None:
        venue = make_venue()
    return Event.objects.create(
        name='Test LAN',
        start_date=datetime.datetime(2025, 1, 1, 12, 0),
        end_date=datetime.datetime(2025, 1, 3, 18, 0),
        venue=venue,
        participant_limit=50,
        description='A test event',
        is_active=is_active,
        registration_enabled=True,
        prepay_price='25.00',
        atd_price='30.00',
    )


def make_user(username='testuser', password='testpass123', is_staff=False):
    return User.objects.create_user(username=username, password=password, email=f'{username}@example.com', is_staff=is_staff)


class VenueModelTest(TestCase):
    def test_str(self):
        venue = make_venue()
        self.assertEqual(str(venue), 'Test Venue')


class EventModelTest(TestCase):
    def test_str(self):
        event = make_event()
        self.assertEqual(str(event), 'Test LAN')

    def test_number_remaining_full(self):
        event = make_event()
        self.assertEqual(event.number_remaining(), 50)

    def test_one_active_signal(self):
        """Saving a second active event should deactivate the first."""
        venue = make_venue()
        e1 = make_event(venue=venue, is_active=True)
        e2 = Event.objects.create(
            name='Second LAN',
            start_date=datetime.datetime(2025, 6, 1, 12, 0),
            end_date=datetime.datetime(2025, 6, 3, 18, 0),
            venue=venue,
            participant_limit=30,
            description='Another event',
            is_active=True,
            registration_enabled=True,
            prepay_price='20.00',
            atd_price='25.00',
        )
        e1.refresh_from_db()
        self.assertFalse(e1.is_active)
        self.assertTrue(e2.is_active)

    def test_number_paid(self):
        event = make_event()
        user = make_user()
        coupon = Coupon.objects.create(event=event, stripe_transaction='ch_test123')
        self.assertEqual(event.number_paid(), 1)

    def test_number_pending(self):
        event = make_event()
        user = make_user()
        Participant.objects.create(user=user, event=event)
        self.assertEqual(event.number_pending(), 1)


class ParticipantModelTest(TestCase):
    def test_str(self):
        event = make_event()
        user = make_user()
        part = Participant.objects.create(user=user, event=event)
        self.assertIn('testuser', str(part))
        self.assertIn('Test LAN', str(part))


class CouponModelTest(TestCase):
    def test_uuid_auto_generated(self):
        event = make_event()
        coupon = Coupon.objects.create(event=event)
        self.assertIsNotNone(coupon.uuid)
        self.assertEqual(len(coupon.uuid), 36)

    def test_activate(self):
        event = make_event()
        coupon = Coupon.objects.create(event=event)
        self.assertFalse(coupon.activated)
        coupon.activate()
        coupon.refresh_from_db()
        self.assertTrue(coupon.activated)
        self.assertIsNotNone(coupon.activated_time)

    def test_str(self):
        event = make_event()
        coupon = Coupon.objects.create(event=event)
        self.assertEqual(str(coupon), coupon.uuid)


class ActivateCouponTest(TestCase):
    def test_activate_coupon_links_participant(self):
        event = make_event()
        user = make_user()
        participant = Participant.objects.create(user=user, event=event)
        coupon = Coupon.objects.create(event=event)
        activate_coupon(participant, coupon)
        participant.refresh_from_db()
        self.assertEqual(participant.coupon, coupon)
        self.assertTrue(coupon.activated)


class WaiverModelTest(TestCase):
    def test_str(self):
        event = make_event()
        user = make_user()
        part = Participant.objects.create(user=user, event=event)
        waiver = Waiver.objects.create(part=part, name='John Doe')
        self.assertIn('testuser', str(waiver))


class RegisterFormTest(TestCase):
    def test_valid_form(self):
        form = RegisterForm(data={'payment_type': 'pp', 'ticket_quantity': '1', 'waiver': True})
        self.assertTrue(form.is_valid())

    def test_missing_waiver(self):
        form = RegisterForm(data={'payment_type': 'pp', 'ticket_quantity': '1', 'waiver': False})
        self.assertFalse(form.is_valid())
        self.assertIn('waiver', form.errors)

    def test_invalid_quantity(self):
        # Ticket quantity must be an integer; non-integer values are rejected
        form = RegisterForm(data={'payment_type': 'pp', 'ticket_quantity': 'abc', 'waiver': True})
        self.assertFalse(form.is_valid())


class WaiverFormTest(TestCase):
    def test_valid(self):
        form = WaiverForm(data={'waiver': True})
        self.assertTrue(form.is_valid())

    def test_invalid_no_acceptance(self):
        form = WaiverForm(data={'waiver': False})
        self.assertFalse(form.is_valid())


class EventIndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.client.login(username='testuser', password='testpass123')

    def test_index_no_active_event(self):
        response = self.client.get('/events/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['event'])

    def test_index_with_active_event(self):
        event = make_event()
        response = self.client.get('/events/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['event'], event)


