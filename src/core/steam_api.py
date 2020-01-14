# For communication with the Steam API
import urllib.request
import json
# For getting the STEAM_API_KEY
from django.conf import settings

STEAM_SERVER = 'https://api.steampowered.com/'
USER_METHOD = 'ISteamUser/GetPlayerSummaries/v2'
INVENTORY_SERVER = 'https://steamcommunity.com/inventory/'


# Get the mandatory gamer info for a gamer
def getUserInfo(steamID, API_KEY=settings.STEAM_API_KEY):
    QUERY = STEAM_SERVER + USER_METHOD + '/?key=' + str(API_KEY) + '&format=json&steamids=' + str(steamID)
    player_object = json.load(urllib.request.urlopen(QUERY))
    return player_object


# Get the CS:GO inventory of a gamer
def getUserInventory(steamID, API_KEY=settings.STEAM_API_KEY, GAME_ID=730):
    QUERY = INVENTORY_SERVER + '/' + steamID + '/' + GAME_ID + '/2?l=english&count=5000'
    inventory_object = json.load(urllib.request.urlopen(QUERY))
    return inventory_object
