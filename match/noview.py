from django.shortcuts import render, redirect
import match.cons
# Create your views here.
from .models import Player, Game, PlayingGame, Hero, Herostats, Playerstats, Playerinterstats, Appearance
from django.utils import timezone
import datetime
import trueskill
import itertools
import math
import random


def removelsk(request):
    allgames = list(Game.objects.all())
    Game.objects.all().delete()
    for game in allgames:
        for i in range(1,10):
            if eval('game.player%d'%i) == 'lsk':
                exec('game.player%d=None'%i)
                exec('game.hero%d=None'%i)
        game.save()
    return

def recal_rank():
    all_players = {}
    all_heros = {}
    for name in match.cons.PLAYERS:
        all_players.update({name: trueskill.Rating(mu=25, sigma=8.333)})
    for hero in match.cons.ALL_HEROES:
        all_heros.update({hero: trueskill.Rating(mu=25, sigma=8.333)})
    games = Game.objects.all()
    def namelist_to_tslist(namelist):
        res = []
        for name in namelist:
            res.append(all_players[name])
        return res

    def updatedict(namelist, new_tslist):
        for name, rank in zip(namelist, new_tslist):
            all_players.update({name:rank})

    def namelist_to_tslist_hero(namelist):
        res = []
        for name in namelist:
            res.append(all_heros[name])
        return res

    def updatedict_hero(namelist, new_tslist):
        for name, rank in zip(namelist, new_tslist):
            all_heros.update({name:rank})
    for game in games:
        win_dict = game.winner_dict()
        lose_dict = game.loser_dict()
        winner_list_player = list(win_dict.keys())
        loser_list_player = list(lose_dict.keys())
        winner_tslist = namelist_to_tslist(winner_list_player)
        loser_tslist = namelist_to_tslist(loser_list_player)
        new_winner_tslist, new_loser_tslist = trueskill.rate([winner_tslist, loser_tslist], ranks=[0,1])
        updatedict(winner_list_player, new_winner_tslist)
        updatedict(loser_list_player, new_loser_tslist)

        winner_list_hero = list(win_dict.values())
        loser_list_hero = list(lose_dict.values())
        winner_tslist_hero = namelist_to_tslist_hero(winner_list_hero)
        loser_tslist_hero = namelist_to_tslist_hero(loser_list_hero)
        new_winner_tslist_hero, new_loser_tslist_hero = trueskill.rate([winner_tslist_hero, loser_tslist_hero], ranks=[0, 1])
        updatedict_hero(winner_list_hero, new_winner_tslist_hero)
        updatedict_hero(loser_list_hero, new_loser_tslist_hero)



    for name in match.cons.PLAYERS:
        p = Player.objects.get(name=name)
        rank = all_players[name]
        p.rank = rank.mu
        p.sigma = rank.sigma
        p.save()

    for hero in match.cons.ALL_HEROES:
        h = Hero.objects.get(name=hero)
        rank = all_heros[hero]
        h.rank = rank.mu
        h.sigma = rank.sigma
        h.save()
    return

