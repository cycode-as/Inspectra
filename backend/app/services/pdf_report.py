"""
PDF Report Generation Service

Service for generating professional PDF inspection reports.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os
from typing import Optional
from app.models.inspection import Inspection


class PDFReportService:
    """
    Service for generating PDF inspection reports.
    
    Creates professional reports with inspection details, images, and heatmaps.
    """
    
    def __init__(self, output_dir: str = "uploads/reports"):
        """
        Initialize PDF service.
        
        Args:
            output_dir: Directory to store generated PDF reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, inspection: Inspection) -> str:
        """
        Generate a PDF report for an inspection.
        
        Args:
            inspection: Inspection record
            
        Returns:
            Path to generated PDF file
        """
        # Generate unique filename
        filename = f"inspection_report_{inspection.id}_{int(datetime.now().timestamp())}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12
        )
        
        # Title
        title = Paragraph("INSPECTRA Inspection Report", title_style)
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Inspection details table
        details_data = [
            ["Inspection ID:", str(inspection.id)],
            ["Product ID:", str(inspection.product_id)],
            ["Status:", inspection.status],
            ["Anomaly Score:", f"{inspection.anomaly_score:.4f}"],
            ["Inference Time:", f"{inspection.inference_time_ms} ms"],
            ["Timestamp:", inspection.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")]
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#fafafa')])
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Original Image section
        if os.path.exists(inspection.image_path):
            story.append(Paragraph("Original Product Image", heading_style))
            try:
                img = Image(inspection.image_path, width=4*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 0.3*inch))
            except Exception as e:
                story.append(Paragraph(f"[Image unavailable: {str(e)}]", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # Heatmap section
        if inspection.heatmap_path and os.path.exists(inspection.heatmap_path):
            story.append(Paragraph("Defect Heatmap Visualization", heading_style))
            try:
                heatmap_img = Image(inspection.heatmap_path, width=4*inch, height=3*inch)
                story.append(heatmap_img)
                story.append(Spacer(1, 0.3*inch))
            except Exception as e:
                story.append(Paragraph(f"[Heatmap unavailable: {str(e)}]", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # Status interpretation
        story.append(Paragraph("Decision Summary", heading_style))
        status_text = self._get_status_interpretation(inspection.status, inspection.anomaly_score)
        story.append(Paragraph(status_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _get_status_interpretation(self, status: str, score: float) -> str:
        """
        Generate human-readable status interpretation.
        
        Args:
            status: Inspection status
            score: Anomaly score
            
        Returns:
            Interpretation text
        """
        interpretations = {
            "PASS": f"The product passed inspection with a low anomaly score of {score:.4f}. No significant defects detected.",
            "REVIEW": f"The product requires manual review. Anomaly score of {score:.4f} indicates potential concerns.",
            "REJECT": f"The product failed inspection with a high anomaly score of {score:.4f}. Significant defects detected."
        }
        return interpretations.get(status, "Status unknown.")
