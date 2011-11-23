from django.db.models.signals import post_save, pre_delete
from django.db import models
from django.dispatch import receiver

from models import Ware, Variant

def recalc_prices(sender, **kwargs):
    ware = kwargs['instance'].ware
    prices = ware.variants.aggregate(models.Min('price'),models.Max('price'))
    Ware.objects.filter(id=ware.id).update(min_price=prices['price__min'], max_price=prices['price__max'])

receiver(post_save, sender=Variant, dispatch_uid='shop.recalc_prices')(recalc_prices)
receiver(pre_delete, sender=Variant, dispatch_uid='shop.recalc_prices')(recalc_prices)
