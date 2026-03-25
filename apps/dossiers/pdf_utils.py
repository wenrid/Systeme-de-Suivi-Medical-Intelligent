from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime

def generer_pdf_dossier(dossier):
    """Génère un PDF pour un dossier médical"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container pour les éléments
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#3498db'),
        spaceAfter=12,
        spaceBefore=12,
        borderWidth=1,
        borderColor=colors.HexColor('#3498db'),
        borderPadding=5,
        backColor=colors.HexColor('#ecf0f1')
    )
    
    normal_style = styles['Normal']
    
    # En-tête
    elements.append(Paragraph("DOSSIER MÉDICAL", title_style))
    elements.append(Spacer(1, 12))
    
    # Informations patient
    elements.append(Paragraph("INFORMATIONS PATIENT", heading_style))
    patient_data = [
        ['Code Patient:', dossier.patient.code_patient],
        ['Nom complet:', dossier.patient.nom_complet],
        ['Date de naissance:', dossier.patient.date_naissance.strftime('%d/%m/%Y')],
        ['Âge:', f"{dossier.patient.age} ans"],
        ['Sexe:', dossier.patient.get_sexe_display() or 'Non renseigné'],
        ['Groupe sanguin:', dossier.patient.groupe_sanguin or 'Non renseigné'],
        ['Téléphone:', dossier.patient.telephone or 'Non renseigné'],
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 20))
    
    # Informations consultation
    elements.append(Paragraph("CONSULTATION", heading_style))
    consult_data = [
        ['Date de consultation:', dossier.date_consultation.strftime('%d/%m/%Y à %H:%M')],
        ['Médecin:', f"Dr. {dossier.medecin.get_full_name()}"],
        ['Urgence:', dossier.get_urgence_display()],
        ['Statut:', dossier.get_statut_display()],
    ]
    
    consult_table = Table(consult_data, colWidths=[2*inch, 4*inch])
    consult_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(consult_table)
    elements.append(Spacer(1, 20))
    
    # Motif de consultation
    elements.append(Paragraph("MOTIF DE CONSULTATION", heading_style))
    elements.append(Paragraph(dossier.motif_consultation or "Non renseigné", normal_style))
    elements.append(Spacer(1, 12))
    
    # Symptômes
    if dossier.symptomes:
        elements.append(Paragraph("SYMPTÔMES", heading_style))
        elements.append(Paragraph(dossier.symptomes, normal_style))
        elements.append(Spacer(1, 12))
    
    # Examen clinique
    elements.append(Paragraph("EXAMEN CLINIQUE", heading_style))
    exam_data = []
    if dossier.temperature:
        exam_data.append(['Température:', f"{dossier.temperature}°C"])
    if dossier.tension_arterielle:
        exam_data.append(['Tension artérielle:', dossier.tension_arterielle])
    if dossier.poids:
        exam_data.append(['Poids:', f"{dossier.poids} kg"])
    if dossier.taille:
        exam_data.append(['Taille:', f"{dossier.taille} cm"])
    if dossier.imc:
        exam_data.append(['IMC:', str(dossier.imc)])
    
    if exam_data:
        exam_table = Table(exam_data, colWidths=[2*inch, 4*inch])
        exam_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(exam_table)
    else:
        elements.append(Paragraph("Aucune donnée d'examen clinique", normal_style))
    elements.append(Spacer(1, 20))
    
    # Diagnostic
    elements.append(Paragraph("DIAGNOSTIC", heading_style))
    elements.append(Paragraph(dossier.diagnostic, normal_style))
    elements.append(Spacer(1, 12))
    
    if dossier.diagnostic_differentiel:
        elements.append(Paragraph("DIAGNOSTIC DIFFÉRENTIEL", heading_style))
        elements.append(Paragraph(dossier.diagnostic_differentiel, normal_style))
        elements.append(Spacer(1, 12))
    
    # Examens complémentaires
    if dossier.examens_complementaires:
        elements.append(Paragraph("EXAMENS COMPLÉMENTAIRES", heading_style))
        elements.append(Paragraph(dossier.examens_complementaires, normal_style))
        elements.append(Spacer(1, 12))
    
    # Prescription
    if dossier.prescription:
        elements.append(Paragraph("PRESCRIPTION", heading_style))
        elements.append(Paragraph(dossier.prescription, normal_style))
        elements.append(Spacer(1, 12))
        
        if dossier.posologie:
            elements.append(Paragraph("POSOLOGIE", heading_style))
            elements.append(Paragraph(dossier.posologie, normal_style))
            elements.append(Spacer(1, 12))
    
    # Recommandations
    if dossier.recommandations:
        elements.append(Paragraph("RECOMMANDATIONS", heading_style))
        elements.append(Paragraph(dossier.recommandations, normal_style))
        elements.append(Spacer(1, 12))
    
    # Notes médicales
    if dossier.notes_medicales:
        elements.append(Paragraph("NOTES MÉDICALES", heading_style))
        elements.append(Paragraph(dossier.notes_medicales, normal_style))
        elements.append(Spacer(1, 12))
    
    # Prochain RDV
    if dossier.date_prochain_rdv:
        elements.append(Paragraph("SUIVI", heading_style))
        elements.append(Paragraph(f"Prochain rendez-vous : {dossier.date_prochain_rdv.strftime('%d/%m/%Y')}", normal_style))
    
    # Pied de page
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", footer_style))
    
    # Construire le PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer