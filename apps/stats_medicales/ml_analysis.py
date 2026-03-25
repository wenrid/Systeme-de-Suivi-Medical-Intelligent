import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from collections import Counter
from django.db.models import Count, Q
from apps.patients.models import Patient
from apps.dossiers.models import DossierMedical

class MedicalAIAnalysis:
    """Système d'analyse IA pour les statistiques médicales"""
    
    @staticmethod
    def calculer_score_risque(patient):
        """
        Calcule un score de risque pour un patient (0-100)
        Plus le score est élevé, plus le risque est important
        """
        score = 0
        facteurs = []
        
        # Âge (max 25 points)
        age = patient.age
        if age > 65:
            score += 25
            facteurs.append("Âge > 65 ans")
        elif age > 50:
            score += 15
            facteurs.append("Âge > 50 ans")
        elif age > 35:
            score += 5
        
        # Maladies chroniques (max 50 points)
        maladies_count = 0
        if patient.diabete:
            score += 15
            maladies_count += 1
            facteurs.append("Diabète")
        if patient.hypertension:
            score += 15
            maladies_count += 1
            facteurs.append("Hypertension")
        if patient.vih:
            score += 10
            maladies_count += 1
            facteurs.append("VIH")
        if patient.drepanocytose:
            score += 10
            maladies_count += 1
            facteurs.append("Drépanocytose")
        if patient.asthme:
            score += 5
            maladies_count += 1
            facteurs.append("Asthme")
        if patient.epilepsie:
            score += 5
            maladies_count += 1
            facteurs.append("Épilepsie")
        
        # Bonus si plusieurs maladies
        if maladies_count >= 3:
            score += 10
            facteurs.append("Multiples pathologies")
        
        # Consultations récentes d'urgence (max 15 points)
        dossiers_urgents = DossierMedical.objects.filter(
            patient=patient,
            urgence__in=['elevee', 'critique']
        ).count()
        
        if dossiers_urgents > 0:
            score += min(dossiers_urgents * 5, 15)
            facteurs.append(f"{dossiers_urgents} consultation(s) urgente(s)")
        
        # Antécédents (max 10 points)
        if patient.antecedents_chirurgicaux:
            score += 5
            facteurs.append("Antécédents chirurgicaux")
        if patient.allergies:
            score += 5
            facteurs.append("Allergies")
        
        # Limiter le score à 100
        score = min(score, 100)
        
        return {
            'score': score,
            'niveau': MedicalAIAnalysis._get_niveau_risque(score),
            'facteurs': facteurs
        }
    
    @staticmethod
    def _get_niveau_risque(score):
        """Détermine le niveau de risque selon le score"""
        if score >= 70:
            return 'Critique'
        elif score >= 50:
            return 'Élevé'
        elif score >= 30:
            return 'Modéré'
        else:
            return 'Faible'
    
    @staticmethod
    def analyser_par_tranche_age():
        """
        Analyse les maladies les plus fréquentes par tranche d'âge
        Retourne des statistiques et prédictions
        """
        tranches = {
            '0-18': {'patients': [], 'ages': (0, 18)},
            '19-35': {'patients': [], 'ages': (19, 35)},
            '36-50': {'patients': [], 'ages': (36, 50)},
            '51-65': {'patients': [], 'ages': (51, 65)},
            '66+': {'patients': [], 'ages': (66, 150)},
        }
        
        # Classifier les patients
        for patient in Patient.objects.all():
            age = patient.age
            for tranche, data in tranches.items():
                min_age, max_age = data['ages']
                if min_age <= age <= max_age:
                    tranches[tranche]['patients'].append(patient)
                    break
        
        # Analyser chaque tranche
        resultats = {}
        for tranche, data in tranches.items():
            patients = data['patients']
            total = len(patients)
            
            if total == 0:
                resultats[tranche] = {
                    'total': 0,
                    'maladies': {},
                    'risque_moyen': 0,
                    'predictions': []
                }
                continue
            
            # Compter les maladies
            maladies = {
                'Diabète': sum(1 for p in patients if p.diabete),
                'Hypertension': sum(1 for p in patients if p.hypertension),
                'Asthme': sum(1 for p in patients if p.asthme),
                'Épilepsie': sum(1 for p in patients if p.epilepsie),
                'Drépanocytose': sum(1 for p in patients if p.drepanocytose),
                'VIH': sum(1 for p in patients if p.vih),
            }
            
            # Calculer les pourcentages
            maladies_pct = {
                maladie: {
                    'count': count,
                    'pourcentage': round((count / total) * 100, 1)
                }
                for maladie, count in maladies.items()
            }
            
            # Calculer le score de risque moyen
            scores = [MedicalAIAnalysis.calculer_score_risque(p)['score'] for p in patients]
            risque_moyen = round(np.mean(scores), 1) if scores else 0
            
            # Générer des prédictions
            predictions = MedicalAIAnalysis._generer_predictions_tranche(tranche, maladies_pct, total)
            
            resultats[tranche] = {
                'total': total,
                'maladies': maladies_pct,
                'risque_moyen': risque_moyen,
                'predictions': predictions
            }
        
        return resultats
    
    @staticmethod
    def _generer_predictions_tranche(tranche, maladies_pct, total):
        """Génère des prédictions pour une tranche d'âge"""
        predictions = []
        
        for maladie, data in maladies_pct.items():
            pct = data['pourcentage']
            if pct > 30:
                predictions.append(f"⚠️ {maladie} très fréquent ({pct}%) - Zone à risque élevé")
            elif pct > 15:
                predictions.append(f"⚡ {maladie} fréquent ({pct}%) - Surveillance recommandée")
        
        # Prédiction globale
        if tranche == '66+' and total > 0:
            predictions.append("🔮 Risque accru de maladies chroniques pour cette tranche")
        elif tranche == '36-50' and total > 0:
            predictions.append("🔮 Tranche à surveiller pour prévention des maladies chroniques")
        
        return predictions
    
    @staticmethod
    def analyser_par_zone_geographique():
        """
        Analyse les maladies par ville/zone géographique
        Identifie les hotspots et zones à risque
        """
        villes = Patient.objects.exclude(ville='').values_list('ville', flat=True).distinct()
        
        resultats = {}
        for ville in villes:
            patients = Patient.objects.filter(ville=ville)
            total = patients.count()
            
            if total == 0:
                continue
            
            # Compter les maladies
            maladies = {
                'Diabète': patients.filter(diabete=True).count(),
                'Hypertension': patients.filter(hypertension=True).count(),
                'Asthme': patients.filter(asthme=True).count(),
                'Épilepsie': patients.filter(epilepsie=True).count(),
                'Drépanocytose': patients.filter(drepanocytose=True).count(),
                'VIH': patients.filter(vih=True).count(),
            }
            
            # Calculer les pourcentages
            maladies_pct = {
                maladie: {
                    'count': count,
                    'pourcentage': round((count / total) * 100, 1)
                }
                for maladie, count in maladies.items()
            }
            
            # Identifier la maladie dominante
            maladie_dominante = max(maladies.items(), key=lambda x: x[1])
            
            # Calculer le niveau de risque de la zone
            total_maladies = sum(maladies.values())
            taux_maladie = (total_maladies / total) * 100 if total > 0 else 0
            
            if taux_maladie > 50:
                niveau_zone = "🔴 Zone à risque élevé"
            elif taux_maladie > 30:
                niveau_zone = "🟠 Zone à surveiller"
            else:
                niveau_zone = "🟢 Zone normale"
            
            # Prédictions
            predictions = []
            if maladie_dominante[1] > 0:
                pct_dominante = (maladie_dominante[1] / total) * 100
                if pct_dominante > 25:
                    predictions.append(f"⚠️ Hotspot {maladie_dominante[0]} : {pct_dominante:.1f}%")
                    predictions.append(f"🔮 Campagne de prévention recommandée pour {maladie_dominante[0]}")
            
            resultats[ville] = {
                'total_patients': total,
                'maladies': maladies_pct,
                'maladie_dominante': maladie_dominante[0],
                'niveau_zone': niveau_zone,
                'taux_maladie_global': round(taux_maladie, 1),
                'predictions': predictions
            }
        
        return resultats
    
    @staticmethod
    def identifier_patients_a_risque(limite=10):
        """
        Identifie les patients avec les scores de risque les plus élevés
        """
        patients = Patient.objects.all()
        patients_risque = []
        
        for patient in patients:
            analyse = MedicalAIAnalysis.calculer_score_risque(patient)
            if analyse['score'] >= 30:  # Seuil de risque modéré
                patients_risque.append({
                    'patient': patient,
                    'score': analyse['score'],
                    'niveau': analyse['niveau'],
                    'facteurs': analyse['facteurs']
                })
        
        # Trier par score décroissant
        patients_risque.sort(key=lambda x: x['score'], reverse=True)
        
        return patients_risque[:limite]
    
    @staticmethod
    def generer_recommandations(patient):
        """
        Génère des recommandations personnalisées basées sur le profil du patient
        """
        recommandations = []
        analyse = MedicalAIAnalysis.calculer_score_risque(patient)
        
        # Recommandations selon le score
        if analyse['score'] >= 70:
            recommandations.append("🚨 Suivi médical urgent recommandé")
            recommandations.append("📅 Consultation mensuelle conseillée")
        elif analyse['score'] >= 50:
            recommandations.append("⚠️ Suivi médical régulier nécessaire")
            recommandations.append("📅 Consultation trimestrielle conseillée")
        elif analyse['score'] >= 30:
            recommandations.append("⚡ Surveillance préventive recommandée")
            recommandations.append("📅 Consultation semestrielle conseillée")
        
        # Recommandations spécifiques par maladie
        if patient.diabete:
            recommandations.append("🍎 Suivi glycémique régulier recommandé")
            recommandations.append("💊 Vérifier l'observance du traitement antidiabétique")
        
        if patient.hypertension:
            recommandations.append("💓 Surveillance de la tension artérielle")
            recommandations.append("🧂 Régime pauvre en sel conseillé")
        
        if patient.asthme:
            recommandations.append("🌬️ Éviter les allergènes et irritants")
        
        if patient.age > 65:
            recommandations.append("👴 Bilan gériatrique annuel recommandé")
        
        # Recommandations générales
        if len(analyse['facteurs']) >= 3:
            recommandations.append("🏥 Consultation pluridisciplinaire conseillée")
        
        return recommandations