"""
Script de génération de données réalistes pour le SSMI
- 200 nouveaux patients générés
- 180 jours d'historique (6 mois)
- Saisonnalité réaliste par maladie
- Tendances progressives (épidémies en courbe gaussienne)
- Volume : 800+ consultations
"""

import os
import django
from datetime import datetime, timedelta, date
import random
import math

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_system.settings')
django.setup()

from apps.patients.models import Patient
from apps.dossiers.models import DossierMedical
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# ========== CONFIGURATION ==========
NB_PATIENTS_A_CREER = 200
NB_JOURS_HISTORIQUE = 180

NOMS = [
    'Kabila', 'Mukendi', 'Tshisekedi', 'Mbuyi', 'Kasongo',
    'Lumumba', 'Mobutu', 'Kalala', 'Ilunga', 'Mutombo',
    'Ngalula', 'Kabuya', 'Mwamba', 'Katanga', 'Dibwe',
    'Nkosi', 'Banda', 'Phiri', 'Tembo', 'Zulu',
    'Diallo', 'Traoré', 'Coulibaly', 'Koné', 'Touré',
    'Mbeki', 'Dlamini', 'Khumalo', 'Nkomo', 'Moyo',
]

PRENOMS_M = [
    'Jean', 'Pierre', 'Paul', 'Patrick', 'Emmanuel',
    'David', 'Daniel', 'Joseph', 'Michel', 'André',
    'Robert', 'François', 'Thomas', 'Jacques', 'Henri',
    'Christophe', 'Philippe', 'Nicolas', 'Alain', 'Marc',
]

PRENOMS_F = [
    'Marie', 'Anne', 'Sophie', 'Claire', 'Julie',
    'Fatima', 'Aminata', 'Aïcha', 'Mariama', 'Kadiatou',
    'Grace', 'Hope', 'Faith', 'Mercy', 'Joyce',
    'Celestine', 'Pascaline', 'Alphonsine', 'Clarisse', 'Odette',
]

VILLES = [
    'Kinshasa', 'Lubumbashi', 'Mbuji-Mayi', 'Kisangani',
    'Kananga', 'Likasi', 'Kolwezi', 'Bukavu', 'Goma',
    'Matadi', 'Kikwit', 'Mwene-Ditu', 'Uvira', 'Butembo',
]

GROUPES_SANGUINS = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
POIDS_GROUPES = [34, 6, 9, 2, 38, 7, 3, 1]

MALADIES_CONFIG = {
    'Paludisme': {
        'base': 2,
        'pic_saison': 0.6,
        'amplitude': 6,
        'description': 'Fièvre, frissons, maux de tête',
        'prescription': 'Traitement antipaludique',
        'urgences': ['elevee', 'moyenne', 'moyenne'],
    },
    'Grippe': {
        'base': 2,
        'pic_saison': 0.1,
        'amplitude': 4,
        'description': 'Fièvre, toux, courbatures',
        'prescription': 'Antiviral, repos',
        'urgences': ['faible', 'faible', 'moyenne'],
    },
    'Hypertension': {
        'base': 1,
        'pic_saison': 0.5,
        'amplitude': 2,
        'description': 'Tension artérielle élevée, maux de tête',
        'prescription': 'Antihypertenseur',
        'urgences': ['faible', 'moyenne'],
    },
    'Diabète': {
        'base': 1,
        'pic_saison': 0.3,
        'amplitude': 2,
        'description': 'Glycémie élevée, fatigue',
        'prescription': 'Insuline ou antidiabétique oral',
        'urgences': ['faible', 'moyenne'],
    },
    'Bronchite': {
        'base': 1,
        'pic_saison': 0.1,
        'amplitude': 3,
        'description': 'Toux persistante, expectorations',
        'prescription': 'Bronchodilatateur, antibiotique',
        'urgences': ['faible', 'moyenne'],
    },
    'Asthme': {
        'base': 1,
        'pic_saison': 0.2,
        'amplitude': 2,
        'description': 'Difficultés respiratoires, sifflement',
        'prescription': 'Bronchodilatateur, corticoïde',
        'urgences': ['faible', 'moyenne', 'elevee'],
    },
    'Gastro-entérite': {
        'base': 1,
        'pic_saison': 0.7,
        'amplitude': 3,
        'description': 'Nausées, vomissements, diarrhée',
        'prescription': 'Réhydratation, antiémétique',
        'urgences': ['faible', 'moyenne'],
    },
    'Angine': {
        'base': 1,
        'pic_saison': 0.0,
        'amplitude': 2,
        'description': 'Mal de gorge, fièvre',
        'prescription': 'Antibiotique, antidouleur',
        'urgences': ['faible'],
    },
}

# Épidémie simulée pour le Paludisme
EPIDEMIE_JOUR_DEBUT = 120
EPIDEMIE_DUREE = 30
EPIDEMIE_INTENSITE = 2.5

# ========== VÉRIFICATIONS ==========
print("=" * 60)
print("GÉNÉRATION DE DONNÉES RÉALISTES POUR LE SSMI")
print("=" * 60)

medecins = list(User.objects.filter(role='medecin'))
admin = User.objects.filter(is_superuser=True).first()

if not medecins:
    print("\nERREUR : Aucun médecin trouvé !")
    exit(1)

if not admin:
    print("\nERREUR : Aucun admin trouvé !")
    exit(1)

print(f"\n{len(medecins)} médecin(s) trouvé(s)")
print(f"Admin : {admin.username}")

# ========== FONCTIONS ==========

