#-*- coding: utf-8 -*-
from django.db import models

from taggit.managers import TaggableManager
from mptt.models import MPTTModel
from autoslug import AutoSlugField

from utils import cached, cached_method

class EnabledManager(models.Manager):
    def get_query_set(self):
	return super(EnabledManager, self).get_query_set().filter(enabled=True)

class Category(MPTTModel):
    class Meta:
	verbose_name=u'Категория'
	verbose_name_plural=u'Категории'
    class MPTTMeta:
	order_insertion_by = ['position']

    parent   = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=u'Родительская категория')
    title    = models.CharField(max_length=250, verbose_name=u'Название')
    slug     = AutoSlugField(max_length=250, populate_from='title', unique=True)
    position = models.IntegerField(verbose_name=u'Положение', default=0)

    _materialized_path = models.TextField(editable=False)

    def save(self, *args, **kwargs):
        self._materialized_path = '/'.join([x.slug for x in self.get_ancestors()] + [self.slug])
        super(Category, self).save(*args, **kwargs)

    @staticmethod
    def get_tree():
        def _get_tree():
            root = Category.objects.root_nodes()[0]
            return root.get_descendants(include_self=True)
        return cached(_get_tree, 'rubrics')

    @cached_method('category-%{id}-showcase')
    def get_showcase(self):
        return Ware.objects.filter(category__in=self.get_descendants(include_self=True)).order_by('-image')[0:4]

    @models.permalink
    def get_absolute_url(self):
        return ('shop.category', (), {'path': self._materialized_path})

    def __unicode__(self):
        return u'%s' % self.title

class Brand(models.Model):
    class Meta:
        verbose_name=u'Бренд'
        verbose_name_plural=u'Бренды'
    
    title = models.CharField(max_length=250, verbose_name=u'Название')
    slug  = AutoSlugField(max_length=250, populate_from='title', unique=True)

    def __unicode__(self):
        return u'%s' % self.title

class Ware(models.Model):
    class Meta:
	verbose_name=u'Товар'
	verbose_name_plural=u'Товары'
	ordering = ['-position', '-id']

    title       = models.CharField(max_length=250, verbose_name=u'Название')
    slug        = AutoSlugField(max_length=250, populate_from='title')
    category    = models.ForeignKey(Category, verbose_name=u'Категория', related_name='wares')
    brand       = models.ForeignKey(Brand, verbose_name=u'Бренд', related_name='wares')
    description = models.TextField(verbose_name=u'Описание',blank=True)
    enabled     = models.BooleanField(verbose_name=u'Активен')
    position    = models.IntegerField(verbose_name=u'Положение', default=0)
    min_price   = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    max_price   = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    image       = models.ImageField(blank=True, verbose_name=u'Изображение', upload_to='media/wares')
    objects     = EnabledManager()
    tags        = TaggableManager()

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        path = self.category._materialized_path + '/' + self.slug + '.html'
        return ('shop.category', (), {'path': path})

class Variant(models.Model):
    class Meta:
	verbose_name=u'Вариант товара'
	verbose_name_plural=u'Варианты товаров'
	ordering = ['-ware', '-position', '-id']

    ware       = models.ForeignKey(Ware, verbose_name=u'Товар', related_name='variants')
    price      = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=u'Цена')
    weight     = models.CharField(max_length=250, verbose_name=u'Вес', default='')
    units      = models.CharField(max_length=250, verbose_name=u'Единицы измерения', default='')
    pack       = models.CharField(max_length=250, verbose_name=u'Упаковка', default='')
    articul    = models.CharField(max_length=250, verbose_name=u'Артикул')
    store_qty  = models.IntegerField(default=0, verbose_name=u'Кол-во на складе')
    position    = models.IntegerField(verbose_name=u'Положение',default=0)

import signals
