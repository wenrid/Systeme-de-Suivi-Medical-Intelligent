from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from io import BytesIO
from datetime import datetime
from django.db.models import Count
from apps.patients.models import Patient
from apps.dossiers.models import DossierMedical

def generer_rapport_statistiques(type_rapport='global', periode=None):
    """
    Génère un rapport statistique en PDF
    type_rapport: 'global', 'patients', 'consultations', 'maladies'
    periode: dict avec 'date_debut' et 'date_fin' optionnels
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#3498db'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=8,
    )
    
    # En-tête du rapport
    elements.append(Paragraph("RAPPORT STATISTIQUE MÉDICAL", title_style))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", subheading_style))
    elements.append(Spacer(1, 20))
    
    # Ligne de séparation
    elements.append(Paragraph("_" * 100, subheading_style))
    elements.append(Spacer(1, 20))
    
    # ===== STATISTIQUES GLOBALES =====
    elements.append(Paragraph("📊 VUE D'ENSEMBLE", heading_style))
    
    total_patients = Patient.objects.count()
    total_dossiers = DossierMedical.objects.count()
    patients_hommes = Patient.objects.filter(sexe='M').count()
    patients_femmes = Patient.objects.filter(sexe='F').count()
    
    overview_data = [
        ['Indicateur', 'Valeur'],
        ['Total Patients', str(total_patients)],
        ['Patients Hommes', str(patients_hommes)],
        ['Patients Femmes', str(patients_femmes)],
        ['Total Consultations', str(total_dossiers)],
        ['Moyenne consultations/patient', f"{total_dossiers/total_patients:.2f}" if total_patients > 0 else "0"],
    ]
    
    overview_table = Table(overview_data, colWidths=[3*inch, 2*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 20))
    
    # ===== RÉPARTITION PAR ÂGE =====
    elements.append(Paragraph("📈 RÉPARTITION PAR TRANCHE D'ÂGE", heading_style))
    
    tranches_age = {
        '0-18 ans': 0,
        '19-35 ans': 0,
        '36-50 ans': 0,
        '51-65 ans': 0,
        '66+ ans': 0
    }
    
    for patient in Patient.objects.all():
        age = patient.age
        if age <= 18:
            tranches_age['0-18 ans'] += 1
        elif age <= 35:
            tranches_age['19-35 ans'] += 1
        elif age <= 50:
            tranches_age['36-50 ans'] += 1
        elif age <= 65:
            tranches_age['51-65 ans'] += 1
        else:
            tranches_age['66+ ans'] += 1
    
    age_data = [['Tranche d\'âge', 'Nombre de patients']]
    for tranche, count in tranches_age.items():
        age_data.append([tranche, str(count)])
    
    age_table = Table(age_data, colWidths=[2.5*inch, 2.5*inch])
    age_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(age_table)
    elements.append(Spacer(1, 20))
    
    # ===== GROUPES SANGUINS =====
    elements.append(Paragraph("🩸 RÉPARTITION PAR GROUPE SANGUIN", heading_style))
    
    groupes_sanguins = Patient.objects.exclude(groupe_sanguin='').values('groupe_sanguin').annotate(
        total=Count('id')
    ).order_by('-total')
    
    if groupes_sanguins:
        gs_data = [['Groupe Sanguin', 'Nombre']]
        for gs in groupes_sanguins:
            gs_data.append([gs['groupe_sanguin'], str(gs['total'])])
        
        gs_table = Table(gs_data, colWidths=[2.5*inch, 2.5*inch])
        gs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(gs_table)
    else:
        elements.append(Paragraph("Aucune donnée disponible", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== MALADIES CHRONIQUES =====
    elements.append(Paragraph("💊 MALADIES CHRONIQUES", heading_style))
    
    maladies = {
        'Diabète': Patient.objects.filter(diabete=True).count(),
        'Hypertension': Patient.objects.filter(hypertension=True).count(),
        'Asthme': Patient.objects.filter(asthme=True).count(),
        'Épilepsie': Patient.objects.filter(epilepsie=True).count(),
        'Drépanocytose': Patient.objects.filter(drepanocytose=True).count(),
        'VIH': Patient.objects.filter(vih=True).count(),
    }
    
    maladies_data = [['Maladie', 'Nombre de patients', 'Pourcentage']]
    for maladie, count in maladies.items():
        pourcentage = (count / total_patients * 100) if total_patients > 0 else 0
        maladies_data.append([maladie, str(count), f"{pourcentage:.1f}%"])
    
    maladies_table = Table(maladies_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    maladies_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a085')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(maladies_table)
    elements.append(Spacer(1, 20))
    
    # ===== CONSULTATIONS PAR URGENCE =====
    elements.append(Paragraph("🚨 CONSULTATIONS PAR NIVEAU D'URGENCE", heading_style))
    
    urgences = DossierMedical.objects.values('urgence').annotate(
        total=Count('id')
    ).order_by('-total')
    
    if urgences:
        urgence_labels = {
            'faible': 'Faible',
            'moyenne': 'Moyenne',
            'elevee': 'Élevée',
            'critique': 'Critique'
        }
        
        urgence_data = [['Niveau d\'urgence', 'Nombre', 'Pourcentage']]
        for urg in urgences:
            label = urgence_labels.get(urg['urgence'], urg['urgence'])
            pourcentage = (urg['total'] / total_dossiers * 100) if total_dossiers > 0 else 0
            urgence_data.append([label, str(urg['total']), f"{pourcentage:.1f}%"])
        
        urgence_table = Table(urgence_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        urgence_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(urgence_table)
    else:
        elements.append(Paragraph("Aucune consultation enregistrée", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # ===== TOP VILLES =====
    elements.append(Paragraph("🏙️ TOP 10 DES VILLES", heading_style))
    
    top_villes = Patient.objects.exclude(ville='').values('ville').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    if top_villes:
        villes_data = [['Ville', 'Nombre de patients']]
        for ville in top_villes:
            villes_data.append([ville['ville'], str(ville['total'])])
        
        villes_table = Table(villes_data, colWidths=[3*inch, 2*inch])
        villes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(villes_table)
    else:
        elements.append(Paragraph("Aucune donnée de ville disponible", styles['Normal']))
    
    # Pied de page
    elements.append(Spacer(1, 40))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph("_" * 100, footer_style))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"Rapport généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", footer_style))
    elements.append(Paragraph("Système de Suivi Médical - Confidentiel", footer_style))
    
    # Construire le PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer