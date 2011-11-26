#-*- coding: utf-8 -*-
from django.db import models

class StaticPage(models.Model):
    class Meta:
        verbose_name=u'Статичная страница'
        verbose_name_plural=u'Статичные страницы'
    url   = models.CharField(max_length=250, verbose_name=u'Адрес (имя файла.html)')
    title = models.CharField(max_length=250, verbose_name=u'Заголовок')
    body  = models.TextField(verbose_name=u'Тело')

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.url)
