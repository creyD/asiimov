from django.contrib import admin
from .models import ItemType, Stickers, ItemInstance, Badge, Gamer


# Register your models here.
@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('paint_index', 'name', 'type', 'rarity', 'min_float', 'max_float', 'tradable')
    list_editable = ()
