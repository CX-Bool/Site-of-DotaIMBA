from django.shortcuts import render, redirect

# Create your views here.
from .models import *
from django.utils import timezone
import match.noview
import datetime
import trueskill
import itertools
import math
import random

PLAYERS = ['ch', 'cx', 'fwk', 'hcd', 'hlk', 'lhy', 'lq', 'lsk', 'lwq', 'mzh', 'pc', 'qfy']
PLAYER_NUM_ERR = None
RANGES = {
    'range3': range(1, 4),
    'range4': range(1, 5),
    'range5': range(1, 6),
    'range10': range(1, 11),
    'range5p':range(6,11),
}
HERO_NAME = {
    'hero11': ['伐木机', '全能', '兽王', '圣教军', '大地', '大牛', '小小', '小牛', '山丘', '斯温', '熊猫', '船长'],
    'hero12': ['人马', '军团', '刚背', '发条', '大树', '沙王', '海民', '潮汐', '炼金', '瓦王', '神灵', '龙骑'],
    'hero13': ['DIABLO', '大屁股', '大鱼', '小狗', '狼人', '猛犸', '白牛', '精灵', '风骑士'],
    'hero14': ['saber', '噩梦骑士', '夜魔', '屠夫', '巫妖王', '斧王', '末日', '死骑', '混沌', '肉山', '骷髅王', '龙卵领主'],
    'hero21': ['剑圣', '娜迦', '敌法', '暗夜刺客', '暗夜哨兵', '月骑', '水人', '火枪', '白虎', '隐刺'],
    'hero22': ['vs', '圣堂', '小黑', '巨魔', '德鲁伊', '拍拍', '掠夺者', '火猫', '美杜莎', '虚空','猎魔人'],
    'hero23': ['剧毒', '小强', '小鱼', '幻刺', '猴子', '电棍', '虚灵猎手', '蜘蛛', '赏金', '骨弓'],
    'hero24': ['2B', 'TB', '地狱诗人', '幽鬼', '影魔', '机枪', '毒龙', '蚂蚁', '血魔', '远古飞蛇'],
    'hero31': ['先知', '冰女', '双头龙', '咏叹者', '圣骑士', '大天使', '天怒', '宙斯', '帕克', '火女', '狮鹫', '蓝猫'],
    'hero32': ['TK', '光法', '冰凤凰', '大魔导师', '小鹿', '沉默', '炸弹', '萨尔', '萨满', '蓝胖', '风行', '飞机'],
    'hero33': ['冰霜巨龙', '凤凰', '卡尔', '女王', '巫医', '戴泽', '死灵法', '老鹿', '莱恩', '蝙蝠', '谜团'],
    'hero34': ['DP', 'DS', '冰魂', '巫妖', '术士', '死灵飞龙', '毒狗', '痛苦之源', '骨法', '黑鸟'],
}

def index(request):
    player_list = Player.objects.order_by('-rank')
    played = player_list.filter(wins__gt=0)|player_list.filter(loses__gt=0)
    played = sort_players(played)
    unplayed = player_list.filter(wins=0).filter(loses=0)

    top1 = played[0].name
    top2 = played[1].name
    top3 = played[2].name
    time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

    context = {'player_list': played, 'time': time,
               'top1':top1, 'top2':top2, 'top3':top3, 'unplayed_list':unplayed}
    return render(request, 'match/index.html', context)

def sort_players(player_queryset):
    player_list=list(player_queryset)
    n = len(player_list)
    for i in range(n):
        for j in range(n-i-1):
            if player_list[j].rank_base() < player_list[j+1].rank_base():
                player_list[j], player_list[j+1] = player_list[j+1], player_list[j]
    return player_list

def start(request):
    if PlayingGame.objects.all().count():
        return playing(request)
    player_list = Player.objects.order_by('-rank')
    player_list = sort_players(player_list)
    time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

    context = {'player_list': player_list, 'time': time}
    if PLAYER_NUM_ERR:
        context['player_num_err'] = True
    if request.method == 'POST':
        context['default_players']=request.POST.get('default_players')
    # print(context['default_players'])
    return render(request, 'match/start.html', context)


