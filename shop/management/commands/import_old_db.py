#-*- coding: utf-8 -*-
import psycopg2

from django.core.management.base import BaseCommand

from shop.models import Ware, Variant, Category, Brand
from taggit.models import Tag

class Command(BaseCommand):
    def iterate_qs(self, qs):
        cursor = self.conn.cursor()
        cursor.execute(qs)
        meta = [w[0] for w in cursor.description]
        while True:
            item = cursor.fetchone()
            if item is None: break
            yield dict(zip(meta,item))
        cursor.close()

    def process_ware(self, ware):
        attr_res = {
            1: lambda i,q: setattr(i, 'weight', q),
            2: lambda i,q: setattr(i, 'units', q),
            3: lambda i,q: setattr(i, 'pack', q)
        }
        tags = [t['title'] for t in self.iterate_qs("SELECT t.title FROM shop_ware_tags AS wt LEFT JOIN shop_tag AS t ON t.id=wt.tag_id WHERE wt.ware_id=%d" % ware['id'])]
        winstance = Ware.objects.create(
            category=self.main_category,
            brand=self.unknown_brand,
            title=ware['title'],
            enabled=True
        )
        variants = self.iterate_qs("SELECT id,price,articul FROM shop_variant WHERE ware_id=%d" % ware['id'])
        for variant in variants:
            vinstance = Variant(price=variant['price'], articul=variant['articul'], ware=winstance)
            attrs = self.iterate_qs("SELECT value_text,schema_id FROM shop_attribute WHERE entity_id=%d" % variant['id'])
            for attr in attrs:
                attr_res[attr['schema_id']](vinstance, attr['value_text'])
            vinstance.save()
        winstance.tags.add(*tags)

    def handle(self, *args, **kwargs):
        self.conn = psycopg2.connect("dbname=barboske_old user=zw0rk")
        self.main_category = Category.objects.get(title=u'Магазин')
        self.unknown_brand, _ = Brand.objects.get_or_create(title=u'Неизвестный')
        for ware in self.iterate_qs("SELECT id,title FROM shop_ware"):
            self.process_ware(ware)
