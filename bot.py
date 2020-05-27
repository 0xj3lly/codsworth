"""
Discord bot Codsworth - Provides multiple features mainly focused around steam
"""
import json
import os
import requests
import discord
from discord.ext.commands import Bot
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from currency_converter import CurrencyConverter

DISCORD_KEY = os.environ.get('DISCORD_KEY')
STEAM_KEY = os.environ.get('STEAM_KEY')
BOT_PREFIX = ("?", "!")

fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.headless = True

currConv = CurrencyConverter()

users = {
    '76561198215710585':['a123oclock', 'Elliot'],
    '76561198007900549':['RyansanH', 'Ryan'],
    '76561198067162709':['MattWay', 'Matt'],
    '76561198046451850':['Harpoon Harry', 'Harry'],
    '76561197979173212':['DavidB', 'David']
}

client = Bot(command_prefix=BOT_PREFIX)

def get_all_games(user_id):
    """
    Gets all Steam games for a given user
    """
    url = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/'
    params = dict(key=STEAM_KEY,
                  steamid=user_id,
                  include_appinfo=True,
                  include_played_free_games=True,
                  appids_filter=None,
                  include_free_sub=False
                 )
    r = requests.get(url, params)
    data = json.loads(r.content)
    return data['response']['games']

def get_mutual_games(s_users):
    """
    Gets all the mutually owned Steam games for given users
    """
    all_games = []
    mutual_games = []
    for member in s_users:
        uid = member
        games = get_all_games(uid)
        for game in games:
            all_games.append(game['name'])
    for game in all_games:
        if all_games.count(game) == len(s_users):
            mutual_games.append(game)
    return set(mutual_games)

def get_recent_games(user_id, how_many='0'):
    """
    Gets the recently played Steam games for a given user
    """
    url = 'https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/'
    params = dict(key=STEAM_KEY, steamid=user_id, count=how_many)
    r = requests.get(url, params)
    data = r.content
    data = json.loads(data)
    recent_games = []

    for game in data['response']['games']:
        recent_games.append(game['name'])
    return recent_games

def get_total_playtime(user):
    """
    Gets the total amount of hours played in Steam for a given user
    """
    user_id = ''
    for key, value in users.items():
        if user.lower() == value[0].lower():
            user_id = key
        elif user.lower() == value[1].lower():
            user_id = key
        else:
            pass
    url = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/'
    params = dict(key=STEAM_KEY,
                  steamid=user_id,
                  include_appinfo=True,
                  include_played_free_games=True,
                  appids_filter=None,
                  include_free_sub=False
                 )
    r = requests.get(url, params)
    data = json.loads(r.content)
    total_minutes = 0
    for game in data['response']['games']:
        total_minutes += game['playtime_forever']
    return total_minutes // 60

def sync_video(url):
    """
    Creates a room in sync-tube.de for a given youtube URL
    """
    driver = webdriver.Firefox(options=fireFoxOptions)
    sync = "https://sync-tube.de/create"
    driver.get(sync)
    room = driver.current_url
    WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.CSS_SELECTOR,
                                                                   'input.searchInput')))
    element = driver.find_element_by_css_selector('input.searchInput')
    element.click()
    element.send_keys(url)
    element.send_keys(Keys.ENTER)
    driver.find_element_by_id('btnSettings').click()
    driver.find_element_by_css_selector(\
        '#table_permissions > tbody:nth-child(1) > \
        tr:nth-child(5) > td:nth-child(2) > div:nth-child(1)'\
            ).click()
    driver.find_element_by_css_selector(\
        '#table_permissions > tbody:nth-child(1) > \
        tr:nth-child(6) > td:nth-child(2) > div:nth-child(1)'\
            ).click()
    driver.quit()
    return room

def account_value(user):
    """
    Gets the current value of all the games for a given Steam account
    (web scrape not API)
    """
    driver = webdriver.Firefox(options=fireFoxOptions)
    url = "https://steamdiscovery.com/calculator.php?q="
    uid = ''
    for key, value in users.items():
        if user.lower() == value[0].lower():
            uid = key
        elif user.lower() == value[1].lower():
            uid = key
        else:
            pass
    driver.get(f'{url}{uid}')
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((\
            By.CSS_SELECTOR,\
            'div.alert.alert-info')))
    element = driver.find_element_by_css_selector(\
            'div.alert.alert-info')
    paragraphs = element.find_elements_by_tag_name('p')
    text = paragraphs[0].text
    text = text.split('\n')
    text = text[0].split(' ')
    a_value = text[7].replace('$', '')
    a_value = a_value.replace(',', '')
    a_value = currConv.convert(float(a_value), 'USD', 'GBP')
    driver.quit()
    return round(a_value, 2)

