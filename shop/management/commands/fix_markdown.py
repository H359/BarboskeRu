#-*- coding: utf-8 -*-
from django.utils.encoding import force_unicode
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from shop.models import Ware, Variant, Category, Brand

class Command(BaseCommand):
    def fix_line(self, line):
	line = unicode(line.strip())
	if line.endswith('\\'):
	    line = line[0:-1]
	if len(line) == 0:
	    line = ''
	return line
    def fix_md(self, md):
	return '\r\n'.join(map(self.fix_line, md.split('\n')))
    def handle(self, *args, **kwargs):
	with transaction.commit_on_success():
	    for category in Category.objects.exclude(text = '').exclude(text__isnull = True):
		category.text.raw = self.fix_md(category.text.raw)
		category.save()
	    for ware in Ware.objects.exclude(description = '').exclude(description__isnull = True):
		ware.description.raw = self.fix_md(ware.description.raw)
		ware.save()