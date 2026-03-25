from django.core.management.base import BaseCommand
from apps.patients.models import Patient
from apps.dossiers.models import DossierMedical
from apps.authentication.models import User
from datetime import datetime, timedelta
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Génère des dossiers médicaux fictifs pour les patients existants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--nombre',
            type=int,
            default=50,
            help='Nombre de dossiers à créer au total'
        )

    def handle(self, *args, **options):
        nombre_dossiers = options['nombre']
        
        # Vérifier qu'il y a des médecins et patients
        medecins = User.objects.filter(role='medecin', is_active=True)
        patients = Patient.objects.filter(statut='actif')
        
        if not medecins.exists():
            self.stdout.write(
                self.style.ERROR('❌ Aucun médecin actif trouvé. Créez d\'abord des médecins.')
            )
            return
        
        if not patients.exists():
            self.stdout.write(
                self.style.ERROR('❌ Aucun patient actif trouvé. Créez d\'abord des patients.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'📋 Création de {nombre_dossiers} dossiers médicaux...')
        )
        self.stdout.write(
            self.style.SUCCESS(f'👨‍⚕️ {medecins.count()} médecin(s) disponible(s)')
        )
        self.stdout.write(
            self.style.SUCCESS(f'👥 {patients.count()} patient(s) disponible(s)\n')
        )
        
        # Diagnostics réalistes par catégorie
        diagnostics_par_type = {
            'infections': [
                {
                    'motif': 'Fièvre et frissons depuis 3 jours',
                    'symptomes': 'Température élevée, frissons, courbatures, maux de tête',
                    'diagnostic': 'Paludisme non compliqué',
                    'prescription': 'Artéméther-Luméfantrine (Coartem)',
                    'posologie': '4 comprimés immédiatement, puis 4 cp à H8, H24, H36, H48 et H60',
                    'urgence': 'moyenne'
                },
                {
                    'motif': 'Toux persistante avec fièvre',
                    'symptomes': 'Toux grasse, fièvre, expectoration, douleur thoracique',
                    'diagnostic': 'Pneumonie communautaire',
                    'prescription': 'Amoxicilline 1g',
                    'posologie': '1g 3 fois par jour pendant 7 jours',
                    'urgence': 'elevee'
                },
                {
                    'motif': 'Diarrhée aqueuse abondante',
                    'symptomes': 'Diarrhée, déshydratation, vomissements',
                    'diagnostic': 'Gastro-entérite aiguë',
                    'prescription': 'SRO (Sels de Réhydratation Orale) + Zinc',
                    'posologie': 'SRO après chaque selle liquide, Zinc 20mg/jour pendant 10 jours',
                    'urgence': 'moyenne'
                },
                {
                    'motif': 'Maux de gorge et fièvre',
                    'symptomes': 'Odynophagie, fièvre modérée, adénopathies cervicales',
                    'diagnostic': 'Angine streptococcique',
                    'prescription': 'Pénicilline V (Oracilline)',
                    'posologie': '1 million UI 2 fois par jour pendant 10 jours',
                    'urgence': 'faible'
                },
                {
                    'motif': 'Céphalées intenses et raideur nuque',
                    'symptomes': 'Céphalées, photophobie, vomissements, raideur de nuque',
                    'diagnostic': 'Méningite suspectée',
                    'prescription': 'Ceftriaxone IV + Hospitalisation',
                    'posologie': 'Ceftriaxone 2g IV toutes les 12h',
                    'urgence': 'critique'
                }
            ],
            
            'chroniques': [
                {
                    'motif': 'Suivi diabète - Contrôle glycémique',
                    'symptomes': 'Polyurie, polydipsie, fatigue',
                    'diagnostic': 'Diabète de type 2 déséquilibré',
                    'prescription': 'Metformine 850mg + Glibenclamide 5mg',
                    'posologie': 'Metformine 850mg matin et soir, Glibenclamide 5mg avant petit-déjeuner',
                    'urgence': 'faible'
                },
                {
                    'motif': 'Tension artérielle élevée',
                    'symptomes': 'Céphalées, vertiges, acouphènes',
                    'diagnostic': 'Hypertension artérielle essentielle',
                    'prescription': 'Amlodipine 5mg + Losartan 50mg',
                    'posologie': 'Amlodipine 5mg le matin, Losartan 50mg le soir',
                    'urgence': 'moyenne'
                },
                {
                    'motif': 'Crise d\'asthme',
                    'symptomes': 'Dyspnée, sifflements respiratoires, toux sèche',
                    'diagnostic': 'Asthme aigu modéré',
                    'prescription': 'Salbutamol inhalateur + Corticoïdes',
                    'posologie': 'Salbutamol 2 bouffées toutes les 4h si besoin, Prednisolone 40mg/jour 5 jours',
                    'urgence': 'elevee'
                },
                {
                    'motif': 'Douleurs articulaires multiples',
                    'symptomes': 'Douleurs inflammatoires, raideur matinale, tuméfaction',
                    'diagnostic': 'Polyarthrite rhumatoïde',
                    'prescription': 'Méthotrexate + Acide folique',
                    'posologie': 'Méthotrexate 15mg une fois/semaine, Acide folique 5mg 24h après',
                    'urgence': 'faible'
                }
            ],
            
            'traumatologie': [
                {
                    'motif': 'Chute avec douleur cheville',
                    'symptomes': 'Douleur cheville, œdème, impossibilité d\'appui',
                    'diagnostic': 'Entorse cheville grade 2',
                    'prescription': 'Ibuprofène 400mg + Immobilisation',
                    'posologie': 'Ibuprofène 400mg 3 fois/jour après repas, Repos 7 jours',
                    'urgence': 'faible'
                },
                {
                    'motif': 'Douleur lombaire aiguë',
                    'symptomes': 'Lombalgie intense, contracture musculaire, limitation mobilité',
                    'diagnostic': 'Lombosciatique commune',
                    'prescription': 'Diclofénac 75mg + Thiocolchicoside',
                    'posologie': 'Diclofénac 75mg 2 fois/jour, Thiocolchicoside 4mg 3 fois/jour pendant 5 jours',
                    'urgence': 'moyenne'
                },
                {
                    'motif': 'Traumatisme crânien léger',
                    'symptomes': 'Céphalées, nausées, pas de perte de connaissance',
                    'diagnostic': 'Commotion cérébrale',
                    'prescription': 'Paracétamol + Surveillance',
                    'posologie': 'Paracétamol 1g toutes les 6h si besoin, Repos 48-72h',
                    'urgence': 'moyenne'
                }
            ],
            
            'gyneco': [
                {
                    'motif': 'Consultation prénatale',
                    'symptomes': 'Grossesse évolutive, pas de plainte particulière',
                    'diagnostic': 'Grossesse normale T2',
                    'prescription': 'Fer + Acide folique + Calcium',
                    'posologie': 'Fer 200mg/jour, Acide folique 5mg/jour, Calcium 500mg 2 fois/jour',
                    'urgence': 'faible'
                },
                {
                    'motif': 'Douleurs pelviennes et leucorrhées',
                    'symptomes': 'Douleurs pelviennes, pertes vaginales, dyspareunie',
                    'diagnostic': 'Infection génitale haute',
                    'prescription': 'Doxycycline + Métronidazole',
                    'posologie': 'Doxycycline 100mg 2 fois/jour 7 jours, Métronidazole 500mg 3 fois/jour 7 jours',
                    'urgence': 'moyenne'
                },
                {
                    'motif': 'Aménorrhée et test positif',
                    'symptomes': 'Absence de règles, nausées matinales, fatigue',
                    'diagnostic': 'Début de grossesse',
                    'prescription': 'Acide folique + Consultation prénatale',
                    'posologie': 'Acide folique 400µg/jour, Rendez-vous échographie à programmer',
                    'urgence': 'faible'
                }
            ],
            
            'pediatrie': [
                {
                    'motif': 'Fièvre et éruption cutanée',
                    'symptomes': 'Fièvre, éruption maculopapuleuse, conjonctivite',
                    'diagnostic': 'Rougeole',
                    'prescription': 'Paracétamol + Vitamine A',
                    'posologie': 'Paracétamol 15mg/kg toutes les 6h, Vitamine A 200 000 UI dose unique',
                    'urgence': 'elevee'
                },
                {
                    'motif': 'Vaccination de routine',
                    'symptomes': 'Enfant en bonne santé',
                    'diagnostic': 'Bilan de santé normal',
                    'prescription': 'Vaccins selon calendrier PEV',
                    'posologie': 'Selon protocole national de vaccination',
                    'urgence': 'faible'
                },
                {
                    'motif': 'Toux et difficulté respiratoire',
                    'symptomes': 'Toux, sifflements, tirage intercostal, dyspnée',
                    'diagnostic': 'Bronchiolite du nourrisson',
                    'prescription': 'Salbutamol nébulisation + Corticoïdes',
                    'posologie': 'Salbutamol 2,5mg en nébulisation 3 fois/jour, Corticoïdes si sévère',
                    'urgence': 'elevee'
                }
            ],
            
            'dermatologie': [
                {
                    'motif': 'Démangeaisons et lésions cutanées',
                    'symptomes': 'Prurit intense, lésions papuleuses, excoriations',
                    'diagnostic': 'Gale (scabiose)',
                    'prescription': 'Perméthrine 5% crème',
                    'posologie': 'Application sur tout le corps, laisser 8-12h, répéter à J7',
                    'urgence': 'faible'
                },
                {
                    'motif': 'Éruption cutanée généralisée',
                    'symptomes': 'Plaques érythémateuses, desquamation, prurit',
                    'diagnostic': 'Eczéma atopique',
                    'prescription': 'Dermocorticoïdes + Émollients',
                    'posologie': 'Hydrocortisone 1% 2 applications/jour 7 jours, Émollients quotidiens',
                    'urgence': 'faible'
                }
            ]
        }
        
        # Examens complémentaires possibles
        examens_complementaires = [
            'Glycémie à jeun, HbA1c',
            'NFS, VS, CRP',
            'Créatininémie, Urée',
            'Radiographie thorax',
            'Échographie abdominale',
            'ECG',
            'Test de grossesse',
            'Goutte épaisse (paludisme)',
            'ECBU',
            'Bilan lipidique',
            'Transaminases (ALAT, ASAT)',
            'Échographie obstétricale',
            'TDR Paludisme',
            'Sérologie VIH'
        ]
        
        # Recommandations
        recommandations_types = [
            'Repos au domicile',
            'Hydratation abondante (2-3L/jour)',
            'Éviter l\'automédication',
            'Contrôle dans 7 jours',
            'Régime pauvre en sel',
            'Régime diabétique strict',
            'Activité physique modérée 30 min/jour',
            'Protection contre moustiques (moustiquaire)',
            'Compléter le traitement même si amélioration',
            'Consulter en urgence si aggravation',
            'Éviter alcool et tabac',
            'Surveiller température quotidiennement',
            'Prise des médicaments aux heures fixes',
            'Éviter automédication'
        ]
        
        dossiers_crees = 0
        
        for i in range(nombre_dossiers):
            # Sélection aléatoire médecin et patient
            medecin = random.choice(medecins)
            patient = random.choice(patients)
            
            # Date consultation (dans les 90 derniers jours)
            jours_passes = random.randint(1, 90)
            date_consultation = datetime.now() - timedelta(days=jours_passes)
            
            # Choisir un diagnostic adapté au patient
            if patient.age < 15:
                categorie = 'pediatrie'
            elif patient.sexe == 'F' and 15 <= patient.age <= 45 and random.random() < 0.3:
                categorie = 'gyneco'
            elif patient.diabete or patient.hypertension or patient.asthme:
                if random.random() < 0.7:
                    categorie = 'chroniques'
                else:
                    categorie = random.choice(['infections', 'traumatologie', 'dermatologie'])
            elif random.random() < 0.5:
                categorie = 'infections'
            else:
                categorie = random.choice(['traumatologie', 'dermatologie'])
            
            diagnostic_data = random.choice(diagnostics_par_type[categorie])
            
            # Examen clinique avec valeurs réalistes
            temperature = round(random.uniform(36.5, 39.5), 1) if random.random() < 0.7 else None
            
            # Tension artérielle
            if patient.hypertension:
                systolique = random.randint(140, 180)
                diastolique = random.randint(90, 110)
            else:
                systolique = random.randint(110, 135)
                diastolique = random.randint(70, 85)
            tension_arterielle = f"{systolique}/{diastolique}"
            
            # Poids et taille
            if patient.age >= 18:
                poids = Decimal(str(round(random.uniform(45, 95), 1)))
                taille = Decimal(str(round(random.uniform(150, 185), 1)))  # En cm
            else:
                # Enfants
                poids = Decimal(str(round(random.uniform(15, 50), 1)))
                taille = Decimal(str(round(random.uniform(90, 160), 1)))  # En cm
            
            # Prochain RDV (30% des cas)
            date_prochain_rdv = None
            if random.random() < 0.30:
                date_prochain_rdv = (datetime.now() + timedelta(days=random.randint(7, 60))).date()
            
            # Statut
            if jours_passes > 30:
                statut = random.choice(['ferme', 'archive'])
            else:
                statut = random.choice(['ouvert', 'ferme'])
            
            # Créer le dossier
            try:
                dossier = DossierMedical.objects.create(
                    patient=patient,
                    medecin=medecin,
                    date_consultation=date_consultation,
                    
                    motif_consultation=diagnostic_data['motif'],
                    symptomes=diagnostic_data['symptomes'],
                    
                    temperature=temperature,
                    tension_arterielle=tension_arterielle,
                    poids=poids,
                    taille=taille,
                    
                    diagnostic=diagnostic_data['diagnostic'],
                    diagnostic_differentiel=random.choice([
                        'À écarter : septicémie',
                        'Diagnostic différentiel : infection virale',
                        'À surveiller : complications possibles',
                        'Surveiller évolution',
                        ''
                    ]) if random.random() < 0.4 else '',
                    
                    examens_complementaires=random.choice(examens_complementaires) if random.random() < 0.5 else '',
                    
                    prescription=diagnostic_data['prescription'],
                    posologie=diagnostic_data['posologie'],
                    recommandations='\n'.join(random.sample(recommandations_types, k=random.randint(2, 4))),
                    
                    date_prochain_rdv=date_prochain_rdv,
                    notes_medicales=f'Patient suivi pour {diagnostic_data["diagnostic"]}. Bonne observance attendue.' if random.random() < 0.3 else '',
                    
                    urgence=diagnostic_data['urgence'],
                    statut=statut
                )
                
                dossiers_crees += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Dossier {dossiers_crees}/{nombre_dossiers} : {patient.nom_complet} par Dr. {medecin.get_full_name()} - {diagnostic_data["diagnostic"]}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erreur création dossier {i+1}: {str(e)}')
                )
        
        # Statistiques finales
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 {dossiers_crees}/{nombre_dossiers} dossiers créés avec succès !\n')
        )
        
        # Afficher répartition par médecin
        self.stdout.write(self.style.SUCCESS('📊 Répartition par médecin :'))
        for medecin in medecins:
            nb = DossierMedical.objects.filter(medecin=medecin).count()
            self.stdout.write(f'   Dr. {medecin.get_full_name()} : {nb} dossiers')
        
        # Répartition par urgence
        self.stdout.write(self.style.SUCCESS('\n🚨 Répartition par urgence :'))
        for urgence_choice in DossierMedical.URGENCE_CHOICES:
            nb = DossierMedical.objects.filter(urgence=urgence_choice[0]).count()
            self.stdout.write(f'   {urgence_choice[1]} : {nb} dossiers')