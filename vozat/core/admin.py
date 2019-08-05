from django.contrib import admin
from .models import Radio, ProgramasRadiales

@admin.register(Radio)
class RadioAdmin(admin.ModelAdmin):
    list_display = ('radio', 'web')
    search_fields = ('radio',)
    fields = ('radio', 'web', 'usuario')

@admin.register(ProgramasRadiales)
class ProgramasAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'radios')
    search_fields = ('nombre',)