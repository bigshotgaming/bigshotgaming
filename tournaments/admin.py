import challonge
from django.contrib import admin
from django.template.defaultfilters import slugify
from tournaments.models import Game, Tournament, Team, _challonge_auth

class GameAdmin(admin.ModelAdmin):
	pass

class TournamentAdmin(admin.ModelAdmin):
    actions = ['publish_and_start_tournament', 'add_to_challonge']

    def publish_and_start_tournament(self, request, queryset):
        for obj in queryset:
            _challonge_auth()
            challonge.tournaments.publish(tournament=obj.slugified_name)
            challonge.tournaments.start(tournament=obj.slugified_name)
            obj.is_active = False
            obj.has_started = True
            obj.save()

    def add_to_challonge(self, request, queryset):
        for obj in queryset:
            tournament = obj
            _challonge_auth()
            tournament_style = tournament.get_tournament_style().lower()
            tournament_name = "%s - %s" % (tournament.event.name, tournament.name)
            challonge.tournaments.create(name=tournament_name, url=tournament.slugified_name, tournament_type=tournament_style)

class TeamAdmin(admin.ModelAdmin):
    actions = ['add_to_challonge']

    def add_to_challonge(self, request, queryset):
        for obj in queryset:
            team = obj
            tournament = team.tournament
            _challonge_auth()
            challonge.participants.create(tournament=tournament.slugified_name, name=team)

admin.site.register(Game, GameAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Team, TeamAdmin)