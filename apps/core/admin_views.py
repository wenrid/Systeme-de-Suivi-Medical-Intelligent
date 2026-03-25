from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from apps.authentication.models import User
from apps.patients.models import Patient
from apps.dossiers.models import DossierMedical
from datetime import datetime, timedelta

@login_required
def admin_dashboard(request):
    """Dashboard principal de l'administrateur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé - Réservé aux administrateurs")
        return redirect('core:dashboard_redirect')
    
    # Statistiques globales
    total_users = User.objects.count()
    medecins = User.objects.filter(role='medecin')
    analystes = User.objects.filter(role='analyste')
    admins = User.objects.filter(role='admin')
    
    total_patients = Patient.objects.count()
    total_dossiers = DossierMedical.objects.count()
    
    # Activité récente (7 derniers jours)
    sept_jours = datetime.now() - timedelta(days=7)
    nouveaux_patients = Patient.objects.filter(date_creation__gte=sept_jours).count()
    nouvelles_consultations = DossierMedical.objects.filter(date_consultation__gte=sept_jours).count()
    
    # Médecins les plus actifs
    medecins_actifs = User.objects.filter(role='medecin').annotate(
        nb_dossiers=Count('dossiers_crees')
    ).order_by('-nb_dossiers')[:5]
    
    # Dossiers par statut
    dossiers_ouverts = DossierMedical.objects.filter(statut='ouvert').count()
    dossiers_fermes = DossierMedical.objects.filter(statut='ferme').count()
    dossiers_urgents = DossierMedical.objects.filter(urgence__in=['elevee', 'critique']).count()
    
    context = {
        'total_users': total_users,
        'total_medecins': medecins.count(),
        'medecins_actifs_count': medecins.filter(is_active=True).count(),
        'total_analystes': analystes.count(),
        'analystes_actifs_count': analystes.filter(is_active=True).count(),
        'total_admins': admins.count(),
        'total_patients': total_patients,
        'total_dossiers': total_dossiers,
        'nouveaux_patients': nouveaux_patients,
        'nouvelles_consultations': nouvelles_consultations,
        'medecins_actifs': medecins_actifs,
        'dossiers_ouverts': dossiers_ouverts,
        'dossiers_fermes': dossiers_fermes,
        'dossiers_urgents': dossiers_urgents,
    }
    
    return render(request, 'admin/dashboard.html', context)

@login_required
def gestion_utilisateurs(request):
    """Liste et gestion de tous les utilisateurs"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    # Filtres
    role_filtre = request.GET.get('role', '')
    statut_filtre = request.GET.get('statut', '')
    search = request.GET.get('search', '')
    
    users = User.objects.all()
    
    if role_filtre:
        users = users.filter(role=role_filtre)
    
    if statut_filtre == 'actif':
        users = users.filter(is_active=True)
    elif statut_filtre == 'inactif':
        users = users.filter(is_active=False)
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'role_filtre': role_filtre,
        'statut_filtre': statut_filtre,
        'search': search,
    }
    
    return render(request, 'admin/gestion_utilisateurs.html', context)

@login_required
def creer_utilisateur(request):
    """Créer un nouveau utilisateur (médecin, analyste, admin)"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        password = request.POST.get('password')
        specialite = request.POST.get('specialite', '')
        
        # Vérifier si l'username existe déjà
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà")
            return render(request, 'admin/creer_utilisateur.html')
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            specialite=specialite if role == 'medecin' else ''
        )
        
        messages.success(request, f"Utilisateur {user.get_full_name()} créé avec succès !")
        return redirect('admin_views:gestion_utilisateurs')
    
    return render(request, 'admin/creer_utilisateur.html')

@login_required
def modifier_utilisateur(request, user_id):
    """Modifier un utilisateur existant"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.is_active = request.POST.get('is_active') == 'on'
        
        if user.role == 'medecin':
            user.specialite = request.POST.get('specialite', '')
        
        # Changer le mot de passe si fourni
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        
        messages.success(request, f"Utilisateur {user.get_full_name()} modifié avec succès !")
        return redirect('admin_views:gestion_utilisateurs')
    
    context = {
        'user_obj': user,
    }
    
    return render(request, 'admin/modifier_utilisateur.html', context)

@login_required
def desactiver_utilisateur(request, user_id):
    """Activer/Désactiver un utilisateur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    user = get_object_or_404(User, id=user_id)
    
    # Ne pas se désactiver soi-même
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte")
        return redirect('admin_views:gestion_utilisateurs')
    
    user.is_active = not user.is_active
    user.save()
    
    statut = "activé" if user.is_active else "désactivé"
    messages.success(request, f"Utilisateur {user.get_full_name()} {statut} avec succès !")
    
    return redirect('admin_views:gestion_utilisateurs')

@login_required
def supprimer_utilisateur(request, user_id):
    """Supprimer un utilisateur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    user = get_object_or_404(User, id=user_id)
    
    # Ne pas se supprimer soi-même
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte")
        return redirect('admin_views:gestion_utilisateurs')
    
    if request.method == 'POST':
        nom_user = user.get_full_name()
        user.delete()
        messages.success(request, f"Utilisateur {nom_user} supprimé avec succès !")
        return redirect('admin_views:gestion_utilisateurs')
    
    context = {
        'user_obj': user,
    }
    
    return render(request, 'admin/confirmer_suppression_user.html', context)

@login_required
def statistiques_globales(request):
    """Statistiques globales détaillées pour l'admin"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    # Toutes les statistiques imaginables
    stats = {
        'patients': {
            'total': Patient.objects.count(),
            'hommes': Patient.objects.filter(sexe='M').count(),
            'femmes': Patient.objects.filter(sexe='F').count(),
            'actifs': Patient.objects.filter(statut='actif').count(),
        },
        'dossiers': {
            'total': DossierMedical.objects.count(),
            'ouverts': DossierMedical.objects.filter(statut='ouvert').count(),
            'fermes': DossierMedical.objects.filter(statut='ferme').count(),
            'urgents': DossierMedical.objects.filter(urgence='critique').count(),
        },
        'utilisateurs': {
            'total': User.objects.count(),
            'medecins': User.objects.filter(role='medecin', is_active=True).count(),
            'analystes': User.objects.filter(role='analyste', is_active=True).count(),
            'admins': User.objects.filter(role='admin').count(),
        }
    }
    
    # Activité par médecin
    medecins_stats = User.objects.filter(role='medecin').annotate(
        nb_consultations=Count('dossiers_crees')
    ).order_by('-nb_consultations')
    
    context = {
        'stats': stats,
        'medecins_stats': medecins_stats,
    }
    
    return render(request, 'admin/statistiques_globales.html', context)