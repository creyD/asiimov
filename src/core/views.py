# Import the local models
from .models import Offer, Gamer, ItemType, ItemInstance
# Django shortcuts for certain things
from django.shortcuts import render, get_object_or_404, redirect
# For catching permission errors
from django.http import HttpResponseForbidden
# For permitting only logged in users to see their private area
from django.contrib.auth.decorators import login_required
# For Steam Open ID handling
from urllib import parse
# For requesting the identification check
import requests
# For manually creating system users
from django.contrib.auth.models import User
# Import for manually logging in user after creation
from django.contrib.auth import login
# For communication with the steam api
import json
import urllib.request
from .forms import ChangeTradeUrl, CreateOffer
from django.conf import settings

# STATIC VARIABLES
# Official Steam Servers
STEAM_SERVER = 'https://api.steampowered.com/'
USER_METHOD = 'ISteamUser/GetPlayerSummaries/v2'
INVENTORY_SERVER = 'https://steamcommunity.com/inventory/'

# CSGOFloats API Server (https://csgofloat.com)
FLOAT_SERVER = 'https://api.csgofloat.com/?url='


# HELPER
def validate_steam_login(params):
    steam_login_url_base = 'https://steamcommunity.com/openid/login'

    new_params = params.copy()
    new_params['openid.mode'] = 'check_authentication'

    r = requests.post(steam_login_url_base, data=new_params)

    if 'is_valid:true' in r.text:
        return True
    return False


def getInstanceData(inventory_object, instance_id):
    for key in inventory_object['descriptions']:
        if key['instanceid'] == instance_id:
            return key


def getFloat(inspect_link):
    QUERY = FLOAT_SERVER + inspect_link
    print(QUERY)
    float_object = json.load(urllib.request.urlopen(QUERY))
    if 'error' in float_object:
        return False
    return float_object


def getSubTag(scope, search_key, search_value):
    for tag in scope:
        if tag[search_key] == search_value:
            return tag
    return False


def getUserInfo(steamID, API_KEY=settings.STEAM_API_KEY):
    QUERY = STEAM_SERVER + USER_METHOD + '/?key=' + str(API_KEY) + '&format=json&steamids=' + str(steamID)
    player_object = json.load(urllib.request.urlopen(QUERY))
    return player_object['response']['players'][0]


# STATIC PAGES
def help(request):
    return render(request, 'static_pages/help.html')


def imprint(request):
    return render(request, 'static_pages/imprint.html')


# PUBLIC AREA
def dashboard(request):
    return render(request, 'core/dashboard.html')


def offer_overview(request):
    return render(request, 'core/offer_overview.html', {'offers': Offer.objects.all()})


def offer(request, offerID):
    offer = get_object_or_404(Offer, id=offerID)
    return render(request, 'code/offer.html', {'offer': offer})


def search(request, filter):
    # TODO: Implement
    return render(request, 'core/filter.html')


# USER SIGNUP
def signup(request):
    steam_openid_url = 'https://steamcommunity.com/openid/login'
    u = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.mode': 'checkid_setup',
        'openid.return_to': 'http://' + request.META['HTTP_HOST'] + '/signup_confirm',
        'openid.realm': 'http://' + request.META['HTTP_HOST'] + ''
    }
    query_string = parse.urlencode(u)
    auth_url = steam_openid_url + '?' + query_string
    return redirect(auth_url)


def signup_confirm(request):
    if validate_steam_login(request.GET):
        claimed_id = request.GET.get('openid.claimed_id')
        claimed_id = claimed_id.split('/')[-1]
        new_user, created = User.objects.get_or_create(username=claimed_id)

        if created:
            info = getUserInfo(claimed_id)
            Gamer.objects.create(
                steamid=claimed_id,
                system_user=new_user,
                communityvisibilitystate=(True if info['communityvisibilitystate'] == 3 else False),
                profilestate=info['profilestate'],
                personaname=info['personaname'],
                profileurl=info['profileurl'],
                avatar=info['avatar'],
                commentpermission=info['commentpermission'],
                timecreated=info['timecreated'] or None,
                loccountrycode=info['loccountrycode'] or None
            )
        login(request, new_user)
        return redirect(profile, steamID=claimed_id)
    return HttpResponseForbidden()


# USER AREA
@login_required
def offer_refresh(request, offerID):
    offer = get_object_or_404(Offer, id=offerID)
    # TODO Refresh Info
    return redirect(offer, offerID=offerID)


