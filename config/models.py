#-*- coding: utf-8 -*-
from decimal import Decimal

from django.db import models

from utils import cached

class Entry(models.Model):
    class Meta:
        verbose_name=u'Настройка'
        verbose_name_plural=u'Настройки'

    TYPES = (
        (1, u'Целое число'),
        (2, u'Действительное число'),
        (3, u'Строка'),
        (4, u'Текст')
    )

    title = models.CharField(max_length=250, verbose_name=u'Название')
    key   = models.CharField(max_length=250, unique=True, verbose_name=u'Ключ')
    type  = models.IntegerField(choices=TYPES, verbose_name=u'Тип значения')
    value = models.TextField(verbose_name=u'Значение')

    def get_value(self):
        if self.type == 1:
            return int(self.value)
        elif self.type == 2:
            return Decimal(self.value)
        else:
            return self.value

    @staticmethod
    def get(key, default=None):
        def dictify(qs):
            res = {}
            for o in qs:
                res[o.key] = o.get_value()
            return res
        config = cached(lambda: dictify(Entry.objects.all()), 'config-settings')
        return config.get(key, default)
