import smtplib
from email.mime.text import MIMEText

SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="bhaskarraju.0406@gmail.com"
SMTP_PASSWORD="nzks vrdz aisf ekla" 
TO_EMAIL="bhaskarraju.0406@gmail.com"

# SMTP_SERVER = "smtp.office365.com"
# SMTP_PORT = 587
# SMTP_USER = "outlook_1D80C5F15983B652@outlook.com"
# SMTP_PASSWORD = "nzks vrdz aisf ekla"  # App password

msg = MIMEText("Test email from Python outside Airflow")
msg["Subject"] = "SMTP Test"
msg["From"] = SMTP_USER
msg["To"] = SMTP_USER

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, SMTP_USER, msg.as_string())
    print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Failed to send email:", e)
