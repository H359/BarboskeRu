#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

from taggit.managers import TaggableManager
from mptt.models import MPTTModel
from autoslug import AutoSlugField
from markitup.fields import MarkupField

from utils import cached, cached_method

class EnabledManager(models.Manager):
    def get_query_set(self):
        return super(EnabledManager, self).get_query_set().filter(enabled=True)

class Category(MPTTModel):
    class Meta:
        verbose_name=u'Категория'
        verbose_name_plural=u'Категории'
        ordering = ('lft',)

    parent        = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=u'Родительская категория')
    title         = models.CharField(max_length=250, verbose_name=u'Название')
    slug          = AutoSlugField(max_length=250, populate_from='title', unique=True)
    text          = MarkupField(verbose_name=u'Описание', blank=True, null=True, default='')
    market_export = models.BooleanField(verbose_name=u'Экспорт в Yandex.Market', help_text ='с подкатегориями', default=False)

    _materialized_path = models.TextField(editable=False)

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        Category.objects.filter(id=self.id).update(_materialized_path = '/'.join([x.slug for x in self.get_ancestors()] + [self.slug]))

    @staticmethod
    def get_tree():
        def _get_tree():
            root = Category.objects.root_nodes()[0]
            return root.get_descendants(include_self=True)
        return cached(_get_tree, 'categories')

    @models.permalink
    def get_absolute_url(self):
        return ('shop-category', (), {'path': self._materialized_path})

    def to_brand(self, brand_name):
        brand, _created = Brand.objects.get_or_create(title=brand_name)  #brand object (may be already added before)
        child_ids = [cat.id for cat in self.get_descendants()] #descendants of current node
        to_move = Ware.objects.filter(category__in=child_ids)  #Ware objects that belong to descendants
        to_move.update(category=self.parent, brand=brand)      #transfering wares from child to parents

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
    
    title       = models.CharField(max_length=250, verbose_name=u'Название')
    slug        = AutoSlugField(max_length=250, populate_from='title', unique=True)
    description = MarkupField(verbose_name=u'Описание', blank=True, null=True, default='')
    logo        = models.ImageField(verbose_name=u'Логотип', blank=True, upload_to='brands/')

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
    description = MarkupField(verbose_name=u'Описание',blank=True, null=True, default='')
    enabled     = models.BooleanField(verbose_name=u'Активен')
    position    = models.IntegerField(verbose_name=u'Положение', default=0)
    min_price   = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    max_price   = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    image       = models.ImageField(blank=True, verbose_name=u'Изображение', upload_to='media/wares')

    objects     = EnabledManager()
    all_objects = models.Manager()
    #tags        = TaggableManager(blank=True)

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

    title          = models.CharField(max_length=250, blank=True, null=True)
    ware           = models.ForeignKey(Ware, verbose_name=u'Товар', related_name='variants')
    price          = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=u'Цена')
    fix_price      = models.BooleanField(verbose_name=u'Фиксировать цену', default=False, help_text=u'Отменяет сброс цены при импорте')
    weight         = models.CharField(max_length=250, verbose_name=u'Вес', default='')
    units          = models.CharField(max_length=250, verbose_name=u'Единицы измерения', default='')
    pack           = models.CharField(max_length=250, verbose_name=u'Упаковка', default='')
    articul        = models.CharField(max_length=250, verbose_name=u'Артикул', db_index=True, unique=True, validators=[MinLengthValidator(2)])
    store_qty      = models.IntegerField(default=0, verbose_name=u'Кол-во на складе')
    position       = models.IntegerField(verbose_name=u'Положение',default=0)
    base_price     = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=u'Цена из базы поставщика')
    original_title = models.CharField(verbose_name=u'Название из базы', max_length=250)

    def __unicode__(self):
        return u'%s - %s - %s' % (self.articul, self.ware, ' '.join([self.weight, self.units, self.pack]))

class ImportIssue(models.Model):
    class Meta:
        verbose_name=u'Проблема импорта'
        verbose_name_plural=u'Проблемы импорта'

    created_at  = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата импорта')
    variant     = models.ForeignKey(Variant, verbose_name=u'Вариант')
    description = models.TextField(verbose_name=u'Описание проблемы')

    def __unicode__(self):
        return u'%s' % self.description

class PriceTransformerASTNode(MPTTModel):
    # PriceTransformer(x) = price_modification_coefficient
    # x = variant with select_related
    LEXEME_TYPE = (
        (1, 'IF'),
        (2, 'OPERATOR'), # +, -, *, >, >=, <, <=, ==
        (3, 'VARIABLE'), # x.ware.title, x.price, x.ware.category, ...
    )
    parent    = models.ForeignKey('self', blank=True, null=True, related_name='children')
    comment   = models.TextField(blank=True)
    lexeme    = models.IntegerField(choices=LEXEME_TYPE)
    value     = models.TextField()
    # compiled s-expr (self and children)
    _compiled = models.TextField(blank=True)

    def to_python(self):
        lType = self.LEXEME_TYPE[self.lexeme]
        children = list( self.children.all() )
        if lType == 'IF':
            res = 'if (%s):\n%s\n' % (children[0].compile(), children[1].compile())
            if len(children) > 2:
                res += 'else:\n%s' % children[2].compile()
        elif lType == 'OPERATOR':
            res = self.value.join(map(lambda w: w.compile(), children))
        elif lType == '':
            res = self.value
        return res

    # compiles self and children
    def compile(self):
        # compile
        self._compiled = self.to_python()
        self.save()
        return self._compiled

class PriceTransformer(models.Model):
    class Meta:
        verbose_name=u'Преобразование цены'
        verbose_name_plural=u'Преобразования цен'

    priority = models.IntegerField(verbose_name=u'Приоритет исполнения', unique=True)
    title    = models.CharField(max_length=250, verbose_name=u'Название')
    ast_root = models.ForeignKey(PriceTransformerASTNode, verbose_name=u'Преобразование',blank=True, null=True)

class Order(models.Model):
    STATUS = (u'Создан', u'Оформлен', u'Обработан', u'Доставлен', u'Ошибка')
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

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        if self.status == 1:
            data = {'order': self}
            # notify user
            EmailTemplate.get('shop.order.create_notification.user').send(receivers=[self.email], data=data)
            # notify manager
            managers = [user.email for user in User.objects.filter(is_staff=True)]
            EmailTemplate.get('shop.order.create_notification.manager').send(receivers=managers, data=data)

class OrderedWare(models.Model):
    class Meta:
        verbose_name=u'Товар в заказе'
        verbose_name_plural=u'Товары в заказах'

    variant = models.ForeignKey(Variant, verbose_name=u'Вариант товара')
    qty     = models.PositiveIntegerField(verbose_name=u'Количество')
    order   = models.ForeignKey(Order, verbose_name=u'Заказ')

import signals