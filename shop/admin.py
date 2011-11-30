from django.contrib import admin
from django.db import models
from django.forms import CharField

from mptt.admin import MPTTModelAdmin

from models import Ware, Variant, Category, Brand, Order, OrderedWare, ImportIssue

class VariantAdminInline(admin.TabularInline):
    model = Variant

    def queryset(self, request):
        return super(VariantAdminInline, self).queryset(request).select_related()

class OrderedWareAdminInline(admin.TabularInline):
    model = OrderedWare
    extra = 0
    max_num = 1
    fields = ('variant', 'qty')
    readonly_fields = ('variant',)
    can_delete = False

class WareAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/admin.css',)
        }

    list_select_related = True
    list_display = ('id', 'brand', 'title', 'enabled', 'category')
    list_editable = ('title', 'enabled')
    list_filter = ('brand',)
    search_fields = ('title',)
    inlines = [VariantAdminInline]

    def queryset(self, request):
        return super(WareAdmin, self).queryset(request).select_related()

class VariantAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ('ware', 'pack', 'price', 'units')
    readonly_fields = ('base_price',)

    def queryset(self, request):
        return super(VariantAdmin, self).queryset(request).select_related()

class OrderAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [OrderedWareAdminInline]

    def get_form(self, request, obj=None, **kwargs):
        request._obj = obj
        return super(OrderAdmin, self).get_form(request, obj, **kwargs)

"""
class PriceTransformerAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/pt_tree.css',)}
        js = ('js/d3.js', 'js/d3.layout.js', 'js/pt.js',)
"""

class ImportIssueAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'variant', 'created_at')
    list_select_related = True

admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Brand)
admin.site.register(Ware, WareAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(Order, OrderAdmin)
#admin.site.register(PriceTransformer, PriceTransformerAdmin)
admin.site.register(ImportIssue, ImportIssueAdmin)