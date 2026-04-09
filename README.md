# 🏥 Système de Suivi Médical Intelligent (SSMI)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2-green.svg)
![Python](https://img.shields.io/badge/Python-3.12+-yellow.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

> Un système intelligent de gestion médicale avec intelligence artificielle embarquée pour la détection précoce des épidémies, l'analyse prédictive des risques sanitaires et la génération de données médicales synthétiques.

---

## 📋 Table des Matières

- [À Propos](#-à-propos)
- [Fonctionnalités Principales](#-fonctionnalités-principales)
- [Modules d'Intelligence Artificielle](#-modules-dintelligence-artificielle)
- [Pipeline IA](#-pipeline-ia)
- [Technologies Utilisées](#-technologies-utilisées)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Structure du Projet](#-structure-du-projet)
- [Notebooks Jupyter](#-notebooks-jupyter)
- [Documentation](#-documentation)
- [Contribution](#-contribution)
- [Auteurs](#-auteurs)
- [Licence](#-licence)

---

## 🎯 À Propos

Le **Système de Suivi Médical Intelligent (SSMI)** est une plateforme web complète de gestion médicale développée avec Django. Il intègre des modules d'intelligence artificielle avancés pour :

- Identifier automatiquement les patients à risque
- Prédire les épidémies grâce à un modèle LSTM intégré en production
- Générer des données médicales synthétiques réalistes via TimeGAN
- Détecter les zones géographiques à forte prévalence de maladies
- Analyser les tendances par tranche d'âge
- Optimiser l'allocation des ressources médicales

### 🌟 Points Forts

✅ **LSTM Intégré en Production** - Remplace la régression linéaire · perte finale 0.001  
✅ **TimeGAN Paludisme** - Génération de données synthétiques · MMD=0.278 · DTW=2.285  
✅ **Pipeline Complet** - TimeGAN → données synthétiques → LSTM enrichi  
✅ **Détection Précoce** - Anticipe les épidémies 2-3 semaines à l'avance  
✅ **Analyse Géographique** - Identification des hotspots épidémiques  
✅ **Multi-Rôles** - Admin, Médecin, Analyste avec permissions granulaires  
✅ **Tableaux de Bord Personnalisés** - Interface adaptée à chaque profil  
✅ **Exports PDF** - Rapports professionnels automatisés  

---

## 🚀 Fonctionnalités Principales

### 👥 Gestion des Patients
- Création et modification de dossiers patients
- Historique médical complet
- Recherche avancée multi-critères
- Gestion des maladies chroniques
- Calcul automatique de l'IMC

### 📋 Dossiers Médicaux
- Consultations détaillées
- Diagnostic et prescription
- Examens complémentaires
- Notes médicales sécurisées
- Suivi des rendez-vous

### 📊 Statistiques et Analyses
- Pathologies fréquentes
- Répartition par âge et sexe
- Évolution temporelle
- Rapports annuels
- Exports PDF professionnels

### 🔐 Sécurité et Authentification
- Authentification multi-rôles
- Permissions granulaires
- Protection des données sensibles
- Conformité RGPD

---

## 🤖 Modules d'Intelligence Artificielle

### 1️⃣ Score de Risque Patient

**Objectif :** Identifier automatiquement les patients nécessitant une attention prioritaire.

**Analyse 6 facteurs :**
- Âge (25%)
- Nombre de maladies (30%)
- Maladies chroniques (20%)
- IMC (15%)
- Groupe sanguin (5%)
- Sexe (5%)

**Résultat :** Score 0-100 avec classification en 4 niveaux :
- 🟢 Faible (0-25)
- 🟡 Modéré (26-50)
- 🟠 Élevé (51-75)
- 🔴 Critique (76-100)

---

### 2️⃣ Analyse par Tranche d'Âge

**Objectif :** Identifier les tranches d'âge les plus touchées par certaines maladies.

**Fonctionnalités :**
- Regroupement automatique en 5 tranches d'âge
- Calcul de prévalence par tranche
- Prédiction sur 30 jours par régression linéaire
- Détection de tendances (hausse/baisse)

**Utilité :** Cibler les campagnes de prévention par groupe d'âge.

---

### 3️⃣ Analyse Géographique

**Objectif :** Détecter les zones à forte concentration de maladies (hotspots).

**Détection :**
- Calcul de prévalence par ville
- Comparaison avec la moyenne
- Identification des zones critiques
- Recommandations d'actions ciblées

**Seuils d'alerte :**
- 🟢 Normal (< 30%)
- 🟡 Modéré (30-50%)
- 🟠 Élevé (50-80%)
- 🔴 Critique (> 80%)

**Recommandations intelligentes** adaptées par maladie :
- Paludisme → Distribution moustiquaires, pulvérisation
- Grippe → Vaccination d'urgence, isolement
- Diabète → Dépistage massif, cliniques mobiles
- Hypertension → Mesure tension gratuite, prévention cardiovasculaire

---

### 4️⃣ Prédiction d'Épidémies — LSTM

**Objectif :** Anticiper les épidémies en analysant les tendances historiques avec un modèle LSTM.

**Architecture LSTM :**
- 2 couches cachées · hidden_size=32
- Fenêtre temporelle : 7 jours
- Optimiseur : Adam (lr=0.01) · MSELoss
- 200 epochs · Perte finale : **0.001**
- 173 séquences d'entraînement · 180 jours

**Processus :**
1. **Collecte** : Extraction des données depuis PostgreSQL (180 jours)
2. **Nettoyage** : Interpolation linéaire des jours manquants
3. **Normalisation** : MinMaxScaler
4. **Séquences** : Fenêtres glissantes de 7 jours (173 séquences)
5. **Entraînement** : LSTM 200 epochs
6. **Prédiction** : 7 jours futurs

**Niveaux de risque :**
- 🔴 Critique (> 50% augmentation prévue)
- 🟠 Élevé (25-50% augmentation)
- 🟡 Modéré (10-25% augmentation)
- 🟢 Faible (< 10% augmentation)

**Actions recommandées automatiques** selon le niveau de risque.

---

### 5️⃣ Génération de Données Synthétiques — TimeGAN

**Objectif :** Générer des données médicales synthétiques réalistes pour pallier le manque de données réelles soumises au RGPD.

**Architecture TimeGAN :**
- Générateur : bruit 32 dim → Linear 64 → LSTM 2 couches → sigmoid
- Discriminateur : LSTM 2 couches → Linear → sigmoid
- Optimiseur : Adam (lr=0.0001) · BCELoss · batch=16
- 1 000 epochs · Générateur entraîné 2× par epoch

**Entraîné spécifiquement sur le Paludisme :**
- 173 séquences · 180 jours
- Génère des séries cohérentes avec les vraies données

**Métriques d'évaluation :**
- MMD (Maximum Mean Discrepancy) = **0.278**
- DTW (Dynamic Time Warping) = **2.285**

---

## 🔄 Pipeline IA
```
Données PostgreSQL (180 jours · 8 maladies · 4 046 consultations)
        ↓
TimeGAN Paludisme
(173 séquences · 1 000 epochs · MMD=0.278 · DTW=2.285)
        ↓
100 séries synthétiques générées
        ↓
Fusion : 173 réelles + 100 synthétiques = 273 séquences
        ↓
LSTM entraîné sur dataset enrichi
(perte finale 0.001 · prédictions 7 jours)
        ↓
Intégré dans epidemic_prediction.py en production
```

---

## 🛠️ Technologies Utilisées

### Backend
- **Django 5.2** - Framework web Python
- **PostgreSQL** - Base de données relationnelle
- **Python 3.12+** - Langage de programmation

### Frontend
- **Bootstrap 5** - Framework CSS responsive
- **Chart.js** - Graphiques interactifs
- **JavaScript (ES6+)** - Interactivité

### Intelligence Artificielle
- **PyTorch** - LSTM et TimeGAN
- **NumPy** - Calculs numériques
- **Pandas** - Analyse de données
- **Scikit-learn** - Normalisation et métriques
- **Matplotlib** - Visualisation des séries temporelles

### Outils de Développement
- **Jupyter Notebook** - Développement et expérimentation IA
- **Git / GitHub** - Contrôle de version
- **VS Code** - Éditeur de code
- **pip** - Gestionnaire de packages Python

---

## 💻 Installation

### Prérequis

- Python 3.12 ou supérieur
- PostgreSQL 14 ou supérieur
- pip (gestionnaire de packages Python)
- Git

### Étapes d'Installation

#### 1. Cloner le Repository
```bash
git clone https://github.com/wenrid/Systeme-de-Suivi-Medical-Intelligent.git
cd Systeme-de-Suivi-Medical-Intelligent
```

#### 2. Créer un Environnement Virtuel

**Windows :**
```bash
python -m venv ssmi
ssmi\Scripts\activate
```

**Linux/Mac :**
```bash
python3 -m venv ssmi
source ssmi/bin/activate
```

#### 3. Installer les Dépendances
```bash
pip install -r requirements.txt
```

#### 4. Configurer la Base de Données

Créez une base de données PostgreSQL :
```sql
CREATE DATABASE medical_system;
CREATE USER medical_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE medical_system TO medical_user;
```

Modifiez `medical_system/settings.py` :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'medical_system',
        'USER': 'medical_user',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### 5. Appliquer les Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Créer un Superutilisateur
```bash
python manage.py createsuperuser
```

Suivez les instructions pour définir :
- Username
- Email
- Password
- Rôle (choisir `admin`)

#### 7. Générer les Données de Test
```bash
python generer_data.py
```

Génère : **249 patients · 4 046 consultations · 8 maladies · 180 jours**

#### 8. Lancer le Serveur
```bash
python manage.py runserver
```

Accédez à l'application : **http://localhost:8000**

---

## 📖 Utilisation

### Premiers Pas

1. **Connexion** : Utilisez le superutilisateur créé
2. **Créer des Patients** : Menu "Gestion des Patients" → "Nouveau Patient"
3. **Créer des Dossiers** : Menu "Dossiers Médicaux" → "Nouvelle Consultation"
4. **Analyser avec l'IA** : Menu "Analyses IA"

### Rôles Utilisateurs

#### 👨‍⚕️ Médecin
- Créer et consulter les dossiers médicaux
- Voir les patients
- Prescrire des traitements
- Accès limité aux statistiques

#### 📊 Analyste
- Accès complet aux statistiques
- Générer des rapports
- Utiliser tous les modules IA
- Exporter des données

#### 👑 Administrateur
- Toutes les permissions
- Gestion des utilisateurs
- Configuration système
- Accès à l'admin Django

### Modules IA

#### Score de Risque Patient
1. Menu **Analyses IA** → **Score de Risque**
2. Liste des patients triés par score
3. Cliquez sur un patient pour les détails

#### Analyse par Âge
1. Menu **Analyses IA** → **Analyse par Âge**
2. Visualisez les graphiques par tranche d'âge
3. Consultez les prédictions

#### Analyse Géographique
1. Menu **Analyses IA** → **Analyse Géographique**
2. Carte des hotspots détectés
3. Recommandations par zone

#### Prédiction d'Épidémies
1. Menu **Analyses IA** → **Prédiction d'Épidémies**
2. Graphiques de tendances LSTM
3. Prédictions sur 7 jours
4. Évaluation du risque

---

## 📓 Notebooks Jupyter

| Notebook | Description | Résultats |
|---|---|---|
| `lstm_ssmi.ipynb` | Entraînement LSTM sur Paludisme | Perte=0.001 · MAE=0.261 |
| `timegan_ssmi.ipynb` | TimeGAN sur 8 maladies · 1 384 séquences | MMD=0.278 · DTW=2.285 |
| `pipeline_complet.ipynb` | Pipeline complet TimeGAN Paludisme → LSTM | 273 séquences enrichies |

### Lancer les Notebooks
```bash
jupyter notebook
```

---

## 📁 Structure du Projet
```
medical_system/
│
├── apps/
│   ├── authentication/      # Gestion authentification
│   ├── core/                # Fonctionnalités de base
│   ├── patients/            # Gestion patients
│   ├── dossiers/            # Dossiers médicaux
│   └── stats_medicales/     # Statistiques et IA
│       ├── ml_analysis.py           # Score risque · Analyse âge · Géographie
│       ├── epidemic_prediction.py   # Prédiction LSTM (intégré en production)
│       └── pdf_reports.py           # Génération PDF
│
├── medical_system/
│   ├── settings.py          # Configuration Django
│   ├── urls.py              # Routes principales
│   └── wsgi.py              # WSGI configuration
│
├── templates/               # Templates HTML
│   ├── base.html
│   ├── patients/
│   ├── dossiers/
│   └── stats/
│
├── static/                  # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                   # Fichiers uploadés
│
├── lstm_ssmi.ipynb          # Notebook LSTM
├── timegan_ssmi.ipynb       # Notebook TimeGAN
├── pipeline_complet.ipynb   # Pipeline complet TimeGAN → LSTM
├── generer_data.py          # Génération données réalistes (180 jours)
├── creer_hotspot.py         # Script création hotspot épidémique
├── manage.py                # Commande Django
├── requirements.txt         # Dépendances Python
└── README.md                # Ce fichier
```

---

## 📚 Documentation

### Commandes Utiles

#### Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Créer un Utilisateur
```bash
python manage.py createsuperuser
```

#### Générer des Données de Test
```bash
python generer_data.py
```

#### Créer un Hotspot Épidémique
```bash
python creer_hotspot.py
```

#### Lancer le Shell Django
```bash
python manage.py shell
```

#### Collecter les Fichiers Statiques
```bash
python manage.py collectstatic
```

### Configuration Avancée

#### Personnaliser les Seuils IA

**Fichier :** `apps/stats_medicales/epidemic_prediction.py`
```python
# Seuils de détection géographique
if taux > 80:      # Critique
if taux > 50:      # Élevé
if taux > 30:      # Modéré

# Période d'analyse
jours_historique = 180  # Modifier selon besoin
jours_prediction = 7    # Modifier selon besoin
```

#### Modifier les Recommandations IA

**Fichier :** `apps/stats_medicales/epidemic_prediction.py`  
**Fonction :** `_generer_recommandation_intelligente()`

Ajoutez vos propres maladies et recommandations dans le dictionnaire `recommandations_par_maladie`.

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

### 1. Fork le Projet
### 2. Créer une Branche
```bash
git checkout -b feature/amelioration
```

### 3. Commit les Changements
```bash
git commit -m "Ajout d'une nouvelle fonctionnalité"
```

### 4. Push vers la Branche
```bash
git push origin feature/amelioration
```

### 5. Ouvrir une Pull Request

---

## 👥 Auteurs

- **Wenchel RIDORE** - *Analyste-Programmeur* - [GitHub](https://github.com/wenrid) - rwenchella@gmail.com
- **Rabbin KIMBANGI MENAKUNTIMA** - *Développeur* - [GitHub](https://github.com/rabbikimbangi) - rabbiskentkimbangi@gmail.com
- **Kandolo HERMAN** - *Développeur* - [GitHub](https://github.com/Herman2691) - Hermankandolo2022@gmail.com

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- Django Software Foundation pour l'excellent framework
- Bootstrap pour le framework CSS
- Chart.js pour les graphiques interactifs
- PyTorch pour les modèles LSTM et TimeGAN
- La communauté open-source Python

---

## 📞 Contact

**Wenchel RIDORE** : rwenchella@gmail.com | [GitHub](https://github.com/wenrid)  
**Rabbin KIMBANGI** : rabbiskentkimbangi@gmail.com | [GitHub](https://github.com/rabbikimbangi)  
**Kandolo HERMAN** : Hermankandolo2022@gmail.com

---

## 🎓 Vision Future

### Améliorations Planifiées

- [ ] Application mobile (React Native)
- [ ] Télémédecine intégrée
- [ ] Module d'imagerie médicale avec Green AI
- [ ] Intégration laboratoire
- [ ] API REST complète
- [ ] NLP pour transcription consultations
- [ ] TimeGAN conditionnel sur données réelles (MOVER)
- [ ] LSTM par maladie (un modèle spécifique par pathologie)
- [ ] Modèles de diffusion conditionnels (WaveStitch)
- [ ] Big Data et analytics avancés
- [ ] Notifications push automatiques
- [ ] Carte interactive des épidémies

---

## 📊 Statistiques du Projet

| Métrique | Valeur |
|---|---|
| Lignes de Code | ~15 000+ |
| Applications Django | 5 |
| Modèles de Données | 10+ |
| Vues Fonctionnelles | 35+ |
| Templates HTML | 25+ |
| Modules IA | 5 |
| Notebooks Jupyter | 3 |
| Patients générés | 249 |
| Consultations | 4 046 |
| Maladies | 8 |
| Jours d'historique | 180 |
| Perte LSTM | 0.001 |
| MMD TimeGAN | 0.278 |
| DTW TimeGAN | 2.285 |

---

<div align="center">
  <p>Développé avec ❤️ pour améliorer la santé publique</p>
  <p>© 2026 Système de Suivi Médical Intelligent</p>
</div>