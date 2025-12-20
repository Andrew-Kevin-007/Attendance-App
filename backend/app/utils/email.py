"""Email utility for sending notifications"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Email configuration from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Smart Task AI")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None
) -> bool:
    """
    Send an email notification.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of the email
        text_body: Plain text content (optional, falls back to stripped HTML)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not EMAIL_ENABLED:
        print(f"[EMAIL DISABLED] Would send to {to_email}: {subject}")
        return True
    
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[EMAIL ERROR] SMTP credentials not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg["To"] = to_email
        
        # Add text and HTML parts
        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, to_email, msg.as_string())
        
        print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
        return True
    
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email: {e}")
        return False


def send_task_assignment_email(
    to_email: str,
    employee_name: str,
    task_title: str,
    task_description: str,
    deadline: Optional[str] = None,
    priority: str = "medium"
) -> bool:
    """Send email notification for task assignment"""
    subject = f"New Task Assigned: {task_title}"
    
    deadline_html = f"<p><strong>Deadline:</strong> {deadline}</p>" if deadline else ""
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
            .priority {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
            .priority-high {{ background: #fee2e2; color: #dc2626; }}
            .priority-medium {{ background: #fef3c7; color: #d97706; }}
            .priority-low {{ background: #d1fae5; color: #059669; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0;">📋 New Task Assigned</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{employee_name}</strong>,</p>
                <p>You have been assigned a new task:</p>
                <h2 style="color: #333;">{task_title}</h2>
                <p>{task_description}</p>
                {deadline_html}
                <p><strong>Priority:</strong> <span class="priority priority-{priority}">{priority.upper()}</span></p>
                <p style="margin-top: 20px;">Please log in to Smart Task AI to view and manage this task.</p>
            </div>
            <div class="footer">
                <p>This email was sent by Smart Task AI</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_body)


def send_task_status_update_email(
    to_email: str,
    employee_name: str,
    task_title: str,
    old_status: str,
    new_status: str
) -> bool:
    """Send email notification for task status update"""
    subject = f"Task Status Updated: {task_title}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
            .status-change {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
            .arrow {{ font-size: 24px; margin: 0 10px; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0;">🔄 Task Status Updated</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{employee_name}</strong>,</p>
                <p>A task you're involved with has been updated:</p>
                <h2 style="color: #333;">{task_title}</h2>
                <div class="status-change">
                    <strong>{old_status}</strong> 
                    <span class="arrow">→</span> 
                    <strong style="color: #059669;">{new_status}</strong>
                </div>
                <p>Please log in to Smart Task AI for more details.</p>
            </div>
            <div class="footer">
                <p>This email was sent by Smart Task AI</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_body)


def send_password_reset_email(
    to_email: str,
    reset_token: str,
    reset_url: str
) -> bool:
    """Send password reset email"""
    subject = "Password Reset Request - Smart Task AI"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            .warning {{ background: #fef3c7; padding: 10px; border-radius: 8px; color: #92400e; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0;">🔐 Password Reset</h1>
            </div>
            <div class="content">
                <p>You requested to reset your password for Smart Task AI.</p>
                <p>Click the button below to reset your password:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}?token={reset_token}" class="button">Reset Password</a>
                </p>
                <div class="warning">
                    <p><strong>⚠️ Important:</strong></p>
                    <ul>
                        <li>This link expires in 1 hour</li>
                        <li>If you didn't request this, please ignore this email</li>
                    </ul>
                </div>
            </div>
            <div class="footer">
                <p>This email was sent by Smart Task AI</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_body)


def send_attendance_reminder_email(
    to_email: str,
    employee_name: str
) -> bool:
    """Send attendance reminder email"""
    subject = "⏰ Daily Attendance Reminder - Smart Task AI"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0;">⏰ Attendance Reminder</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{employee_name}</strong>,</p>
                <p>This is a friendly reminder to mark your attendance for today.</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="#" class="button">Mark Attendance</a>
                </p>
                <p>Have a productive day!</p>
            </div>
            <div class="footer">
                <p>This email was sent by Smart Task AI</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_body)
