"""
SendGrid Integration - Email automation
"""

import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SendGridIntegration:
    """
    SendGrid email platform integration

    Features:
    - Send transactional emails
    - Send marketing emails
    - Template management
    - Contact list management
    - Email analytics
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SendGrid integration

        Args:
            api_key: SendGrid API key (or from SENDGRID_API_KEY env)
        """
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')

        if not self.api_key:
            logger.warning("SendGrid API key not provided")

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            self.client = SendGridAPIClient(self.api_key) if self.api_key else None
            self.Mail = Mail
            logger.info("SendGrid integration initialized")
        except ImportError:
            logger.error("sendgrid package not installed. Run: pip install sendgrid")
            self.client = None
            self.Mail = None

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """
        Send a transactional email

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML email content
            from_email: Sender email (default: from SENDGRID_FROM_EMAIL)
            from_name: Sender name

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client or not self.Mail:
            logger.error("SendGrid not available")
            return False

        from_email = from_email or os.getenv('SENDGRID_FROM_EMAIL')
        if not from_email:
            logger.error("Sender email not provided")
            return False

        try:
            message = self.Mail(
                from_email=(from_email, from_name) if from_name else from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def send_template_email(
        self,
        to_email: str,
        template_id: str,
        template_data: Dict,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email using template

        Args:
            to_email: Recipient email
            template_id: SendGrid template ID
            template_data: Template data/variables
            from_email: Sender email

        Returns:
            True if sent successfully
        """
        if not self.client or not self.Mail:
            return False

        from_email = from_email or os.getenv('SENDGRID_FROM_EMAIL')
        if not from_email:
            logger.error("Sender email not provided")
            return False

        try:
            message = self.Mail(
                from_email=from_email,
                to_emails=to_email
            )

            message.template_id = template_id
            message.dynamic_template_data = template_data

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Template email sent to {to_email}")
                return True
            else:
                logger.error(f"Failed to send template email: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending template email: {e}")
            return False

    def send_bulk_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> Dict:
        """
        Send bulk emails

        Args:
            to_emails: List of recipient emails
            subject: Email subject
            html_content: HTML content
            from_email: Sender email

        Returns:
            Summary with success count
        """
        success_count = 0
        failed_count = 0

        for email in to_emails:
            if self.send_email(email, subject, html_content, from_email):
                success_count += 1
            else:
                failed_count += 1

        return {
            'total': len(to_emails),
            'success': success_count,
            'failed': failed_count
        }

    def add_contact(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        custom_fields: Optional[Dict] = None
    ) -> bool:
        """
        Add contact to list

        Args:
            email: Contact email
            first_name: First name
            last_name: Last name
            custom_fields: Custom field values

        Returns:
            True if added successfully
        """
        if not self.client:
            return False

        try:
            data = {
                'contacts': [{
                    'email': email,
                    'first_name': first_name or '',
                    'last_name': last_name or '',
                }]
            }

            if custom_fields:
                data['contacts'][0].update(custom_fields)

            response = self.client.client.marketing.contacts.put(
                request_body=data
            )

            if response.status_code in [200, 201, 202]:
                logger.info(f"Contact added: {email}")
                return True
            else:
                logger.error(f"Failed to add contact: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error adding contact: {e}")
            return False

    def get_stats(self, days: int = 7) -> Dict:
        """
        Get email statistics

        Args:
            days: Number of days to look back

        Returns:
            Email stats
        """
        if not self.client:
            return {
                'delivered': 0,
                'opens': 0,
                'clicks': 0,
                'bounces': 0
            }

        try:
            from datetime import datetime, timedelta

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            response = self.client.client.stats.get(
                query_params={
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                }
            )

            if response.status_code == 200:
                stats = response.body
                total_delivered = sum(stat.get('stats', [{}])[0].get('metrics', {}).get('delivered', 0) for stat in stats)
                total_opens = sum(stat.get('stats', [{}])[0].get('metrics', {}).get('opens', 0) for stat in stats)
                total_clicks = sum(stat.get('stats', [{}])[0].get('metrics', {}).get('clicks', 0) for stat in stats)
                total_bounces = sum(stat.get('stats', [{}])[0].get('metrics', {}).get('bounces', 0) for stat in stats)

                return {
                    'delivered': total_delivered,
                    'opens': total_opens,
                    'clicks': total_clicks,
                    'bounces': total_bounces,
                    'open_rate': (total_opens / total_delivered * 100) if total_delivered > 0 else 0,
                    'click_rate': (total_clicks / total_delivered * 100) if total_delivered > 0 else 0
                }

        except Exception as e:
            logger.error(f"Error fetching stats: {e}")

        return {
            'delivered': 0,
            'opens': 0,
            'clicks': 0,
            'bounces': 0
        }

    def create_list(self, name: str) -> Optional[str]:
        """
        Create a contact list

        Args:
            name: List name

        Returns:
            List ID or None
        """
        if not self.client:
            return None

        try:
            data = {
                'name': name
            }

            response = self.client.client.marketing.lists.post(
                request_body=data
            )

            if response.status_code in [200, 201]:
                list_id = response.body.get('id')
                logger.info(f"Created list: {name} ({list_id})")
                return list_id

        except Exception as e:
            logger.error(f"Error creating list: {e}")

        return None
