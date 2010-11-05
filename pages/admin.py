from django.contrib import admin
from .models import Section, Post

class SectionAdmin(admin.ModelAdmin):
    filter_horizontal = ('posts',)
    prepopulated_fields = {'url': ('name',)}
    
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'is_published')

admin.site.register(Post, PostAdmin)
admin.site.register(Section, SectionAdmin)
