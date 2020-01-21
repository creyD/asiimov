# Import forms for creating custom template forms
from django import forms
from .models import Gamer, Offer


class ChangeTradeUrl(forms.ModelForm):
    class Meta:
        model = Gamer
        fields = ['tradeurl']


class CreateOffer(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('items_give', 'items_want')
