#coding: utf-8

import re

from django.core.management.base import BaseCommand

from shop.models import Ware, Category


class Command(BaseCommand):

	def handle(self, *args, **kwargs):
		cats = Category.objects.all()
		for cat in cats:
			brand_p, brand_name = TitleClassifier.classify(cat.title)
			if brand_p:
				print "The category ID %s title %s is actually a brand %s" % (cat.pk, cat.title, brand_name)
				print "Transfering it to brand now"
				updated = cat.to_brand(brand_name)
				print "Complete, %s records updated" % (updated, )


class WordClassifier(object):

	number_re = re.compile('^[0-9]+$')
	latin_re = re.compile('^[a-zA-Z\-\'0-9]+$')
	russian_re = re.compile(u'^[а-яА-Я\-]+$')
	dash_re = re.compile('^\-$')
	open_brace_re = re.compile('\(')
	close_brace_re = re.compile('\)')
	preposition_re = re.compile(u'^(для|про|от|с)$')
	mixed_word_re = re.compile(u'[а-яА-Я\-a-zA-Z]+')
		
	@classmethod
	def classify(cls, word):
		if cls.number_re.match(word):
			return "number"
		elif cls.preposition_re.match(word):
			return "preposition"
		elif cls.dash_re.match(word):
			return "dash"
		elif cls.latin_re.match(word):
			return "latin"
		elif cls.russian_re.match(word):
			return "russian"
		elif cls.open_brace_re.match(word):
			return "open_brace"
		elif cls.close_brace_re.match(word):
			return "close_brace"
		elif cls.mixed_word_re.match(word):
			return "mixed_word"
		else:
			raise ValueError('Unable to classify word: "%s"' % (word, ))


class TitleClassifier(object):

	@staticmethod
	def classify_words(title):
		title = re.sub('\(', ' ( ', title)
		title = re.sub('\)', ' ) ', title)
		title = re.sub(',', ' ', title)
		title = re.sub('\-', ' - ', title)
		title = re.sub('[\s]{2,}', ' ', title)
		words = title.split(' ')
		classified_list = []
		for w in words:
			if w != u'':
				classified_list.append((WordClassifier.classify(w), w))
		return classified_list

	resolution_table = {
		'number': {
			'russian': ('russian', True),
			'latin': ('latin', True),
			'preposition': ('preposition', False)
		},
		'open_brace': {
			'russian': ("open_brace_ru", True),
			'latin': ('open_brace_lat', True),
			'preposition': ('open_brace_prep', True)
		},
		'open_brace_ru': {
			'russian': ('open_brace_ru', True),
			'preposition': ('open_brace_prep', True),
			'close_brace': ('braced_ru', True)
		},
		'open_brace_lat': {
			'latin': ('open_brace_lat', True),
			'close_brace': ('braced_lat', True)
		},
		'open_brace_prep': {
			'russian': ('open_brace_prep', True),
			'preposition': ('open_brace_prep', True),
			'close_brace': ('braced_prep', True)
		},
		'russian': {
			'latin': ('latin', False),
			'open_brace': ('open_brace', False),
			'preposition': ('russian', True)
		},
		'latin': {
			'russian': ('russian', False),
			'open_brace': ('open_brace', False),
			'preposition': ('russian', False)
		},
		'preposition': {
			'russian': ('russian', True),
			'open_brace': ('open_brace', False),
			'preposition': ('russian', True)
		}
	}

	@classmethod
	def reduce(cls, clfy_list):
		reduced_list = []
		current_state, current_word = clfy_list[0]
		for (cl, w) in clfy_list[1:]:
			if current_state == cl:
				current_word = current_word + ' ' + w
			else:
				branch = cls.resolution_table.get(current_state, None)
				if branch:
					nc, app = branch.get(cl, (None, None))
					if nc is not None:
						if app:
							current_state, current_word = nc, current_word + ' ' + w
						else:
							reduced_list.append((current_state, current_word))
							current_state, current_word = (nc, w)
					else:
						reduced_list.append((current_state, current_word))
						current_state, current_word = (cl, w)
				else:
					reduced_list.append((current_state, current_word))
					current_state, current_word = (cl, w)
		if current_word:
			branch = cls.resolution_table.get(current_state, None)
			if branch:
				nc, app = branch.get(current_state, (None, None))
				if nc is not None:
					reduced_list.append((nc, current_word))
				else:
					reduced_list.append((current_state, current_word))
			else:
				reduced_list.append((current_state, current_word))
		return reduced_list

	@classmethod
	def classify(cls, title):
		""" Return a pair. First member is True/False and shows if the title belongs to brand,
		second is the actual brand name, or None.
		"""
		pairs_list = TitleClassifier.reduce(TitleClassifier.classify_words(title))
		reduced_list = [ cl for (cl, w) in pairs_list ]
		word_list = [ w for (cl, w) in pairs_list ]
		brand_classes = [ ['russian', 'braced_ru'],
			['latin', 'braced_ru'],
			['latin'],
			['latin', 'braced_lat'],
			['russian', 'braced_lat'],
			['latin', 'dash', 'russian', 'braced_ru'],
			['russian', 'dash', 'latin', 'braced_ru']
		]
		if reduced_list in brand_classes:
			#TODO: brand name extraction here
			if 'russian' in reduced_list:
				k = 'russian'
			elif 'braced_ru' in reduced_list:
				k = 'braced_ru'
			elif 'latin' in reduced_list:
				k = 'latin'
			name = ''
			for cl, val in pairs_list:
				if cl == k:
					name += val
			return (True, name.strip(" ()"))
		else:
			return (False, None)