def groupe_sanguin_aleatoire():
    return random.choices(GROUPES_SANGUINS, weights=POIDS_GROUPES, k=1)[0]

def date_naissance_aleatoire():
    annee = random.randint(1950, 2005)
    mois = random.randint(1, 12)
    jour = random.randint(1, 28)
    return date(annee, mois, jour)

def calculer_saisonnalite(jour_index, pic_saison, amplitude):
    progression = jour_index / NB_JOURS_HISTORIQUE
    facteur = math.sin(math.pi * (progression - pic_saison)) ** 2
    return max(0, facteur * amplitude)

def calculer_vague_epidemique(jour_epidemie, duree, intensite):
    progression = jour_epidemie / duree
    centre = 0.5
    largeur = 0.15
    return intensite * math.exp(
        -((progression - centre) ** 2) / (2 * largeur ** 2)
    )

def nb_consultations_jour(maladie, jour_index):
    config = MALADIES_CONFIG[maladie]
    base = config['base']
    saisonnier = calculer_saisonnalite(
        jour_index,
        config['pic_saison'],
        config['amplitude']
    )
    tendance = 1.0
    if maladie == 'Paludisme':
        if EPIDEMIE_JOUR_DEBUT <= jour_index <= EPIDEMIE_JOUR_DEBUT + EPIDEMIE_DUREE:
            jour_epi = jour_index - EPIDEMIE_JOUR_DEBUT
            tendance = 1.0 + calculer_vague_epidemique(
                jour_epi, EPIDEMIE_DUREE, EPIDEMIE_INTENSITE
            )
    bruit = random.uniform(-0.3, 0.3)
    total = (base + saisonnier) * tendance + bruit
    return max(0, round(total))

# ========== ÉTAPE 1 : GÉNÉRER LES PATIENTS ==========
print(f"\nÉtape 1 : Génération de {NB_PATIENTS_A_CREER} patients...")

patients_crees = 0
for i in range(NB_PATIENTS_A_CREER):
    sexe = random.choice(['M', 'F'])
    prenom = random.choice(PRENOMS_M if sexe == 'M' else PRENOMS_F)
    nom = random.choice(NOMS)
    ville = random.choice(VILLES)
    gs = groupe_sanguin_aleatoire()
    ddn = date_naissance_aleatoire()

    # Maladies chroniques selon l'âge
    age = (date.today() - ddn).days // 365
    diabete = random.random() < (0.15 if age > 40 else 0.03)
    hypertension = random.random() < (0.25 if age > 40 else 0.05)
    asthme = random.random() < 0.08

    code = f"P{timezone.now().strftime('%Y%m')}{str(i + 1000).zfill(4)}"

    Patient.objects.create(
        code_patient=code,
        nom=nom,
        prenom=prenom,
        date_naissance=ddn,
        sexe=sexe,
        groupe_sanguin=gs,
        ville=f"{ville}",
        adresse=f"{random.randint(1, 999)} Avenue {random.choice(NOMS)}",
        telephone=f"+243 {random.randint(800,999)} {random.randint(100,999)} {random.randint(100,999)}",
        diabete=diabete,
        hypertension=hypertension,
        asthme=asthme,
        statut='actif',
        cree_par=admin,
    )
    patients_crees += 1

print(f"   {patients_crees} patients créés !")

# ========== ÉTAPE 2 : GÉNÉRER LES CONSULTATIONS ==========
print(f"\nÉtape 2 : Génération des consultations sur {NB_JOURS_HISTORIQUE} jours...")

patients = list(Patient.objects.all())
consultations_creees = 0
consultations_par_maladie = {m: 0 for m in MALADIES_CONFIG}

for i in range(NB_JOURS_HISTORIQUE):
    date_consultation = timezone.now() - timedelta(
        days=NB_JOURS_HISTORIQUE - i
    )

    for maladie, config in MALADIES_CONFIG.items():
        nb = nb_consultations_jour(maladie, i)

        for _ in range(nb):
            patient = random.choice(patients)
            medecin = random.choice(medecins)
            urgence = random.choice(config['urgences'])

            DossierMedical.objects.create(
                patient=patient,
                medecin=medecin,
                date_consultation=date_consultation,
                motif_consultation=f"Consultation pour {maladie}",
                symptomes=config['description'],
                diagnostic=maladie,
                prescription=config['prescription'],
                posologie="Selon protocole médical",
                notes_medicales=f"Jour {i} — généré automatiquement",
                urgence=urgence,
                statut='ouvert'
            )
            consultations_creees += 1
            consultations_par_maladie[maladie] += 1

    if (i + 1) % 30 == 0:
        print(f"   {i+1}/{NB_JOURS_HISTORIQUE} jours "
              f"({consultations_creees} consultations)")

# ========== STATISTIQUES ==========
print("\n" + "=" * 60)
print("GÉNÉRATION TERMINÉE !")
print("=" * 60)
print(f"\nPatients créés      : {patients_crees}")
print(f"Total consultations : {consultations_creees}")
print(f"Période             : {NB_JOURS_HISTORIQUE} jours")
print(f"Moyenne             : "
      f"{consultations_creees/NB_JOURS_HISTORIQUE:.1f} consultations/jour")

print(f"\nRÉPARTITION PAR MALADIE :")
for maladie in sorted(consultations_par_maladie,
                      key=lambda x: consultations_par_maladie[x],
                      reverse=True):
    nb = consultations_par_maladie[maladie]
    pct = (nb / consultations_creees) * 100
    barre = '#' * int(pct / 2)
    print(f"   {maladie:<25} : {nb:>4} cas ({pct:>5.1f}%) {barre}")
