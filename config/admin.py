from django.contrib import admin

from models import Entry

class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'key', 'value',)
    search_field = ('key',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

admin.site.register(Entry, EntryAdmin)