@login_required
def offer_delete(request, offerID):
    offer = get_object_or_404(Offer, id=offerID)
    if request.user == offer.offeror.system_user:
        offer.delete()
        return redirect(dashboard)
    return HttpResponseForbidden()


@login_required
def offer_create(request):
    form = CreateOffer(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.offeror = request.user.gamer
        form.save()
    dude = get_object_or_404(Gamer, steamid=request.user.gamer.steamid)
    context = {
        'inventory': dude.inventory,
        'form': form
    }
    return render(request, 'core/offer_create.html', context)


@login_required
def profile(request, steamID):
    dude = get_object_or_404(Gamer, steamid=steamID)
    return render(request, 'profile/profile.html', {'gamer': dude, 'live_offers': Offer.objects.filter(offeror=dude).count()})


@login_required
def profile_inventory(request, steamID):
    dude = get_object_or_404(Gamer, steamid=steamID)
    return render(request, 'profile/inventory.html', {'gamer': dude})


@login_required
def profile_update(request, steamID):
    if request.user.steamid == steamID or request.user.is_staff:
        the_gamer = get_object_or_404(Gamer, steamid=steamID)
        info = getUserInfo(steamID)
        the_gamer.communityvisibilitystate = (True if info['communityvisibilitystate'] == 3 else False)
        the_gamer.profilestate = info['profilestate']
        the_gamer.personaname = info['personaname']
        the_gamer.profileurl = info['profileurl']
        the_gamer.avatar = info['avatar']
        the_gamer.commentpermission = info['commentpermission']
        if 'timecreated' in info:
            the_gamer.timecreated = info['timecreated']
        if 'loccountrycode' in info:
            the_gamer.loccountrycode = info['loccountrycode']
        the_gamer.save()
        return redirect(profile, steamID=steamID)
    return HttpResponseForbidden()


# PRIVATE AREA
@login_required
def me(request):
    return redirect(profile, steamID=request.user.gamer.steamid)


@login_required
def me_inventory(request):
    return redirect(profile_inventory, steamID=request.user.gamer.steamid)


@login_required
def profile_inventory_update(request, steamID):
    gamer = get_object_or_404(Gamer, steamid=steamID)
    QUERY = INVENTORY_SERVER + str(steamID) + '/' + str(730) + '/2?l=english&count=5000'
    try:
        inventory_object = json.load(urllib.request.urlopen(QUERY))
    except urllib.URLError:
        print('Error accessing Steam')

    if 'success' in inventory_object:
        if inventory_object['success'] == 1:
            gamer.inventory.clear()  # Clear any old invetory data that we have
            for count, item in enumerate(inventory_object['assets']):
                item_desc = inventory_object['descriptions'][count]
                wear = "NO WEAR"
                rarity = "NO RARITY"
                if getSubTag(item_desc['tags'], 'category', 'Exterior'):
                    wear = getSubTag(item_desc['tags'], 'category', 'Exterior')['localized_tag_name']
                if getSubTag(item_desc['tags'], 'category', 'Rarity'):
                    rarity = getSubTag(item_desc['tags'], 'category', 'Rarity')['localized_tag_name']
                new_item, created = ItemType.objects.get_or_create(
                    paint_index=item_infos['iteminfo']['paintindex'],
                    wear=wear,
                    classid=item['classid'],
                    appid=item['appid'],
                    tradable=(True if 'marketable' in item else False),
                    icon_url=item_desc['icon_url'],
                    name=item_desc['name'],
                    name_color=item_desc['name_color'],
                    type=item_desc['type'],
                    rarity=rarity,
                )
                gamer.inventory_2.add(new_item)
        else:
            print('STEAM API CALL RETURNED SUCESS !=1!')
    else:
        print('STEAM API CALL NOT SUCCESSFULL!')
    return redirect(profile_inventory, steamID=steamID)


@login_required
def me_settings(request):
    dude = get_object_or_404(Gamer, system_user=request.user)
    trade_form = ChangeTradeUrl(request.POST or None, instance=dude)
    if trade_form.is_valid() and request.method == 'POST':
        dude.tradeurl = trade_form.cleaned_data['tradeurl']
        dude.save()
    return render(request, 'profile/settings.html', {'gamer': dude, 'form': trade_form})