def account_shame(user):
    """
    Gets the current value of all the Steam games
    that have never been played for a given account
    """
    driver = webdriver.Firefox(options=fireFoxOptions)
    url = "https://steamdiscovery.com/calculator.php?q="
    uid = ''
    for key, value in users.items():
        if user.lower() == value[0].lower():
            uid = key
        elif user.lower() == value[1].lower():
            uid = key
        else:
            pass
    driver.get(f'{url}{uid}&pile-of-shame')
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((\
            By.CSS_SELECTOR,\
            'div.alert.alert-info')))
    element = driver.find_element_by_css_selector('div.alert.alert-info')
    text = element.text
    text = text.split('\n')
    game_count = text[0].split(' ')
    game_count = game_count[3]
    value = text[2].split(' ')
    value = value[7].replace('$', '')
    value = value.replace(',', '')
    value = currConv.convert(float(value), 'USD', 'GBP')
    driver.quit()
    return game_count, round(value, 2)

def members(ctx):
    """
    Gets the current members of the discord channel
    """
    memids = []
    for member in ctx.channel.members:
        if not member.bot:
            memids.append(member.name)
    return memids

@client.command()
async def on_command_error(ctx, error):
    """
    Default Discord error message
    """
    await ctx.send('I can\'t believe you\'ve done this')

@client.command()
async def hours(ctx, *arg):
    """
    Gets the total hours by calling the function
    """
    if arg:
        await ctx.send(f'{arg[0].title()} has played {get_total_playtime(arg[0])} hours in steam')
    else:
        await ctx.send(f'{ctx.message.author.name} has played {get_total_playtime(ctx.message.author.name)} hours in steam')

@client.command()
async def value(ctx, *arg):
    """
    Gets the value by calling the function
    """
    if arg:
        await ctx.send('Working on it...')
        await ctx.send(f'{arg[0].title()}\'s steam account is worth £{account_value(arg[0])}')
    else:
        await ctx.send('Working on it...')
        await ctx.send(f'{ctx.message.author.name}\'s steam account is worth £{account_value(ctx.message.author.name)}')

@client.command()
async def shame(ctx, *arg):
    """
    Gets the pile of shame by calling the fucntion
    """
    if arg:
        await ctx.send('Working on it...')
        result = account_shame(arg[0])
        if ctx.message.guild.name == "Watching Over":
            await ctx.send(f'{arg[0].title()} has {result[0]} unplayed games in steam worth £{result[1]} <:MattShock:715219402760388680>')
        else:
            await ctx.send(f'{arg[0].title()} has {result[0]} unplayed games in steam worth £{result[1]}')
    else:
        result = account_shame(ctx.message.author.name)
        await ctx.send('Working on it...')
        await ctx.send(f'{ctx.message.author.name} has {result[0]} unplayed games in steam worth £{result[1]}')

@client.command()
async def games(ctx, *arg):
    """
    Gets the steam games by calling the function
    """
    mems = ''
    if arg:
        mems = arg
    else:
        mems = members(ctx)
    ids = []
    for key, value in users.items():
        for mem in mems:
            if mem.lower() == value[0].lower():
                ids.append(key)
            elif mem.lower() == value[1].lower():
                ids.append(key)
            else:
                pass
    result = sorted(get_mutual_games(ids))
    message = '\n'.join(result)
    for chunk in [message[i:i+2000] for i in range(0, len(message), 2000)]:
        await ctx.send(f'{chunk}')

@client.command()
async def sync(ctx, arg):
    """
    Gets the sync room by calling the function
    """
    await ctx.send('Getting the room ready...')
    await ctx.send(f'{sync_video(arg)}')

@client.command()
async def commands(ctx):
    """
    Help but cleaner
    """
    await ctx.send('''
!games                        - List all the games owned by members of this server
!games [names]       - List all the games owned by the people you specify
!hours                          - Shows how much of your life you've wasted
!hours [name]           - Shows how much time they have wasted
!value [name]           - Shows how much the games in their steam account is worth
!shame [name]           - Shows how much the games they've never played are worth
!sync [url]                   - Create a room to watch a toutube video together 
    ''')

async def list_servers():
    """
    Required for discord bot
    """
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)

client.loop.create_task(list_servers())
client.run(DISCORD_KEY)
