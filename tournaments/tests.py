import test_mocks  # noqa: F401 – installs third-party stubs before Django loads

import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from events.models import Event, Venue, Participant
from tournaments.models import Game, Tournament, Team, team_full, tournament_full, password_correct
from tournaments.forms import JoinTeamForm, CreateTeamForm


def make_venue():
    return Venue.objects.create(
        name='Test Venue', address='1 Main', city='Detroit', state='MI', zipcode='48201'
    )


def make_event():
    return Event.objects.create(
        name='Test LAN',
        start_date=datetime.datetime(2025, 1, 1, 12, 0),
        end_date=datetime.datetime(2025, 1, 3, 18, 0),
        venue=make_venue(),
        participant_limit=50,
        description='A test event',
        is_active=True,
        registration_enabled=True,
        prepay_price='25.00',
        atd_price='30.00',
    )


def make_user(username='player1', password='pass1234'):
    return User.objects.create_user(username=username, password=password)


def make_participant(user=None, event=None):
    if user is None:
        user = make_user()
    if event is None:
        event = make_event()
    return Participant.objects.create(user=user, event=event)


def make_game():
    return Game.objects.create(name='Counter-Strike 2', platform='P')


_tournament_counter = 0


def make_tournament(event=None, game=None, team_size=5, max_teams=8, name=None):
    global _tournament_counter
    if event is None:
        event = make_event()
    if game is None:
        game = make_game()
    _tournament_counter += 1
    if name is None:
        name = 'CS2 Open %d' % _tournament_counter
    # Use save() to avoid triggering challonge signal in unit tests
    t = Tournament(
        name=name,
        game=game,
        event=event,
        team_size=team_size,
        max_teams=max_teams,
        style='S',
    )
    # Manually set slugified_name to avoid save() signal issues in tests
    from django.template.defaultfilters import slugify
    t.slugified_name = slugify('%s %s' % (event.name, t.name)).replace('-', '_')
    Tournament.objects.bulk_create([t])
    return Tournament.objects.get(slugified_name=t.slugified_name)


class GameModelTest(TestCase):
    def test_str(self):
        game = make_game()
        self.assertEqual(str(game), 'Counter-Strike 2')


class TournamentModelTest(TestCase):
    def test_get_tournament_style(self):
        tournament = make_tournament()
        self.assertEqual(tournament.get_tournament_style(), 'Single Elimination')

    def test_is_automated_active_default_false(self):
        tournament = make_tournament()
        self.assertFalse(tournament.is_automated_active())


class TeamModelTest(TestCase):
    def setUp(self):
        self.event = make_event()
        self.user = make_user()
        self.participant = Participant.objects.create(user=self.user, event=self.event)
        self.tournament = make_tournament(event=self.event)

    def _make_team(self, name='Alpha', password='secret'):
        team = Team.objects.create(
            name=name,
            password=password,
            tournament=self.tournament,
            owner=self.participant,
        )
        team.members.add(self.participant)
        return team

    def test_str(self):
        team = self._make_team()
        self.assertEqual(str(team), 'Alpha')

    def test_team_full_when_at_limit(self):
        # Create a 1-person-max tournament for this test
        tiny_tournament = make_tournament(event=self.event, team_size=1)
        team = Team.objects.create(
            name='TinyTeam', password='x', tournament=tiny_tournament, owner=self.participant
        )
        team.members.add(self.participant)
        self.assertTrue(team_full(tiny_tournament, team))

    def test_team_not_full_when_below_limit(self):
        big_tournament = make_tournament(event=self.event, team_size=5)
        team = Team.objects.create(
            name='Beta', password='abc', tournament=big_tournament, owner=self.participant
        )
        team.members.add(self.participant)
        self.assertFalse(team_full(big_tournament, team))

    def test_tournament_full_at_limit(self):
        for i in range(self.tournament.max_teams):
            u = make_user(username=f'extra{i}')
            p = Participant.objects.create(user=u, event=self.event)
            Team.objects.create(name=f'Team{i}', password='x', tournament=self.tournament, owner=p)
        self.assertTrue(tournament_full(self.tournament))

    def test_tournament_not_full(self):
        self.assertFalse(tournament_full(self.tournament))

    def test_password_correct(self):
        team = self._make_team(password='secret')
        self.assertTrue(password_correct(team, 'secret'))
        self.assertFalse(password_correct(team, 'wrong'))


class JoinTeamFormTest(TestCase):
    def setUp(self):
        self.event = make_event()
        self.user = make_user()
        self.participant = Participant.objects.create(user=self.user, event=self.event)
        self.tournament = make_tournament(event=self.event, team_size=5)
        self.team = Team.objects.create(
            name='Alpha', password='secret', tournament=self.tournament, owner=self.participant
        )

    def test_correct_password_valid(self):
        form = JoinTeamForm({'password': 'secret'}, team=self.team, tournament=self.tournament)
        self.assertTrue(form.is_valid())

    def test_wrong_password_invalid(self):
        form = JoinTeamForm({'password': 'wrong'}, team=self.team, tournament=self.tournament)
        self.assertFalse(form.is_valid())

    def test_full_team_invalid(self):
        # Fill the team to capacity (team_size=5, add owner + 4 more)
        self.team.members.add(self.participant)
        for i in range(4):
            u = make_user(username=f'member{i}')
            p = Participant.objects.create(user=u, event=self.event)
            self.team.members.add(p)
        form = JoinTeamForm({'password': 'secret'}, team=self.team, tournament=self.tournament)
        self.assertFalse(form.is_valid())


class CreateTeamFormTest(TestCase):
    def setUp(self):
        self.event = make_event()
        self.tournament = make_tournament(event=self.event)

    def test_valid_form(self):
        form = CreateTeamForm({'name': 'Bravo', 'password': 'pass123'}, tournament=self.tournament)
        self.assertTrue(form.is_valid())

    def test_tournament_full_invalid(self):
        user = make_user()
        part = Participant.objects.create(user=user, event=self.event)
        for i in range(self.tournament.max_teams):
            Team.objects.create(name=f'Team{i}', password='x', tournament=self.tournament, owner=part)
        form = CreateTeamForm({'name': 'Extra', 'password': 'pass'}, tournament=self.tournament)
        self.assertFalse(form.is_valid())


