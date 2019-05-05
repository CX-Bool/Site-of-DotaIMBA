from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('start', views.start, name='start'),
    path('team', views.team, name='team'),
    path('playing', views.playing, name='playing'),
    path('result', views.result, name='result'),
    path('recal', views.recal, name='recal'),
    path('manual', views.manual_team, name='manual'),
    path('heroes', views.heroes, name='heroes'),
    path('games', views.games, name='games'),
    path('herodetail/<str:hero>', views.herodetail, name='herodetail'),
    path('playerdetail/<str:player>', views.playerdetail, name='playerdetail'),
]