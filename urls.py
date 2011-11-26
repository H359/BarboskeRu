from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'views.home', name='home'),
    url(r'^catalog/(?P<path>.*)$', 'shop.views.category', name='shop-category'),
    url(r'^basket/$', 'shop.views.basket', name='shop-basket'),
    url(r'^page/(?P<url>.*)$', 'staticpages.views.page', name='staticpages-page'),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
      url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
