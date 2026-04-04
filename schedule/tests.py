import test_mocks  # noqa: F401 – installs third-party stubs before Django loads

import datetime

from django.test import TestCase, Client

from events.models import Event, Venue
from schedule.models import ScheduleItem


def make_event():
    venue = Venue.objects.create(
        name='Venue', address='1 St', city='Detroit', state='MI', zipcode='48201'
    )
    return Event.objects.create(
        name='Test LAN',
        start_date=datetime.datetime(2025, 1, 1, 12, 0),
        end_date=datetime.datetime(2025, 1, 3, 18, 0),
        venue=venue,
        participant_limit=50,
        description='Test',
        is_active=True,
        registration_enabled=True,
        prepay_price='25.00',
        atd_price='30.00',
    )


class ScheduleItemModelTest(TestCase):
    def test_str(self):
        event = make_event()
        item = ScheduleItem.objects.create(
            name='Opening Ceremony',
            description='Welcome!',
            start_time=datetime.datetime(2025, 1, 1, 14, 0),
            end_time=datetime.datetime(2025, 1, 1, 15, 0),
            event=event,
        )
        self.assertEqual(str(item), 'Opening Ceremony')

    def test_default_ordering_by_start_time(self):
        event = make_event()
        ScheduleItem.objects.create(
            name='Second',
            start_time=datetime.datetime(2025, 1, 1, 16, 0),
            end_time=datetime.datetime(2025, 1, 1, 17, 0),
            event=event,
        )
        ScheduleItem.objects.create(
            name='First',
            start_time=datetime.datetime(2025, 1, 1, 10, 0),
            end_time=datetime.datetime(2025, 1, 1, 11, 0),
            event=event,
        )
        items = list(ScheduleItem.objects.filter(event=event))
        self.assertEqual(items[0].name, 'First')
        self.assertEqual(items[1].name, 'Second')


class ScheduleIndexViewTest(TestCase):
    def test_no_active_event(self):
        response = Client().get('/schedule/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['event'])

    def test_active_event_shows_schedule(self):
        event = make_event()
        ScheduleItem.objects.create(
            name='Opening',
            start_time=datetime.datetime(2025, 1, 1, 14, 0),
            end_time=datetime.datetime(2025, 1, 1, 15, 0),
            event=event,
        )
        response = Client().get('/schedule/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['event'], event)
        self.assertIn('Opening', response.context['schedule'].values_list('name', flat=True))

