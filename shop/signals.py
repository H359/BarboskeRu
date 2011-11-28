from django.db.models.signals import post_save, pre_delete
from django.db import models
from django.dispatch import receiver

from django.core.cache import cache

from models import Ware, Variant, Category

def recalc_prices(sender, **kwargs):
    ware = kwargs['instance'].ware
    prices = ware.variants.aggregate(models.Min('price'),models.Max('price'))
    Ware.objects.filter(id=ware.id).update(min_price=prices['price__min'], max_price=prices['price__max'])

def update_categories_cache(sender, **kwargs):
    cache.delete('categories')

receiver(post_save, sender=Variant, dispatch_uid='shop.recalc_prices')(recalc_prices)
receiver(pre_delete, sender=Variant, dispatch_uid='shop.recalc_prices')(recalc_prices)

receiver(post_save, sender=Category, dispatch_uid='shop.categories_cache_update')(update_categories_cache)
receiver(pre_delete, sender=Category, dispatch_uid='shop.categories_cache_update')(update_categories_cache)
