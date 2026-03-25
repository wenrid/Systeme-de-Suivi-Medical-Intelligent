from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.liste_patients, name='liste_patients'),
    path('ajouter/', views.ajouter_patient, name='ajouter_patient'),
    path('<int:pk>/', views.detail_patient, name='detail_patient'),
    path('<int:pk>/modifier/', views.modifier_patient, name='modifier_patient'),
    path('<int:pk>/supprimer/', views.supprimer_patient, name='supprimer_patient'),
]