import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from apps.patients.models import Patient
from apps.dossiers.models import DossierMedical

class EpidemicPredictor:
    """Système de prédiction d'épidémies et détection de pics"""
    
    @staticmethod
    def analyser_tendances_maladies(jours_historique=180, jours_prediction=30):
        """
        Analyse les tendances des maladies sur les X derniers jours
        et prédit les Y prochains jours
        """
        date_debut = datetime.now() - timedelta(days=jours_historique)
        
        # Récupérer les consultations par jour
        consultations = DossierMedical.objects.filter(
            date_consultation__gte=date_debut
        ).annotate(
            date_seule=TruncDate('date_consultation')
        ).values('date_seule').annotate(
            total=Count('id')
        ).order_by('date_seule')
        
        # Préparer les données
        dates = []
        totaux = []
        
        for item in consultations:
            dates.append(item['date_seule'])
            totaux.append(item['total'])
        
        if len(dates) < 10:
            return {
                'statut': 'insuffisant',
                'message': 'Données insuffisantes pour la prédiction (minimum 10 jours requis)',
                'historique': [],
                'predictions': []
            }
        
        # Calculer la moyenne mobile
        moyenne_mobile = EpidemicPredictor._calculer_moyenne_mobile(totaux, fenetre=7)
        
        # Détecter les pics
        pics = EpidemicPredictor._detecter_pics(totaux, dates)
        
        # Prédiction Lstm (moyenne mobile + tendance)
        predictions = EpidemicPredictor._predire_lstm(totaux, jours_prediction)
        
        # Évaluer le niveau de risque
        risque = EpidemicPredictor._evaluer_risque_epidemique(totaux, predictions)
        
        return {
            'statut': 'success',
            'historique': {
                'dates': [d.strftime('%Y-%m-%d') for d in dates],
                'valeurs': totaux,
                'moyenne_mobile': moyenne_mobile
            },
            'pics_detectes': pics,
            'predictions': predictions,
            'risque_epidemique': risque,
            'jours_historique': jours_historique,
            'jours_prediction': jours_prediction
        }
    
    @staticmethod
    def analyser_maladies_chroniques_tendances():
        """
        Analyse les tendances d'évolution des maladies chroniques
        """
        # Compter les patients par maladie
        maladies = {
            'Diabète': Patient.objects.filter(diabete=True).count(),
            'Hypertension': Patient.objects.filter(hypertension=True).count(),
            'Asthme': Patient.objects.filter(asthme=True).count(),
            'Épilepsie': Patient.objects.filter(epilepsie=True).count(),
            'Drépanocytose': Patient.objects.filter(drepanocytose=True).count(),
            'VIH': Patient.objects.filter(vih=True).count(),
        }
        
        total_patients = Patient.objects.count()
        
        # Calculer les taux de prévalence
        prevalence = {}
        alertes = []
        
        for maladie, count in maladies.items():
            taux = (count / total_patients * 100) if total_patients > 0 else 0
            prevalence[maladie] = {
                'cas': count,
                'taux': round(taux, 2),
                'statut': EpidemicPredictor._evaluer_prevalence(taux)
            }
            
            # Générer des alertes
            if taux > 20:
                alertes.append({
                    'maladie': maladie,
                    'type': 'critique',
                    'message': f"🔴 Prévalence critique de {maladie} : {taux:.1f}% des patients"
                })
            elif taux > 10:
                alertes.append({
                    'maladie': maladie,
                    'type': 'attention',
                    'message': f"🟠 Prévalence élevée de {maladie} : {taux:.1f}% des patients"
                })
        
        return {
            'prevalence': prevalence,
            'alertes': alertes,
            'total_patients': total_patients
        }
    
    @staticmethod
    def detecter_epidemies_locales():
        """
        Détecte les épidémies locales par zone géographique
        Analyse les diagnostics des consultations récentes
        """
        from django.utils import timezone
        
        # Analyser les 30 derniers jours
        date_limite = timezone.now() - timedelta(days=30)
        
        # Utiliser un set pour garantir l'unicité et nettoyer les espaces
        villes_raw = Patient.objects.exclude(ville='').values_list('ville', flat=True)
        villes = set([v.strip() for v in villes_raw if v])
        
        epidemies_locales = []
        stats_globales = {}
        
        # Calculer les taux pour chaque ville
        for ville in villes:
            patients_ville = Patient.objects.filter(ville=ville)
            total_patients = patients_ville.count()
            
            if total_patients < 3:
                continue
            
            # Analyser les diagnostics des consultations récentes
            consultations = DossierMedical.objects.filter(
                patient__ville=ville,
                date_consultation__gte=date_limite
            )
            
            # Compter par diagnostic
            diagnostics = consultations.values('diagnostic').annotate(
                count=Count('id')
            )
            
            for diag in diagnostics:
                maladie = diag['diagnostic']
                nb_cas = diag['count']
                
                if not maladie:
                    continue
                
                # Calculer le taux de prévalence
                taux = (nb_cas / total_patients) * 100
                
                # Déterminer le niveau selon des seuils réalistes
                if taux > 80:
                    niveau = 'critique'
                    recommandation = EpidemicPredictor._generer_recommandation_intelligente(maladie, ville, taux, 'critique')
                elif taux > 50:
                    niveau = 'élevé'
                    recommandation = EpidemicPredictor._generer_recommandation_intelligente(maladie, ville, taux, 'élevé')
                elif taux > 30:
                    niveau = 'modéré'
                    recommandation = EpidemicPredictor._generer_recommandation_intelligente(maladie, ville, taux, 'modéré')
                else:
                    # Taux < 30% : pas d'alerte
                    continue
                
                # Ajouter seulement si taux > 30%
                epidemies_locales.append({
                    'ville': ville,
                    'maladie': maladie,
                    'cas': nb_cas,
                    'total_patients': total_patients,
                    'taux': round(taux, 1),
                    'niveau': niveau,
                    'recommandation': recommandation
                })
                
                # Stocker pour calcul global
                if maladie not in stats_globales:
                    stats_globales[maladie] = {'total_cas': 0, 'total_patients': 0}
                stats_globales[maladie]['total_cas'] += nb_cas
                stats_globales[maladie]['total_patients'] += total_patients
        
        # Trier par taux décroissant
        epidemies_locales.sort(key=lambda x: x['taux'], reverse=True)
        
        return epidemies_locales
    
    @staticmethod
    def _calculer_moyenne_mobile(valeurs, fenetre=7):
        """Calcule la moyenne mobile"""
        if len(valeurs) < fenetre:
            return valeurs
        
        moyennes = []
        for i in range(len(valeurs)):
            if i < fenetre - 1:
                moyennes.append(valeurs[i])
            else:
                moyenne = sum(valeurs[i-fenetre+1:i+1]) / fenetre
                moyennes.append(round(moyenne, 2))
        
        return moyennes
    
    @staticmethod
    def _detecter_pics(valeurs, dates):
        """Détecte les pics anormaux dans les données"""
        if len(valeurs) < 10:
            return []
        
        moyenne = np.mean(valeurs)
        ecart_type = np.std(valeurs)
        seuil = moyenne + (2 * ecart_type)
        
        pics = []
        for i, val in enumerate(valeurs):
            if val > seuil:
                pics.append({
                    'date': dates[i].strftime('%Y-%m-%d'),
                    'valeur': val,
                    'moyenne': round(moyenne, 1),
                    'ecart': round(val - moyenne, 1)
                })
        
        return pics
    
    @staticmethod
    def _predire_lstm(valeurs, jours):
        """
        Prédiction basée sur le modèle LSTM entraîné
        Remplace la régression linéaire
        """
        import torch
        import torch.nn as nn
        import pickle
        import os

        # ── Définition du modèle LSTM ─────────────────────────
        class LSTMModel(nn.Module):
            def __init__(self, input_size=1, hidden_size=32, num_layers=2):
                super(LSTMModel, self).__init__()
                self.lstm = nn.LSTM(input_size, hidden_size,
                                num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, 1)

            def forward(self, x):
                out, _ = self.lstm(x)
                out = self.fc(out[:, -1, :])
                return out

        # ── Chemins des modèles sauvegardés ──────────────────
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        ))
        model_path = os.path.join(base_dir, 'models', 'lstm_paludisme.pth')
        scaler_path = os.path.join(base_dir, 'models', 'scaler_lstm.pkl')

        # ── Fallback régression linéaire si modèle absent ────
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            x = np.arange(len(valeurs))
            y = np.array(valeurs, dtype=float)
            tendance = np.polyfit(x, y, 1)[0]
            derniere_valeur = valeurs[-1]
            predictions = []
            for i in range(1, jours + 1):
                prediction = derniere_valeur + (tendance * i)
                prediction = max(0, round(prediction, 1))
                predictions.append(prediction)
            return predictions

        # ── Charger le modèle et le scaler ───────────────────
        model = LSTMModel()
        model.load_state_dict(torch.load(
            model_path, map_location=torch.device('cpu')
        ))
        model.eval()

        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)

        # ── Préparer les données ──────────────────────────────
        taille_fenetre = 7
        valeurs_array = np.array(
            valeurs[-taille_fenetre:], dtype=float
        ).reshape(-1, 1)
        valeurs_norm = scaler.transform(valeurs_array)
        input_tensor = torch.FloatTensor(
            valeurs_norm.reshape(1, taille_fenetre, 1)
        )

        # ── Prédire jour par jour ─────────────────────────────
        predictions = []
        input_actuel = input_tensor.clone()

        with torch.no_grad():
            for _ in range(jours):
                prediction = model(input_actuel)
                predictions.append(prediction.item())
                nouveau_jour = prediction.unsqueeze(0)
                input_actuel = torch.cat(
                    [input_actuel[:, 1:, :], nouveau_jour], dim=1
                )

        # ── Dénormaliser ──────────────────────────────────────
        predictions_array = np.array(predictions).reshape(-1, 1)
        predictions_reelles = scaler.inverse_transform(predictions_array)
        predictions_reelles = np.clip(predictions_reelles, 0, None)

        return [round(float(p), 1) for p in predictions_reelles.flatten()]
    
    @staticmethod
    def _evaluer_risque_epidemique(historique, predictions):
        """Évalue le niveau de risque épidémique"""
        moyenne_historique = np.mean(historique) if historique else 0
        moyenne_predictions = np.mean(predictions) if predictions else 0
        
        augmentation = ((moyenne_predictions - moyenne_historique) / moyenne_historique * 100) if moyenne_historique > 0 else 0
        
        if augmentation > 50:
            return {
                'niveau': 'critique',
                'pourcentage': round(augmentation, 1),
                'message': '🔴 Risque épidémique CRITIQUE - Augmentation prévue de plus de 50%',
                'actions': [
                    'Activer le protocole d\'urgence',
                    'Augmenter les ressources médicales',
                    'Lancer une campagne de prévention immédiate'
                ]
            }
        elif augmentation > 25:
            return {
                'niveau': 'élevé',
                'pourcentage': round(augmentation, 1),
                'message': '🟠 Risque épidémique ÉLEVÉ - Augmentation significative prévue',
                'actions': [
                    'Renforcer la surveillance',
                    'Préparer les ressources supplémentaires',
                    'Informer les équipes médicales'
                ]
            }
        elif augmentation > 10:
            return {
                'niveau': 'modéré',
                'pourcentage': round(augmentation, 1),
                'message': '🟡 Risque épidémique MODÉRÉ - Légère augmentation prévue',
                'actions': [
                    'Maintenir la surveillance',
                    'Suivre l\'évolution quotidiennement'
                ]
            }
        else:
            return {
                'niveau': 'faible',
                'pourcentage': round(augmentation, 1),
                'message': '🟢 Risque épidémique FAIBLE - Situation stable',
                'actions': [
                    'Continuer la surveillance de routine'
                ]
            }
    
    @staticmethod
    def _evaluer_prevalence(taux):
        """Évalue le niveau de prévalence d'une maladie"""
        if taux > 20:
            return 'critique'
        elif taux > 10:
            return 'élevé'
        elif taux > 5:
            return 'modéré'
        else:
            return 'normal'
    
    @staticmethod
    def _generer_recommandation_intelligente(maladie, ville, taux, niveau):
        """
        Génère des recommandations intelligentes selon la maladie et le niveau
        """
        # Recommandations spécifiques par maladie
        recommandations_par_maladie = {
            'Paludisme': {
                'critique': f"🚨 URGENCE à {ville} : Distribution massive de moustiquaires imprégnées + Pulvérisation insecticide immédiate + Traitement préventif de masse",
                'élevé': f"⚠️ {ville} : Campagne de distribution de moustiquaires + Sensibilisation sur l'élimination des eaux stagnantes + Dépistage actif",
                'modéré': f"📋 {ville} : Surveillance renforcée + Distribution ciblée de moustiquaires + Information sur les symptômes"
            },
            'Grippe': {
                'critique': f"🚨 URGENCE à {ville} : Campagne de vaccination d'urgence + Isolement des cas + Renforcement personnel médical",
                'élevé': f"⚠️ {ville} : Accélérer la vaccination + Mesures de distanciation + Stocks antiviraux",
                'modéré': f"📋 {ville} : Campagne de vaccination préventive + Hygiène des mains + Surveillance"
            },
            'Diabète': {
                'critique': f"🚨 URGENCE à {ville} : Programme de dépistage massif + Cliniques mobiles + Formation personnel + Distribution glucomètres",
                'élevé': f"⚠️ {ville} : Dépistage ciblé + Éducation nutritionnelle + Suivi médical renforcé",
                'modéré': f"📋 {ville} : Campagne de sensibilisation diabète + Dépistage volontaire + Ateliers nutrition"
            },
            'Diabete': {
                'critique': f"🚨 URGENCE à {ville} : Programme de dépistage massif + Cliniques mobiles + Formation personnel + Distribution glucomètres",
                'élevé': f"⚠️ {ville} : Dépistage ciblé + Éducation nutritionnelle + Suivi médical renforcé",
                'modéré': f"📋 {ville} : Campagne de sensibilisation diabète + Dépistage volontaire + Ateliers nutrition"
            },
            'Hypertension': {
                'critique': f"🚨 URGENCE à {ville} : Dépistage gratuit de masse + Distribution tensiomètres + Consultation cardiologique gratuite",
                'élevé': f"⚠️ {ville} : Campagne de mesure tension + Ateliers prévention cardiovasculaire + Suivi médical",
                'modéré': f"📋 {ville} : Sensibilisation hygiène de vie + Dépistage volontaire + Exercice physique"
            },
            'Asthme': {
                'critique': f"🚨 URGENCE à {ville} : Distribution inhalateurs + Analyse qualité de l'air + Consultations pneumologie gratuites",
                'élevé': f"⚠️ {ville} : Dépistage respiratoire + Distribution inhalateurs subventionnés + Éducation sur triggers",
                'modéré': f"📋 {ville} : Sensibilisation allergènes + Conseil utilisation inhalateurs + Surveillance pollution"
            },
            'Bronchite': {
                'critique': f"🚨 URGENCE à {ville} : Consultations respiratoires d'urgence + Distribution antibiotiques + Mesures anti-pollution",
                'élevé': f"⚠️ {ville} : Dépistage infections respiratoires + Traitement précoce + Hygiène respiratoire",
                'modéré': f"📋 {ville} : Prévention infections + Vaccination grippe + Éviter tabac et pollution"
            },
            'Gastro-entérite': {
                'critique': f"🚨 URGENCE à {ville} : Contrôle eau potable + Distribution sels de réhydratation + Sensibilisation hygiène alimentaire",
                'élevé': f"⚠️ {ville} : Campagne hygiène mains + Contrôle sanitaire + Traitement rapide déshydratation",
                'modéré': f"📋 {ville} : Éducation hygiène alimentaire + Eau potable + Lavage mains"
            },
            'Angine': {
                'critique': f"🚨 URGENCE à {ville} : Consultations ORL d'urgence + Distribution antibiotiques + Dépistage streptocoque",
                'élevé': f"⚠️ {ville} : Traitement rapide angines + Tests streptocoque + Prévention complications",
                'modéré': f"📋 {ville} : Consultation médicale précoce + Hygiène gorge + Éviter contagion"
            }
        }
        
        # Recommandation par défaut si maladie non listée
        recommandations_default = {
            'critique': f"🚨 URGENCE à {ville} : Intervention sanitaire immédiate pour {maladie} - Dépistage massif + Traitement gratuit + Personnel médical renforcé",
            'élevé': f"⚠️ {ville} : Campagne ciblée contre {maladie} - Dépistage actif + Sensibilisation + Ressources médicales",
            'modéré': f"📋 {ville} : Surveillance de {maladie} - Dépistage volontaire + Information population + Suivi statistique"
        }
        
        # Retourner la recommandation appropriée
        if maladie in recommandations_par_maladie:
            return recommandations_par_maladie[maladie].get(niveau, recommandations_default[niveau])
        else:
            return recommandations_default[niveau]