from django.urls import path
from . import views

app_name = 'dossiers'

urlpatterns = [
    path('', views.liste_dossiers, name='liste'),
    path('creer/', views.creer_dossier, name='creer'),
    path('<uuid:pk>/', views.detail_dossier, name='detail'),
    path('<uuid:pk>/modifier/', views.modifier_dossier, name='modifier'),
    path('<uuid:pk>/supprimer/', views.supprimer_dossier, name='supprimer'),
    path('<uuid:pk>/pdf/', views.exporter_pdf_dossier, name='exporter_pdf'), 
]