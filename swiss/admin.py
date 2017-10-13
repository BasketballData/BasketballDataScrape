from django.contrib import admin
from swiss.models import SwissGame

class SwissGameAdmin(admin.ModelAdmin):
    list_display = ['home_name', 'away_name']
    ordering = ('home_name',)
admin.site.register(SwissGame, SwissGameAdmin)