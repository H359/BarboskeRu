#-*- coding: utf-8 -*-
import re
import ydbf
import Levenshtein

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from shop.models import Ware, Variant, Category, Brand, ImportIssue

class Command(BaseCommand):
    weights = reversed(sorted([u'гр', u'мм', u'см', u'таб', u'мл', u'л', u'шт', u'кг'], key=len))
    def handle(self, *args, **kwargs):
	self.weights_re = re.compile(r'[ ]+(?P<wght>([0-9]+[,"]*[/-xх*]+)*([0-9]+[,]*)+)+[ ]*(%s)+[ ]*' % u'|'.join(self.weights).encode('utf-8'), re.U | re.I)
	self.abbr_re = re.compile(r'[ ]+д/[ ]*(\S+)', re.U | re.I)
	self.spaces_re = re.compile(r'[ ]+', re.U)
	self.useless_symb_re = re.compile('\s+(\*[0-9]+)+', re.U)
	def get_distance(a,b):
	    dst = Levenshtein.distance(a['NAME_ARTIC'].lower(), b['NAME_ARTIC'].lower())
	    return dst
	def transform(record):
	    name = record['NAME_ARTIC'].encode('utf-8')
	    record['ORIGINAL_NAME'] = name
	    subs = self.weights_re.search(name)
	    if subs is not None:
		record['WEIGHT_ZAM'] = subs.groupdict()['wght']
		name = self.weights_re.sub(' ', name)
	    name = self.abbr_re.sub(' для \\1', name)
	    name = self.useless_symb_re.sub(' ', name)
	    name = self.spaces_re.sub(' ', name)
	    record['NAME_ARTIC'] = name
	    return record
	with open('/home/zw0rk/Downloads/price_kolc_zoost.dbf', 'rb') as f:
	    dbf = ydbf.open(f, encoding='cp866')
	    clusters = []
	    records = [transform(record) for record in dbf]
	    records.sort(key=lambda w: w['NAME_ARTIC'])
	    distance, threshold = 0, 5
	    cur = 0
	    l = len(records)
	    cluster = []
	    for i in range(l):
		if i == l-1: break
		if i == cur: cluster.append(records[i])
		distance = get_distance(records[cur], records[i])
		if distance > threshold:
		    clusters.append(cluster)
		    cluster = []
		    cur = i+1
		else:
		    cluster.append(records[i])
	    for x in clusters:
		for y in x:
		    print y['NAME_ARTIC']
		    #,' ||| ', y['ORIGINAL_NAME'], y.get('WEIGHT_ZAM', '[NO]')
		print '-'*50