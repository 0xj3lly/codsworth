import json
import time
import re
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

def getAllGames(userID):
    url = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/'
    params = dict(key=STEAM_KEY,
                  steamid=userID,
                  include_appinfo=True,
                  include_played_free_games=True,
                  appids_filter=None,
                  include_free_sub=False
                 )
    r = requests.get(url, params)
    data = json.loads(r.content)
    return data['response']['games']

def getMutualGames(sUsers):
    allGames = []
    mutualGames = []
    for member in sUsers:
        uid = member
        games = getAllGames(uid)
        for game in games:
            allGames.append(game['name'])
    for game in allGames:
        if allGames.count(game) == len(sUsers):
            mutualGames.append(game)
    return set(mutualGames)

def getRecentGames(userID, howMany='0'):
    url = 'https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/'
    params = dict(key=STEAM_KEY, steamid=userID, count=howMany)
    r = requests.get(url, params)
    data = r.content
    data = json.loads(data)
    recentGames = []

    for game in data['response']['games']:
        recentGames.append(game['name'])
    return recentGames

def getTotalPlaytime(user):
    userID = ''
    for key, value in users.items():
        if user.lower() == value[0].lower():
            userID = key
        elif user.lower() == value[1].lower():
            userID = key
        else:
            pass
    url = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/'
    params = dict(key=STEAM_KEY,
                  steamid=userID,
                  include_appinfo=True,
                  include_played_free_games=True,
                  appids_filter=None,
                  include_free_sub=False
                 )
    r = requests.get(url, params)
    data = json.loads(r.content)
    totalMinutes = 0
    for game in data['response']['games']:
        totalMinutes += game['playtime_forever']
    return totalMinutes // 60

def syncVideo(url):
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
    driver.find_element_by_css_selector('#table_permissions > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(2) > div:nth-child(1)').click()
    driver.find_element_by_css_selector('#table_permissions > tbody:nth-child(1) > tr:nth-child(6) > td:nth-child(2) > div:nth-child(1)').click()
    driver.quit()
    return room

def accountValue(user):
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
    aValue = text[7].replace('$', '')
    aValue = aValue.replace(',', '')
    aValue = currConv.convert(float(aValue), 'USD', 'GBP')
    driver.quit()
    return round(aValue, 2)

def accountShame(user):
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
    gameCount = text[0].split(' ')
    gameCount = gameCount[3]
    value = text[2].split(' ')
    value = value[7].replace('$', '')
    value = value.replace(',', '')
    value = currConv.convert(float(value), 'USD', 'GBP')
    driver.quit()
    return gameCount, round(value, 2)

def members(ctx):
    memids = []
    for member in ctx.channel.members:
        if not member.bot:
            memids.append(member.name)
    return memids

@client.command()
async def on_command_error(ctx, error):
    await ctx.send('I can\'t believe you\'ve done this')

@client.command()
async def hours(ctx, *arg):
    if arg:
        await ctx.send(f'{arg[0].title()} has played {getTotalPlaytime(arg[0])} hours in steam')
    else:
        await ctx.send(f'{ctx.message.author.name} has played {getTotalPlaytime(ctx.message.author.name)} hours in steam')

@client.command()
async def value(ctx, *arg):
    if arg:
        await ctx.send('Working on it...')
        await ctx.send(f'{arg[0].title()}\'s steam account is worth £{accountValue(arg[0])}')
    else:
        await ctx.send('Working on it...')
        await ctx.send(f'{ctx.message.author.name}\'s steam account is worth £{accountValue(ctx.message.author.name)}')

@client.command()
async def shame(ctx, *arg):
    if arg:
        await ctx.send('Working on it...')
        result = accountShame(arg[0])
        await ctx.send(f'{arg[0].title()} has {result[0]} unplayed games in steam worth £{result[1]}')
    else:
        result = accountShame(ctx.message.author.name)
        await ctx.send('Working on it...')
        await ctx.send(f'{ctx.message.author.name} has {result[0]} unplayed games in steam worth £{result[1]}')

@client.command()
async def games(ctx, *arg):
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
    result = sorted(getMutualGames(ids))
    message = '\n'.join(result)
    for chunk in [message[i:i+2000] for i in range(0, len(message), 2000)]:
        await ctx.send(f'{chunk}')

@client.command()
async def sync(ctx, arg):
    await ctx.send('Getting the room ready...')
    await ctx.send(f'{syncVideo(arg)}')

@client.command()
async def commands(ctx):
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
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)

client.loop.create_task(list_servers())
client.run(DISCORD_KEY)
