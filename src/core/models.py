from django.db import models
# For tracking Authors and Editors
from django.contrib.auth.models import User
# For catching the save method for keeping user objects in sync
from django.db.models.signals import post_save
from django.dispatch import receiver


# CHOICE HELPERS
BADGE_RARITIES = [
    (1, 'Normal'),
    (2, 'Rare'),
    (3, 'Super Rare')
]


# STEAM MIRROR MODELS
# -- Models that mirror parts of the steam inventory system --
# Storing the classes of items for quick selection in some menues
class ItemType(models.Model):
    paint_index = models.IntegerField(primary_key=True, unique=True)  # Skin
    wear = models.CharField(max_length=100)  # tags > category = exterior > localized_tag_name

    classid = models.IntegerField()  # Weapon Class
    appid = models.IntegerField()  # The appid which items of this type belong to

    tradable = models.BooleanField(default=False)  # Wether the item is tradable or not
    icon_url = models.URLField(max_length=512, null=True)
    name = models.CharField(max_length=1000)  # i.e. ★ Butterfly Knife
    name_color = models.CharField(max_length=7)  # Hexadecimal color of the name
    type = models.CharField(max_length=1000)  # i.e. ★ Covert Knife
    rarity = models.CharField(max_length=1000)  # tags > category = rarity > localized_tag_name
    min_float = models.FloatField(null=True)  # At creation time there is no data, so we need null=True
    max_float = models.FloatField(null=True)  # At creation time there is no data, so we need null=True


# Class for storing stickers applied to weapons
class Stickers(models.Model):
    stickerid = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=1000)


# Storing the single instances of items
class ItemInstance(models.Model):
    item_class = models.ForeignKey(ItemType, on_delete=models.PROTECT)
    instanceid = models.IntegerField(primary_key=True, unique=True)  # 0 for something like cases, which will be excluded here
    market_tradable_restriction = models.CharField(max_length=1, null=True)  # How long the item will be trade locked | null is not tradelocked
    inspect_link = models.URLField(max_length=512)

    float = models.FloatField()  # Float of the object
    paintseed = models.IntegerField()  # Pattern ID | Migrate to type?
    killeatervalue = models.IntegerField(null=True)  # StatTrack | null is no StatTrack | Migrate to type?
    customname = models.CharField(max_length=128, null=True)  # Nametag | null is no Nametag
    stickers = models.ManyToManyField(Stickers)

    def getInspectLink(self):
        if self.getOwner():
            fresh_link = self.inspect_link
            link = fresh_link.replace("%owner_steamid%", self.getOwner().steamid).replace("%assetid%", self.instanceid)
            return link
        return False

    def getOwner(self):
        if Gamer.objects.filter(inventory__contains=self).exists():
            return Gamer.objects.filter(inventory__contains=self)[0]
        return False


# Badges that can be eared on the site
class Badge(models.Model):
    name = models.CharField(max_length=256, unique=True)
    desc = models.CharField(max_length=1000)
    icon = models.FileField(upload_to='badge_icons/')
    rarity = models.CharField(choices=BADGE_RARITIES, default=1, max_length=10)


# ASIIMOV MODELS
# -- Models that are explicitly for our site --
# For storing user info like steamID (...)
class Gamer(models.Model):
    steamid = models.IntegerField(primary_key=True, unique=True)  # This is a maximum of 32 chars long

    # https://developer.valvesoftware.com/wiki/Steam_Web_API#GetPlayerSummaries_.28v0002.29
    communityvisibilitystate = models.BooleanField()  # 1 -> False, 3 -> True | Determines wether the profile is private or not
    profilestate = models.BooleanField()  # 1 -> True, 0 -> False | Determines wether the profile was configured or not
    personaname = models.CharField(max_length=32)  # Display name on the steam profile
    profileurl = models.URLField(max_length=256)
    avatar = models.URLField(max_length=256)
    commentpermission = models.BooleanField()  # If set, profile allows public comments

    # Optional Fields (only available if public profile else null)
    timecreated = models.IntegerField(null=True)  # Only visible if user has profile visibility
    loccountrycode = models.CharField(max_length=2, null=True)  # 2 char ISO country code

    tradeurl = models.URLField(max_length=256, null=True)

    # Asiimov specific information
    inventory = models.ManyToManyField(ItemInstance)  # Temporary storage of items for improving site performance
    badges = models.ManyToManyField(Badge)
    system_user = models.OneToOneField(User, on_delete=models.CASCADE)
    offer_count = models.IntegerField(default=0)


class Offer(models.Model):
    offeror = models.ForeignKey(Gamer, on_delete=models.CASCADE)
    items_give = models.ManyToManyField(ItemInstance, related_name='OfferedItems')
    items_want = models.ManyToManyField(ItemType, related_name='WantedItems')
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if Gamer.objects.filter(system_user=instance).exists():
        instance.gamer.save()
