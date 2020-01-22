# For communication with the Steam API
import urllib.request
import json
# For getting the STEAM_API_KEY
from django.conf import settings
from .models import Gamer, ItemType, ItemInstance
from django.shortcuts import get_object_or_404

# Official Steam Servers
STEAM_SERVER = 'https://api.steampowered.com/'
USER_METHOD = 'ISteamUser/GetPlayerSummaries/v2'
INVENTORY_SERVER = 'https://steamcommunity.com/inventory/'

# CSGOFloats API Server (https://csgofloat.com)
FLOAT_SERVER = 'https://api.csgofloat.com/?url='


# Get the mandatory gamer info for a gamer
def getUserInfo(steamID, API_KEY=settings.STEAM_API_KEY):
    QUERY = STEAM_SERVER + USER_METHOD + '/?key=' + str(API_KEY) + '&format=json&steamids=' + str(steamID)
    player_object = json.load(urllib.request.urlopen(QUERY))
    return player_object['response']['players'][0]


def getInstanceData(inventory_object, instance_id):
    for key in inventory_object['descriptions']:
        if key['instanceid'] == instance_id:
            return key


def getFloat(inspect_link):
    QUERY = FLOAT_SERVER + inspect_link
    float_object = json.load(urllib.request.urlopen(QUERY))
    if 'error' in float_object:
        return False
    return float_object


def getSubTag(scope, search_key, search_value):
    for tag in scope:
        if tag.search_key == search_value:
            return tag
    return False


# Get the CS:GO inventory of a gamer
def updateInventory(steamID, GAME_ID=730):
    gamer = get_object_or_404(Gamer, steamid=steamID)
    QUERY = INVENTORY_SERVER + str(steamID) + '/' + str(GAME_ID) + '/2?l=english&count=5000'
    inventory_object = json.load(urllib.request.urlopen(QUERY))
    if 'success' in inventory_object:
        for item in inventory_object['assets']:
            if item['instanceid'] == 0:
                pass
            else:
                instance_data = getInstanceData(inventory_object, item['instanceid'])
                link = instance_data['actions'][0]['link'].replace("%owner_steamid%", str(steamID)).replace("%assetid%", str(item['instanceid']))
                while (True):
                    item_infos = getFloat(link)
                    if item_infos:
                        break
                item_class = ItemType.objects.get_or_create(
                    paint_index=item_infos['iteminfo']['paintindex'],
                    classid=item['classid'],
                    appid=item['appid'],
                    tradable=(True if item['marketable'] == 1 else False),
                    icon_url=item_infos['iteminfo']['imageurl'],
                    name=item['name'],
                    name_color=item['name_color'],
                    type=item['type'],
                    rarity=getSubTag(item['tags'], 'category', 'Rarity').localized_tag_name,
                    min_float=item_infos['iteminfo']['min'],
                    max_float=item_infos['iteminfo']['max']
                )
                new_item = ItemInstance.objects.get_or_create(
                    item_class=item_class[0],
                    instanceid=item['instanceid'],
                    market_tradable_restriction=(item['owner_descriptions'][1]['value']
                                                 if 'owner_descriptions' in item else None),
                    inspect_link=instance_data['actions'][0]['link'],
                    wear=item_infos['iteminfo']['wear_name'],
                    float=item_infos['iteminfo']['floatvalue'],
                    paintseed=item_infos['iteminfo']['paintseed'],
                    killeatervalue=(item_infos['iteminfo']['killeatervalue'] if 'killeatervalue' in item_infos['iteminfo'] else None),
                    customname=(item_infos['iteminfo']['customname'] if 'customname' in item_infos['iteminfo'] else None)
                )
                gamer.inventory.add(new_item)
        return inventory_object
    return False
