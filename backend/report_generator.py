from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
import matplotlib.pyplot as plt
from datetime import datetime

def generate_pdf_report(data):
    """
    Generates a professional investor-ready PDF report.
    Returns bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=1))
    
    # Custom Styles
    title_style = styles['Heading1']
    title_style.alignment = 1
    
    subtitle_style = styles['Heading2']
    subtitle_style.textColor = colors.HexColor('#4F46E5')
    
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    elements = []
    
    # --- Title Page ---
    elements.append(Paragraph("Financial Health & Investment Report", title_style))
    elements.append(Spacer(1, 12))
    
    date_str = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Generated on: {date_str}", styles['Normal']))
    elements.append(Spacer(1, 24))
    
    # --- Score Section ---
    score = data.get('score', 0)
    score_color = 'green' if score > 80 else 'orange' if score > 50 else 'red'
    
    elements.append(Paragraph(f"Overall Financial Health Score: <font color='{score_color}'><b>{score}/100</b></font>", subtitle_style))
    elements.append(Spacer(1, 12))
    
    # --- Structured Insights Section ---
    structured_insights = data.get('structured_insights')
    if structured_insights and isinstance(structured_insights, dict):
        elements.append(Paragraph("Executive Summary", subtitle_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(structured_insights.get('summary', ''), normal_style))
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph("Strategic Diagnosis", subtitle_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(structured_insights.get('diagnosis', ''), normal_style))
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph("Actionable Strategies", subtitle_style))
        elements.append(Spacer(1, 6))
        
        recs = structured_insights.get('recommendations', [])
        for rec in recs:
            # Bullet point simulation with paragraph
            elements.append(Paragraph(f"• {rec}", normal_style))
    
    else:
        # Legacy Fallback
        narrative = data.get('ai_insights_en', data.get('ai_insights', 'No analysis available.'))
        narrative = narrative.replace('**', '') 
        elements.append(Paragraph(narrative, normal_style))
    
    elements.append(Spacer(1, 24))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
