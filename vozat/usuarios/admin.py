from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_active')
    search_fields = ('username', 'first_name', 'last_name')
    fieldsets = (
            ('Información Usuario', {'fields': ('username', 'password')}),
            ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'avatar')}),
            ('Administración', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions', 'last_login', 'date_joined')}),
        )

#admin.site.register(Usuario, UsuarioAdmin)