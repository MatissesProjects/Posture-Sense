from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import os
import json

class ReportGenerator:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1, # Center
            textColor=colors.HexColor("#4F46E5") # Indigo 600
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor("#1E293B") # Slate 800
        ))

    def generate_assessment_report(self, history_data, sessions_data):
        """ Generates a professional ergonomic assessment PDF report. """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ergonomic_report_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []

        # Title
        story.append(Paragraph("Professional Ergonomic Assessment", self.styles['ReportTitle']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
        story.append(Spacer(1, 24))

        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        avg_score = sum(h['score'] for h in history_data) / len(history_data) if history_data else 0
        total_minutes = sum(s['total_ergonomic_minutes'] for s in sessions_data) if sessions_data else 0
        
        summary_text = f"""
            This report provides a comprehensive analysis of the user's postural habits and ergonomic risks 
            captured over the last {len(history_data)} data points across {len(sessions_data)} sessions. 
            The user maintained an average ergonomic score of <b>{avg_score:.1f}%</b>, with a total of 
            <b>{total_minutes} minutes</b> of high-compliance ergonomic work time.
        """
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 12))

        # Risk Assessment (RULA/REBA)
        story.append(Paragraph("Ergonomic Risk Assessment", self.styles['SectionHeader']))
        avg_rula = sum(h['rula_score'] for h in history_data) / len(history_data) if history_data else 0
        avg_reba = sum(h['reba_score'] for h in history_data) / len(history_data) if history_data else 0
        
        risk_data = [
            ["Framework", "Average Score", "Risk Level", "Action Required"],
            ["RULA (Upper Limb)", f"{avg_rula:.1f}", self._get_rula_risk(avg_rula), self._get_rula_action(avg_rula)],
            ["REBA (Entire Body)", f"{avg_reba:.1f}", self._get_reba_risk(avg_reba), self._get_reba_action(avg_reba)]
        ]
        
        t = Table(risk_data, colWidths=[120, 100, 120, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#475569")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t)
        story.append(Spacer(1, 24))

        # Detailed Metrics
        story.append(Paragraph("Detailed Postural Metrics", self.styles['SectionHeader']))
        avg_blink = sum(h['blink_rate'] for h in history_data) / len(history_data) if history_data else 0
        avg_dist = sum(h['distance_cm'] for h in history_data) / len(history_data) if history_data else 0
        
        metrics_text = f"""
            <b>Visual Load:</b> Average blink rate of {avg_blink:.1f} blinks/min. Values below 10 blinks/min 
            indicate high visual cognitive load and risk of Digital Eye Strain.<br/><br/>
            <b>Workspace Geometry:</b> Average viewing distance of {avg_dist:.1f} cm. Recommended distance 
            for ergonomic compliance is typically 50-70 cm.
        """
        story.append(Paragraph(metrics_text, self.styles['Normal']))
        
        # Recommendations
        story.append(Paragraph("Professional Recommendations", self.styles['SectionHeader']))
        recommendations = [
            "• Implement the 20-20-20 rule to reduce ciliary muscle fatigue.",
            "• Adjust monitor height to ensure a neutral cervical gaze angle (0-15 degrees downward).",
            "• Consider a lumbar support intervention if slouching trends persist in afternoon sessions.",
            "• Increase frequency of thoracic extension micro-breaks during long sitting periods."
        ]
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['Normal']))
            story.append(Spacer(1, 6))

        doc.build(story)
        return filepath

    def _get_rula_risk(self, score):
        if score <= 2: return "Negligible"
        if score <= 4: return "Low"
        if score <= 6: return "Medium"
        return "High"

    def _get_rula_action(self, score):
        if score <= 2: return "No action needed"
        if score <= 4: return "Further investigation"
        if score <= 6: return "Change soon"
        return "Change immediately"

    def _get_reba_risk(self, score):
        if score <= 1: return "Negligible"
        if score <= 3: return "Low"
        if score <= 7: return "Medium"
        if score <= 10: return "High"
        return "Very High"

    def _get_reba_action(self, score):
        if score <= 1: return "None"
        if score <= 3: return "May be necessary"
        if score <= 7: return "Necessary"
        if score <= 10: return "Necessary soon"
        return "Necessary now"
