from django.contrib import admin
from .models import ItemType, ItemInstance, Badge, Gamer


# Register your models here.
@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('paint_index', 'wear', 'name', 'type', 'rarity', 'min_float', 'max_float', 'tradable')
    list_editable = ()


@admin.register(Gamer)
class GamerAdmin(admin.ModelAdmin):
    list_display = ('steamid', 'communityvisibilitystate', 'profilestate', 'personaname', 'commentpermission', 'timecreated', 'loccountrycode')


@admin.register(ItemInstance)
class ItemInstanceAdmin(admin.ModelAdmin):
    list_display = ('item_class', 'instanceid', 'market_tradable_restriction', 'inspect_link', 'float', 'paintseed', 'killeatervalue', 'customname')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'icon', 'rarity')
