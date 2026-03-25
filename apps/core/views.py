from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from apps.patients.models import Patient
from apps.dossiers.models import DossierMedical
from django.db.models import Count, Q, Avg
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import datetime, timedelta
import json

def login_view(request):
    """Page de connexion personnalisée"""
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('core:dashboard_redirect')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect')
    
    return render(request, 'login.html')

def logout_view(request):
    """Déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès')
    return redirect('core:login')

@login_required
def dashboard_redirect(request):
    """Redirige vers le bon tableau de bord selon le rôle"""
    if request.user.role == 'medecin':
        return redirect('core:dashboard_medecin')
    elif request.user.role == 'analyste':
        return redirect('core:dashboard_analyste')
    elif request.user.role == 'admin':
        return redirect('core:dashboard_admin')
    else:
        messages.error(request, "Rôle non reconnu")
        return redirect('core:login')

@login_required
def dashboard_medecin(request):
    """Tableau de bord pour les médecins"""
    if request.user.role != 'medecin':
        messages.error(request, "Accès non autorisé")
        return redirect('core:login')
    
    # Statistiques pour le médecin
    mes_patients = Patient.objects.filter(dossiers__medecin=request.user).distinct()
    mes_dossiers = DossierMedical.objects.filter(medecin=request.user)
    
    context = {
        'total_patients': mes_patients.count(),
        'total_dossiers': mes_dossiers.count(),
        'dossiers_ouverts': mes_dossiers.filter(statut='ouvert').count(),
        'derniers_dossiers': mes_dossiers.order_by('-date_consultation')[:5],
    }
    
    return render(request, 'dashboard/medecin.html', context)

@login_required
def dashboard_analyste(request):
    """Tableau de bord pour les analystes avec statistiques avancées"""
    if request.user.role != 'analyste':
        messages.error(request, "Accès non autorisé")
        return redirect('core:login')
    
    # Statistiques globales
    total_patients = Patient.objects.count()
    total_dossiers = DossierMedical.objects.count()
    
    # Patients par sexe
    patients_hommes = Patient.objects.filter(sexe='M').count()
    patients_femmes = Patient.objects.filter(sexe='F').count()
    
    # Patients par groupe sanguin
    groupes_sanguins = Patient.objects.exclude(groupe_sanguin='').values('groupe_sanguin').annotate(
        total=Count('id')
    ).order_by('-total')
    
    # Répartition par tranche d'âge
    tranches_age = {
        '0-18': 0,
        '19-35': 0,
        '36-50': 0,
        '51-65': 0,
        '66+': 0
    }
    
    for patient in Patient.objects.all():
        age = patient.age
        if age <= 18:
            tranches_age['0-18'] += 1
        elif age <= 35:
            tranches_age['19-35'] += 1
        elif age <= 50:
            tranches_age['36-50'] += 1
        elif age <= 65:
            tranches_age['51-65'] += 1
        else:
            tranches_age['66+'] += 1
    
    # Dossiers par statut
    dossiers_par_statut = DossierMedical.objects.values('statut').annotate(
        total=Count('id')
    )
    
    # Dossiers par urgence
    dossiers_par_urgence = DossierMedical.objects.values('urgence').annotate(
        total=Count('id')
    )
    
    # Top 5 des villes
    top_villes = Patient.objects.exclude(ville='').values('ville').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    # Maladies chroniques les plus fréquentes
    maladies_chroniques = {
        'Diabète': Patient.objects.filter(diabete=True).count(),
        'Hypertension': Patient.objects.filter(hypertension=True).count(),
        'Asthme': Patient.objects.filter(asthme=True).count(),
        'Épilepsie': Patient.objects.filter(epilepsie=True).count(),
        'Drépanocytose': Patient.objects.filter(drepanocytose=True).count(),
        'VIH': Patient.objects.filter(vih=True).count(),
    }
    
    # Consultations par mois (6 derniers mois)
    six_mois_ago = datetime.now() - timedelta(days=180)
    consultations_par_mois = DossierMedical.objects.filter(
        date_consultation__gte=six_mois_ago
    ).annotate(
        mois=ExtractMonth('date_consultation'),
        annee=ExtractYear('date_consultation')
    ).values('mois', 'annee').annotate(
        total=Count('id')
    ).order_by('annee', 'mois')
    
    # Préparer les données pour les graphiques (format JSON)
    context = {
        'total_patients': total_patients,
        'total_dossiers': total_dossiers,
        'patients_hommes': patients_hommes,
        'patients_femmes': patients_femmes,
        
        # Données pour graphiques
        'groupes_sanguins': json.dumps(list(groupes_sanguins)),
        'tranches_age': json.dumps(tranches_age),
        'dossiers_par_statut': json.dumps(list(dossiers_par_statut)),
        'dossiers_par_urgence': json.dumps(list(dossiers_par_urgence)),
        'top_villes': json.dumps(list(top_villes)),
        'maladies_chroniques': json.dumps(maladies_chroniques),
        'consultations_par_mois': json.dumps(list(consultations_par_mois)),
    }
    
    return render(request, 'stats/dashboard.html', context)

@login_required  
def dashboard_admin(request):
    """Tableau de bord pour les administrateurs - Redirection"""
    if request.user.role != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('core:login')
    
    # Rediriger vers le nouveau dashboard admin complet
    return redirect('admin_views:dashboard')