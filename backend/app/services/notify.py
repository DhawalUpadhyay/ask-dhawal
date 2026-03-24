import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv

# Resolve .env relative to this file's location so it works regardless of CWD.
# notify.py lives at backend/app/services/notify.py
# parents[3] is the project root (ask-dhawal/)
_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_ENV_PATH)


def _credentials():
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    return user, password


def _send_email(to: str, subject: str, body: str) -> None:
    user, password = _credentials()

    print(f"[notify] {user} {password} Attempting to send email to {to}")
    print(f"[notify] GMAIL_USER set: {bool(user)} | GMAIL_APP_PASSWORD set: {bool(password)}")

    if not user or not password:
        print("[notify] ERROR: GMAIL_USER or GMAIL_APP_PASSWORD is not set in environment. Email not sent.")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = user
        msg["To"] = to
        msg.attach(MIMEText(body, "plain"))

        print(f"[notify] Connecting to smtp.gmail.com:465 ...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user, password)
            server.sendmail(user, to, msg.as_string())

        print(f"[notify] Email sent successfully → {to} | Subject: {subject}")

    except smtplib.SMTPAuthenticationError:
        print("[notify] ERROR: Gmail authentication failed. Check GMAIL_APP_PASSWORD — it must be a Google App Password, not your regular Gmail password.")
    except smtplib.SMTPException as e:
        print(f"[notify] ERROR: SMTP error: {e}")
    except Exception as e:
        print(f"[notify] ERROR: Unexpected error sending email: {e}")


def _async(fn, *args) -> None:
    def run():
        try:
            fn(*args)
        except Exception as e:
            print(f"[notify] ERROR: Thread crashed: {e}")

    threading.Thread(target=run, daemon=True).start()


def send_otp_email(to_email: str, name: str, otp: str) -> None:
    # Synchronous — must complete before the HTTP response returns.
    # On serverless (Vercel), daemon threads are killed when the function returns,
    # so the OTP would never be delivered if sent in a background thread.
    print(f"[notify] Sending OTP email to {to_email}")
    subject = "Your verification code — Ask Dhawal"
    body = f"""Hi {name or 'there'},

Your one-time code to access Dhawal's AI resume chatbot is:

    {otp}

This code expires in 10 minutes.

— Ask Dhawal
"""
    _send_email(to_email, subject, body)


def send_alert_email(name: str, email: str) -> None:
    notify_email = os.getenv("NOTIFY_EMAIL") or os.getenv("GMAIL_USER")
    print(f"[notify] Queuing alert email to {notify_email}")
    subject = f"New recruiter session — {name or email}"
    body = f"""Someone just verified their email and started a conversation on your AI resume.

Name:  {name or 'Not provided'}
Email: {email}
"""
    _async(_send_email, notify_email, subject, body)


def send_summary_email(name: str, email: str, transcript: str, summary: str) -> None:
    notify_email = os.getenv("NOTIFY_EMAIL") or os.getenv("GMAIL_USER")
    print(f"[notify] Queuing summary email to {notify_email}")
    subject = f"Conversation summary — {name or email}"
    body = f"""Recruiter session ended (2 min inactivity).

Name:  {name or 'Not provided'}
Email: {email}

--- Summary ---
{summary}

--- Full Transcript ---
{transcript}
"""
    _async(_send_email, notify_email, subject, body)
