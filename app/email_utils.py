import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

MAILTRAP_HOST = os.getenv("MAILTRAP_HOST")
MAILTRAP_PORT = int(os.getenv("MAILTRAP_PORT", "587"))
MAILTRAP_USERNAME = os.getenv("MAILTRAP_USERNAME")
MAILTRAP_PASSWORD = os.getenv("MAILTRAP_PASSWORD")
FROM_EMAIL = os.getenv("MAILTRAP_FROM", "noreply@example.com")

def send_enrollment_email(email: str, course_title: str):
    msg = EmailMessage()
    msg["Subject"] = f"Enrollment Confirmation: {course_title}"
    msg["From"] = FROM_EMAIL
    msg["To"] = email
    msg.set_content(
        f"Hello,\n\nYou have been successfully enrolled in the course: '{course_title}'.\n\nBest regards,\nYour Team"
    )

    with smtplib.SMTP(MAILTRAP_HOST, MAILTRAP_PORT) as server:
        server.starttls()
        server.login(MAILTRAP_USERNAME, MAILTRAP_PASSWORD)
        server.send_message(msg)
