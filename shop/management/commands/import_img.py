#-*- coding: utf-8 -*-
import os.path

from django.core.management.base import BaseCommand
from django.conf import settings

from shop.models import Ware, Variant

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
	for ware in Ware.objects.all():
	    for variant in ware.variants.all():
		if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'wares/%s.jpg' % variant.articul)):
		    Ware.objects.filter(id=ware.id).update(image='wares/%s.jpg' % variant.articul)