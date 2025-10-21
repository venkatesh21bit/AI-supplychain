"""
Email notification service for LOGI-BOT alerts and workflow updates.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_PORT', '587'))
        self.smtp_user = os.getenv('EMAIL_USER', '')
        self.smtp_password = os.getenv('EMAIL_PASSWORD', '')
        self.from_email = os.getenv('EMAIL_FROM', self.smtp_user)
        self.use_tls = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
        
    def send_low_stock_alert(self, product_name: str, current_stock: int, 
                           threshold: int, company_name: str, 
                           recipient_emails: List[str]) -> bool:
        """
        Send low stock alert email notification.
        
        Args:
            product_name: Name of the product
            current_stock: Current stock level
            threshold: Stock threshold level
            company_name: Company name
            recipient_emails: List of email addresses to send to
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.smtp_user or not recipient_emails:
            logger.warning("Email credentials not configured or no recipients")
            return False
            
        try:
            subject = f"🚨 CRITICAL: Low Stock Alert - {product_name}"
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .alert-box {{ 
                        background-color: #fee; 
                        border: 2px solid #f00; 
                        padding: 20px; 
                        margin: 20px 0; 
                        border-radius: 8px;
                    }}
                    .info-table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    .info-table th, .info-table td {{
                        border: 1px solid #ddd;
                        padding: 12px;
                        text-align: left;
                    }}
                    .info-table th {{
                        background-color: #f2f2f2;
                    }}
                    .critical {{ color: #d32f2f; font-weight: bold; }}
                    .logo {{ font-size: 24px; font-weight: bold; color: #1976d2; }}
                </style>
            </head>
            <body>
                <div class="logo">🤖 LOGI-BOT Alert System</div>
                
                <div class="alert-box">
                    <h2>⚠️ CRITICAL INVENTORY ALERT</h2>
                    <p><strong>Product:</strong> <span class="critical">{product_name}</span></p>
                    <p><strong>Company:</strong> {company_name}</p>
                    <p><strong>Alert Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <table class="info-table">
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Status</th>
                    </tr>
                    <tr>
                        <td>Current Stock</td>
                        <td class="critical">{current_stock} units</td>
                        <td class="critical">BELOW THRESHOLD</td>
                    </tr>
                    <tr>
                        <td>Minimum Threshold</td>
                        <td>{threshold} units</td>
                        <td>Expected Level</td>
                    </tr>
                    <tr>
                        <td>Shortage</td>
                        <td class="critical">{threshold - current_stock} units</td>
                        <td>IMMEDIATE ACTION REQUIRED</td>
                    </tr>
                </table>
                
                <h3>🚀 LOGI-BOT Autonomous Response Initiated:</h3>
                <ul>
                    <li>✅ Root cause analysis in progress</li>
                    <li>✅ Optimal replenishment strategy generation</li>
                    <li>✅ Supplier coordination and order automation</li>
                    <li>✅ Stakeholder notification and task assignment</li>
                </ul>
                
                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>Check the LOGI-BOT dashboard for real-time updates</li>
                    <li>Review automated replenishment recommendations</li>
                    <li>Approve or modify suggested supplier orders</li>
                    <li>Monitor execution progress and delivery timeline</li>
                </ol>
                
                <hr>
                <p><em>This alert was automatically generated by LOGI-BOT Autonomous Supply Chain Agent.</em></p>
                <p><em>Dashboard: <a href="http://localhost:3000/manufacturer/logibot-dashboard">LOGI-BOT Control Center</a></em></p>
            </body>
            </html>
            """
            
            text_body = f"""
LOGI-BOT CRITICAL ALERT: Low Stock Detected

Product: {product_name}
Company: {company_name}
Current Stock: {current_stock} units
Threshold: {threshold} units
Shortage: {threshold - current_stock} units

IMMEDIATE ACTION REQUIRED

LOGI-BOT autonomous response initiated:
- Root cause analysis in progress
- Optimal replenishment strategy generation
- Supplier coordination and order automation
- Stakeholder notification and task assignment

Check the LOGI-BOT dashboard for real-time updates: http://localhost:3000/manufacturer/logibot-dashboard

This alert was automatically generated by LOGI-BOT Autonomous Supply Chain Agent.
            """
            
            return self._send_email(recipient_emails, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending low stock alert email: {str(e)}")
            return False
    
    def send_workflow_completion_notification(self, execution_data: Dict[str, Any], 
                                           recipient_emails: List[str]) -> bool:
        """
        Send workflow completion notification email.
        
        Args:
            execution_data: Execution result data
            recipient_emails: List of email addresses
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.smtp_user or not recipient_emails:
            return False
            
        try:
            product_name = execution_data.get('product', 'Unknown Product')
            subject = f"✅ LOGI-BOT Workflow Completed - {product_name}"
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .success-box {{ 
                        background-color: #e8f5e8; 
                        border: 2px solid #4caf50; 
                        padding: 20px; 
                        margin: 20px 0; 
                        border-radius: 8px;
                    }}
                    .summary-table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    .summary-table th, .summary-table td {{
                        border: 1px solid #ddd;
                        padding: 12px;
                        text-align: left;
                    }}
                    .summary-table th {{
                        background-color: #f2f2f2;
                    }}
                    .success {{ color: #388e3c; font-weight: bold; }}
                    .logo {{ font-size: 24px; font-weight: bold; color: #1976d2; }}
                </style>
            </head>
            <body>
                <div class="logo">🤖 LOGI-BOT Alert System</div>
                
                <div class="success-box">
                    <h2>✅ WORKFLOW COMPLETED SUCCESSFULLY</h2>
                    <p><strong>Product:</strong> <span class="success">{product_name}</span></p>
                    <p><strong>Execution ID:</strong> {execution_data.get('execution_id', 'N/A')}</p>
                    <p><strong>Completion Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <h3>📊 Execution Summary:</h3>
                <table class="summary-table">
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Status</td><td class="success">{execution_data.get('status', 'COMPLETED')}</td></tr>
                    <tr><td>Steps Completed</td><td>{execution_data.get('steps_completed', '3/3')}</td></tr>
                    <tr><td>Root Cause</td><td>{execution_data.get('root_cause', 'Demand surge')}</td></tr>
                    <tr><td>Replenishment Quantity</td><td>{execution_data.get('replenishment_qty', 'N/A')} units</td></tr>
                </table>
                
                <h3>🎯 Actions Taken:</h3>
                <ul>
            """
            
            for action in execution_data.get('actions_taken', []):
                html_body += f"<li>✅ {action}</li>"
            
            html_body += """
                </ul>
                
                <p><strong>View complete details in the LOGI-BOT dashboard:</strong></p>
                <p><a href="http://localhost:3000/manufacturer/logibot-dashboard">LOGI-BOT Control Center</a></p>
                
                <hr>
                <p><em>This notification was automatically generated by LOGI-BOT Autonomous Supply Chain Agent.</em></p>
            </body>
            </html>
            """
            
            text_body = f"""
LOGI-BOT WORKFLOW COMPLETED

Product: {product_name}
Execution ID: {execution_data.get('execution_id', 'N/A')}
Status: {execution_data.get('status', 'COMPLETED')}
Steps Completed: {execution_data.get('steps_completed', '3/3')}

Root Cause: {execution_data.get('root_cause', 'Demand surge')}
Replenishment Quantity: {execution_data.get('replenishment_qty', 'N/A')} units

Actions Taken:
{chr(10).join(['- ' + action for action in execution_data.get('actions_taken', [])])}

View complete details: http://localhost:3000/manufacturer/logibot-dashboard

This notification was automatically generated by LOGI-BOT Autonomous Supply Chain Agent.
            """
            
            return self._send_email(recipient_emails, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending workflow completion email: {str(e)}")
            return False
    
    def _send_email(self, to_emails: List[str], subject: str, 
                   text_body: str, html_body: str = None) -> bool:
        """
        Send email using SMTP.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            text_body: Plain text email body
            html_body: HTML email body (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.smtp_user or not to_emails:
            logger.info(f"EMAIL NOTIFICATION (SIMULATED):")
            logger.info(f"To: {', '.join(to_emails)}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {text_body[:200]}...")
            return True  # Return True for simulation
            
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            
            # Add text version
            text_part = MIMEText(text_body, 'plain')
            msg.attach(text_part)
            
            # Add HTML version if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            # For demo purposes, log the email content even if sending fails
            logger.info(f"EMAIL NOTIFICATION (FAILED TO SEND):")
            logger.info(f"To: {', '.join(to_emails)}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {text_body[:200]}...")
            return False


# Global email service instance
email_service = EmailService()