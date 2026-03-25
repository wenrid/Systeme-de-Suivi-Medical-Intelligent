from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient
from .forms import PatientForm
from django.db.models import Q

@login_required
def liste_patients(request):
    """Liste des patients avec recherche avancée"""
    if request.user.role not in ['medecin', 'analyste', 'admin']:
        messages.error(request, "Accès non autorisé")
        return redirect('core:login')
    
    # Récupérer tous les patients
    patients = Patient.objects.all().order_by('-date_creation')
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(code_patient__icontains=search_query) |
            Q(telephone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filtres avancés
    sexe = request.GET.get('sexe', '')
    if sexe:
        patients = patients.filter(sexe=sexe)
    
    groupe_sanguin = request.GET.get('groupe_sanguin', '')
    if groupe_sanguin:
        patients = patients.filter(groupe_sanguin=groupe_sanguin)
    
    statut = request.GET.get('statut', '')
    if statut:
        patients = patients.filter(statut=statut)
    
    ville = request.GET.get('ville', '')
    if ville:
        patients = patients.filter(ville__icontains=ville)
    
    # Filtres par maladies chroniques
    if request.GET.get('diabete'):
        patients = patients.filter(diabete=True)
    if request.GET.get('hypertension'):
        patients = patients.filter(hypertension=True)
    if request.GET.get('asthme'):
        patients = patients.filter(asthme=True)
    
    context = {
        'patients': patients,
        'search_query': search_query,
        'sexe': sexe,
        'groupe_sanguin': groupe_sanguin,
        'statut': statut,
        'ville': ville,
        'total_resultats': patients.count(),
    }
    
    return render(request, 'patients/liste.html', context)

@login_required
def ajouter_patient(request):
    """Ajouter un nouveau patient"""
    if request.user.role != 'medecin':
        messages.error(request, "Seuls les médecins peuvent créer des patients")
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.cree_par = request.user
            patient.statut = 'actif'
            patient.save()
            messages.success(request, f'Patient {patient.nom_complet} créé avec succès !')
            return redirect('patients:liste_patients')
    else:
        form = PatientForm()
    
    context = {
        'form': form,
        'titre': 'Ajouter un patient',
    }
    
    return render(request, 'patients/form.html', context)

@login_required
def modifier_patient(request, pk):
    """Modifier un patient existant"""
    if request.user.role != 'medecin':
        messages.error(request, "Seuls les médecins peuvent modifier des patients")
        return redirect('core:dashboard_redirect')
    
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f'Patient {patient.nom_complet} modifié avec succès !')
            return redirect('patients:liste_patients')
    else:
        form = PatientForm(instance=patient)
    
    context = {
        'form': form,
        'patient': patient,
        'titre': 'Modifier le patient',
    }
    
    return render(request, 'patients/form.html', context)

@login_required
def detail_patient(request, pk):
    """Voir les détails d'un patient"""
    if request.user.role not in ['medecin', 'analyste', 'admin']:
        messages.error(request, "Accès non autorisé")
        return redirect('core:login')
    
    patient = get_object_or_404(Patient, pk=pk)
    
    context = {
        'patient': patient,
        'user': request.user,
    }
    
    return render(request, 'patients/detail.html', context)

@login_required
def supprimer_patient(request, pk):
    """Supprimer un patient (admin uniquement)"""
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent supprimer des patients")
        return redirect('patients:liste_patients')
    
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        nom_patient = patient.nom_complet
        patient.delete()
        messages.success(request, f"Patient {nom_patient} supprimé avec succès")
        return redirect('patients:liste_patients')
    
    context = {
        'patient': patient
    }
    
    return render(request, 'patients/supprimer.html', context)