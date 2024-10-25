from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors


# Function to generate a PDF using ReportLab's built-in fonts (no local fonts)
def generate_pdf_report(file_path: str, html_content: str):
    # Create a PDF document
    doc = SimpleDocTemplate(file_path, pagesize=A4)

    # Use built-in fonts and styles from ReportLab
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]

    # Convert the HTML content to ReportLab-compatible Paragraphs
    story = []

    # Add a title with some spacing
    story.append(Paragraph("<b>Human Resource Interview Report</b>", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))  # Add space between the title and the content

    # Add the content wrapped in a table with borders
    data = []

    # Split the converted content by line to create Paragraph objects
    for line in html_content.split("\n"):
        if line.strip():
            data.append([Paragraph(line, style_normal)])

    # Create a Table to wrap the content with borders
    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.1,
                    colors.black,
                ),  # Add a border grid to the table
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),  # Align all text to the left
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),  # Vertically align all text to the top
                ("FONTSIZE", (0, 0), (-1, -1), 12),  # Set font size for the text
                ("LEFTPADDING", (0, 0), (-1, -1), 8),  # Add some padding to the left
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),  # Add some padding to the right
                ("TOPPADDING", (0, 0), (-1, -1), 6),  # Add padding to the top
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),  # Add padding to the bottom
            ]
        )
    )

    # Add the table to the story (content of the PDF)
    story.append(table)

    # Build the PDF document
    doc.build(story)
