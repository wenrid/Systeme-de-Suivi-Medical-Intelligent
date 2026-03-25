"""
Script pour créer un hotspot épidémique artificiel
Génère beaucoup de cas d'une même maladie dans une seule ville
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_system.settings')
django.setup()

from apps.patients.models import Patient
from apps.dossiers.models import DossierMedical
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

# ========== CONFIGURATION DU HOTSPOT ==========
VILLE_HOTSPOT = "Kinshasa"  # Ville où créer le hotspot
MALADIE_HOTSPOT = "Paludisme"  # Maladie concentrée
NB_CAS_HOTSPOT = 15  # Nombre de cas à créer
NB_JOURS = 7  # Sur les 7 derniers jours

print("=" * 60)
print("CREATION D'UN HOTSPOT EPIDEMIQUE")
print("=" * 60)

# Récupérer les patients de la ville ciblée
patients_ville = list(Patient.objects.filter(ville=VILLE_HOTSPOT))
medecins = list(User.objects.filter(role='medecin'))

if not medecins:
    print("\nERREUR : Aucun médecin trouvé!")
    exit(1)

if len(patients_ville) < 5:
    print(f"\nATTENTION : Seulement {len(patients_ville)} patients à {VILLE_HOTSPOT}")
    print(f"Il faut au moins 5 patients dans cette ville pour créer un hotspot réaliste")
    print("\nVilles disponibles avec nombre de patients :")
    
    villes = Patient.objects.values('ville').distinct()
    for ville in villes:
        nb = Patient.objects.filter(ville=ville['ville']).count()
        print(f"   - {ville['ville']} : {nb} patients")
    
    print(f"\nOptions :")
    print(f"1. Crée plus de patients à {VILLE_HOTSPOT}")
    print(f"2. Change VILLE_HOTSPOT dans le script vers une ville avec plus de patients")
    exit(1)

print(f"\nVille cible : {VILLE_HOTSPOT}")
print(f"Maladie : {MALADIE_HOTSPOT}")
print(f"Patients disponibles : {len(patients_ville)}")
print(f"Nombre de cas à créer : {NB_CAS_HOTSPOT}")
print(f"Période : {NB_JOURS} derniers jours")

# ========== GÉNÉRATION DU HOTSPOT ==========
print(f"\nCreation du hotspot en cours...")

cas_crees = 0

for i in range(NB_JOURS):
    date_consultation = timezone.now() - timedelta(days=i)
    
    # Concentrer les cas sur les 3 derniers jours (plus réaliste)
    if i < 3:
        nb_cas_jour = NB_CAS_HOTSPOT // 3 + random.randint(-2, 3)
    else:
        nb_cas_jour = random.randint(1, 3)
    
    for j in range(nb_cas_jour):
        if cas_crees >= NB_CAS_HOTSPOT:
            break
            
        patient = random.choice(patients_ville)
        medecin = random.choice(medecins)
        
        DossierMedical.objects.create(
            patient=patient,
            medecin=medecin,
            date_consultation=date_consultation,
            motif_consultation=f"Symptomes de {MALADIE_HOTSPOT} - HOTSPOT",
            symptomes=f"Fievre, frissons, maux de tete - Suspicion {MALADIE_HOTSPOT}",
            diagnostic=MALADIE_HOTSPOT,
            prescription=f"Traitement antipaludique",
            posologie="Selon protocole",
            notes_medicales=f"Cas dans le cadre du hotspot à {VILLE_HOTSPOT}",
            urgence='elevee' if random.random() < 0.3 else 'moyenne',
            statut='ouvert'
        )
        
        cas_crees += 1
    
    if cas_crees >= NB_CAS_HOTSPOT:
        break

print(f"\n{cas_crees} cas de {MALADIE_HOTSPOT} crees à {VILLE_HOTSPOT}")

# ========== STATISTIQUES ==========
print("\n" + "=" * 60)
print("HOTSPOT CREE AVEC SUCCES !")
print("=" * 60)

# Calculer la prévalence dans cette ville
total_patients_ville = len(patients_ville)
prevalence = (cas_crees / total_patients_ville) * 100

print(f"\nSTATISTIQUES DU HOTSPOT :")
print(f"   Ville : {VILLE_HOTSPOT}")
print(f"   Maladie : {MALADIE_HOTSPOT}")
print(f"   Cas crees : {cas_crees}")
print(f"   Total patients ville : {total_patients_ville}")
print(f"   Taux prevalence : {prevalence:.1f}%")

# Comparer avec d'autres villes
print(f"\nCOMPARAISON AVEC AUTRES VILLES :")
villes = Patient.objects.values_list('ville', flat=True).distinct()

for ville in villes:
    if ville:
        nb_patients_ville = Patient.objects.filter(ville=ville).count()
        nb_cas_maladie = DossierMedical.objects.filter(
            patient__ville=ville,
            diagnostic=MALADIE_HOTSPOT,
            date_consultation__gte=timezone.now() - timedelta(days=NB_JOURS)
        ).count()
        
        if nb_patients_ville > 0:
            prev = (nb_cas_maladie / nb_patients_ville) * 100
            statut = "🔴 HOTSPOT" if prev > 30 else "🟡 Élevé" if prev > 15 else "🟢 Normal"
            print(f"   {ville:<20} : {nb_cas_maladie:>3} cas / {nb_patients_ville:>3} patients ({prev:>5.1f}%) {statut}")

print("\n" + "=" * 60)
print("PROCHAINES ETAPES :")
print("=" * 60)
print("\n1. Va sur le dashboard")
print("2. Clique sur : Analyses IA")
print("3. Clique sur : Analyse Geographique")
print("4. Tu verras maintenant :")
print(f"   🔴 HOTSPOT detecte à {VILLE_HOTSPOT}")
print(f"   🦠 {MALADIE_HOTSPOT} - {prevalence:.1f}% de prevalence")
print("   💊 Recommandations d'actions")
print("\n" + "=" * 60)