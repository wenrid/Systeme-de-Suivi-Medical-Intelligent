from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DossierMedical
from .forms import DossierMedicalForm
from django.db.models import Q

@login_required
def liste_dossiers(request):
    """Liste tous les dossiers du médecin avec recherche avancée"""
    if request.user.role != 'medecin':
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    # Récupérer les dossiers du médecin
    dossiers = DossierMedical.objects.filter(medecin=request.user)
    
    # Recherche générale
    search_query = request.GET.get('search', '')
    if search_query:
        dossiers = dossiers.filter(
            Q(patient__nom__icontains=search_query) |
            Q(patient__prenom__icontains=search_query) |
            Q(patient__code_patient__icontains=search_query) |
            Q(motif_consultation__icontains=search_query) |
            Q(diagnostic__icontains=search_query)
        )
    
    # Filtres avancés
    statut = request.GET.get('statut', '')
    if statut:
        dossiers = dossiers.filter(statut=statut)
    
    urgence = request.GET.get('urgence', '')
    if urgence:
        dossiers = dossiers.filter(urgence=urgence)
    
    date_debut = request.GET.get('date_debut', '')
    if date_debut:
        dossiers = dossiers.filter(date_consultation__gte=date_debut)
    
    date_fin = request.GET.get('date_fin', '')
    if date_fin:
        dossiers = dossiers.filter(date_consultation__lte=date_fin)
    
    # Tri
    ordre = request.GET.get('ordre', '-date_consultation')
    dossiers = dossiers.order_by(ordre)
    
    context = {
        'dossiers': dossiers,
        'total': dossiers.count(),
        'ouverts': dossiers.filter(statut='ouvert').count(),
        'search_query': search_query,
        'statut': statut,
        'urgence': urgence,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'ordre': ordre,
    }
    
    return render(request, 'dossiers/liste.html', context)

@login_required
def creer_dossier(request):
    """Créer un nouveau dossier médical"""
    if request.user.role != 'medecin':
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        form = DossierMedicalForm(request.POST)
        if form.is_valid():
            dossier = form.save(commit=False)
            dossier.medecin = request.user
            dossier.save()
            messages.success(request, "Dossier médical créé avec succès")
            return redirect('dossiers:detail', pk=dossier.pk)
    else:
        form = DossierMedicalForm()
    
    return render(request, 'dossiers/form.html', {'form': form, 'action': 'Créer'})

@login_required
def detail_dossier(request, pk):
    """Afficher les détails d'un dossier"""
    dossier = get_object_or_404(DossierMedical, pk=pk)
    
    # Vérifier que le médecin a accès à ce dossier
    if request.user.role == 'medecin' and dossier.medecin != request.user:
        messages.error(request, "Vous n'avez pas accès à ce dossier")
        return redirect('dossiers:liste')
    
    return render(request, 'dossiers/detail.html', {'dossier': dossier})

@login_required
def modifier_dossier(request, pk):
    """Modifier un dossier existant"""
    dossier = get_object_or_404(DossierMedical, pk=pk, medecin=request.user)
    
    if request.method == 'POST':
        form = DossierMedicalForm(request.POST, instance=dossier)
        if form.is_valid():
            form.save()
            messages.success(request, "Dossier modifié avec succès")
            return redirect('dossiers:detail', pk=dossier.pk)
    else:
        form = DossierMedicalForm(instance=dossier)
    
    return render(request, 'dossiers/form.html', {'form': form, 'action': 'Modifier', 'dossier': dossier})

@login_required
def supprimer_dossier(request, pk):
    """Supprimer un dossier"""
    dossier = get_object_or_404(DossierMedical, pk=pk, medecin=request.user)
    
    if request.method == 'POST':
        dossier.delete()
        messages.success(request, "Dossier supprimé avec succès")
        return redirect('dossiers:liste')
    
    return render(request, 'dossiers/confirmer_suppression.html', {'dossier': dossier})
from django.http import HttpResponse
from .pdf_utils import generer_pdf_dossier

@login_required
def exporter_pdf_dossier(request, pk):
    """Exporter un dossier médical en PDF"""
    dossier = get_object_or_404(DossierMedical, pk=pk)
    
    # Vérifier que l'utilisateur a accès à ce dossier
    if request.user.role == 'medecin' and dossier.medecin != request.user:
        messages.error(request, "Vous n'avez pas accès à ce dossier")
        return redirect('dossiers:liste')
    
    # Générer le PDF
    buffer = generer_pdf_dossier(dossier)
    
    # Créer la réponse HTTP
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"dossier_{dossier.patient.code_patient}_{dossier.date_consultation.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response