from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

import plotly.express as px
import pandas as pd
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import seaborn as sns

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Frame, PageBreak


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


def generate_short_report(scores_dic, overall_assesment="", filename="test.pdf"):
    """
    Generate a short report with graphics on the user interview

    Parameters:
        scores_dic (dictionary): A JSON object containing question scores and criteria.
        overall_assesment (string): Overall assessment of the interviewee
        filename (string): Output PDF filename
    """

    # Preprocess the scores_dic
    scores = []
    metrics = []

    for question in scores_dic["question_scores"]:
        question_scores = []
        for criterion in question["criteria_scores"]:
            question_scores.append(criterion["score"] / 100)
            if criterion["criterion"].title() not in metrics:
                metrics.append(criterion["criterion"].title())
        scores.append(question_scores)

    average_scores = []
    for i in range(len(scores[0])):
        total = 0
        for j in range(len(scores)):
            total += scores[j][i]
        average_scores.append(total / len(scores))

    # Generate Heatmap
    data_array = np.array(scores)

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        data_array, annot=True, fmt=".2f", cmap="coolwarm", annot_kws={"fontsize": 12}
    )
    plt.xticks(np.arange(len(metrics)) + 0.5, metrics)  # Adjust x-tick positions
    plt.yticks(
        np.arange(len(scores)) + 0.5, [f"Q{i+1}" for i in range(len(scores))]
    )  # Adjust y-tick positions
    plt.xlabel("")
    plt.ylabel("")
    plt.title("Heatmap of Applicant Answer Evaluations by Question", fontsize=14)
    plt.savefig("assets/Heatmap.png", transparent=True)
    plt.close()

    # Generate Radar Chart
    df = pd.DataFrame(dict(r=average_scores, theta=metrics))
    fig = px.line_polar(df, r="r", theta="theta", line_close=True, range_r=[0, 1])
    fig.update_traces(fill="toself")
    fig.write_image("assets/Radar_chart.png")

    # Create PDF
    pdf = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Title Page
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(200, 700, "Interview Evaluation Report")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(
        100,
        650,
        "This report provides an evaluation of the interview based on key metrics.",
    )
    pdf.drawString(
        100,
        630,
        "Generated visuals include a heatmap and a radar chart for better insights.",
    )
    pdf.showPage()

    # Heatmap Page
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(30, 750, "Heatmap of Applicant Answer Evaluations")
    pdf.drawImage("assets/Heatmap.png", 50, 450, width=500, height=250)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(
        30,
        400,
        "The heatmap shows the performance of the interviewee across different questions.",
    )
    pdf.drawString(
        30, 380, "Each cell represents a score for a criterion in a specific question."
    )
    pdf.showPage()

    # Radar Chart Page
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(30, 750, "Performance Evaluation Across Key Metrics")
    pdf.drawImage("assets/Radar_chart.png", 50, 450, width=500, height=250)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(
        30,
        400,
        "The radar chart highlights the average performance across key metrics.",
    )
    pdf.drawString(
        30, 380, "This helps in identifying strong and weak areas at a glance."
    )
    pdf.showPage()

    # # Overall Assessment Page
    # pdf.setFont("Helvetica-Bold", 16)
    # pdf.drawString(30, 750, "Overall Assessment")
    # pdf.setFont("Helvetica", 12)
    # text = Paragraph(overall_assesment, getSampleStyleSheet()["Normal"])
    # frame = Frame(30, 600, 540, 100, showBoundary=False)
    # frame.addFromList([text], pdf)

    pdf.save()