def recal_winloses():
    games = Game.objects.all()
    wins = {}
    loses = {}
    herostats = {} # 第一层行(某个玩家) 第二层列(英雄)(某个玩家使用这一列英雄的数据)
    playerstats={} # 第一层行(某个英雄) 第二层列(玩家)(某个英雄被这一列玩家使用的数据)
    playerinterstats={} # 第一层行(某个玩家) 第二层列(玩家)(某个玩家和这一列玩家一起玩的数据)
    for player in match.cons.PLAYERS:
        wins[player]=0
        loses[player]=0
        herostats[player] = {}
        playerinterstats[player] = {}
        for hero in match.cons.ALL_HEROES:
            herostats[player].update({'%s_wins'%hero:0, '%s_loses'%hero:0})

    for hero in match.cons.ALL_HEROES:
        wins[hero]=0
        loses[hero]=0
        playerstats[hero] = {}
        for player in match.cons.PLAYERS:
            playerstats[hero].update({'%s_wins'%player:0, '%s_loses'%player:0})

    for player in match.cons.PLAYERS:
        for inplayer in match.cons.PLAYERS:
            playerinterstats[player].update({'%s_winswith'%inplayer:0,'%s_loseswith'%inplayer:0,
                                             '%s_winsagainst'%inplayer:0, '%s_losesagainst'%inplayer:0})
    for game in games:
        winner_dict = game.winner_dict()
        loser_dict = game.loser_dict()
        for player,hero in winner_dict.items():
            wins[player]+=1
            wins[hero]+=1
            playerstats[hero]['%s_wins'%player]+=1
            herostats[player]['%s_wins'%hero]+=1
        for player,hero in loser_dict.items():
            loses[player]+=1
            loses[hero] += 1
            playerstats[hero]['%s_loses'%player] += 1
            herostats[player]['%s_loses'%hero] += 1

        winner_list = game.winner_list()
        loser_list = game.loser_list()
        for winner in winner_list:
            for loser in loser_list:
                playerinterstats[winner]['%s_losesagainst'%loser] += 1
            for winner2 in winner_list:
                if winner != winner2:
                    playerinterstats[winner]['%s_winswith'%winner2] += 1
        for loser in loser_list:
            for loser2 in loser_list:
                if loser != loser2:
                    playerinterstats[loser]['%s_loseswith'%loser2] += 1
            for winner in winner_list:
                playerinterstats[loser]['%s_winsagainst'%winner] += 1

    # update players
    for player in match.cons.PLAYERS:
        p = Player.objects.get(name=player)
        p.wins = wins[player]
        p.loses = loses[player]
        p.save()

    # update heroes
    for hero in match.cons.ALL_HEROES:
        h = Hero.objects.get(name=hero)
        h.wins = wins[hero]
        h.loses = loses[hero]
        h.save()

    # update herostats
    for player in match.cons.PLAYERS:
        row = Herostats.objects.select_for_update().filter(name=player)
        row.update(**herostats[player])

    # update playerstats
    for hero in match.cons.ALL_HEROES:
        row = Playerstats.objects.select_for_update().filter(name=hero)
        row.update(**playerstats[hero])

    # update playerinterstats
    for player in match.cons.PLAYERS:
        row = Playerinterstats.objects.select_for_update().filter(name=player)
        row.update(**playerinterstats[player])

def recal_all():
    reset_player_and_heroes()
    print('reset OK!')
    recal_rank()
    print('recal_rank OK')
    recal_winloses()
    print('OK')
    return

def update_stats():
    game = Game.objects.last()
    winner_dict = game.winner_dict()
    loser_dict = game.loser_dict()
    def namelist_to_tslist_hero(namelist):
        res = []
        for name in namelist:
            h = Hero.objects.get(name=name)
            mu = h.rank
            sig = h.sigma
            res.append(trueskill.Rating(mu=mu, sigma=sig))
        return res

    def update_hero(namelist, new_tslist):
        for name, rank in zip(namelist, new_tslist):
            h = Hero.objects.get(name=name)
            h.rank = rank.mu
            h.sigma = rank.sigma
            h.save()

    winner_list_hero = list(winner_dict.values())
    loser_list_hero = list(loser_dict.values())
    winner_tslist_hero = namelist_to_tslist_hero(winner_list_hero)
    loser_tslist_hero = namelist_to_tslist_hero(loser_list_hero)
    new_winner_tslist_hero, new_loser_tslist_hero = trueskill.rate([winner_tslist_hero, loser_tslist_hero],
                                                                   ranks=[0, 1])
    update_hero(winner_list_hero, new_winner_tslist_hero)
    update_hero(loser_list_hero, new_loser_tslist_hero)

    for player, hero in winner_dict.items():
        #wins[player] += 1
        p = Player.objects.get(name=player)
        p.wins += 1
        p.save()
        #wins[hero] += 1
        h = Hero.objects.get(name=hero)
        h.wins += 1
        h.save()
        #playerstats[hero]['%s_wins' % player] += 1
        ps = Playerstats.objects.get(name=hero)
        setattr(ps, '%s_wins' % player, getattr(ps, '%s_wins' % player)+1)
        ps.save()
        #herostats[player]['%s_wins' % hero] += 1
        hs = Herostats.objects.get(name=player)
        setattr(hs, '%s_wins' % hero, getattr(hs, '%s_wins' % hero) + 1)
        hs.save()

    for player, hero in loser_dict.items():
        #loses[player] += 1
        p = Player.objects.get(name=player)
        p.loses += 1
        p.save()
        #loses[hero] += 1
        h = Hero.objects.get(name=hero)
        h.loses += 1
        h.save()
        #playerstats[hero]['%s_loses' % player] += 1
        ps = Playerstats.objects.get(name=hero)
        setattr(ps, '%s_loses' % player, getattr(ps, '%s_loses' % player) + 1)
        ps.save()
        #herostats[player]['%s_loses' % hero] += 1
        hs = Herostats.objects.get(name=player)
        setattr(hs, '%s_loses' % hero, getattr(hs, '%s_loses' % hero) + 1)
        hs.save()

    winner_list = game.winner_list()
    loser_list = game.loser_list()
    for winner in winner_list:
        for loser in loser_list:
            #playerinterstats[winner]['%s_losesagainst' % loser] += 1
            p = Playerinterstats.objects.get(name=winner)
            setattr(p, '%s_losesagainst' % loser, getattr(p, '%s_losesagainst' % loser) + 1)
            p.save()
        for winner2 in winner_list:
            if winner != winner2:
                #playerinterstats[winner]['%s_winswith' % winner2] += 1
                p = Playerinterstats.objects.get(name=winner)
                setattr(p, '%s_winswith' % winner2, getattr(p, '%s_winswith' % winner2) + 1)
                p.save()
    for loser in loser_list:
        for loser2 in loser_list:
            if loser != loser2:
                #playerinterstats[loser]['%s_loseswith' % loser2] += 1
                p = Playerinterstats.objects.get(name=loser)
                setattr(p, '%s_loseswith' % loser2, getattr(p, '%s_loseswith' % loser2) + 1)
                p.save()
        for winner in winner_list:
            #playerinterstats[loser]['%s_winsagainst' % winner] += 1
            p = Playerinterstats.objects.get(name=loser)
            setattr(p, '%s_winsagainst' % winner, getattr(p, '%s_winsagainst' % winner) + 1)
            p.save()
    return

