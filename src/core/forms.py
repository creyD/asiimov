# Import forms for creating custom template forms
from django import forms
from .models import Gamer


class ChangeTradeUrl(forms.ModelForm):
    class Meta:
        model = Gamer
        fields = ('tradeurl',)
