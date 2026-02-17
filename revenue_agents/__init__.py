"""
Revenue-Generating Agents for NovaOS V2

Three autonomous agents that generate revenue 24/7:
1. Digital Product Creator - Creates and sells products on Gumroad
2. Content Arbitrage - Fulfills content gigs on Upwork/Fiverr
3. Lead Generator - Finds and qualifies leads for services
"""

from .digital_product_creator import DigitalProductCreator
from .content_arbitrage import ContentArbitrage
from .lead_generator import LeadGenerator

__all__ = [
    'DigitalProductCreator',
    'ContentArbitrage',
    'LeadGenerator'
]

__version__ = '1.0.0'
