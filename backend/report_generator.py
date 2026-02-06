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
    
    narrative = data.get('ai_insights_en', data.get('ai_insights', 'No analysis available.'))
    # Clean markdown
    narrative = narrative.replace('**', '') 
    
    elements.append(Paragraph(narrative, normal_style))
    elements.append(Spacer(1, 24))
    
    # --- Metrics Table ---
    elements.append(Paragraph("Key Financial Metrics (Monthly Avg)", subtitle_style))
    elements.append(Spacer(1, 12))
    
    metrics = data.get('metrics', {})
    table_data = [
        ['Metric', 'Value', 'Status'],
        ['Expense Ratio', f"{metrics.get('expense_ratio', 0)*100:.1f}%", 'High' if metrics.get('expense_ratio') > 0.8 else 'Healthy'],
        ['Debt Burden', f"{metrics.get('debt_burden_ratio', 0)*100:.1f}%", 'Critical' if metrics.get('debt_burden_ratio') > 0.3 else 'Stable'],
        ['Net Cash Flow', f"₹ {metrics.get('net_cash_flow', 0):,.2f}", 'Positive' if metrics.get('net_cash_flow') > 0 else 'Negative'],
        ['Creditworthiness*', f"{data.get('credit_score', 'N/A')}", 'Indicative'],
        ['Working Capital', f"₹ {metrics.get('working_capital', 0):,.2f}", ''],
    ]
    
    t = Table(table_data, colWidths=[200, 150, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(t)
    elements.append(Paragraph("* Creditworthiness Indicator (300–900 range, non-bureau, indicative only).", styles['Italic']))
    elements.append(Spacer(1, 24))

    # --- Charts (Generated via Matplotlib) ---
    # In a real deployed env, we might generate these on the fly. 
    # For now, we will skip image embedding to keep dependencies simple and fast, 
    # but the structure is ready.
    
    # --- Risk Factors ---
    if data.get('flags'):
        elements.append(Paragraph("Risk Assessment", subtitle_style))
        elements.append(Spacer(1, 12))
        for flag in data['flags']:
            elements.append(Paragraph(f"• <b>{flag['type']}</b> ({flag['severity']}): This requires immediate attention.", normal_style))
            
    elements.append(Spacer(1, 24))
    
    elements.append(Paragraph("Strategic Recommendations", subtitle_style))
    elements.append(Spacer(1, 12))
    
    recs = "1. Optimize inventory turnover.\n2. Negotiate longer payment terms."
    if score > 80:
        recs = "1. Reinvest surplus into growth channels.\n2. Consider short-term liquid investments."
    elif score < 50:
         recs = "1. Immediately cut non-essential OPEX.\n2. Freeze new hiring and debt."
         
    for line in recs.split('\n'):
        elements.append(Paragraph(line, normal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
