"""
Stripe Integration - Payment processing
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StripeIntegration:
    """
    Stripe payment processing integration

    Features:
    - Payment processing
    - Subscription management
    - Revenue tracking
    - Customer management
    - Webhook handling
    """

    def __init__(self, api_key: Optional[str] = None, test_mode: bool = True):
        """
        Initialize Stripe integration

        Args:
            api_key: Stripe API key (or from STRIPE_API_KEY env)
            test_mode: Use test mode (default: True)
        """
        self.api_key = api_key or os.getenv('STRIPE_API_KEY')
        self.test_mode = test_mode

        if not self.api_key:
            logger.warning("Stripe API key not provided")

        try:
            import stripe
            self.stripe = stripe
            stripe.api_key = self.api_key
            logger.info("Stripe integration initialized")
        except ImportError:
            logger.error("stripe package not installed. Run: pip install stripe")
            self.stripe = None

    def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Create a payment intent

        Args:
            amount: Amount in dollars
            currency: Currency code
            metadata: Additional metadata

        Returns:
            Payment intent object or None
        """
        if not self.stripe:
            logger.error("Stripe not available")
            return None

        try:
            intent = self.stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                metadata=metadata or {}
            )

            logger.info(f"Created payment intent: {intent.id}")
            return {
                'id': intent.id,
                'amount': amount,
                'currency': currency,
                'status': intent.status,
                'client_secret': intent.client_secret
            }

        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            return None

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Create a subscription

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            metadata: Additional metadata

        Returns:
            Subscription object or None
        """
        if not self.stripe:
            return None

        try:
            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                metadata=metadata or {}
            )

            logger.info(f"Created subscription: {subscription.id}")
            return {
                'id': subscription.id,
                'customer': customer_id,
                'status': subscription.status,
                'current_period_end': subscription.current_period_end
            }

        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return None

    def get_revenue(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get revenue for date range

        Args:
            start_date: Start date (default: 30 days ago)
            end_date: End date (default: now)

        Returns:
            Revenue summary
        """
        if not self.stripe:
            return {'total': 0.0, 'count': 0, 'charges': []}

        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        try:
            charges = self.stripe.Charge.list(
                created={
                    'gte': int(start_date.timestamp()),
                    'lte': int(end_date.timestamp())
                },
                limit=100
            )

            total_revenue = 0.0
            charge_list = []

            for charge in charges.auto_paging_iter():
                if charge.paid and not charge.refunded:
                    amount = charge.amount / 100  # Convert from cents
                    total_revenue += amount

                    # Safe timestamp conversion with fallback
                    try:
                        created_dt = datetime.fromtimestamp(charge.created)
                    except (OSError, OverflowError, ValueError):
                        # Use current time as fallback for invalid timestamps
                        created_dt = datetime.now()

                    charge_list.append({
                        'id': charge.id,
                        'amount': amount,
                        'currency': charge.currency,
                        'created': created_dt,
                        'customer': charge.customer
                    })

            return {
                'total': total_revenue,
                'count': len(charge_list),
                'charges': charge_list,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Error fetching revenue: {e}")
            return {'total': 0.0, 'count': 0, 'charges': []}

    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Create a customer

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata

        Returns:
            Customer object or None
        """
        if not self.stripe:
            return None

        try:
            customer = self.stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )

            logger.info(f"Created customer: {customer.id}")
            return {
                'id': customer.id,
                'email': email,
                'name': name
            }

        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return None

    def handle_webhook(self, payload: str, sig_header: str, endpoint_secret: str) -> Optional[Dict]:
        """
        Handle Stripe webhook

        Args:
            payload: Request body
            sig_header: Stripe signature header
            endpoint_secret: Webhook endpoint secret

        Returns:
            Event object or None
        """
        if not self.stripe:
            return None

        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )

            logger.info(f"Received webhook: {event['type']}")
            return event

        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return None

    def get_balance(self) -> Dict:
        """
        Get Stripe balance

        Returns:
            Balance information
        """
        if not self.stripe:
            return {'available': 0.0, 'pending': 0.0}

        try:
            balance = self.stripe.Balance.retrieve()

            available = sum(b['amount'] for b in balance.available) / 100
            pending = sum(b['amount'] for b in balance.pending) / 100

            return {
                'available': available,
                'pending': pending,
                'currency': 'usd'
            }

        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {'available': 0.0, 'pending': 0.0}
