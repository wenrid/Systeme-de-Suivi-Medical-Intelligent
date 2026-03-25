from django.core.management.base import BaseCommand
from apps.patients.models import Patient
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Génère des patients fictifs de différentes villes de RDC'

    def handle(self, *args, **options):
        # Données fictives réalistes
        noms_congolais = [
            'Mukendi', 'Tshilombo', 'Kabongo', 'Mbuyi', 'Kasongo',
            'Kabamba', 'Mwamba', 'Ilunga', 'Ngoy', 'Kalenga',
            'Mutombo', 'Kabangu', 'Tshisekedi', 'Kalala', 'Mwanza',
            'Nkulu', 'Mujinga', 'Kibwe', 'Mwenze', 'Musonda'
        ]
        
        prenoms_hommes = [
            'Jean', 'Pierre', 'Paul', 'Jacques', 'François',
            'Joseph', 'André', 'Michel', 'Daniel', 'Claude',
            'Emmanuel', 'Patrick', 'Christian', 'Pascal', 'David'
        ]
        
        prenoms_femmes = [
            'Marie', 'Jeanne', 'Anne', 'Claire', 'Sophie',
            'Christine', 'Françoise', 'Thérèse', 'Louise', 'Bernadette',
            'Grace', 'Joséphine', 'Brigitte', 'Nicole', 'Denise'
        ]
        
        # Villes de la RDC avec leurs quartiers/communes
        villes_rdc = [
            # Kinshasa et communes
            {'ville': 'Kinshasa', 'quartiers': [
                'Gombe', 'Bandalungwa', 'Barumbu', 'Bumbu', 'Kalamu',
                'Kasa-Vubu', 'Kimbanseke', 'Kintambo', 'Lemba', 'Limete',
                'Lingwala', 'Makala', 'Masina', 'Matete', 'Mont-Ngafula',
                'Ndjili', 'Ngaba', 'Ngaliema', 'Ngiri-Ngiri', 'Selembao'
            ]},
            
            # Lubumbashi et quartiers
            {'ville': 'Lubumbashi', 'quartiers': [
                'Kampemba', 'Kamalondo', 'Katuba', 'Kenya', 'Kipushi',
                'Ruashi', 'Annexe', 'Golf', 'Industriel', 'Lumumba'
            ]},
            
            # Bukavu et quartiers
            {'ville': 'Bukavu', 'quartiers': [
                'Bagira', 'Ibanda', 'Kadutu', 'Nyalukemba', 'Panzi',
                'Essence', 'Mulongwe', 'Cahi', 'Nyawera', 'Ciriri'
            ]},
            
            # Goma et quartiers
            {'ville': 'Goma', 'quartiers': [
                'Himbi', 'Karisimbi', 'Kasika', 'Katindo', 'Mugunga',
                'Kyeshero', 'Virunga', 'Ndosho', 'Mapendo', 'Bujovu'
            ]},
            
            # Kisangani et quartiers
            {'ville': 'Kisangani', 'quartiers': [
                'Kabondo', 'Makiso', 'Mangobo', 'Tshopo', 'Lubunga',
                'Basoko', 'Boyoma', 'Kisangani', 'Wagenia', 'Plateau'
            ]},
            
            # Matadi
            {'ville': 'Matadi', 'quartiers': [
                'Camp Luka', 'Kinkanda', 'Mvuzi', 'Nzanza', 'Soyo',
                'Matadi Centre', 'Nkouikou', 'Plateau', 'Victoria', 'Port'
            ]},
            
            # Kananga
            {'ville': 'Kananga', 'quartiers': [
                'Kananga', 'Katoka', 'Nganza', 'Ndesha', 'Plateau',
                'Kamuesha', 'Railway', 'Bipemba', 'Lukonga', 'Cemea'
            ]},
            
            # Mbuji-Mayi
            {'ville': 'Mbuji-Mayi', 'quartiers': [
                'Dibindi', 'Kanshi', 'Muya', 'Bipemba', 'Nzaba',
                'Tshibangu', 'Bonzola', 'Dikelenge', 'Kabala', 'Kalenda'
            ]}
        ]
        
        groupes_sanguins = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        patients_crees = 0
        
        for i in range(20):
            # Sexe aléatoire
            sexe = random.choice(['M', 'F'])
            
            # Nom et prénom selon le sexe
            nom = random.choice(noms_congolais)
            prenom = random.choice(prenoms_hommes if sexe == 'M' else prenoms_femmes)
            
            # Date de naissance (entre 5 et 80 ans)
            age_annees = random.randint(5, 80)
            date_naissance = date.today() - timedelta(days=age_annees * 365 + random.randint(0, 364))
            
            # Ville et quartier aléatoires
            ville_data = random.choice(villes_rdc)
            ville_nom = ville_data['ville']
            quartier = random.choice(ville_data['quartiers'])
            ville = f"{ville_nom} - {quartier}"
            
            # Groupe sanguin
            groupe_sanguin = random.choice(groupes_sanguins)
            
            # Téléphone (format RDC)
            telephone = f"+243 {random.randint(800, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
            
            # Adresse fictive
            avenues = ['Lumumba', 'Kasa-Vubu', 'du Port', 'Colonel Ebeya', 'Kabila', 'Mobutu', 'de la Paix', 'Kasavubu']
            adresse = f"{random.randint(1, 500)} Avenue {random.choice(avenues)}, {quartier}"
            
            # Maladies chroniques (probabilités réalistes)
            diabete = random.random() < 0.15
            hypertension = random.random() < 0.20
            asthme = random.random() < 0.10
            epilepsie = random.random() < 0.05
            drepanocytose = random.random() < 0.08
            vih = random.random() < 0.03
            
            # Allergies (30% de chance d'en avoir)
            allergies = ""
            if random.random() < 0.30:
                allergies_possibles = ['Pénicilline', 'Aspirine', 'Pollen', 'Arachides', 'Fruits de mer']
                allergies = random.choice(allergies_possibles)
            
            # Antécédents médicaux (40% de chance)
            antecedents_medicaux = ""
            if random.random() < 0.40:
                antecedents_possibles = [
                    'Paludisme récurrent',
                    'Tuberculose traitée',
                    'Gastrite chronique',
                    'Troubles thyroïdiens',
                    'Anémie'
                ]
                antecedents_medicaux = random.choice(antecedents_possibles)
            
            # Antécédents chirurgicaux (20% de chance)
            antecedents_chirurgicaux = ""
            if random.random() < 0.20:
                chirurgies_possibles = [
                    'Appendicectomie 2015',
                    'Césarienne 2018',
                    'Hernie inguinale 2019',
                    'Cholécystectomie 2020',
                    'Fracture fémur 2017'
                ]
                antecedents_chirurgicaux = random.choice(chirurgies_possibles)
            
            # Email (50% ont un email)
            email = ""
            if random.random() < 0.50:
                email = f"{prenom.lower()}.{nom.lower()}@email.cd"
            
            # Créer le patient
            try:
                patient = Patient.objects.create(
                    nom=nom,
                    prenom=prenom,
                    date_naissance=date_naissance,
                    sexe=sexe,
                    groupe_sanguin=groupe_sanguin,
                    telephone=telephone,
                    email=email,
                    adresse=adresse,
                    ville=ville,
                    diabete=diabete,
                    hypertension=hypertension,
                    asthme=asthme,
                    epilepsie=epilepsie,
                    drepanocytose=drepanocytose,
                    vih=vih,
                    allergies=allergies,
                    antecedents_medicaux=antecedents_medicaux,
                    antecedents_chirurgicaux=antecedents_chirurgicaux,
                    statut='actif'
                )
                
                patients_crees += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Patient créé : {patient.code_patient} - {patient.nom_complet} ({patient.age} ans) - {ville}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erreur création patient {i+1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 {patients_crees}/20 patients fictifs créés avec succès !')
        )