from django.contrib import admin
from schedule.models import ScheduleItem

class ScheduleItemAdmin(admin.ModelAdmin):
    pass

admin.site.register(ScheduleItem, ScheduleItemAdmin)
