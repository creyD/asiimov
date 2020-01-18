# Import the local models
from .models import Offer, Gamer
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
# For getting the API interaction methods
from .steam_api import getUserInfo
# Import for manually logging in user after creation
from django.contrib.auth import login


# HELPER
def validate_steam_login(params):
    steam_login_url_base = "https://steamcommunity.com/openid/login"

    new_params = params.copy()
    new_params["openid.mode"] = "check_authentication"

    r = requests.post(steam_login_url_base, data=new_params)

    if "is_valid:true" in r.text:
        return True
    return False


# STATIC PAGES
def help(request):
    return render(request, 'static_pages/help.html')


def imprint(request):
    return render(request, 'static_pages/imprint.html')


def about(request):
    return render(request, 'static_pages/about.html')


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
        'openid.ns': "http://specs.openid.net/auth/2.0",
        'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
        'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
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
                communityvisibilitystate=(True if info['response']['players'][0]['communityvisibilitystate'] == 3 else False),
                profilestate=info['response']['players'][0]['profilestate'],
                personaname=info['response']['players'][0]['personaname'],
                profileurl=info['response']['players'][0]['profileurl'],
                avatar=info['response']['players'][0]['avatar'],
                commentpermission=info['response']['players'][0]['commentpermission'],
                timecreated=info['response']['players'][0]['timecreated'] or None,
                loccountrycode=info['response']['players'][0]['loccountrycode'] or None
            )
        login(request, new_user)
        return redirect(me)
    return HttpResponseForbidden()


# USER AREA
@login_required
def offer_refresh(request, offerID):
    offer = get_object_or_404(Offer, id=offerID)
    return redirect(offer, offerID=offerID)


@login_required
def offer_delete(request, offerID):
    offer = get_object_or_404(Offer, id=offerID)
    if request.user == offer.offeror.system_user:
        offer.delete()
        return redirect(dashboard)
    else:
        return HttpResponseForbidden()


@login_required
def offer_create(request):
    # TODO: Implement
    return render(request, 'core/offer_create.html')


@login_required
def profile(request, steamID):
    dude = get_object_or_404(Gamer, steamid=steamID)
    return render(request, 'core/profile.html', {'gamer': dude})


# PRIVATE AREA
@login_required
def me(request):
    return render(request, 'core/profile.html', {'gamer': Gamer.objects.get(system_user=request.user)})


@login_required
def me_settings(request):
    dude = get_object_or_404(Gamer, system_user=request.user)
    return render(request, 'core/settings.html', {'gamer': dude})
