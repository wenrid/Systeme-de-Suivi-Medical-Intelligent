from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class MedicalUserAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'role', 'specialite', 'is_active_medical', 'date_joined']
    list_filter = ['role', 'is_active_medical', 'specialite', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'numero_ordre']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations médicales', {
            'fields': ('role', 'numero_ordre', 'specialite', 'telephone', 'is_active_medical')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations médicales', {
            'fields': ('role', 'numero_ordre', 'specialite', 'telephone')
        }),
    )