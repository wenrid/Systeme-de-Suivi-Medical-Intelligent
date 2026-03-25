from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from apps.authentication.models import User

class Command(BaseCommand):
    help = 'Configure les permissions et groupes pour le système médical'

    def handle(self, *args, **options):
        self.stdout.write('Configuration des permissions médicales...')
        
        # Créer les groupes
        medecin_group, created = Group.objects.get_or_create(name='Médecins')
        analyste_group, created = Group.objects.get_or_create(name='Analystes')
        admin_group, created = Group.objects.get_or_create(name='Administrateurs')
        
        # Créer les permissions personnalisées
        content_type = ContentType.objects.get_for_model(User)
        
        # Permissions pour médecins
        medecin_perms = [
            ('can_create_dossier', 'Peut créer des dossiers médicaux'),
            ('can_view_own_patients', 'Peut voir ses propres patients'),
            ('can_modify_dossier', 'Peut modifier les dossiers médicaux'),
        ]
        
        # Permissions pour analystes
        analyste_perms = [
            ('can_view_statistics', 'Peut voir les statistiques'),
            ('can_export_reports', 'Peut exporter des rapports'),
            ('can_view_all_data', 'Peut voir toutes les données anonymisées'),
        ]
        
        # Permissions pour admins
        admin_perms = [
            ('can_manage_users', 'Peut gérer les utilisateurs'),
            ('can_backup_system', 'Peut sauvegarder le système'),
            ('can_view_audit_logs', 'Peut voir les logs d\'audit'),
        ]
        
        # Créer et assigner les permissions
        for codename, name in medecin_perms:
            perm, created = Permission.objects.get_or_create(
                codename=codename, name=name, content_type=content_type
            )
            medecin_group.permissions.add(perm)
        
        for codename, name in analyste_perms:
            perm, created = Permission.objects.get_or_create(
                codename=codename, name=name, content_type=content_type
            )
            analyste_group.permissions.add(perm)
        
        for codename, name in admin_perms:
            perm, created = Permission.objects.get_or_create(
                codename=codename, name=name, content_type=content_type
            )
            admin_group.permissions.add(perm)
        
        # Assigner les utilisateurs aux groupes selon leur rôle
        for user in User.objects.all():
            user.groups.clear()  # Nettoyer d'abord
            if user.role == 'medecin':
                user.groups.add(medecin_group)
            elif user.role == 'analyste':
                user.groups.add(analyste_group)
            elif user.role == 'admin':
                user.groups.add(admin_group)
        
        self.stdout.write(
            self.style.SUCCESS('Permissions configurées avec succès!')
        )