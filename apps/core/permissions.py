from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.color import no_style
from django.db import connection

class RoleBasedPermissionMixin:
    """Mixin pour les permissions basées sur les rôles"""
    
    def has_medecin_permission(self):
        return self.user.role == 'medecin'
    
    def has_analyste_permission(self):
        return self.user.role == 'analyste'
    
    def has_admin_permission(self):
        return self.user.role == 'admin'

def create_custom_permissions():
    """Créer les permissions personnalisées pour le système médical"""
    
    # Permissions pour les médecins
    medecin_permissions = [
        ('can_create_dossier', 'Peut créer des dossiers médicaux'),
        ('can_view_own_patients', 'Peut voir ses propres patients'),
        ('can_modify_dossier', 'Peut modifier les dossiers médicaux'),
    ]
    
    # Permissions pour les analystes
    analyste_permissions = [
        ('can_view_statistics', 'Peut voir les statistiques'),
        ('can_export_reports', 'Peut exporter des rapports'),
        ('can_view_all_data', 'Peut voir toutes les données anonymisées'),
    ]
    
    # Permissions pour les administrateurs
    admin_permissions = [
        ('can_manage_users', 'Peut gérer les utilisateurs'),
        ('can_backup_system', 'Peut sauvegarder le système'),
        ('can_view_audit_logs', 'Peut voir les logs d\'audit'),
    ]
    
    # Créer les permissions dans la base
    from apps.authentication.models import User
    content_type = ContentType.objects.get_for_model(User)
    
    all_permissions = medecin_permissions + analyste_permissions + admin_permissions
    
    for codename, name in all_permissions:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type,
        )
        if created:
            print(f"Créé: {name}")