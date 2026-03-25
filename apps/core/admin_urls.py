from django.urls import path
from . import admin_views

app_name = 'admin_views'

urlpatterns = [
    path('dashboard/', admin_views.admin_dashboard, name='dashboard'),
    path('utilisateurs/', admin_views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('utilisateurs/creer/', admin_views.creer_utilisateur, name='creer_utilisateur'),
    path('utilisateurs/<int:user_id>/modifier/', admin_views.modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateurs/<int:user_id>/desactiver/', admin_views.desactiver_utilisateur, name='desactiver_utilisateur'),
    path('utilisateurs/<int:user_id>/supprimer/', admin_views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('statistiques/', admin_views.statistiques_globales, name='statistiques_globales'),
]