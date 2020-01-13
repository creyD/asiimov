from .models import Offer, Gamer
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

# STATIC PAGES


def help(request):
    return render(request, 'core/help.html')


def imprint(request):
    return render(request, 'core/imprint.html')


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
    return render(request, 'core/profile.html', {'gamer': Gamer.object.get(system_user=request.User)})


@login_required
def me_settings(request):
    dude = get_object_or_404(Gamer, system_user=request.User)
    return render(request, 'core/settings.html', {'gamer': dude})
