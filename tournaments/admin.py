from django.contrib import admin
from tournaments.models import Game, Tournament, Team

class GameAdmin(admin.ModelAdmin):
	pass

class TournamentAdmin(admin.ModelAdmin):
	pass

class TeamAdmin(admin.ModelAdmin):
	pass

admin.site.register(Game, GameAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Team, TeamAdmin)