from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from apps.patients.models import Patient
from apps.dossiers.models import DossierMedical
from .models import AnalyseStatistique, RapportAnnuel
import json

class StatisticsService:
    """Service pour générer des analyses statistiques"""
    
    @staticmethod
    def analyser_par_tranche_age():
        """Analyse la répartition des patients par tranche d'âge"""
        aujourd_hui = timezone.now().date()
        
        tranches = {
            '0-18': 0,
            '19-30': 0,
            '31-50': 0,
            '51-70': 0,
            '70+': 0
        }
        
        patients = Patient.objects.all()
        
        for patient in patients:
            age = (aujourd_hui - patient.date_naissance).days // 365
            
            if age <= 18:
                tranches['0-18'] += 1
            elif age <= 30:
                tranches['19-30'] += 1
            elif age <= 50:
                tranches['31-50'] += 1
            elif age <= 70:
                tranches['51-70'] += 1
            else:
                tranches['70+'] += 1
        
        return tranches
    
    @staticmethod
    def pathologies_frequentes(limit=10):
        """Retourne les pathologies les plus fréquentes"""
        # Analyse des mots-clés dans les diagnostics
        dossiers = DossierMedical.objects.exclude(diagnostic='')
        
        pathologies = {}
        mots_cles_medicaux = [
            'grippe', 'hypertension', 'diabète', 'asthme', 'migraine',
            'arthrite', 'bronchite', 'pneumonie', 'gastrite', 'allergie',
            'infection', 'inflammation', 'douleur', 'fièvre', 'toux'
        ]
        
        for dossier in dossiers:
            diagnostic_lower = dossier.diagnostic.lower()
            for mot_cle in mots_cles_medicaux:
                if mot_cle in diagnostic_lower:
                    pathologies[mot_cle] = pathologies.get(mot_cle, 0) + 1
        
        # Trier par fréquence
        pathologies_triees = sorted(pathologies.items(), key=lambda x: x[1], reverse=True)
        return pathologies_triees[:limit]
    
    @staticmethod
    def statistiques_par_sexe():
        """Statistiques de répartition par sexe"""
        return {
            'masculin': Patient.objects.filter(sexe='M').count(),
            'feminin': Patient.objects.filter(sexe='F').count(),
            'autre': Patient.objects.filter(sexe='A').count(),
        }
    
    @staticmethod
    def generer_rapport_annuel(annee, user):
        """Génère un rapport annuel complet"""
        from django.utils import timezone as django_timezone
        
        debut_annee = django_timezone.make_aware(datetime(annee, 1, 1))
        fin_annee = django_timezone.make_aware(datetime(annee, 12, 31, 23, 59, 59))
        
        # Patients créés cette année
        patients_annee = Patient.objects.filter(
            date_creation__range=[debut_annee, fin_annee]
        ).count()
        
        # Consultations de l'année
        consultations_annee = DossierMedical.objects.filter(
            date_consultation__range=[debut_annee, fin_annee]
        ).count()
        
        # Créer le rapport
        rapport, created = RapportAnnuel.objects.update_or_create(
            annee=annee,
            defaults={
                'total_patients': patients_annee,
                'total_consultations': consultations_annee,
                'pathologies_principales': StatisticsService.pathologies_frequentes(),
                'statistiques_age': StatisticsService.analyser_par_tranche_age(),
                'statistiques_sexe': StatisticsService.statistiques_par_sexe(),
                'created_by': user,
            }
        )
        
        return rapport
    
    @staticmethod
    def sauvegarder_analyse(type_analyse, titre, resultats, user, parametres=None):
        """Sauvegarde une analyse dans la base"""
        analyse = AnalyseStatistique.objects.create(
            type_analyse=type_analyse,
            titre=titre,
            resultats=resultats,
            parametres=parametres or {},
            created_by=user,
        )
        return analyse