from .models import Banned, Misc
import datetime
from django.utils import timezone


def checkBan(us_ip):
    if Banned.objects.all().filter(ip_ad=us_ip):
        ban = Banned.objects.all().get(ip_ad=us_ip)
        ban_date = ban.length
        now = timezone.now()
        if ban_date > now:
            return True
        else:
            ban.delete()
            return False

def bumpThread(highestPos):
    my_list = []
    for key,value in highestPos.items():
        my_list.append(value)
    max_pos = my_list[0]
    if max_pos is not None:
        position = max_pos + 1
    else:
        position = 1
    return position

def incrementPostCount(obj):
    post_count = obj.post_count + 1
    obj.post_count = post_count
    obj.save()
    return post_count