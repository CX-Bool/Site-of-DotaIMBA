from django.contrib import admin

# Register your models here.
from .models import *

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'rank', 'sigma', 'wins', 'loses', 'win_rate')
admin.site.register(Player, PlayerAdmin)

class HeroAdmin(admin.ModelAdmin):
    list_display = ('name', 'wins', 'loses')
admin.site.register(Hero, HeroAdmin)

class GameAdmin(admin.ModelAdmin):
    list_display = ('finish_time', 'winner_dict', 'loser_dict')
admin.site.register(Game, GameAdmin)

admin.site.register(PlayingGame)

admin.site.register(Herostats)

admin.site.register(Playerstats)

admin.site.register(Playerinterstats)

