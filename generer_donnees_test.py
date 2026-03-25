"""
Script de génération de données de test pour le SSMI
Crée des consultations antidatées pour tester les modules IA
"""

import os
import django
from datetime import datetime, timedelta
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_system.settings')
django.setup()

from patients.models import Patient
from dossiers.models import DossierMedical, Consultation
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# ========== CONFIGURATION ==========
NB_JOURS_HISTORIQUE = 30  # Nombre de jours dans le passé (7, 30, ou 90)
MIN_CONSULTATIONS_PAR_JOUR = 2  # Minimum de consultations par jour
MAX_CONSULTATIONS_PAR_JOUR = 8  # Maximum de consultations par jour

# Liste des maladies à utiliser
MALADIES = [
    'Grippe',
    'Paludisme', 
    'Hypertension',
    'Diabète',
    'Asthme',
    'Bronchite',
    'Gastro-entérite',
    'Angine'
]

# Pondération des maladies (pour créer des tendances réalistes)
POIDS_MALADIES = {
    'Grippe': 30,        # Plus fréquente
    'Paludisme': 25,
    'Hypertension': 20,
    'Diabète': 10,
    'Asthme': 5,
    'Bronchite': 5,
    'Gastro-entérite': 3,
    'Angine': 2
}

# ========== VÉRIFICATIONS PRÉALABLES ==========
print("=" * 60)
print("🏥 GÉNÉRATION DE DONNÉES TEST POUR LE SSMI")
print("=" * 60)

patients = list(Patient.objects.all())
medecins = list(User.objects.filter(role='medecin'))

if not medecins:
    print("\n❌ ERREUR : Aucun médecin trouvé dans la base !")
    print("   → Crée au moins un utilisateur avec le rôle 'medecin'")
    exit(1)

if len(patients) < 3:
    print(f"\n❌ ERREUR : Seulement {len(patients)} patient(s) trouvé(s)")
    print("   → Crée au moins 3 patients avant de lancer ce script")
    exit(1)

print(f"\n✅ {len(patients)} patients trouvés")
print(f"✅ {len(medecins)} médecin(s) trouvé(s)")
print(f"\n📅 Génération sur {NB_JOURS_HISTORIQUE} jours...")
print(f"📊 {MIN_CONSULTATIONS_PAR_JOUR}-{MAX_CONSULTATIONS_PAR_JOUR} consultations/jour")

# ========== FONCTION DE SÉLECTION PONDÉRÉE ==========
def choisir_maladie():
    """Choisit une maladie selon les poids définis"""
    maladies_liste = []
    for maladie, poids in POIDS_MALADIES.items():
        maladies_liste.extend([maladie] * poids)
    return random.choice(maladies_liste)

# ========== GÉNÉRATION DES CONSULTATIONS ==========
consultations_creees = 0
consultations_par_maladie = {maladie: 0 for maladie in MALADIES}
consultations_par_jour = []

print("\n🔄 Génération en cours...")

for i in range(NB_JOURS_HISTORIQUE):
    # Date dans le passé (i jours en arrière)
    date_consultation = timezone.now() - timedelta(days=i)
    
    # Créer un pattern réaliste avec plus de cas certains jours
    # Simule des pics (20% de chance d'avoir beaucoup de consultations)
    if random.random() < 0.2:  # 20% de chance de pic
        nb_consultations = random.randint(
            MAX_CONSULTATIONS_PAR_JOUR - 2, 
            MAX_CONSULTATIONS_PAR_JOUR
        )
    else:
        nb_consultations = random.randint(
            MIN_CONSULTATIONS_PAR_JOUR, 
            MAX_CONSULTATIONS_PAR_JOUR - 2
        )
    
    consultations_jour = 0
    
    for j in range(nb_consultations):
        # Choisir un patient et un médecin aléatoirement
        patient = random.choice(patients)
        medecin = random.choice(medecins)
        
        # Récupérer ou créer le dossier médical
        dossier, _ = DossierMedical.objects.get_or_create(patient=patient)
        
        # Choisir une maladie avec pondération
        maladie = choisir_maladie()
        
        # Créer la consultation avec date antidatée
        consultation = Consultation.objects.create(
            dossier=dossier,
            medecin=medecin,
            date_consultation=date_consultation,
            motif=f"Symptômes de {maladie}",
            diagnostic=maladie,
            traitement=f"Traitement prescrit pour {maladie}",
            notes=f"Consultation de test générée automatiquement (Jour -{i})"
        )
        
        consultations_creees += 1
        consultations_par_maladie[maladie] += 1
        consultations_jour += 1
    
    consultations_par_jour.append(consultations_jour)
    
    # Afficher progression tous les 5 jours
    if (i + 1) % 5 == 0:
        print(f"   ✓ {i + 1}/{NB_JOURS_HISTORIQUE} jours traités ({consultations_creees} consultations)")

# ========== STATISTIQUES FINALES ==========
print("\n" + "=" * 60)
print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS !")
print("=" * 60)

print(f"\n📊 STATISTIQUES GLOBALES :")
print(f"   • Total consultations : {consultations_creees}")
print(f"   • Période : {NB_JOURS_HISTORIQUE} jours")
print(f"   • Moyenne : {consultations_creees/NB_JOURS_HISTORIQUE:.1f} consultations/jour")
print(f"   • Minimum : {min(consultations_par_jour)} consultations/jour")
print(f"   • Maximum : {max(consultations_par_jour)} consultations/jour")

print(f"\n🦠 RÉPARTITION PAR MALADIE :")
for maladie in sorted(consultations_par_maladie.keys(), 
                      key=lambda x: consultations_par_maladie[x], 
                      reverse=True):
    nb = consultations_par_maladie[maladie]
    if nb > 0:
        pourcentage = (nb / consultations_creees) * 100
        print(f"   • {maladie:<20} : {nb:>3} cas ({pourcentage:>5.1f}%)")

print(f"\n👥 RÉPARTITION PAR PATIENT :")
consultations_par_patient = {}
for consultation in Consultation.objects.filter(
    date_consultation__gte=timezone.now() - timedelta(days=NB_JOURS_HISTORIQUE)
):
    patient_nom = f"{consultation.dossier.patient.nom} {consultation.dossier.patient.prenom}"
    consultations_par_patient[patient_nom] = consultations_par_patient.get(patient_nom, 0) + 1

for patient_nom, nb in sorted(consultations_par_patient.items(), 
                               key=lambda x: x[1], 
                               reverse=True)[:5]:  # Top 5
    print(f"   • {patient_nom:<30} : {nb} consultations")

print("\n" + "=" * 60)
print("🚀 PROCHAINES ÉTAPES :")
print("=" * 60)
print("\n1. Redémarre ton serveur Django si nécessaire :")
print("   python manage.py runserver")
print("\n2. Connecte-toi à ton compte (Admin ou Médecin)")
print("\n3. Va dans le menu : 🤖 Analyses IA")
print("\n4. Clique sur : 🦠 Prédiction d'Épidémies")
print("\n5. Tu devrais maintenant voir :")
print("   ✓ Graphiques avec données historiques")
print("   ✓ Prédictions sur 30 jours")
print("   ✓ Détection de pics anormaux")
print("   ✓ Évaluation du risque épidémique")
print("\n" + "=" * 60)
print("💡 TIP : Si tu ne vois pas assez de données :")
print("   → Augmente NB_JOURS_HISTORIQUE à 60 ou 90")
print("   → Relance ce script")
print("=" * 60)