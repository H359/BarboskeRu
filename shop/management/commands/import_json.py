#-*- coding: utf-8 -*-
import ujson
import os
import pandoc
import tidy

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_unicode
from django.conf import settings
from django.db import transaction

from shop.models import Variant, Category, Brand

pandoc.Document.OUTPUT_FORMATS += ('textile',)
PANDOC_PATH = '/home/zw0rk/.cabal/bin/pandoc'
class Command(BaseCommand):
    # id -> {'children': children, 'object': category_object}
    root_category = Category.objects.root_nodes()[0]
    brand = Brand.objects.get_or_create(title=u'Неизвестный')
    categories = {}
    doc = pandoc.Document(PANDOC_PATH)
    tidy_opts = dict(
	indent=1, tidy_mark=0, drop_font_tags=1, show_body_only=1,
	hide_comments=1, input_xml=0, merge_divs=1, merge_spans=1,
	output_html=0, output_xml=0, output_xhtml=0, input_encoding='utf8',
	output_encoding='utf8', drop_empty_paras=1, clean=1
    )
    def get_or_create_category(self, path):
	category = self.root_category
	if path[0] in [u'Главная', u'Home']:
	    path = path[1:]
	for p in range(len(path)):
	    pslice = tuple(path[:p+1])
	    if pslice not in self.categories:
		self.categories[pslice], created = Category.objects.get_or_create(title=pslice[-1], parent=category)
		if created:
		    print u'created %s (%s)' % (self.categories[pslice], category)
		#print u'%s as child for %s' % (self.categories[pslice].title, category.title)
	    category = self.categories[pslice]
	return category
    def get_clean(self, html):
	desc = u'<html><body>%s</body></html>' % html
	desc = tidy.parseString(desc.encode('utf-8'), **self.tidy_opts)
	self.doc.html = str(desc)
	md = self.doc.markdown
	return md
    def parse_product(self, obj):
	if len(obj['articul'].strip()) == 0: return
	category = self.get_or_create_category(obj['category'])
	try:
	    variant = Variant.objects.select_related().get(articul=obj['articul'].strip())
	    ware = variant.ware
	    ware.category = category
	    ware.description.raw = smart_unicode(self.get_clean(''.join(obj['description'])))
	    ware.save()
	except ObjectDoesNotExist:
	    print 'NO OBJ', obj['articul']
    def parse_category(self, obj):
	category = self.get_or_create_category(obj['path'])
	category.text.raw = smart_unicode(self.get_clean(u''.join(obj['description'])))
	category.save()
    def handle(self, *args, **kwargs):
	if len(args) < 1:
	    print u'No input file specified.'
	    return
	if not os.path.exists(args[0]):
	    print u'%s not found.' % args[0]
	    return
	with transaction.commit_on_success():
	    with open(args[0], 'r') as jsonfile:
		data = ujson.load(jsonfile)
		for obj in data:
		    if obj['type'] == 'product':
			self.parse_product(obj)
		    else:
			self.parse_category(obj)
	#Category.objects.rebuild()