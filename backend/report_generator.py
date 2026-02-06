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

    # --- Metrics Table ---
    elements.append(Paragraph("Key Financial Metrics (Monthly Avg)", subtitle_style))
    elements.append(Spacer(1, 12))
    
    metrics = data.get('metrics', {})
    table_data = [
        ['Metric', 'Value', 'Status'],
        ['Net Profit Margin', f"{metrics.get('net_profit_margin', 0):.1f}%", 'High' if metrics.get('net_profit_margin') > 15 else 'Low'],
        ['Expense Ratio', f"{metrics.get('expense_ratio', 0)*100:.1f}%", 'High' if metrics.get('expense_ratio') > 0.8 else 'Healthy'],
        ['Debt Burden', f"{metrics.get('debt_burden_ratio', 0)*100:.1f}%", 'Critical' if metrics.get('debt_burden_ratio') > 0.3 else 'Stable'],
        ['DSCR', f"{metrics.get('dscr', 0):.2f}", 'Risk' if metrics.get('dscr') < 1.2 else 'Safe'],
        ['Net Cash Flow', f"₹ {metrics.get('net_cash_flow', 0):,.2f}", 'Positive' if metrics.get('net_cash_flow') > 0 else 'Negative'],
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
    elements.append(Spacer(1, 24))

    # --- Charts (Generated via Matplotlib) ---
    charts_data = data.get('charts_data', [])
    if charts_data:
        elements.append(Paragraph("Financial Trends", subtitle_style))
        elements.append(Spacer(1, 12))
        
        # Helper to generate chart image bytes
        def generate_chart(chart_data, title):
            plt.figure(figsize=(6, 3))
            months = [d['Month'] for d in chart_data]
            
            if title == 'Revenue vs Expenses':
                plt.plot(months, [d['Revenue'] for d in chart_data], label='Revenue', color='green', marker='o')
                plt.plot(months, [d['Operating Expenses'] for d in chart_data], label='OpEx', color='red', marker='x')
                plt.legend()
            elif title == 'Net Cash Flow':
                colors_bar = ['green' if d['Net Cash Flow'] > 0 else 'red' for d in chart_data]
                plt.bar(months, [d['Net Cash Flow'] for d in chart_data], color=colors_bar)
            
            plt.title(title)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            plt.close()
            buf.seek(0)
            return buf

        try:
            # 1. Trend Chart
            img_buf = generate_chart(charts_data, 'Revenue vs Expenses')
            elements.append(Image(img_buf, width=400, height=200))
            elements.append(Spacer(1, 12))
            
            # 2. Cash Flow Chart
            img_buf2 = generate_chart(charts_data, 'Net Cash Flow')
            elements.append(Image(img_buf2, width=400, height=200))

        except Exception as e:
            print(f"Chart generation failed: {e}")
            elements.append(Paragraph("(Charts could not be generated)", normal_style))
            
    elements.append(Spacer(1, 24))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
