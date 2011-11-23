from django.contrib import admin
from django.db import models

from mptt.admin import MPTTModelAdmin

from models import Ware, Variant, Category, Brand

class WareAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/admin.css',)
        }

    list_select_related = True
    list_display = ('id', 'brand', 'title', 'enabled', 'category')
    list_editable = ('brand', 'title', 'enabled')
    list_filter = ('brand',)
    search_fields = ('title',)

class VariantAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ('ware', 'pack', 'price', 'units')

admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Brand)
admin.site.register(Ware, WareAdmin)
admin.site.register(Variant, VariantAdmin)
