from django.contrib import admin
from .models import Brew, BrewType, Quality


class QualityAdmin(admin.ModelAdmin):
    list_display = ('value',)
    ordering = ('value',)
    search_fields = ('value',)


class BrewTypeAdmin(admin.ModelAdmin):
    list_display = ('value',)
    ordering = ('value',)
    search_fields = ('value',)


class BrewAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'completion_date', 'get_brew_type', 'get_brewer')
    ordering = ('-completion_date', '-start_date')
    search_fields = ('start_date', 'completion_date', 'brew_type__value', 'creator__username')

    def get_brew_type(self, obj):
        return obj.brew_type.value
    
    get_brew_type.short_description = 'Brew Type'
    get_brew_type.admin_order_field  = 'brew_type'
    
    def get_brewer(self, obj):
        return obj.creator.username
    
    get_brewer.short_description = 'Brewer'
    get_brewer.admin_order_field  = 'creator__username'
    
    


admin.site.register(Quality, QualityAdmin)
admin.site.register(BrewType, BrewTypeAdmin)
admin.site.register(Brew, BrewAdmin)