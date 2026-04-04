import test_mocks  # noqa: F401 – installs third-party stubs before Django loads

import datetime
import json

from django.contrib.auth.models import User
from django.test import TestCase, Client

from events.models import Event, Venue, Participant
from seatmap.models import SeatMap, Seat, Table


def make_venue():
    return Venue.objects.create(
        name='Venue', address='1 St', city='Detroit', state='MI', zipcode='48201'
    )


def make_event(is_active=True):
    return Event.objects.create(
        name='LAN 2025',
        start_date=datetime.datetime(2025, 1, 1, 12, 0),
        end_date=datetime.datetime(2025, 1, 3, 18, 0),
        venue=make_venue(),
        participant_limit=50,
        description='Test',
        is_active=is_active,
        registration_enabled=True,
        prepay_price='25.00',
        atd_price='30.00',
    )


def make_user(username='player', password='pass1234', is_staff=False):
    return User.objects.create_user(username=username, password=password, is_staff=is_staff)


def make_seatmap(event=None):
    if event is None:
        event = make_event()
    return SeatMap.objects.create(event=event, seat_size=30)


class SeatMapModelTest(TestCase):
    def test_str(self):
        sm = make_seatmap()
        self.assertIn('LAN 2025', str(sm))


class SeatModelTest(TestCase):
    def test_str(self):
        sm = make_seatmap()
        seat = Seat.objects.create(seatmap=sm, x=1, y=2, status='O')
        self.assertIn('(1, 2)', str(seat))

    def test_status_display(self):
        sm = make_seatmap()
        seat = Seat.objects.create(seatmap=sm, x=0, y=0, status='O')
        self.assertEqual(seat.get_status_display(), 'Open')


class TableModelTest(TestCase):
    def test_str(self):
        sm = make_seatmap()
        table = Table.objects.create(seatmap=sm, name='Table A', x=0, y=0)
        self.assertEqual(str(table), 'Table Table A')


class SeatmapDataViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.sm = make_seatmap()

    def test_missing_seatmap_id_returns_400(self):
        response = self.client.get('/seatmap/data/', {'seatmap_id': 99999})
        self.assertEqual(response.status_code, 400)

    def test_valid_seatmap_id_returns_json(self):
        response = self.client.get('/seatmap/data/', {'seatmap_id': self.sm.id, 'object_type': 'seat'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')


class SeatAdminViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.sm = make_seatmap()
        self.staff_user = make_user(username='admin', password='admin123', is_staff=True)
        self.regular_user = make_user(username='regular', password='pass1234')
        self.seat = Seat.objects.create(seatmap=self.sm, x=5, y=5, status='O')

    def test_non_staff_gets_403(self):
        self.client.login(username='regular', password='pass1234')
        response = self.client.get('/seatmap/admin/')
        self.assertIn(response.status_code, [302, 403])

    def test_staff_can_access_admin(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/seatmap/admin/')
        self.assertEqual(response.status_code, 200)

    def test_seat_admin_invalid_status_returns_400(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(
            '/seatmap/admin/seat/%d/' % self.seat.id,
            {'x-edit': '5', 'y-edit': '5', 'status-edit': 'Z', 'part-edit': ''},
        )
        self.assertEqual(response.status_code, 400)

    def test_seat_admin_valid_update(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(
            '/seatmap/admin/seat/%d/' % self.seat.id,
            {'x-edit': '10', 'y-edit': '10', 'status-edit': 'T', 'part-edit': ''},
        )
        self.assertEqual(response.status_code, 200)
        self.seat.refresh_from_db()
        self.assertEqual(self.seat.x, 10)
        self.assertEqual(self.seat.status, 'T')


class SeatmapUserSearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user(username='searchtest', password='pass1234')
        self.client.login(username='searchtest', password='pass1234')

    def test_search_requires_query(self):
        response = self.client.get('/seatmap/users/')
        self.assertEqual(response.status_code, 400)

    def test_search_returns_matching_users(self):
        response = self.client.get('/seatmap/users/', {'q': 'searchtest'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('searchtest', data)

    def test_search_limits_results(self):
        for i in range(25):
            User.objects.create_user(username=f'limituser{i}', password='x')
        response = self.client.get('/seatmap/users/', {'q': 'limituser'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertLessEqual(len(data), 20)


