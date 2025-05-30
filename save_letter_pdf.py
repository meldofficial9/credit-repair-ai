from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def save_letter_as_pdf(text, filename="dispute_letter.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Courier", 12)
    y = 750
    for line in text.split("\n"):
        c.drawString(50, y, line)
        y -= 15
    c.save()