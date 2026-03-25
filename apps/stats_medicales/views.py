from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .services import StatisticsService
from .models import AnalyseStatistique, RapportAnnuel
from django.http import HttpResponse
from .pdf_reports import generer_rapport_statistiques
from datetime import datetime
from .ml_analysis import MedicalAIAnalysis
from django.shortcuts import render, redirect, get_object_or_404
from .epidemic_prediction import EpidemicPredictor
import json

@login_required
def dashboard_statistiques(request):
    """Dashboard principal des statistiques"""
    analyses_recentes = AnalyseStatistique.objects.filter(is_public=True)[:5]
    rapport_recent = RapportAnnuel.objects.first()
    
    context = {
        'analyses_recentes': analyses_recentes,
        'rapport_recent': rapport_recent,
        'annee_courante': timezone.now().year,
    }
    
    return render(request, 'stats/dashboard.html', context)

@login_required
def generer_analyse_age(request):
    """Génère une analyse par tranche d'âge"""
    resultats = StatisticsService.analyser_par_tranche_age()
    
    analyse = StatisticsService.sauvegarder_analyse(
        type_analyse='age_groups',
        titre=f'Analyse par âge - {timezone.now().strftime("%d/%m/%Y")}',
        resultats=resultats,
        user=request.user
    )
    
    return redirect('dashboard_statistiques')

@login_required
def generer_pathologies(request):
    """Génère l'analyse des pathologies fréquentes"""
    resultats = StatisticsService.pathologies_frequentes()
    
    analyse = StatisticsService.sauvegarder_analyse(
        type_analyse='pathologies',
        titre=f'Pathologies fréquentes - {timezone.now().strftime("%d/%m/%Y")}',
        resultats=dict(resultats),
        user=request.user
    )
    
    return redirect('dashboard_statistiques')

@login_required
def generer_rapport_annuel(request, annee=None):
    """Génère un rapport annuel"""
    if not annee:
        annee = timezone.now().year
    
    rapport = StatisticsService.generer_rapport_annuel(annee, request.user)


    
    
    return redirect('dashboard_statistiques')


@login_required
def exporter_rapport_pdf(request):
    """Exporter un rapport statistique en PDF"""
    if request.user.role != 'analyste':
        messages.error(request, "Seuls les analystes peuvent générer des rapports")
        return redirect('core:dashboard_redirect')
    
    # Générer le rapport
    buffer = generer_rapport_statistiques(type_rapport='global')
    
    # Créer la réponse HTTP
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"rapport_statistiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response



@login_required
def analyse_ia_dashboard(request):
    """Dashboard principal des analyses IA"""
    if request.user.role not in ['analyste', 'admin']:
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    # Analyses IA
    patients_risque = MedicalAIAnalysis.identifier_patients_a_risque(limite=10)
    analyse_age = MedicalAIAnalysis.analyser_par_tranche_age()
    analyse_geo = MedicalAIAnalysis.analyser_par_zone_geographique()
    
    context = {
        'patients_risque': patients_risque,
        'analyse_age': analyse_age,
        'analyse_geo': analyse_geo,
    }
    
    return render(request, 'stats/ia_dashboard.html', context)

@login_required
def patient_risque_detail(request, patient_id):
    """Détail du score de risque d'un patient"""
    if request.user.role not in ['analyste', 'medecin']:
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    from apps.patients.models import Patient
    patient = get_object_or_404(Patient, pk=patient_id)
    
    analyse = MedicalAIAnalysis.calculer_score_risque(patient)
    recommandations = MedicalAIAnalysis.generer_recommandations(patient)
    
    context = {
        'patient': patient,
        'score': analyse['score'],
        'niveau': analyse['niveau'],
        'facteurs': analyse['facteurs'],
        'recommandations': recommandations,
    }
    
    return render(request, 'stats/patient_risque.html', context)


@login_required
def prediction_epidemies(request):
    """Dashboard de prédiction d'épidémies"""
    if request.user.role not in ['analyste', 'admin']:
        messages.error(request, "Accès non autorisé")
        return redirect('core:dashboard_redirect')
    
    # Analyse des tendances temporelles
    tendances = EpidemicPredictor.analyser_tendances_maladies(
        jours_historique=90,
        jours_prediction=30
    )
    
    # Analyse des maladies chroniques
    maladies_tendances = EpidemicPredictor.analyser_maladies_chroniques_tendances()
    
    # Détection d'épidémies locales
    epidemies_locales = EpidemicPredictor.detecter_epidemies_locales()
    
    context = {
        'tendances': tendances,
        'maladies_tendances': maladies_tendances,
        'epidemies_locales': epidemies_locales,
        'tendances_json': json.dumps(tendances) if tendances.get('statut') == 'success' else '{}',
    }
    
    return render(request, 'stats/prediction_epidemies.html', context)