def upto5(lst):
    return lst+['NO' for _ in range((5-len(lst)))]
def reset_player_and_heroes():
    Player.objects.all().delete()
    for name in match.cons.PLAYERS:
        Player.objects.create(name=name)
    Hero.objects.all().delete()
    for name in match.cons.ALL_HEROES:
        Hero.objects.create(name=name)
    Herostats.objects.all().delete()
    for name in match.cons.PLAYERS:
        Herostats.objects.create(name=name)
    Playerinterstats.objects.all().delete()
    for name in match.cons.PLAYERS:
        Playerinterstats.objects.create(name=name)
    Playerstats.objects.all().delete()
    for name in match.cons.ALL_HEROES:
        Playerstats.objects.create(name=name)

def get_rank_and_sigma_by_name(name):
    p = Player.objects.get(name=name)
    return p.rank, p.sigma
def update_player(name, new_rank, iswinner):
    if not name:
        return
    p = Player.objects.get(name=name)
    p.rank = new_rank.mu
    p.sigma = new_rank.sigma
    if iswinner == 0:
        p.wins += 1
    else:
        p.loses += 1
    p.save()

def team_with_condition(group1, group2, active_players):
    if len(group1)>len(group2):
        group1,group2 = group2,group1
    context = {}
    remain =list(set(active_players)-set(group1)-set(group2))
    mid = len(active_players)/2
    l_g1 = len(group1)
    if mid <= l_g1:
        return group1, group2
    rank_dict = {}
    for name in active_players:
        value, sigma = get_rank_and_sigma_by_name(name)
        rank_dict[name] = trueskill.Rating(mu=value, sigma=sigma)
    def win_probability(team1, team2):
        delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
        sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
        size = len(team1) + len(team2)
        denom = math.sqrt(size * (trueskill.BETA * trueskill.BETA) + sum_sigma)
        ts = trueskill.global_env()
        return ts.cdf(delta_mu / denom)
    # 检查分队水平
    def check(namelist1, namelist2):
        team1 = [rank_dict[n] for n in namelist1]
        team2 = [rank_dict[n] for n in namelist2]
        if len(namelist1) == len(namelist2):
            return 0.4 < win_probability(team1, team2) < 0.6
        else:
            return 0.25 < win_probability(team1, team2) < 0.75
    # 按照分数分队
    r = random.random()
    r_mid = mid - len(group1)
    if r < 0.8:
        n = 0
        while not check(group1+remain[:r_mid], group2+remain[r_mid:]):
            random.shuffle(remain)
            n += 1
            if n == 1000:
                break
    # 完全随机分队
    else:
        random.shuffle(remain)

    return group1+remain[:r_mid], group2+remain[r_mid:]
