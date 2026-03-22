from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from datetime import date
import random
import qrcode

app = Flask(__name__)
app.secret_key = "studyhub123"

# ---------------- DATABASE INIT ----------------
def init_cert_db():
    conn = sqlite3.connect('certificates.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id TEXT,
            username TEXT,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_cert_db()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template("index.html")

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['username']
        return redirect('/dashboard')
    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template("dashboard.html", user=session['user'])
    return redirect('/login')

# ---------------- EXAM ----------------
@app.route('/exam')
def exam():
    return render_template("exam.html")

# ---------------- RESULT ----------------
@app.route('/result', methods=['POST'])
def result():
    score = 0

    if request.form.get('q1') == 'HTML':
        score += 1
    if request.form.get('q2') == 'CSS':
        score += 1

    if score == 2:
        return render_template("certificate.html", user=session['user'])

    return f"Your Score: {score}"

# ---------------- DOWNLOAD CERTIFICATE ----------------
@app.route('/download_certificate')
def download_certificate():
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch

    user = session.get('user', 'Student')

    cert_id = "CERT-" + str(random.randint(10000, 99999))
    today = str(date.today())

    # SAVE TO DATABASE
    conn = sqlite3.connect('certificates.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO certificates VALUES (?, ?, ?)", (cert_id, user, today))
    conn.commit()
    conn.close()

    # QR CODE
    verify_url = f"https://certificate-project-gv50.onrender.com"+ cert_id
    qr = qrcode.make(verify_url)
    qr.save("static/qr.png")

    file_name = f"{cert_id}.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=A4)

    # STYLES
    title = ParagraphStyle(name='t', fontSize=28, alignment=1, textColor=colors.darkblue)
    name_style = ParagraphStyle(name='n', fontSize=24, alignment=1, textColor=colors.darkred)
    normal = ParagraphStyle(name='no', fontSize=14, alignment=1)

    content = []

    # ---------------- LOGO ----------------
    try:
        logo = Image("static/logo.png", width=1.6*inch, height=1.6*inch)
        logo.hAlign = 'CENTER'
        content.append(logo)
        content.append(Spacer(1, 10))
    except:
        pass

    # TITLE
    content.append(Paragraph("🏆 Certificate of Completion", title))
    content.append(Spacer(1, 25))

    # TEXT
    content.append(Paragraph("This is proudly awarded to", normal))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>{user}</b>", name_style))
    content.append(Spacer(1, 25))

    content.append(Paragraph("For successfully completing HTML Course", normal))
    content.append(Spacer(1, 20))

    content.append(Paragraph(f"📅 Date: {today}", normal))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"🆔 Certificate ID: {cert_id}", normal))
    content.append(Spacer(1, 30))

    # SIGNATURE TABLE
    signature = Table([
        ["Instructor", "", "Authorized By"],
        ["(Study Hub Mentor)", "", "Study Hub"]
    ], colWidths=[2.5*inch, 1*inch, 2.5*inch])

    signature.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (0,0), 1, colors.black),
        ('LINEABOVE', (2,0), (2,0), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    content.append(signature)
    content.append(Spacer(1, 20))

    # QR CODE
    content.append(Image("static/qr.png", width=1.2*inch, height=1.2*inch))

    doc.build(content, onFirstPage=add_border)

    return send_file(file_name, as_attachment=True)

# ---------------- VERIFY CERTIFICATE ----------------
@app.route('/verify/<cert_id>')
def verify(cert_id):
    conn = sqlite3.connect('certificates.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM certificates WHERE id=?", (cert_id,))
    data = cursor.fetchone()

    conn.close()

    if data:
        return f"""
        <h2>✅ Certificate Verified</h2>
        <p>Name: {data[1]}</p>
        <p>Certificate ID: {data[0]}</p>
        <p>Date: {data[2]}</p>
        """
    else:
        return "<h2>❌ Invalid Certificate</h2>"

# ---------------- BORDER DESIGN ----------------
def add_border(canvas, doc):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4

    width, height = A4

    # BACKGROUND
    canvas.setFillColorRGB(0.95, 0.97, 1)
    canvas.rect(0, 0, width, height, fill=1)

    # WATERMARK
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 60)
    canvas.setFillColorRGB(0.8, 0.85, 0.95)
    canvas.translate(width/2, height/2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "STUDY HUB")
    canvas.restoreState()

    # BORDER
    canvas.setStrokeColor(colors.darkblue)
    canvas.setLineWidth(4)
    canvas.rect(30, 30, width-60, height-60)

    canvas.setLineWidth(2)
    canvas.rect(40, 40, width-80, height-80)

    # STAMP
    try:
        canvas.drawImage("static/stamp.png", width-180, 80, width=100, height=100, mask='auto')
    except:
        pass

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)