#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from django.conf import settings
from django.template import Template, Context

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

    @models.permalink
    def get_absolute_url(self):
        return ('shop-category', (), {'path': self._materialized_path})

    def get_node_ancestors(self):
        tree = Category.get_tree()
        path = [self]
        while path[-1].parent_id is not None:
            for candidate in tree:
                if candidate.id == path[-1].parent_id:
                    path.append(candidate)
                    break
        return reversed(path)


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
        return ('shop-category', (), {'path': path})

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
    position   = models.IntegerField(verbose_name=u'Положение',default=0)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.articul, self.ware, ' '.join([self.weight, self.units, self.pack]))

class EmailTemplate(models.Model):
    TYPE = (
        u'Уведомление о поступлении заказа',
        u'Уведомление об обработке заказа'
    )
    class Meta:
        verbose_name=u'Шаблон письма'
        verbose_name_plural=u'Шаблоны писем'
    type = models.IntegerField(choices=enumerate(TYPE), verbose_name=u'Тип')
    subj = models.CharField(max_length=200, verbose_name=u'Тема письма')
    text = models.TextField(verbose_name=u'Тело письма')

    def __unicode__(self):
        return self.TYPE[self.type]

class Order(models.Model):
    STATUS = (u'Создан', u'Обработан', u'Доставлен', u'Ошибка')
    class Meta:
        verbose_name=u'Заказ'
        verbose_name_plural=u'Заказы'
        ordering = ['status', '-created_at']
    
    status     = models.IntegerField(choices=enumerate(STATUS), default=0, verbose_name=u'Статус')
    fio        = models.CharField(max_length=250, verbose_name=u'Имя')
    phone      = models.CharField(max_length=250, verbose_name=u'Телефон', blank=True)
    email      = models.EmailField(verbose_name=u'Email')
    address    = models.TextField(verbose_name=u'Адрес')
    user       = models.ForeignKey(User, verbose_name=u'Пользователь', editable=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,verbose_name=u'Создан')
    comment    = models.TextField(verbose_name=u'Комментарий', blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.fio, self.phone)

    def send_notification(self):
        c = Context({'order': self})
        # notify user
        user_message_template = EmailTemplate.objects.get(type=0)
        subject = Template(user_message_template.subj)
        message = Template(user_message_template.text)
        usermessage = (subject.render(c), message.render(c), settings.EMAIL_FROM, [self.email])
        # notify manager
        managermessage = (
            u'Поступил новый заказ', 
            u'Номер %d' % self.id, 
            settings.EMAIL_FROM, 
            [user.email for user in User.objects.filter(is_staff=True)]
        )
        send_mass_mail( (usermessage, managermessage), fail_silently=not settings.DEBUG)

class OrderedWare(models.Model):
    class Meta:
        verbose_name=u'Товар в заказе'
        verbose_name_plural=u'Товары в заказах'

    variant = models.ForeignKey(Variant, verbose_name=u'Вариант товара')
    qty     = models.PositiveIntegerField(verbose_name=u'Количество')
    order   = models.ForeignKey(Order, verbose_name=u'Заказ')

import signals
