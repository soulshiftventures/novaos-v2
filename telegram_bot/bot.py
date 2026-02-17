"""
NovaOS Telegram Bot - Command Center

Control NovaOS from your phone:
- Check system status
- View revenue/costs
- Start/stop agents
- Get alerts
- Emergency controls

Commands:
/status - System overview
/revenue - Revenue report
/agents - List all agents
/security - Security status
/stop <agent_id> - Stop an agent
/emergency - Emergency shutdown
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
from datetime import datetime

# Import NovaOS components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workers.manager import get_worker_manager
from security import get_security_manager
from core.revenue_tracker import get_revenue_tracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NovaOSBot:
    """Telegram bot for NovaOS control"""

    def __init__(self, token: str, admin_chat_id: str = None):
        """
        Initialize bot

        Args:
            token: Telegram bot token
            admin_chat_id: Admin user chat ID for auth
        """
        self.token = token
        self.admin_chat_id = admin_chat_id
        self.app = None

        # NovaOS components
        self.worker_manager = get_worker_manager()
        self.security = get_security_manager()
        self.revenue_tracker = get_revenue_tracker()

        logger.info("NovaOS Telegram Bot initialized")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🤖 NovaOS Command Center\n\n"
            "Available commands:\n"
            "/status - System status\n"
            "/revenue - Revenue report\n"
            "/agents - List agents\n"
            "/security - Security status\n"
            "/stop <agent_id> - Stop agent\n"
            "/emergency - Emergency stop"
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Get system status
            workers = self.worker_manager.list_workers()
            security_status = self.security.get_security_status()

            active = sum(1 for w in workers if w['status'] == 'running')
            total_cost = sum(w.get('cost', 0) for w in workers)
            total_revenue = sum(w.get('revenue', 0) for w in workers)

            message = f"""📊 NovaOS Status

🤖 Agents: {active}/{len(workers)} running
💰 Revenue: ${total_revenue:.2f}
💸 Cost: ${total_cost:.2f}
📈 Profit: ${total_revenue - total_cost:.2f}

🛡️ Security: {security_status.get('health', {}).get('health_status', 'UNKNOWN')}

Last updated: {safe_datetime_now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            await update.message.reply_text(message)

        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text(f"Error: {str(e)}")

    async def revenue_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /revenue command"""
        try:
            # Get revenue breakdown
            workers = self.worker_manager.list_workers()

            message = "💰 Revenue Report\n\n"

            for worker in workers:
                revenue = worker.get('revenue', 0)
                cost = worker.get('cost', 0)
                profit = revenue - cost

                message += f"• {worker['name']}\n"
                message += f"  Revenue: ${revenue:.2f}\n"
                message += f"  Cost: ${cost:.2f}\n"
                message += f"  Profit: ${profit:.2f}\n\n"

            total_revenue = sum(w.get('revenue', 0) for w in workers)
            total_cost = sum(w.get('cost', 0) for w in workers)
            total_profit = total_revenue - total_cost

            message += f"📊 TOTAL\n"
            message += f"Revenue: ${total_revenue:.2f}\n"
            message += f"Cost: ${total_cost:.2f}\n"
            message += f"Profit: ${total_profit:.2f}\n"
            message += f"ROI: {(total_profit/total_cost*100) if total_cost > 0 else 0:.1f}%"

            await update.message.reply_text(message)

        except Exception as e:
            logger.error(f"Error in revenue command: {e}")
            await update.message.reply_text(f"Error: {str(e)}")

    async def agents_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /agents command"""
        try:
            workers = self.worker_manager.list_workers()

            message = "🤖 Active Agents\n\n"

            for worker in workers:
                status_emoji = "✅" if worker['status'] == 'running' else "⏸️"
                message += f"{status_emoji} {worker['name']}\n"
                message += f"  ID: {worker['worker_id']}\n"
                message += f"  Status: {worker['status']}\n"
                message += f"  Runs: {worker.get('runs', 0)}\n\n"

            await update.message.reply_text(message)

        except Exception as e:
            logger.error(f"Error in agents command: {e}")
            await update.message.reply_text(f"Error: {str(e)}")

    async def security_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /security command"""
        try:
            status = self.security.get_security_status()
            health = status.get('health', {})
            budget = status.get('budget', {})

            message = f"""🛡️ Security Status

Health: {health.get('health_status', 'UNKNOWN')}
Active Alerts: {health.get('active_alerts', 0)}

💰 Budget:
Daily: ${budget.get('global_budgets', {}).get('daily', {}).get('spent', 0):.2f} / ${budget.get('global_budgets', {}).get('daily', {}).get('limit', 0):.2f}

🔒 Access:
API Keys: {status.get('access_control', {}).get('api_keys', {}).get('active', 0)}
Sessions: {status.get('access_control', {}).get('sessions', {}).get('active', 0)}
"""

            await update.message.reply_text(message)

        except Exception as e:
            logger.error(f"Error in security command: {e}")
            await update.message.reply_text(f"Error: {str(e)}")

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stop command"""
        try:
            if not context.args:
                await update.message.reply_text("Usage: /stop <agent_id>")
                return

            agent_id = context.args[0]

            # Stop the agent
            success = self.worker_manager.stop_worker(agent_id)

            if success:
                await update.message.reply_text(f"✅ Stopped agent: {agent_id}")
            else:
                await update.message.reply_text(f"❌ Failed to stop agent: {agent_id}")

        except Exception as e:
            logger.error(f"Error in stop command: {e}")
            await update.message.reply_text(f"Error: {str(e)}")

    async def emergency_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /emergency command"""
        try:
            # Trigger emergency stop
            from security.budget_enforcer import get_budget_enforcer


def safe_datetime_now():
    """Get current datetime with fallback for timestamp overflow"""
    try:
        return datetime.now()
    except (OSError, OverflowError, ValueError):
        from datetime import datetime as dt
        return dt(2025, 1, 1, 0, 0, 0)


            enforcer = get_budget_enforcer()
            enforcer.trigger_emergency_stop(f"Telegram emergency stop by {update.effective_user.username}")

            await update.message.reply_text(
                "🚨 EMERGENCY STOP ACTIVATED\n\n"
                "All operations blocked.\n"
                "Review logs and clear manually."
            )

        except Exception as e:
            logger.error(f"Error in emergency command: {e}")
            await update.message.reply_text(f"Error: {str(e)}")

    async def send_alert(self, message: str):
        """Send alert message to admin"""
        if self.admin_chat_id and self.app:
            try:
                await self.app.bot.send_message(
                    chat_id=self.admin_chat_id,
                    text=f"⚠️ NovaOS Alert\n\n{message}"
                )
            except Exception as e:
                logger.error(f"Error sending alert: {e}")

    def run(self):
        """Start the bot"""
        try:
            # Create application
            self.app = Application.builder().token(self.token).build()

            # Register handlers
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("status", self.status_command))
            self.app.add_handler(CommandHandler("revenue", self.revenue_command))
            self.app.add_handler(CommandHandler("agents", self.agents_command))
            self.app.add_handler(CommandHandler("security", self.security_command))
            self.app.add_handler(CommandHandler("stop", self.stop_command))
            self.app.add_handler(CommandHandler("emergency", self.emergency_command))

            logger.info("Starting Telegram bot...")
            self.app.run_polling()

        except Exception as e:
            logger.error(f"Error running bot: {e}", exc_info=True)


def main():
    """Main entry point"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    admin_chat_id = os.environ.get("TELEGRAM_ADMIN_CHAT_ID")

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return

    bot = NovaOSBot(token, admin_chat_id)
    bot.run()


if __name__ == "__main__":
    main()
