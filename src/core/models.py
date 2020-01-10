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


# MODELS
# Storing the classes of items for quick selection in some menues
class ItemType(models.model):
    paint_index = models.IntegerField(primary_key=True, unique=True)  # Skin

    classid = models.IntegerField()  # Weapon Class
    appid = models.IntegerField()  # The appid which items of this type belong to

    tradable = models.BooleanField(default=False)  # Wether the item is tradable or not
    icon_url = models.URLField(max_length=512, null=True)
    name = models.CharField(max_length=1000)  # i.e. ★ Butterfly Knife
    name_color = models.CharField(max_length=7)  # Hexadecimal color of the name
    type = models.CharField(max_length=1000)  # i.e. ★ Covert Knife
    rarity = models.CharField(max_length=1000)  # tags > category = rarity > localized_tag_name
    min_float = models.FloatField()
    max_float = models.FloatField()


# Class for storing stickers applied to weapons
class Stickers(models.model):
    stickerid = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField()


# Storing the single instances of items
class ItemInstance(models.model):
    item_class = models.ForeignKey(ItemType, on_delete=models.PROTECT)
    instanceid = models.IntegerField(primary_key=True, unique=True)  # 0 for something like cases, which will be excluded here
    market_tradable_restriction = models.IntegerField()  # How long the item will be trade locked
    inspect_link = models.URLField(max_length=512, null=True)
    wear = models.CharField(max_length=100)  # tags > category = exterior > localized_tag_name
    float = models.FloatField()  # Float of the object
    paintseed = models.IntegerField()  # Pattern ID
    killeatervalue = models.IntegerField(null=True)  # StatTrack
    customname = models.CharField(max_length=128, null=True)  # Nametag
    stickers = models.ManyToManyField()


# Badges that can be eared on the site
class Badge(models.model):
    name = models.CharField(max_length=256, unique=True)
    desc = models.CharField(max_length=1000)
    icon = models.FileField(upload_to='badge_icons/')
    rarity = models.CharField(choices=BADGE_RARITIES, default=1)


# For storing user info like steamID (...)
class Gamer(models.model):
    steamid = models.IntegerField(primary_key=True, unique=True)  # This is a maximum of 32 chars long

    # https://developer.valvesoftware.com/wiki/Steam_Web_API#GetPlayerSummaries_.28v0002.29
    communityvisibilitystate = models.BooleanField()  # 1 -> False, 3 -> True | Determines wether the profile is private or not
    profilestate = models.BooleanField()  # 1 -> True, 0 -> False | Determines wether the profile was configured or not
    personaname = models.CharField(max_length=32)  # Display name on the steam profile
    profileurl = models.URLField(max_length=256)
    avatar = models.URLField(max_length=256)
    commentpermission = models.BooleanField()  # If set, profile allows public comments

    # Optional Fields (only available if public profile)
    timecreated = models.IntegerField(null=True)  # Only visible if user has profile visibility
    loccountrycode = models.CharField(max_length=2, null=True)  # 2 char ISO country code

    # Asiimov specific information
    inventory = models.ManyToManyField(ItemInstance)  # Temporary storage of items for improving site performance
    API_KEY = models.CharField(max_length=32, null=True)  # Optionally use the API KEY of the user
    badges = models.ManyToManyField(Badge)
    system_user = models.OneToOneField(User, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.gamer.save()
