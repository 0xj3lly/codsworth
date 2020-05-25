import discord
from discord.ext.commands import Bot
import requests
import json
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



DISCORD_KEY = os.environ.get('DISCORD_KEY')
STEAM_KEY = os.environ.get('STEAM_KEY')
BOT_PREFIX = ("?", "!")


fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.set_headless()



users = {
    '76561198215710585':['a123oclock','Elliot'],
    '76561198007900549':['RyansanH','Ryan'],
    '76561198067162709':['MattWay','Matt'],
    '76561198046451850':['Harpoon Harry','Harry'],
    '76561197979173212':['DavidB','David']
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
    return(data['response']['games'])


def getMutualGames(members=users):
    allGames = []
    mutualGames = []
    for member in members:
        uid = member
        games = getAllGames(uid)
        for game in games:
            allGames.append(game['name'])
    for game in allGames:
        if allGames.count(game) == len(members):
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



def getAccountValue(user):
    url = 'https://store.steampowered.com/api/appdetails'
    value = 0
    for game in getAllGames():
        params = dict(appids=game['appid'])
        r = requests.get(url, params)
        time.sleep(0.2)
        data = json.loads(r.content)
        app = data[f"{game['appid']}"]
        if app['success']:
            if app['data']['is_free']:
                continue
            else:
                value += app['data']['price_overview']['initial']
        else:
            break

    value = value / 100
    return value

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
    return(totalMinutes // 60)

driver = webdriver.Firefox(options=fireFoxOptions)
def syncVideo(url):
    sync = "https://sync-tube.de/create"
    driver.get(sync)
    room = driver.current_url
    WebDriverWait(driver,5).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input.searchInput')))
    element = driver.find_element_by_css_selector('input.searchInput')
    element.click()
    element.send_keys(url)
    element.send_keys(Keys.ENTER)
    driver.find_element_by_id('btnSettings').click()
    driver.find_element_by_css_selector('#table_permissions > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(2) > div:nth-child(1)').click()
    driver.find_element_by_css_selector('#table_permissions > tbody:nth-child(1) > tr:nth-child(6) > td:nth-child(2) > div:nth-child(1)').click()
    driver.quit()
    return room
    
    

def members(ctx):
    memids = []
    for guild in client.guilds:
        for member in guild.members:
            if not member.bot:
                memids.append(member.name)
    return memids

@client.command()
async def on_command_error(ctx, error):
    await ctx.send(f'I can\'t believe you\'ve done this')

@client.command()
async def hours(ctx, *arg):
    if arg:
        await ctx.send(f'{arg[0].title()} has played {getTotalPlaytime(arg[0])} hours in steam')
    else:
        await ctx.send(f'{ctx.message.author.name} has played {getTotalPlaytime(ctx.message.author.name)} hours in steam')

@client.command()
async def games(ctx):
    mems = members(ctx)
    ids = {}
    for item in users.items():
        if item[1][0] in mems:
            ids.update({item[0]:item[1]})
    result = sorted(getMutualGames(ids))
    message = '\n'.join(result)
    for chunk in [message[i:i+2000] for i in range(0, len(message), 2000)]:
        await ctx.send(f'{chunk}')
    

""" @client.event
async def sync(message):
    pattern = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"
    ytLink = re.split(pattern, message.content)
    print(ytLink)
    if ytLink:
        await ctx.send(f'{syncvideo(ytLink[0])}')
    else:
        pass """

@client.command()
async def sync(ctx, arg):
    await ctx.send('Getting the room ready...')
    await ctx.send(f'{syncVideo(arg)}')

@client.command()
async def commands(ctx):
    await ctx.send('''
!games        - List all the games owned by members of this server
!hours        - Shows how much of your life you've wasted
!hours [name] - Shows how much time they have wasted
!sync [url]   - Create a room to watch a toutube video together
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