def team(request):
    if request.method == 'GET':
        return start(request)
    if PlayingGame.objects.all().count():
        return playing(request)
    global PLAYER_NUM_ERR
    player_list = Player.objects.order_by('-rank')
    time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(
        datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
    # 获取选定的玩家
    active_players = []
    if request.method == 'POST':
        for name in PLAYERS:
            if request.POST.get(name, default='no') == 'go':
                active_players.append(name)
    # 检查玩家数量
    if not 4 <= len(active_players) <= 10:
        PLAYER_NUM_ERR = True
        return start(request)
    PLAYER_NUM_ERR = False

    # 从数据库获取玩家分数
    def get_rank_and_sigma_by_name(name):
        p = Player.objects.get(name=name)
        return p.rank, p.sigma
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

    mid = len(active_players) // 2
    if random.random()<0.2:

        # 根据分数进行分队
        rank_dict = {}
        for name in active_players:
            value, sigma = get_rank_and_sigma_by_name(name)
            rank_dict[name] = trueskill.Rating(mu=value, sigma=sigma)


        # 随机分队
        mid = len(active_players) // 2
        n = 0
        while not check(active_players[:mid], active_players[mid:]):
            random.shuffle(active_players)
            n += 1
            if n == 1000:
                break

    elif random.random()<0.3:
        random.shuffle(active_players)

    else:
        p_list = [Player.objects.get(name=name) for name in active_players]
        p_list = sort_players(p_list)
        top = p_list[:4]
        bot = p_list[4:]
        random.shuffle(top)
        mid_top = len(top)//2
        mid_bot = len(bot)//2
        random.shuffle(bot)
        ac_new = top[:mid_top]+bot[:mid_bot]+top[mid_top:]+bot[mid_bot:]
        active_players = [player.name for player in ac_new]

    context = {'player_list': player_list, 'time': time, 'active_players': active_players}

    if random.random() < 0.5:
        context['radiant'] = upto5(active_players[:mid])
        context['dire'] = upto5(active_players[mid:])
    else:
        context['radiant'] = upto5(active_players[mid:])
        context['dire'] = upto5(active_players[:mid])
    tt = context['radiant']+context['dire']
    range_no = []
    for i, name in enumerate(tt):
        if name == 'NO':
            range_no.append(i+1)
        else:
            range_no.append(0)
    context['range_no']=range_no


    context.update(HERO_NAME)
    context.update(RANGES)

    return render(request, 'match/team.html', context)

def playing(request):

    if PlayingGame.objects.all().count():#已经有正在进行的比赛
        playinggame = PlayingGame.objects.all()[0]
        radiant = []
        dire=[]
        for i in range(1,6):
            name = eval('playinggame.player%s'%i)
            radiant.append(name)
        for i in range(6,11):
            name = eval('playinggame.player%s' % i)
            dire.append(name)
        time = playinggame.start_time.strftime('%Y-%m-%d %H:%M:%S')
        active_players = radiant+dire
        if not 4 <= len(active_players)<=10:
            player_list = Player.objects.order_by('-rank')
            sub_context = {'player_list': player_list, 'player_num_err': True, 'default_players':active_players}
            return render(request, 'match/start.html', sub_context)
        def upto5(lst):
            return lst + ['NO' for _ in range((5 - len(lst)))]
        radiant = upto5(radiant)
        dire = upto5(dire)
        context = {'active_players':active_players, 'radiant':radiant, 'dire':dire, 'time':time}
        tt = context['radiant'] + context['dire']
        range_no = []
        for i, name in enumerate(tt):
            if name == 'NO':
                range_no.append(i + 1)
            else:
                range_no.append(0)
        context['range_no'] = range_no
        context.update(HERO_NAME)
        context.update(RANGES)
        return render(request, 'match/playing.html', context)
    else:
        if request.method == 'GET':
            return start(request)
        PlayingGame.objects.all().delete()
        start_time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(
            datetime.timezone(datetime.timedelta(hours=8)))

        current_game = PlayingGame.objects.create(start_time=start_time)
        context = {}
        time = start_time.strftime('%Y-%m-%d %H:%M:%S')
        if request.method == 'POST':
            active_players = eval(request.POST.get('active_players'))
            if not 4 <= len(active_players) <= 10:
                player_list = Player.objects.order_by('-rank')
                sub_context = {'player_list': player_list, 'player_num_err': True, 'default_players': active_players}
                return render(request, 'match/start.html', sub_context)
            radiant = eval(request.POST.get('radiant'))
            dire = eval(request.POST.get('dire'))
            context.update({'active_players':active_players, 'radiant':radiant, 'dire':dire, 'time':time})
            for i, name in enumerate(radiant):
                exec('current_game.player%s=radiant[%d]'%(i+1,i))
            for i, name in enumerate(dire):
                exec('current_game.player%s=dire[%d]' % (i + 6,i))
            current_game.save()
        tt = context['radiant'] + context['dire']
        range_no = []
        for i, name in enumerate(tt):
            if name == 'NO':
                range_no.append(i + 1)
            else:
                range_no.append(0)
        context['range_no'] = range_no
        context.update(HERO_NAME)
        context.update(RANGES)
        return render(request, 'match/playing.html', context)

def result(request):
    if request.method == 'GET':
        return redirect('/')
    if not PlayingGame.objects.all().count():
        return redirect('/')
    if request.method == 'POST':
        winner = request.POST.get('winner')
        if winner == 'no':
            PlayingGame.objects.all().delete()
            return redirect('/')

        active_players = eval(request.POST.get('active_players'))
        radiant = eval(request.POST.get('radiant'))
        dire = eval(request.POST.get('dire'))
        playinggame = PlayingGame.objects.all()[0]
        finish_time = datetime.datetime.now()

        if winner == 'radiant':
            result = 'W'
        elif winner == 'dire':
            result = 'L'
        else:
            result = 'D'
        # 对局记录
        game = Game.objects.create(result=result, start_time=playinggame.start_time, finish_time=finish_time)
        # 从数据库获取玩家分数
        def remove_no(lst):
            new_lst = lst[:]
            while new_lst[-1] == 'NO':
                new_lst.pop()
            return new_lst

        # 获取分队信息
        radiant_name = remove_no(radiant)
        dire_name = remove_no(dire)
        radiant_rank = [trueskill.Rating(mu=get_rank_and_sigma_by_name(name)[0], sigma=get_rank_and_sigma_by_name(name)[1]) for name in radiant_name]
        dire_rank = [trueskill.Rating(mu=get_rank_and_sigma_by_name(name)[0], sigma=get_rank_and_sigma_by_name(name)[1]) for name in dire_name]

        # 0:win 1:lose
        if winner == 'radiant':
            ranks=[0,1]
        elif winner == 'dire':
            ranks=[1,0]
        new_radiant_rank, new_dire_rank = trueskill.rate([radiant_rank, dire_rank], ranks=ranks)

        # 往数据库中更新Player表
        for name, new_rank in zip(radiant_name, new_radiant_rank):
            update_player_rank(name, new_rank)
        for name, new_rank in zip(dire_name, new_dire_rank):
            update_player_rank(name, new_rank)


        # 更新英雄胜场和对局记录Game
        for i in range(len(radiant_name)):
            exec("game.player%s = radiant_name[i]"%(i+1))
            exec("hname = request.POST.get('hero%s')"%(i+1))
            exec("game.hero%s = hname"%(i+1))
        for i in range(len(dire_name)):
            exec("game.player%s = dire_name[i]"%(i+6))
            exec("hname = request.POST.get('hero%s')"%(i+6))
            exec("game.hero%s = hname"%(i+6))

        game.save()
        PlayingGame.objects.all().delete()
        res = ['胜利','失败']
        match_info = '对局保存成功！\n'+str(radiant_name)+res[ranks[0]]+'\n'+str(dire_name)+res[ranks[1]]
        player_list = Player.objects.order_by('-rank')
        match.noview.update_stats()
        context={'default_players':active_players, 'match_info':match_info, 'player_list':player_list}

        return render(request, 'match/start.html', context)
ALL_HEROES=['伐木机', '全能', '兽王', '圣教军', '大地', '大牛', '小小', '小牛', '山丘', '斯温', '熊猫', '船长', '人马', '军团', '刚背', '发条', '大树', '沙王', '海民', '潮汐', '炼金', '瓦王', '神灵', '龙骑', 'DIABLO', '大屁股', '大鱼', '小狗', '狼人', '猛犸', '白牛', '精灵', '风骑士', 'saber', '噩梦骑士', '夜魔', '屠夫', '巫妖王', '斧王', '末日', '死骑', '混沌', '肉山', '骷髅王', '龙卵领主', '剑圣', '娜迦', '敌法', '暗夜刺客', '暗夜哨兵', '月骑', '水人', '火枪', '白虎', '隐刺', 'vs', '圣堂', '小黑', '巨魔', '德鲁伊', '拍拍', '掠夺者', '火猫','猎魔人', '美杜莎', '虚空', '剧毒', '小强', '小鱼', '幻刺', '猴子', '电棍', '虚灵猎手', '蜘蛛', '赏金', '骨弓', '2B', 'TB', '地狱诗人', '幽鬼', '影魔', '机枪', '毒龙', '蚂蚁', '血魔', '远古飞蛇', '先知', '冰女', '双头龙', '咏叹者', '圣骑士', '大天使', '天怒', '宙斯', '帕克', '火女', '狮鹫', '蓝猫', 'TK', '光法', '冰凤凰', '大魔导师', '小鹿', '沉默', '炸弹', '萨尔', '萨满', '蓝胖', '风行', '飞机', '冰霜巨龙', '凤凰', '卡尔', '女王', '巫医', '戴泽', '死灵法', '老鹿', '莱恩', '蝙蝠', '谜团', 'DP', 'DS', '冰魂', '巫妖', '术士', '死灵飞龙', '毒狗', '痛苦之源', '骨法', '黑鸟']

def recal(request):
    match.noview.recal_all()
    return redirect('/')

def herodetail(request, hero):
    p_list = []
    for player in PLAYERS:
        row = Herostats.objects.get(name=player)
        p = {'name':player}
        p.update({'wins':getattr(row, '%s_wins'%hero)})
        p.update({'loses': getattr(row, '%s_loses' % hero)})
        p.update({'winrate': row.cal_winrate(hero)})
        p.update({'appearance': row.cal_appearance(hero)})
        p_list.append(p)
    context = {'data':p_list, 'hero':hero}
    return render(request, 'match/herodetail.html', context)

def playerdetail(request, player):
    h_list = []
    for hero in ALL_HEROES:
        row = Playerstats.objects.get(name=hero)
        h = {'name':hero}
        h.update({'wins':getattr(row, '%s_wins'%player)})
        h.update({'loses': getattr(row, '%s_loses' % player)})
        h.update({'winrate': row.cal_winrate(player)})
        h.update({'appearance': row.cal_appearance(player)})
        h_list.append(h)
    p_list = []
    for pl in PLAYERS:
        row = Playerinterstats.objects.get(name=pl)
        p = {'name':pl}
        p.update({'wins_with':getattr(row, '%s_winswith'%player)})
        p.update({'loses_with': getattr(row, '%s_loseswith' % player)})
        p.update({'winrate_with': row.cal_winrate(player,'with')})
        p.update({'plays_with': row.cal_appearance(player,'with')})
        p.update({'wins_against': getattr(row, '%s_winsagainst' % player)})
        p.update({'loses_against': getattr(row, '%s_losesagainst' % player)})
        p.update({'winrate_against': row.cal_winrate(player,'against')})
        p.update({'plays_against': row.cal_appearance(player,'against')})
        p_list.append(p)
    context = {'data':h_list, 'player':player, 'playerdata':p_list}
    return render(request, 'match/playerdetail.html', context)


def manual_team(request):
    ra = eval(request.GET.get('radiant'))
    di = eval(request.GET.get('dire'))
    print(ra)
    print(di)
    radiant = upto5(ra)
    dire = upto5(di)
    active_players = ra+di
    context = {'radiant':radiant, 'dire':dire, 'active_players':active_players}
    print(context)
    return render(request, 'match/team.html', context)

def heroes(request):
    herolist = Hero.objects.all()
    context={'herolist':herolist}
    return render(request, 'match/heroes.html', context)

def games(request):
    gamelist = Game.objects.all().order_by('-finish_time')
    context = {'gamelist':gamelist}
    context.update(RANGES)
    return render(request, 'match/games.html', context)

def upto5(lst):
    return lst+['NO' for _ in range((5-len(lst)))]
def reset_player_and_heroes():
    Player.objects.all().delete()
    for name in PLAYERS:
        Player.objects.create(name=name)
    Hero.objects.all().delete()
    for name in ALL_HEROES:
        Hero.objects.create(name=name)
def get_rank_and_sigma_by_name(name):
    p = Player.objects.get(name=name)
    return p.rank, p.sigma
def update_player_rank(name, new_rank):
    if not name:
        return
    p = Player.objects.get(name=name)
    p.rank = new_rank.mu
    p.sigma = new_rank.sigma
    p.save()
