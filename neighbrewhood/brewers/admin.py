from django.contrib import admin
from .models import Brewer


class BrewerAdmin(admin.ModelAdmin):
    list_display = ('get_first_name', 'get_last_name', 'get_email', 'get_username', 'phone_number', 'location')
    ordering = ()
    search_fields = ('user__username', 'user__last_name', 'phone_number')

    def get_first_name(self, obj):
        return obj.user.first_name
    
    def get_last_name(self, obj):
        return obj.user.last_name
    
    def get_email(self, obj):
        return obj.user.email
    
    def get_username(self, obj):
        return obj.user.username
    
    get_first_name.short_description = "First Name"
    get_first_name.admin_order_field = "user__first_name"
    get_last_name.short_description = "Last Name"
    get_last_name.admin_order_field = "user__last_name"
    get_email.short_description = "Email"
    get_email.admin_order_field = "user__email"
    get_username.short_description = "Username"
    get_username.admin_order_field = "user__username"


admin.site.register(Brewer, BrewerAdmin)
