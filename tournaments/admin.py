from tournaments.tasks import publish_and_start_tournament
from django.contrib import admin
from django.template.defaultfilters import slugify
from tournaments.models import Game, Tournament, Team

class GameAdmin(admin.ModelAdmin):
	pass

class TournamentAdmin(admin.ModelAdmin):
    actions = ['pub_tournament']

    def pub_tournament(self, request, queryset):
        for obj in queryset:
            publish_and_start_tournament.delay(obj)
            obj.is_active = False
            obj.has_started = True
            obj.save()

    pub_tournament.short_description = 'Publish and start tournament'

class TeamAdmin(admin.ModelAdmin):
    pass


admin.site.register(Game, GameAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Team, TeamAdmin)