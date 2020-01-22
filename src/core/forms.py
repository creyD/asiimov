# Import forms for creating custom template forms
from django import forms
# Import models for creating modelforms
from .models import Gamer, Offer


# Form for adding own trade url
class ChangeTradeUrl(forms.ModelForm):
    class Meta:
        model = Gamer
        fields = ['tradeurl']


# Form for creating offers
class CreateOffer(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('items_give', 'items_want')
