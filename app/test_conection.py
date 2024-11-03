import smtplib

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'centrokainos@gmail.com'
SMTP_PASSWORD = 'dpjtssfkqlncdxay'  # Replace with your actual App Password

try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(SMTP_USER, SMTP_PASSWORD)
    print("SMTP connection successful.")
    server.quit()
except Exception as e:
    print(f"SMTP connection failed: {e}")
