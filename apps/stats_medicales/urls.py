from django.urls import path
from . import views

app_name = 'stats_medicales'

urlpatterns = [
    path('stats/', views.dashboard_statistiques, name='dashboard_statistiques'),
    path('stats/age/', views.generer_analyse_age, name='generer_analyse_age'),
    path('stats/pathologies/', views.generer_pathologies, name='generer_pathologies'),
    path('stats/rapport/<int:annee>/', views.generer_rapport_annuel, name='generer_rapport_annuel'),
    path('stats/rapport/', views.generer_rapport_annuel, name='generer_rapport_annuel_current'),
    path('rapport-pdf/', views.exporter_rapport_pdf, name='exporter_rapport_pdf'),
    path('ia/', views.analyse_ia_dashboard, name='analyse_ia_dashboard'),
    path('ia/patient/<int:patient_id>/', views.patient_risque_detail, name='patient_risque_detail'),
    path('epidemies/', views.prediction_epidemies, name='prediction_epidemies'),  # ← NOUVELLE LIGNE
]