from django.db import models
import datetime
import match.cons
# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
    rank = models.FloatField(default=25.0) # trueskill mu default
    sigma = models.FloatField(default=8.333) # trueskill sigma default
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    def win_rate(self):
        if self.wins+self.loses == 0:
            return 0
        return 1.0*self.wins/(self.wins+self.loses)
    def games_played(self):
        return self.wins+self.loses
    def rank_base(self):
        return  self.rank - 2*self.sigma

class Hero(models.Model):
    name = models.CharField(max_length=32, primary_key=True)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)
    rank = models.FloatField(default=25.0,null=True)  # trueskill mu default
    sigma = models.FloatField(default=8.333,null=True)  # trueskill sigma default
    def rank_base(self):
        return  self.rank - 3*self.sigma
    def win_rate(self):
        if self.wins+self.loses == 0:
            return 0.0
        return 1.0*self.wins/(self.wins+self.loses)
    def appearance(self):
        return self.wins+self.loses
    def __str__(self):
        return self.name

RESULTS = (
    ('W', 'Radiant Win'),
    ('D', 'Draw'),
    ('L', 'Dire Win'),
)
PLAYERS=(('ch','ch'),('cx','cx'),('fwk','fwk'),('hcd','hcd'),('hlk','hlk'),('lhy','lhy'),('lq','lq'),
         ('lsk','lsk'),('lwq','lwq'),('mzh','mzh'),('pc','pc'),('qfy','qfy'),('yzh','yzh'))
class Game(models.Model):
    result = models.CharField(max_length=1, choices=RESULTS)
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    player1 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player2 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player3 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player4 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player5 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player6 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player7 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player8 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player9 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player10 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    hero1 = models.CharField(max_length=32, blank=True, null=True)
    hero2 = models.CharField(max_length=32, blank=True, null=True)
    hero3 = models.CharField(max_length=32, blank=True, null=True)
    hero4 = models.CharField(max_length=32, blank=True, null=True)
    hero5 = models.CharField(max_length=32, blank=True, null=True)
    hero6 = models.CharField(max_length=32, blank=True, null=True)
    hero7 = models.CharField(max_length=32, blank=True, null=True)
    hero8 = models.CharField(max_length=32, blank=True, null=True)
    hero9 = models.CharField(max_length=32, blank=True, null=True)
    hero10 = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return self.finish_time.replace(tzinfo=datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

    def winner(self):
        if self.result == 'W':
            return 'radiant'
        else:
            return 'dire'

    def radiant_result(self):
        if self.result == 'W':
            return '胜利'
        else:
            return ''
    def dire_result(self):
        if self.result == 'L':
            return '胜利'
        else:
            return ''

    def winner_list(self):
        if self.result == 'W':
            return self.radiant_players()
        else:
            return self.dire_players()
    def loser_list(self):
        if self.result == 'L':
            return self.radiant_players()
        else:
            return self.dire_players()
    def active_players(self):
        res = []
        for i in range(1, 11):
            exec('res.append(self.player%d)' % i)
        return [name for name in res if name]
    def radiant_players(self):
        res = []
        for i in range(1, 6):
            exec('res.append(self.player%d)' % i)
        return [name for name in res if name]
    def dire_players(self):
        res = []
        for i in range(6, 11):
            exec('res.append(self.player%d)' % i)
        return [name for name in res if name]

    def radiant_dict(self):
        res = {}
        for i in range(1, 6):
            if getattr(self, 'player%d'%i):
                res[getattr(self, 'player%d'%i)] = getattr(self, 'hero%d'%i)
        return res
    def dire_dict(self):
        res = {}
        for i in range(6, 11):
            if getattr(self, 'player%d'%i):
                res[getattr(self, 'player%d'%i)] = getattr(self, 'hero%d'%i)
        return res
    def winner_dict(self):
        if self.result == 'W':
            return self.radiant_dict()
        else:
            return self.dire_dict()
    def loser_dict(self):
        if self.result == 'L':
            return self.radiant_dict()
        else:
            return self.dire_dict()
class PlayingGame(models.Model):
    start_time = models.DateTimeField()
    player1 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player2 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player3 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player4 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player5 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player6 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player7 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player8 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player9 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)
    player10 = models.CharField(max_length=16, blank=True, null=True, choices=PLAYERS)

    def __str__(self):
        return self.start_time.strftime('%Y-%m-%d %H:%M:%S')

class Herostats(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
    for label in match.cons.ALL_HEROES:
        locals()[label + '_wins'] = models.IntegerField(default=0)
        locals()[label + '_loses'] = models.IntegerField(default=0)
    del locals()['label']

    def cal_winrate(self, name):
        appr = self.cal_appearance(name)
        if appr:
            return 1.0*getattr(self, name+'_wins')/appr
        else:
            return 0.0

    def cal_appearance(self, name):
        return getattr(self, name+'_wins')+getattr(self, name+'_loses')

class Playerstats(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
    for label in match.cons.PLAYERS:
        locals()[label + '_wins'] = models.IntegerField(default=0)
        locals()[label + '_loses'] = models.IntegerField(default=0)
    del locals()['label']
    def cal_winrate(self, name):
        appr = self.cal_appearance(name)
        if appr:
            return 1.0*getattr(self, name+'_wins')/appr
        else:
            return 0.0

    def cal_appearance(self, name):
        return getattr(self, name+'_wins')+getattr(self, name+'_loses')

class Playerinterstats(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
    for label in match.cons.PLAYERS:
        locals()[label + '_winswith'] = models.IntegerField(default=0)
        locals()[label + '_loseswith'] = models.IntegerField(default=0)
        locals()[label + '_winsagainst'] = models.IntegerField(default=0)
        locals()[label + '_losesagainst'] = models.IntegerField(default=0)
    del locals()['label']
    def cal_winrate(self, name, side):
        appr = self.cal_appearance(name,side)
        if appr:
            return 1.0*getattr(self, name+'_wins'+side)/appr
        else:
            return 0.0
    def cal_appearance(self, name,side):
        return getattr(self, name+'_wins'+side)+getattr(self, name+'_loses'+side)

class Appearance(models.Model):
    name = models.CharField(max_length=16, primary_key=True)
    for label in match.cons.PLAYERS:
        locals()[label + '_plays'] = models.IntegerField(default=0)
    del locals()['label']