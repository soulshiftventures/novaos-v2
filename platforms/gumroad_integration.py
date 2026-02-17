"""
Gumroad Integration - Digital product sales
"""

import os
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return safe_datetime_now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)


logger = logging.getLogger(__name__)


class GumroadIntegration:
    """
    Gumroad digital product platform integration

    Features:
    - Product management
    - Sales tracking
    - Revenue reporting
    - Customer data
    """

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Gumroad integration

        Args:
            access_token: Gumroad access token (or from GUMROAD_ACCESS_TOKEN env)
        """
        self.access_token = access_token or os.getenv('GUMROAD_ACCESS_TOKEN')
        self.base_url = "https://api.gumroad.com/v2"

        if not self.access_token:
            logger.warning("Gumroad access token not provided")

        logger.info("Gumroad integration initialized")

    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request to Gumroad"""
        if not self.access_token:
            logger.error("Gumroad access token not available")
            return None

        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Gumroad API error: {e}")
            return None

    def get_products(self) -> List[Dict]:
        """
        Get all products

        Returns:
            List of products
        """
        result = self._make_request("products")

        if result and result.get('success'):
            products = result.get('products', [])
            return [{
                'id': p.get('id'),
                'name': p.get('name'),
                'price': p.get('price', 0) / 100,  # Convert cents to dollars
                'sales_count': p.get('sales_count', 0),
                'url': p.get('short_url')
            } for p in products]

        return []

    def get_sales(
        self,
        after: Optional[str] = None,
        before: Optional[str] = None,
        page: int = 1
    ) -> Dict:
        """
        Get sales data

        Args:
            after: Filter sales after date (YYYY-MM-DD)
            before: Filter sales before date (YYYY-MM-DD)
            page: Page number

        Returns:
            Sales data
        """
        params = {'page': page}
        if after:
            params['after'] = after
        if before:
            params['before'] = before

        result = self._make_request("sales", data=params)

        if result and result.get('success'):
            sales = result.get('sales', [])

            total_revenue = 0.0
            sale_list = []

            for sale in sales:
                amount = sale.get('price', 0) / 100  # Convert cents to dollars
                total_revenue += amount

                sale_list.append({
                    'id': sale.get('id'),
                    'product_name': sale.get('product_name'),
                    'amount': amount,
                    'email': sale.get('email'),
                    'created_at': sale.get('created_at'),
                    'refunded': sale.get('refunded', False)
                })

            return {
                'total_revenue': total_revenue,
                'count': len(sale_list),
                'sales': sale_list
            }

        return {'total_revenue': 0.0, 'count': 0, 'sales': []}

    def get_revenue(
        self,
        days: int = 30
    ) -> Dict:
        """
        Get revenue for last N days

        Args:
            days: Number of days to look back

        Returns:
            Revenue summary
        """
        end_date = safe_datetime_now()
        start_date = end_date - timedelta(days=days)

        after = start_date.strftime('%Y-%m-%d')
        before = end_date.strftime('%Y-%m-%d')

        sales_data = self.get_sales(after=after, before=before)

        return {
            'total_revenue': sales_data['total_revenue'],
            'sales_count': sales_data['count'],
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            }
        }

    def get_subscribers(self, product_id: str) -> List[Dict]:
        """
        Get subscribers for a product

        Args:
            product_id: Product ID

        Returns:
            List of subscribers
        """
        result = self._make_request(f"products/{product_id}/subscribers")

        if result and result.get('success'):
            subscribers = result.get('subscribers', [])
            return [{
                'id': s.get('id'),
                'email': s.get('email'),
                'status': s.get('status'),
                'created_at': s.get('created_at')
            } for s in subscribers]

        return []

    def create_product(
        self,
        name: str,
        price: float,
        description: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create a new product

        Args:
            name: Product name
            price: Price in dollars
            description: Product description

        Returns:
            Created product or None
        """
        data = {
            'name': name,
            'price': int(price * 100),  # Convert to cents
        }

        if description:
            data['description'] = description

        result = self._make_request("products", method="POST", data=data)

        if result and result.get('success'):
            product = result.get('product', {})
            return {
                'id': product.get('id'),
                'name': product.get('name'),
                'price': product.get('price', 0) / 100,
                'url': product.get('short_url')
            }

        return None

    def verify_license(self, product_id: str, license_key: str) -> bool:
        """
        Verify a license key

        Args:
            product_id: Product ID
            license_key: License key to verify

        Returns:
            True if valid, False otherwise
        """
        result = self._make_request(
            f"licenses/verify",
            method="POST",
            data={
                'product_id': product_id,
                'license_key': license_key
            }
        )

        if result and result.get('success'):
            return result.get('purchase', {}).get('license_key') == license_key

        return False
