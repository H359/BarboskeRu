from django.contrib import admin
from models import EmailTemplate, EmailQueue

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'key',)
    def has_delete_permission(self, request, obj=None):
	return False

class EmailQueueAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
	return False

admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(EmailQueue, EmailQueueAdmin)