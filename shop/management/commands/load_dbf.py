#-*- coding: utf-8 -*-
import tempfile
import urllib2
import ydbf

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from shop.models import Ware, Variant, Category, Brand, ImportIssue

class Command(BaseCommand):
    dbf_url = 'http://www.zoostandart.ru/price/price_kolc_zoost.dbf'
    def handle(self, *args, **kwargs):
        fh = urllib2.urlopen(self.dbf_url)
        tf = tempfile.NamedTemporaryFile()
        tf.write(fh.read())
        #tf = open('/home/zw0rk/Downloads/price_kolc_zoost.dbf', 'rb')
	dbf = ydbf.open(tf, encoding='cp866')
        unknown_brand, _ = Brand.objects.get_or_create(title=u'Неизвестный')
        unknown_category, _ = Category.objects.get_or_create(title=u'Неразобранное', parent=None)
        with transaction.commit_on_success():
            for record in dbf:
                created = False
                try:
                    variant = Variant.objects.select_related().get(articul=record['COD_ARTIC'])
                except ObjectDoesNotExist, e:
                    ware = Ware.objects.create(
                        enabled=False,
                        title=record['NAME_ARTIC'],
                        category=unknown_category,
                        brand=unknown_brand
                        )
                    variant = Variant()
                    variant.ware = ware
                    variant.articul = record['COD_ARTIC']
                    created = True
                    try:
                        variant.store_qty = int(record['REZ_KOLCH'])
                        variant.base_price = record['CENA_ARTIC']
                        variant.pack = int(record['EDN_V_UPAK'])
                        variant.units = record['EDIN_IZMER']
                        variant.save()
                        if variant.fix_price:
                            raise Exception, u'Цена для товара зафиксирована, цена из базы -- %s' % record['CENA_ARTIC']
                        if created:
                            raise Exception, u'Создан новый товар и вариант -- %s' % record['NAME_ARTIC']
                    except Exception, e:
                        print unicode(e)
                        ImportIssue.objects.create(
                            variant=variant,
                            description=unicode(e)
                            )
        tf.close()
