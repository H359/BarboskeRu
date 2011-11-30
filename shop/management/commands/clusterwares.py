#-*- coding: utf-8 -*-
import re
import ydbf
import Levenshtein

from decimal import Decimal

from django.utils.encoding import force_unicode
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from shop.models import Ware, Variant, Category, Brand
from config.models import Entry

class Command(BaseCommand):
    weights = u'|'.join(map(unicode, reversed(sorted([
	u'гр', u'мм', u'см', u'таб', u'мл', u'л', u'шт', u'кг'
    ], key=len))))
    def handle(self, *args, **kwargs):
	main_category, _ = Category.objects.get_or_create(title=u'Магазин', parent=None)
	unknown_brand, _ = Brand.objects.get_or_create(title=u'Неизвестный')
	markup = Entry.get('shop.discount.markup')
	weights_re = re.compile(ur'[ ]+(?P<wght>([0-9]+[,]*[/-xх*]+)*([0-9]+[,]*)+)+[ ]*(%s)+[ ]*' % self.weights, re.U | re.I)
	abbr_re = re.compile(ur'[ ]+д/[ ]*(\S+)', re.U | re.I)
	spaces_re = re.compile(ur'[ ]+', re.U)
	useless_symb_re = re.compile(ur'^[-+*]*[0-9-/]*|\s+(\*[0-9]+)+|НОВИНКА|[ ]+-[ ]+', re.U | re.I)
	brand_re = re.compile(ur'^[*]*\"(?P<brand>[^\"]+)\"', re.U)
	def get_common_name(cluster):
	    spls = map(lambda w: w.split(u' '), map(lambda w: w['NAME_ARTIC'], cluster))
	    min_length = min(map(len, spls))
	    res = []
	    for x in range(min_length):
		default = spls[0][x]
		if reduce(lambda acc, w: acc and (w[x] == default), spls, True):
		    res.append(default)
	    return u' '.join(res)
	def get_distance(a,b):
	    return Levenshtein.distance(a['NAME_ARTIC'].lower(), b['NAME_ARTIC'].lower())
	def transform(record):
	    name = unicode(record['NAME_ARTIC']) #.encode('utf-8')
	    record['ORIGINAL_NAME'] = name
	    subs = weights_re.search(name)
	    if subs is not None:
		record['WEIGHT_ZAM'] = subs.groupdict()['wght']
		name = weights_re.sub(u' ', name)
	    subs = brand_re.search(name)
	    if subs is not None:
		record['BRAND'] = subs.groupdict()['brand']
		name = brand_re.sub(' ', name)
	    name = abbr_re.sub(u' для \\1', name)
	    name = useless_symb_re.sub(' ', name)
	    name = spaces_re.sub(u' ', name)
	    record['NAME_ARTIC'] = name.strip()
	    return record
	with open('/home/zw0rk/Downloads/price_kolc_zoost.dbf', 'rb') as f:
	    dbf = ydbf.open(f, encoding='cp866')
	    clusters = []
	    records = map(transform, dbf)
	    records.sort(key=lambda w: w['NAME_ARTIC'])
	    threshold = 10
	    cur = 0
	    l = len(records)
	    cluster = []
	    for i in range(l):
		distance = get_distance(records[cur], records[i])
		if distance > threshold:
		    clusters.append(cluster)
		    cluster = [records[i]]
		    cur = i
		else:
		    cluster.append(records[i])
	    with transaction.commit_on_success():
		for x in clusters:
		    """
		    for y in x:
			print y['NAME_ARTIC'].encode('utf-8'), ' ||| ',  y['ORIGINAL_NAME'].encode('utf-8')
		    print '-'*80
		    """
		    brand, _ = Brand.objects.get_or_create(title=x[0].get('BRAND', u'Неизвестный'))
		    ware = Ware.objects.create(title=get_common_name(x), category=main_category, brand=brand)
		    for y in x:
			Variant.objects.create(
			    price=(1+Decimal(markup/100.0))*y['CENA_ARTIC'],
			    articul=y['COD_ARTIC'],
			    ware=ware,
			    title=y['NAME_ARTIC'],
			    base_price=y['CENA_ARTIC'],
			    pack=y['EDN_V_UPAK'],
			    units=y['EDIN_IZMER'],
			    weight=y.get('WEIGHT_ZAM', ''),
			    original_title=y['ORIGINAL_NAME']
			)