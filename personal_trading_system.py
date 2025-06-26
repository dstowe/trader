# personal_trading_system.py
"""
Personal Trading System with Webull Integration
- Only scans stocks in current positions + affordable stocks
- Long-only positions, no short selling
- No day trading rules
- Interactive confirmation for trades
"""

import sys
import os
import getpass
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_system import TradingSystem, StockLists
from trading_system.webull.webull import webull
from trading_system.database.models import DatabaseManager
from personal_config import PersonalTradingConfig

class PersonalTradingSystem:
    """Personal Trading System with Webull Integration and Position Management"""
    
    def __init__(self):
        self.config = PersonalTradingConfig()
        self.wb = webull()
        self.trading_system = TradingSystem()
        self.db = DatabaseManager(self.config.DATABASE_PATH)
        
        # Account data
        self.account_data = None
        self.positions = []
        self.settled_funds = 0.0
        self.account_value = 0.0
        self.is_logged_in = False
        
        # Trading restrictions
        self.today = datetime.now().date()
        
    def login_to_webull(self):
        """Interactive login to Webull"""
        print("🔐 Webull Login")
        print("=" * 30)
        
        username = input("Enter your Webull username/email: ")
        password = getpass.getpass("Enter your Webull password: ")
        
        print("Attempting to login...")
        
        try:
            login_result = self.wb.login(username, password)
            
            if 'accessToken' in login_result:
                print("✅ Login successful!")
                self.is_logged_in = True
                return True
            else:
                print("❌ Login failed:")
                if 'msg' in login_result:
                    print(f"   {login_result['msg']}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_account_info(self):
        """Get account information and positions"""
        if not self.is_logged_in:
            print("❌ Not logged in to Webull")
            return False
        
        try:
            print("📊 Fetching account information...")
            self.account_data = self.wb.get_account()
            
            # Extract settled funds
            for member in self.account_data['accountMembers']:
                if member['key'] == 'settledFunds':
                    self.settled_funds = float(member['value'])
                    break
            
            # Use netLiquidation as the true account size (includes cash + positions)
            if 'netLiquidation' in self.account_data:
                self.account_value = float(self.account_data['netLiquidation'])
            else:
                # Fallback to totalMarketValue if netLiquidation not available
                for member in self.account_data['accountMembers']:
                    if member['key'] == 'totalMarketValue':
                        self.account_value = float(member['value'])
                        break
            
            # Update config ACCOUNT_SIZE to use real account value
            self.config.ACCOUNT_SIZE = self.account_value
            
            # Extract positions
            self.positions = []
            total_position_value = 0
            for position in self.account_data['positions']:
                pos_data = {
                    'symbol': position['ticker']['symbol'],
                    'quantity': float(position['position']),
                    'cost_price': float(position['costPrice']),
                    'current_price': float(position['lastPrice']),
                    'market_value': float(position['marketValue']),
                    'unrealized_pnl': float(position['unrealizedProfitLoss']),
                    'pnl_rate': float(position['unrealizedProfitLossRate']),
                    'last_open_time': position['lastOpenTime']
                }
                self.positions.append(pos_data)
                total_position_value += pos_data['market_value']
            
            # Calculate cash balance
            cash_balance = self.account_value - total_position_value
            
            print(f"✅ Account loaded - Net Liquidation: ${self.account_value:.2f}")
            print(f"💰 Cash Balance: ${cash_balance:.2f}, Settled Funds: ${self.settled_funds:.2f}")
            print(f"📊 Positions Value: ${total_position_value:.2f} ({len(self.positions)} positions)")
            
            # Sync positions to database (including external positions)
            self.sync_positions_to_db()
            
            # Detect positions added outside the trading system
            self.detect_new_positions()
            
            return True
            
        except Exception as e:
            print(f"❌ Error fetching account info: {e}")
            return False
    
    def sync_positions_to_db(self):
        """Sync all current Webull positions to database for tracking"""
        if not self.positions:
            return
        
        try:
            # Create positions table if it doesn't exist
            with self.db as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS position_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sync_date TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        quantity REAL NOT NULL,
                        cost_price REAL NOT NULL,
                        current_price REAL NOT NULL,
                        market_value REAL NOT NULL,
                        unrealized_pnl REAL NOT NULL,
                        pnl_rate REAL NOT NULL,
                        last_open_time TEXT,
                        account_value REAL,
                        settled_funds REAL,
                        is_fractional INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(sync_date, symbol)
                    )
                ''')
                
                # Create fractional position tracking table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS fractional_positions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        quantity REAL NOT NULL,
                        entry_price REAL NOT NULL,
                        entry_date TEXT NOT NULL,
                        target_stop_loss REAL,
                        target_take_profit REAL,
                        status TEXT DEFAULT 'active',
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, entry_date)
                    )
                ''')
            
            sync_date = datetime.now().strftime('%Y-%m-%d')
            positions_synced = 0
            
            for pos in self.positions:
                try:
                    # Check if this is a fractional position
                    is_fractional = pos['quantity'] < 1.0 or pos['quantity'] != int(pos['quantity'])
                    
                    with self.db as conn:
                        conn.execute('''
                            INSERT OR REPLACE INTO position_history 
                            (sync_date, symbol, quantity, cost_price, current_price, 
                             market_value, unrealized_pnl, pnl_rate, last_open_time,
                             account_value, settled_funds, is_fractional)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            sync_date,
                            pos['symbol'],
                            pos['quantity'],
                            pos['cost_price'],
                            pos['current_price'],
                            pos['market_value'],
                            pos['unrealized_pnl'],
                            pos['pnl_rate'],
                            pos['last_open_time'],
                            self.account_value,
                            self.settled_funds,
                            1 if is_fractional else 0
                        ))
                        
                        # Track fractional positions separately for monitoring
                        if is_fractional:
                            entry_date = datetime.now().strftime('%Y-%m-%d')
                            stop_loss_price = pos['current_price'] * (1 - self.config.PERSONAL_STOP_LOSS)
                            take_profit_price = pos['current_price'] * (1 + self.config.PERSONAL_TAKE_PROFIT)
                            
                            conn.execute('''
                                INSERT OR REPLACE INTO fractional_positions 
                                (symbol, quantity, entry_price, entry_date, 
                                 target_stop_loss, target_take_profit, status, notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                pos['symbol'],
                                pos['quantity'],
                                pos['cost_price'],
                                entry_date,
                                stop_loss_price,
                                take_profit_price,
                                'active',
                                f"Auto-tracked fractional position from {entry_date}"
                            ))
                    
                    positions_synced += 1
                except Exception as e:
                    print(f"⚠️  Failed to sync {pos['symbol']}: {e}")
            
            print(f"📊 Synced {positions_synced} positions to database")
            
        except Exception as e:
            print(f"❌ Error syncing positions: {e}")
    
    def get_position_history(self, symbol=None, days=30):
        """Get position history from database"""
        try:
            with self.db as conn:
                if symbol:
                    query = '''
                        SELECT * FROM position_history 
                        WHERE symbol = ? AND sync_date >= date('now', '-{} days')
                        ORDER BY sync_date DESC
                    '''.format(days)
                    cursor = conn.execute(query, (symbol,))
                else:
                    query = '''
                        SELECT * FROM position_history 
                        WHERE sync_date >= date('now', '-{} days')
                        ORDER BY sync_date DESC, symbol
                    '''.format(days)
                    cursor = conn.execute(query)
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"❌ Error getting position history: {e}")
            return []
    
    def display_position_trends(self, symbol=None, days=7):
        """Display position P&L trends over time"""
        history = self.get_position_history(symbol, days)
        
        if not history:
            print(f"📭 No position history found")
            return
        
        print(f"\n📈 POSITION TRENDS (Last {days} days)")
        print("=" * 50)
        
        if symbol:
            # Show trend for specific symbol
            symbol_history = [h for h in history if h['symbol'] == symbol]
            if symbol_history:
                print(f"Symbol: {symbol}")
                for entry in symbol_history:
                    pnl_emoji = "🟢" if entry['unrealized_pnl'] >= 0 else "🔴"
                    print(f"  {entry['sync_date']}: {pnl_emoji} ${entry['unrealized_pnl']:+.2f} ({entry['pnl_rate']*100:+.1f}%)")
        else:
            # Show summary by date
            from collections import defaultdict
            by_date = defaultdict(list)
            for entry in history:
                by_date[entry['sync_date']].append(entry)
            
            for date in sorted(by_date.keys(), reverse=True):
                total_pnl = sum(entry['unrealized_pnl'] for entry in by_date[date])
                total_value = sum(entry['market_value'] for entry in by_date[date])
                pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
                
                print(f"{date}: {pnl_emoji} ${total_pnl:+.2f} (${total_value:.2f} total)")
                for entry in sorted(by_date[date], key=lambda x: x['unrealized_pnl'], reverse=True):
                    pos_emoji = "🟢" if entry['unrealized_pnl'] >= 0 else "🔴"
                    print(f"  {entry['symbol']:6s} {pos_emoji} ${entry['unrealized_pnl']:+6.2f}")
    
    def detect_new_positions(self):
        """Detect positions that were added outside of the trading system"""
        try:
            # Get yesterday's positions
            yesterday_history = self.get_position_history(days=2)
            yesterday_symbols = set()
            
            if yesterday_history:
                # Get the most recent sync date
                recent_date = max(entry['sync_date'] for entry in yesterday_history)
                yesterday_symbols = {
                    entry['symbol'] for entry in yesterday_history 
                    if entry['sync_date'] == recent_date
                }
            
            # Compare with current positions
            current_symbols = {pos['symbol'] for pos in self.positions}
            new_positions = current_symbols - yesterday_symbols
            closed_positions = yesterday_symbols - current_symbols
            
            if new_positions:
                print(f"\n🆕 NEW POSITIONS DETECTED:")
                for symbol in new_positions:
                    pos = next(p for p in self.positions if p['symbol'] == symbol)
                    print(f"  • {symbol}: {pos['quantity']} shares @ ${pos['cost_price']:.2f}")
                    print(f"    Added outside trading system")
            
            if closed_positions:
                print(f"\n📤 CLOSED POSITIONS:")
                for symbol in closed_positions:
                    print(f"  • {symbol}: Position closed")
            
            return new_positions, closed_positions
            
        except Exception as e:
            print(f"⚠️  Could not detect position changes: {e}")
            return set(), set()
    
    def get_position_symbols(self) -> List[str]:
        """Get list of symbols we currently have positions in"""
        return [pos['symbol'] for pos in self.positions]
    
    def get_affordable_stocks(self) -> List[str]:
        """Get stocks from database that we can afford with settled funds"""
        if self.settled_funds <= 0:
            return []
        
        affordable = []
        
        # Get all stocks from our trading universe
        all_stocks = list(set(
            StockLists.BOLLINGER_MEAN_REVERSION + 
            StockLists.GAP_TRADING
        ))
        
        for symbol in all_stocks:
            try:
                # Get latest price from database
                data = self.db.get_stock_data(symbol, 1)
                if not data.empty:
                    latest_price = data['Close'].iloc[-1]
                    if latest_price <= self.settled_funds:
                        affordable.append(symbol)
            except:
                continue
        
        return affordable
    
    def get_scan_universe(self) -> List[str]:
        """Get the universe of stocks to scan based on personal criteria"""
        position_symbols = self.get_position_symbols()
        
        # Use PersonalTradingConfig method for smarter universe selection
        scan_universe = self.config.get_personal_scan_universe(
            account_positions=position_symbols,
            settled_funds=self.settled_funds
        )
        
        # Add affordable stocks from database
        affordable_stocks = self.get_affordable_stocks()
        
        # Combine and deduplicate
        scan_universe.extend(affordable_stocks)
        scan_universe = list(set(scan_universe))
        
        return scan_universe
    
    def check_day_trade_restriction(self, symbol: str) -> bool:
        """Check if selling this position would violate day trade rules"""
        # Find the position
        position = None
        for pos in self.positions:
            if pos['symbol'] == symbol:
                position = pos
                break
        
        if not position:
            return False  # No position to sell
        
        try:
            # Parse the last open time
            last_open_str = position['last_open_time']
            # Format: "06/23/2025 13:50:39 UTC"
            last_open_date = datetime.strptime(last_open_str.split()[0], "%m/%d/%Y").date()
            
            # If we bought today, don't recommend selling
            if last_open_date == self.today:
                return True  # Would be day trade
                
        except:
            # If we can't parse the date, be conservative
            return True
        
        return False  # Safe to sell
    
    def get_overnight_positions(self):
        """Get positions that were held overnight (not opened today)"""
        overnight_positions = []
        
        for pos in self.positions:
            symbol = pos['symbol']
            # If it's NOT a day trade restriction, it means it was opened before today
            if not self.check_day_trade_restriction(symbol):
                overnight_positions.append(pos)
        
        return overnight_positions
    
    def get_existing_orders(self):
        """Check for existing stop-loss and take-profit orders"""
        try:
            current_orders = self.wb.get_current_orders()
            orders_by_symbol = {}
            
            for order in current_orders:
                if order.get('action') == 'SELL':
                    symbol = order['ticker']['symbol']
                    if symbol not in orders_by_symbol:
                        orders_by_symbol[symbol] = {'stop_orders': [], 'profit_orders': [], 'bracket_orders': []}
                    
                    # Classify order types
                    order_type = order.get('orderType', '')
                    combo_type = order.get('comboType', '')
                    
                    if combo_type == 'STOP_LOSS':
                        orders_by_symbol[symbol]['bracket_orders'].append(order)
                    elif combo_type == 'STOP_PROFIT':
                        orders_by_symbol[symbol]['bracket_orders'].append(order)
                    elif order_type in ['STP', 'STP LMT']:
                        orders_by_symbol[symbol]['stop_orders'].append(order)
                    elif order_type == 'LMT':
                        # Check if it's above current price (take-profit)
                        current_price = order.get('ticker', {}).get('close', 0)
                        limit_price = order.get('lmtPrice', 0)
                        if limit_price > current_price:
                            orders_by_symbol[symbol]['profit_orders'].append(order)
            
            return orders_by_symbol
            
        except Exception as e:
            print(f"⚠️  Could not fetch existing orders: {e}")
            return {}
    
    def get_existing_stop_orders(self):
        """Legacy method - check for existing stop-loss orders only"""
        all_orders = self.get_existing_orders()
        stop_orders = {}
        
        for symbol, orders in all_orders.items():
            if orders['stop_orders'] or orders['bracket_orders']:
                # Return the first stop order found
                stop_order = (orders['stop_orders'] + orders['bracket_orders'])[0]
                stop_orders[symbol] = stop_order
        
        return stop_orders
    
    def round_price_for_webull(self, price: float) -> float:
        """Round price according to Webull's increment requirements"""
        if price >= 1.0:
            # For prices >= $1.00: Round to penny increments (2 decimal places)
            return round(price, 2)
        else:
            # For prices < $1.00: Round to sub-penny increments (4 decimal places)
            return round(price, 4)
    
    def place_stop_order(self, symbol: str, quantity: int, stop_price: float) -> bool:
        """Place a protective stop-loss order"""
        try:
            # Round stop price to proper Webull increments
            rounded_stop_price = self.round_price_for_webull(stop_price)
            
            print(f"📋 Placing stop order: SELL {quantity} {symbol} @ ${rounded_stop_price:.2f}")
            
            # Place stop-market order (will sell at market when stop triggered)
            order_result = self.wb.place_order(
                stock=symbol,
                action='SELL',
                orderType='STP',  # Stop market order
                stpPrice=rounded_stop_price,  # Stop trigger price (properly rounded)
                quant=quantity,
                enforce='GTC',  # Good-till-canceled
                outsideRegularTradingHour=False  # Regular hours only
            )
            
            if 'success' in order_result and order_result['success']:
                print("✅ Protective stop order placed successfully!")
                print(f"Order ID: {order_result.get('orderId', 'N/A')}")
                return True
            else:
                print("❌ Stop order failed:")
                print(f"   {order_result.get('msg', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error placing stop order: {e}")
            return False
    
    def place_bracket_order(self, symbol: str, quantity: int, stop_price: float, profit_price: float) -> bool:
        """Place both stop-loss and take-profit orders using OTOCO bracket ordering with fallback"""
        try:
            # Round both prices to proper Webull increments
            rounded_stop_price = self.round_price_for_webull(stop_price)
            rounded_profit_price = self.round_price_for_webull(profit_price)
            
            print(f"📋 Attempting bracket order for {symbol}:")
            print(f"   Stop-Loss: SELL {quantity} @ ${rounded_stop_price:.2f}")
            print(f"   Take-Profit: SELL {quantity} @ ${rounded_profit_price:.2f}")
            
            # Try bracket order first
            order_result = self.wb.place_order_tp_sl(
                stock=symbol,
                stop_loss_price=rounded_stop_price,
                limit_profit_price=rounded_profit_price,
                quant=quantity,
                time_in_force='GTC'  # Good-till-canceled
            )

            # Check if bracket order succeeded
            if isinstance(order_result, dict) and order_result.get('success'):
                print("✅ Bracket order placed successfully!")
                print(f"   Stop & Profit orders are now active")
                print(f"   When one fills, the other will be automatically canceled")
                return True
            
            # Bracket order failed - try fallback to stop-loss only
            print("⚠️  Bracket order failed, falling back to stop-loss only...")
            if isinstance(order_result, dict):
                error_msg = order_result.get('msg', 'Unknown error')
                print(f"   Bracket error: {error_msg}")
            
            # Fallback: Place individual stop-loss order
            print(f"🔄 Placing fallback stop-loss order...")
            fallback_success = self.place_stop_order(symbol, quantity, rounded_stop_price)
            
            if fallback_success:
                print("✅ Fallback stop-loss order placed successfully!")
                print(f"   Note: No automatic take-profit (bracket order unavailable)")
                return True
            else:
                print("❌ Both bracket order and fallback stop-loss failed")
                return False
                
        except Exception as e:
            print(f"❌ Error in bracket order process: {e}")
            
            # Emergency fallback: Try basic stop order
            try:
                print("🚨 Emergency fallback: Attempting basic stop order...")
                rounded_stop_price = self.round_price_for_webull(stop_price)
                fallback_success = self.place_stop_order(symbol, quantity, rounded_stop_price)
                
                if fallback_success:
                    print("✅ Emergency stop-loss placed successfully!")
                    return True
                else:
                    print("❌ All protection order attempts failed")
                    return False
                    
            except Exception as fallback_error:
                print(f"❌ Emergency fallback also failed: {fallback_error}")
                return False
    
    def calculate_take_profit_price(self, current_price: float) -> float:
        """Calculate take-profit price using personal config"""
        return current_price * (1 + self.config.PERSONAL_TAKE_PROFIT)
    
    def cancel_stop_order(self, order_id: str) -> bool:
        """Cancel an existing stop order"""
        try:
            print(f"🗑️ Canceling stop order ID: {order_id}")
            
            cancel_result = self.wb.cancel_order(order_id)
            
            if 'success' in cancel_result and cancel_result['success']:
                print("✅ Stop order canceled successfully!")
                return True
            else:
                print("❌ Failed to cancel stop order:")
                print(f"   {cancel_result.get('msg', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error canceling stop order: {e}")
            return False
    
    def offer_trailing_stops(self, positions_with_stops):
        """Offer to raise stops on profitable positions (trailing stops)"""
        if not positions_with_stops:
            return
        
        print(f"\n📈 TRAILING STOP OPPORTUNITIES")
        print("=" * 50)
        
        trailing_candidates = []
        
        # Identify positions where we can raise the stop
        for pos, stop_order, *_ in positions_with_stops:
            symbol = pos['symbol']
            current_price = pos['current_price']
            unrealized_pnl = pos['unrealized_pnl']
            
            # Get current stop price
            current_stop_price = float(stop_order.get('auxPrice', stop_order.get('stpPrice', 0)))
            
            # Calculate new trailing stop price and round properly
            calculated_stop_price = current_price * (1 - self.config.PERSONAL_STOP_LOSS)
            new_stop_price = self.round_price_for_webull(calculated_stop_price)
            
            # Only offer if:
            # 1. Position is profitable (P&L > 0)
            # 2. New stop would be higher than current stop
            # 3. Difference is meaningful (at least $0.10)
            stop_improvement = new_stop_price - current_stop_price
            
            if unrealized_pnl > 0 and stop_improvement > 0.10:
                trailing_candidates.append({
                    'position': pos,
                    'stop_order': stop_order,
                    'current_stop_price': current_stop_price,
                    'new_stop_price': new_stop_price,
                    'improvement': stop_improvement
                })
        
        if not trailing_candidates:
            print("📭 No trailing stop opportunities found")
            print("   (Positions either not profitable enough or stops already optimal)")
            return
        
        print(f"Found {len(trailing_candidates)} positions that can benefit from trailing stops:")
        
        trailing_orders_updated = 0
        
        for candidate in trailing_candidates:
            pos = candidate['position']
            stop_order = candidate['stop_order']
            symbol = pos['symbol']
            current_price = pos['current_price']
            quantity = int(pos['quantity'])
            unrealized_pnl = pos['unrealized_pnl']
            current_stop_price = candidate['current_stop_price']
            new_stop_price = candidate['new_stop_price']
            improvement = candidate['improvement']
            
            # Calculate additional profit protection
            additional_protection = improvement * quantity
            
            print(f"\n📊 {symbol} Trailing Stop Analysis:")
            print(f"  Current Position: {quantity} shares @ ${current_price:.2f}")
            print(f"  Current P&L: ${unrealized_pnl:+.2f} 🟢")
            print(f"  Current Stop: ${current_stop_price:.2f}")
            print(f"  New Trailing Stop: ${new_stop_price:.2f} ({self.config.PERSONAL_STOP_LOSS:.1%} below current)")
            print(f"  ↗️  Raise stop by: ${improvement:.2f}")
            print(f"  💰 Additional profit protection: ${additional_protection:.2f}")
            
            # Get user confirmation
            choice = input(f"Raise stop for {symbol} to ${new_stop_price:.2f}? (y/n): ").lower().strip()
            
            if choice in ['y', 'yes']:
                # Cancel existing stop order first
                order_id = stop_order['orderId']
                if self.cancel_stop_order(order_id):
                    # Place new higher stop order
                    if self.place_stop_order(symbol, quantity, new_stop_price):
                        trailing_orders_updated += 1
                        print(f"✅ Trailing stop updated for {symbol}")
                    else:
                        print(f"❌ Failed to place new stop for {symbol}")
                        print("⚠️  Original stop was canceled - position is now unprotected!")
                else:
                    print(f"❌ Failed to cancel existing stop for {symbol}")
            else:
                print(f"⏭️  Kept existing stop for {symbol}")
        
        print(f"\n📋 Trailing Stops Summary: {trailing_orders_updated} stops raised")
        if trailing_orders_updated > 0:
            print("📱 Check your Webull app for updated stop orders")
            print("💡 Trailing stops help lock in profits as positions move in your favor")
    
    def get_fractional_positions(self):
        """Get all active fractional positions from database"""
        try:
            with self.db as conn:
                cursor = conn.execute('''
                    SELECT * FROM fractional_positions 
                    WHERE status = 'active'
                    ORDER BY symbol
                ''')
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Error getting fractional positions: {e}")
            return []
    
    def check_fractional_exit_levels(self):
        """Check if fractional positions have hit their exit levels"""
        fractional_positions = self.get_fractional_positions()
        if not fractional_positions:
            return []
        
        exit_alerts = []
        
        for frac_pos in fractional_positions:
            symbol = frac_pos['symbol']
            
            # Find current position data
            current_pos = None
            for pos in self.positions:
                if pos['symbol'] == symbol:
                    current_pos = pos
                    break
            
            if not current_pos:
                # Position no longer exists - mark as closed
                try:
                    with self.db as conn:
                        conn.execute('''
                            UPDATE fractional_positions 
                            SET status = 'closed', updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        ''', (frac_pos['id'],))
                    print(f"📤 Fractional position {symbol} marked as closed (no longer in account)")
                except:
                    pass
                continue
            
            current_price = current_pos['current_price']
            target_stop_loss = frac_pos['target_stop_loss']
            target_take_profit = frac_pos['target_take_profit']
            
            # Check if stop loss or take profit levels are hit
            stop_loss_hit = current_price <= target_stop_loss
            take_profit_hit = current_price >= target_take_profit
            
            if stop_loss_hit or take_profit_hit:
                exit_alerts.append({
                    'fractional_position': frac_pos,
                    'current_position': current_pos,
                    'stop_loss_hit': stop_loss_hit,
                    'take_profit_hit': take_profit_hit,
                    'current_price': current_price
                })
        
        return exit_alerts
    
    def place_fractional_sell_order(self, symbol: str, quantity: float, price: float) -> bool:
        """Place a fractional sell order"""
        try:
            print(f"📋 Placing fractional sell order: SELL {quantity:.4f} {symbol} @ ${price:.2f}")
            
            # Place limit order for fractional shares
            order_result = self.wb.place_order(
                stock=symbol,
                price=price,
                action='SELL',
                orderType='LMT',  # Limit order
                enforce='DAY',    # Day order
                quant=quantity,   # Fractional quantity
                outsideRegularTradingHour=False
            )
            
            if 'success' in order_result and order_result['success']:
                print("✅ Fractional sell order placed successfully!")
                print(f"Order ID: {order_result.get('orderId', 'N/A')}")
                return True
            else:
                print("❌ Fractional sell order failed:")
                print(f"   {order_result.get('msg', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error placing fractional sell order: {e}")
            return False
    
    def offer_fractional_monitoring(self):
        """Check and offer actions for fractional positions"""
        exit_alerts = self.check_fractional_exit_levels()
        
        if not exit_alerts:
            fractional_positions = self.get_fractional_positions()
            if fractional_positions:
                print(f"\n📊 FRACTIONAL POSITION MONITORING")
                print("=" * 50)
                print(f"✅ {len(fractional_positions)} fractional positions monitored - no exit levels hit")
                for frac_pos in fractional_positions:
                    symbol = frac_pos['symbol']
                    current_pos = next((p for p in self.positions if p['symbol'] == symbol), None)
                    if current_pos:
                        current_price = current_pos['current_price']
                        stop_distance = ((current_price - frac_pos['target_stop_loss']) / current_price) * 100
                        profit_distance = ((frac_pos['target_take_profit'] - current_price) / current_price) * 100
                        pnl_color = "🟢" if current_pos['unrealized_pnl'] >= 0 else "🔴"
                        print(f"  {symbol}: ${current_price:.2f} | Stop: {stop_distance:+.1f}% | Profit: {profit_distance:+.1f}% | P&L: {pnl_color} ${current_pos['unrealized_pnl']:+.2f}")
            return
        
        print(f"\n🚨 FRACTIONAL POSITION ALERTS")
        print("=" * 50)
        print(f"Found {len(exit_alerts)} fractional positions at exit levels!")
        
        orders_placed = 0
        
        for alert in exit_alerts:
            frac_pos = alert['fractional_position']
            current_pos = alert['current_position']
            symbol = frac_pos['symbol']
            current_price = alert['current_price']
            quantity = current_pos['quantity']
            
            # Determine exit reason
            if alert['stop_loss_hit']:
                exit_reason = "STOP LOSS HIT"
                target_price = frac_pos['target_stop_loss']
                exit_emoji = "🔴"
            else:
                exit_reason = "TAKE PROFIT HIT"
                target_price = frac_pos['target_take_profit']
                exit_emoji = "🟢"
            
            # Calculate P&L
            entry_price = frac_pos['entry_price']
            current_pnl = (current_price - entry_price) * quantity
            
            print(f"\n{exit_emoji} {symbol} - {exit_reason}")
            print(f"  Entry: ${entry_price:.2f} | Current: ${current_price:.2f} | Target: ${target_price:.2f}")
            print(f"  Quantity: {quantity:.4f} shares | P&L: ${current_pnl:+.2f}")
            print(f"  Entry Date: {frac_pos['entry_date']}")
            
            # Offer to place sell order
            choice = input(f"Place fractional sell order for {symbol}? (y/n): ").lower().strip()
            
            if choice in ['y', 'yes']:
                # Use current market price for better execution
                sell_price = self.round_price_for_webull(current_price)
                
                if self.place_fractional_sell_order(symbol, quantity, sell_price):
                    # Mark position as pending closure
                    try:
                        with self.db as conn:
                            conn.execute('''
                                UPDATE fractional_positions 
                                SET status = 'pending_close', 
                                    notes = ?, 
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE id = ?
                            ''', (f"Sell order placed at ${sell_price:.2f} - {exit_reason}", frac_pos['id']))
                        orders_placed += 1
                        print(f"✅ Fractional sell order placed for {symbol}")
                    except Exception as e:
                        print(f"⚠️  Could not update fractional position status: {e}")
                else:
                    print(f"❌ Failed to place fractional sell order for {symbol}")
            else:
                print(f"⏭️  Skipped {symbol}")
        
        print(f"\n📋 Fractional Position Summary: {orders_placed} sell orders placed")
        if orders_placed > 0:
            print("📱 Check your Webull app for fractional order status")
            print("💡 Fractional orders may take longer to fill than whole share orders")
    
    def offer_protective_stops(self, overnight_positions):
        """Offer to place protective stops and take-profits for overnight positions"""
        if not overnight_positions:
            return
        
        print(f"\n🛡️ PROTECTIVE ORDER MANAGEMENT")
        print("=" * 50)
        
        # Filter out fractional positions (they can't use bracket orders)
        whole_share_positions = []
        fractional_positions_found = []
        
        for pos in overnight_positions:
            is_fractional = pos['quantity'] < 1.0 or pos['quantity'] != int(pos['quantity'])
            if is_fractional:
                fractional_positions_found.append(pos)
            else:
                whole_share_positions.append(pos)
        
        if fractional_positions_found:
            print(f"📊 Note: {len(fractional_positions_found)} fractional positions detected")
            print("   Fractional positions will be monitored separately (no bracket orders available)")
            for pos in fractional_positions_found:
                print(f"   • {pos['symbol']}: {pos['quantity']:.4f} shares")
        
        if not whole_share_positions:
            print("ℹ️  No whole-share positions available for bracket orders")
            return
        
        # Get all existing orders
        all_existing_orders = self.get_existing_orders()
        
        positions_needing_orders = []
        positions_with_orders = []
        
        for pos in whole_share_positions:
            symbol = pos['symbol']
            if symbol in all_existing_orders:
                # Has some kind of order
                orders = all_existing_orders[symbol]
                has_stop = bool(orders['stop_orders'] or orders['bracket_orders'])
                has_profit = bool(orders['profit_orders'] or orders['bracket_orders'])
                
                if has_stop:
                    # Use the first stop order for trailing stops functionality
                    stop_order = (orders['stop_orders'] + orders['bracket_orders'])[0]
                    positions_with_orders.append((pos, stop_order, 'has_stop'))
                else:
                    positions_needing_orders.append(pos)
            else:
                positions_needing_orders.append(pos)
        
        # Show positions that already have orders
        if positions_with_orders:
            print(f"✅ Positions with existing orders:")
            for pos, order, order_type in positions_with_orders:
                symbol = pos['symbol']
                orders = all_existing_orders.get(symbol, {})
                
                # Display order status
                has_stop = bool(orders.get('stop_orders', []) or orders.get('bracket_orders', []))
                has_profit = bool(orders.get('profit_orders', []) or orders.get('bracket_orders', []))
                
                order_status = []
                if has_stop:
                    order_status.append("Stop")
                if has_profit:
                    order_status.append("Profit")
                
                pnl_emoji = "🟢" if pos['unrealized_pnl'] >= 0 else "🔴"
                print(f"  {symbol:6s}: {'/'.join(order_status)} orders | P&L: {pnl_emoji} ${pos['unrealized_pnl']:+.2f}")
        
        # Offer trailing stops for profitable positions with existing stops
        if positions_with_orders:
            self.offer_trailing_stops(positions_with_orders)
        
        # Offer bracket orders for positions without protection
        if not positions_needing_orders:
            if not positions_with_orders:
                print("✅ All overnight positions already have protective orders!")
            return
        
        print(f"\n🎯 Positions needing protective orders:")
        bracket_orders_placed = 0
        
        for pos in positions_needing_orders:
            symbol = pos['symbol']
            current_price = pos['current_price']
            quantity = int(pos['quantity'])
            cost_price = pos['cost_price']
            unrealized_pnl = pos['unrealized_pnl']
            
            # Calculate both stop and profit prices using personal config
            stop_price = current_price * (1 - self.config.PERSONAL_STOP_LOSS)
            profit_price = self.calculate_take_profit_price(current_price)
            
            # Calculate potential outcomes
            potential_loss = (current_price - stop_price) * quantity
            potential_gain = (profit_price - current_price) * quantity
            risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else 0
            
            # Show enhanced position details with bracket order info
            print(f"\n📊 {symbol} Bracket Order Analysis:")
            print(f"  Current Position: {quantity} shares @ ${current_price:.2f}")
            print(f"  Cost Basis: ${cost_price:.2f}")
            print(f"  Current P&L: ${unrealized_pnl:+.2f}")
            print(f"  ────────────────────────────────────────")
            print(f"  📉 Stop-Loss: ${stop_price:.2f} ({self.config.PERSONAL_STOP_LOSS:.1%} below)")
            print(f"  📈 Take-Profit: ${profit_price:.2f} ({self.config.PERSONAL_TAKE_PROFIT:.1%} above)")
            print(f"  ────────────────────────────────────────")
            print(f"  💸 Max Loss: ${potential_loss:.2f}")
            print(f"  💰 Max Gain: ${potential_gain:.2f}")
            print(f"  ⚖️  Risk/Reward: {risk_reward_ratio:.1f}:1")
            
            # Offer bracket order (recommended) or individual stop order
            print(f"\n🎯 Order Options for {symbol}:")
            print(f"  [1] Bracket Order (Stop + Profit) - RECOMMENDED")
            print(f"  [2] Stop-Loss Only")
            print(f"  [3] Skip")
            
            choice = input(f"Choose option (1-3): ").strip()
            
            if choice == '1':
                if self.place_bracket_order(symbol, quantity, stop_price, profit_price):
                    bracket_orders_placed += 1
                    print(f"✅ Bracket order placed for {symbol}")
                else:
                    print(f"❌ Failed to place bracket order for {symbol}")
                    
            elif choice == '2':
                if self.place_stop_order(symbol, quantity, stop_price):
                    bracket_orders_placed += 1
                    print(f"✅ Stop-loss order placed for {symbol}")
                else:
                    print(f"❌ Failed to place stop order for {symbol}")
                    
            else:
                print(f"⏭️  Skipped {symbol}")
        
        print(f"\n📋 Summary: {bracket_orders_placed} protective orders placed")
        if bracket_orders_placed > 0:
            print("📱 Check your Webull app to monitor orders")
            print("💡 Bracket orders provide both downside protection and upside targets")
    
    def filter_signals_by_rules(self, signals: List[Dict]) -> List[Dict]:
        """Filter signals based on personal trading rules"""
        filtered_signals = []
        
        for signal in signals:
            symbol = signal['symbol']
            signal_type = signal['signal_type']
            
            # Use PersonalTradingConfig to check if signal should be executed
            should_execute, reason = self.config.should_execute_signal(
                signal, 
                current_positions=self.get_position_symbols(),
                account_value=self.account_value
            )
            
            if not should_execute:
                print(f"⚠️  Skipping {signal_type} {symbol} - {reason}")
                continue
            
            # Additional personal rules
            if signal_type == 'SELL':
                # Only allow sells if we have a position in this stock
                if symbol not in self.get_position_symbols():
                    continue
                
                # No day trades - don't sell if bought today
                if self.check_day_trade_restriction(symbol):
                    print(f"⚠️  Skipping SELL signal for {symbol} - would be day trade")
                    continue
            
            elif signal_type == 'BUY':
                # Only buy if we can afford it with position sizing
                position_info = self.config.get_position_size(
                    signal['price'], 
                    self.account_value, 
                    self.settled_funds
                )
                
                if position_info['type'] == 'none':
                    print(f"⚠️  Skipping BUY signal for {symbol} - position would be too small")
                    continue
                
                # Store calculated position info in signal for later use
                signal['calculated_position_info'] = position_info
            
            filtered_signals.append(signal)
        
        return filtered_signals
    
    def display_positions(self):
        """Display current positions with account allocation"""
        print(f"\n💼 ACCOUNT OVERVIEW")
        print("=" * 60)
        print(f"🏦 Net Liquidation: ${self.account_value:.2f}")
        print(f"💰 Settled Funds: ${self.settled_funds:.2f}")
        
        if not self.positions:
            cash_pct = (self.settled_funds / self.account_value * 100) if self.account_value > 0 else 0
            print(f"📭 No positions - {cash_pct:.1f}% cash")
            return
        
        print(f"📊 Positions: {len(self.positions)}/{self.config.MAX_POSITIONS_TOTAL}")
        print("=" * 60)
        
        total_position_value = 0
        total_pnl = 0
        fractional_count = 0
        
        # Sort positions by market value (largest first)
        sorted_positions = sorted(self.positions, key=lambda x: x['market_value'], reverse=True)
        
        for pos in sorted_positions:
            pnl_pct = pos['pnl_rate'] * 100
            pnl_color = "🟢" if pos['unrealized_pnl'] >= 0 else "🔴"
            
            # Check if fractional
            is_fractional = pos['quantity'] < 1.0 or pos['quantity'] != int(pos['quantity'])
            if is_fractional:
                fractional_count += 1
            
            # Calculate position as % of account
            pos_pct_of_account = (pos['market_value'] / self.account_value * 100) if self.account_value > 0 else 0
            
            # Display fractional shares properly
            if is_fractional:
                quantity_display = f"{pos['quantity']:>8.4f}"
                fractional_indicator = "📊"
            else:
                quantity_display = f"{pos['quantity']:>8.0f}"
                fractional_indicator = ""
            
            print(f"{pos['symbol']:6s} | {quantity_display} shares | "
                  f"${pos['current_price']:>7.2f} | "
                  f"${pos['market_value']:>8.2f} ({pos_pct_of_account:>4.1f}%) | "
                  f"{pnl_color} ${pos['unrealized_pnl']:>+7.2f} ({pnl_pct:>+5.1f}%) {fractional_indicator}")
            
            total_position_value += pos['market_value']
            total_pnl += pos['unrealized_pnl']
        
        # Calculate percentages
        cash_pct = (self.settled_funds / self.account_value * 100) if self.account_value > 0 else 0
        positions_pct = (total_position_value / self.account_value * 100) if self.account_value > 0 else 0
        total_pnl_pct = (total_pnl / (total_position_value - total_pnl)) * 100 if (total_position_value - total_pnl) != 0 else 0
        pnl_color = "🟢" if total_pnl >= 0 else "🔴"
        
        print("-" * 60)
        print(f"{'TOTAL':6s} | ${total_position_value:>10.2f} ({positions_pct:>4.1f}%) | "
              f"{pnl_color} ${total_pnl:>+7.2f} ({total_pnl_pct:>+5.1f}%)")
        print(f"{'CASH':6s} | ${self.settled_funds:>10.2f} ({cash_pct:>4.1f}%)")
        
        if fractional_count > 0:
            print(f"📊 Fractional positions: {fractional_count} (no bracket orders available)")
        
        # Show max position size for new buys
        max_new_position = self.account_value * self.config.MAX_POSITION_VALUE_PERCENT
        max_affordable = min(max_new_position, self.settled_funds)
        print(f"📈 Max new position: ${max_affordable:.2f} ({self.config.MAX_POSITION_VALUE_PERCENT:.1%} of account)")
    
    def confirm_trade(self, signal: Dict) -> bool:
        """Ask user to confirm trade execution"""
        symbol = signal['symbol']
        signal_type = signal['signal_type']
        price = signal['price']
        confidence = signal.get('confidence', 0)
        
        print(f"\n🎯 TRADE RECOMMENDATION")
        print("=" * 40)
        
        # Get position data for display
        position_data = None
        if signal_type == 'SELL':
            for pos in self.positions:
                if pos['symbol'] == symbol:
                    position_data = pos
                    break
        
        # Use PersonalTradingConfig formatting
        display_text = self.config.format_signal_display(signal, position_data)
        print(f"Signal: {display_text}")
        
        # Show additional details
        if 'calculated_shares' in signal:
            shares = signal['calculated_shares']
            total_cost = shares * price
            pct_of_account = (total_cost / self.account_value) * 100 if self.account_value > 0 else 0
            print(f"Shares: {shares} (${total_cost:.2f} = {pct_of_account:.1f}% of account)")
        
        if 'metadata' in signal:
            try:
                import json
                metadata = json.loads(signal['metadata'])
                if 'stop_loss' in metadata:
                    print(f"Stop Loss: ${metadata['stop_loss']:.2f}")
                if 'target' in metadata:
                    print(f"Target: ${metadata['target']:.2f}")
            except:
                pass
        
        print("=" * 40)
        choice = input("Execute this trade? (y/n): ").lower().strip()
        return choice in ['y', 'yes']
    
    def execute_trade(self, signal: Dict) -> bool:
        """Execute the trade with Webull (supports fractional shares)"""
        symbol = signal['symbol']
        signal_type = signal['signal_type']
        price = signal['price']
        
        # Get trading PIN
        trading_pin = getpass.getpass("Enter your 6-digit Webull trading PIN: ")
        
        try:
            # Get trade token
            print("🔑 Authorizing trade...")
            if not self.wb.get_trade_token(trading_pin):
                print("❌ Invalid trading PIN")
                return False
            
            print("✅ Trade authorized")
            
            # Calculate quantity or dollar amount
            if signal_type == 'BUY':
                # Use pre-calculated position sizing from signal
                if 'calculated_position_info' in signal:
                    position_info = signal['calculated_position_info']
                else:
                    # Fallback calculation
                    position_info = self.config.get_position_size(
                        price, self.account_value, self.settled_funds
                    )
                
                if position_info['type'] == 'none':
                    print("❌ Insufficient funds for minimum position")
                    return False
                
                action = 'BUY'
                
            elif signal_type == 'SELL':
                # Sell entire position (whole or fractional)
                position = None
                for pos in self.positions:
                    if pos['symbol'] == symbol:
                        position = pos
                        break
                
                if not position:
                    print(f"❌ No position found for {symbol}")
                    return False
                
                # For sells, always use share-based quantity
                position_info = {
                    'type': 'shares',
                    'amount': position['quantity'],
                    'is_fractional': self.config.is_fractional_position(position['quantity'])
                }
                action = 'SELL'
            
            # Determine order type and display info
            if position_info['type'] == 'shares':
                quantity = position_info['amount']
                is_fractional = position_info['is_fractional']
                fractional_indicator = "📊" if is_fractional else ""
                total_value = quantity * price
                
                if is_fractional:
                    print(f"📋 Placing fractional order: {action} {quantity:.4f} shares of {symbol} {fractional_indicator}")
                else:
                    print(f"📋 Placing order: {action} {int(quantity)} shares of {symbol}")
                
                print(f"💰 Order value: ${total_value:.2f}")
                
                if is_fractional:
                    print("💡 Note: Fractional orders may take longer to execute and only work during market hours")
                
                # Place share-based order
                order_result = self.wb.place_order(
                    stock=symbol,
                    price=price,
                    action=action,
                    orderType='MKT',  # Limit order
                    enforce='DAY',    # Day order
                    quant=quantity,   # Can be fractional
                    outsideRegularTradingHour=False  # Fractional shares only work during market hours
                )
                print(order_result)
            elif position_info['type'] == 'dollars':
                dollar_amount = position_info['amount']
                
                # Show buffer information if applied
                if position_info.get('buffer_applied'):
                    original_amount = position_info['original_amount']
                    buffer_pct = position_info['buffer_percentage'] * 100
                    print(f"📋 Placing buffered fractional order: {action} ${dollar_amount:.2f} of {symbol} 📊")
                    print(f"💰 Investment amount: ${dollar_amount:.2f} (was ${original_amount:.2f})")
                    print(f"🛡️ Safety buffer: {buffer_pct:.0f}% applied to prevent API failures")
                else:
                    print(f"📋 Placing dollar-based fractional order: {action} ${dollar_amount:.2f} of {symbol} 📊")
                    print(f"💰 Investment amount: ${dollar_amount:.2f}")
                
                print("💡 Note: Refreshing price to avoid movement issues...")
                
                # Get fresh price quote to avoid price movement issues
                try:
                    fresh_quote = self.wb.get_quote(symbol)
                    if fresh_quote and 'close' in fresh_quote:
                        current_market_price = float(fresh_quote['close'])
                        print(f"💡 Updated price: ${current_market_price:.2f} (was ${price:.2f})")
                    else:
                        current_market_price = price
                        print(f"⚠️  Could not get fresh price, using ${price:.2f}")
                except Exception as e:
                    current_market_price = price
                    print(f"⚠️  Price refresh failed, using ${price:.2f}: {e}")
                
                # Calculate fractional shares based on fresh price
                quantity = dollar_amount / current_market_price
                quantity = round(quantity, 4)  # Round to 4 decimal places
                
                print(f"📊 Calculated shares: {quantity:.4f} shares @ ${current_market_price:.2f}")
                
                # Use limit order for better execution and API compatibility
                order_type = self.config.FRACTIONAL_ORDER_TYPE
                limit_price = self.round_price_for_webull(current_market_price * 1.005)  # Small premium for execution
                
                print(f"💡 Using {order_type} order @ ${limit_price:.2f} for better fractional execution")
                
                # Place fractional share order with limit price
                order_result = self.wb.place_order(
                    stock=symbol,
                    price=limit_price,
                    action=action,
                    orderType=order_type,  # Use configured order type (default: LMT)
                    enforce='DAY',         # Day order
                    quant=quantity,        # Fractional quantity
                    outsideRegularTradingHour=False
                )
                
                self._log_trade(signal, quantity, order_result)
                
                return True
            else:
                print("❌ Order failed:")
                print(f"   {order_result.get('msg', 'Unknown error')}")
                
                if is_fractional:
                    print("💡 Tip: Fractional orders require market hours and may have additional restrictions")
                
                return False
                
        except Exception as e:
            print(f"❌ Trade execution error: {e}")
            return False
    
    def _track_new_fractional_position(self, symbol: str, quantity: float, entry_price: float):
        """Track a new fractional position in the database"""
        try:
            entry_date = datetime.now().strftime('%Y-%m-%d')
            stop_loss_price = entry_price * (1 - self.config.PERSONAL_STOP_LOSS)
            take_profit_price = entry_price * (1 + self.config.PERSONAL_TAKE_PROFIT)
            
            with self.db as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO fractional_positions 
                    (symbol, quantity, entry_price, entry_date, 
                     target_stop_loss, target_take_profit, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    quantity,
                    entry_price,
                    entry_date,
                    stop_loss_price,
                    take_profit_price,
                    'pending_fill',
                    f"New fractional buy order placed at ${entry_price:.2f}"
                ))
            
            print(f"📊 Fractional position tracking added for {symbol}")
            print(f"   Target stop-loss: ${stop_loss_price:.2f} ({self.config.PERSONAL_STOP_LOSS:.1%})")
            print(f"   Target take-profit: ${take_profit_price:.2f} ({self.config.PERSONAL_TAKE_PROFIT:.1%})")
            
        except Exception as e:
            print(f"⚠️  Error tracking fractional position: {e}")
    
    def _log_trade(self, signal: Dict, quantity: int, order_result: Dict):
        """Log trade details for record keeping"""
        try:
            trade_log = {
                'timestamp': datetime.now().isoformat(),
                'symbol': signal['symbol'],
                'action': signal['signal_type'],
                'quantity': quantity,
                'price': signal['price'],
                'confidence': signal.get('confidence', 0),
                'order_id': order_result.get('orderId'),
                'strategy': signal.get('strategy', 'Unknown')
            }
            
            # You could save this to a file or database
            print(f"📝 Trade logged: {trade_log}")
            
        except Exception as e:
            print(f"⚠️  Could not log trade: {e}")
    
    def _display_summary(self, executed_trades: int):
        """Display final summary with real account allocation"""
        print(f"\n✅ Analysis complete!")
        print("=" * 40)
        
        # Get account allocation info
        allocation = self.config.get_account_allocation_info(
            self.account_value, 
            self.settled_funds, 
            self.positions
        )
        
        print(f"📊 Trades executed: {executed_trades}")
        print(f"🏦 Account value: ${allocation['account_value']:.2f}")
        print(f"💰 Available cash: ${allocation['settled_funds']:.2f} ({allocation['cash_percentage']:.1f}%)")
        print(f"📈 Positions: ${allocation['total_position_value']:.2f} ({allocation['positions_percentage']:.1f}%)")
        print(f"🎯 Position slots: {allocation['positions_count']}/{allocation['max_positions']} used")
        
        if allocation['available_position_slots'] > 0:
            print(f"💡 Max new position: ${allocation['max_new_position']:.2f}")
        else:
            print(f"⚠️  At max positions - only sells available")
        
        if executed_trades > 0:
            print(f"📱 Check your Webull app for order status")
        
        print(f"🕐 Next: Run quick_daily_check.py anytime")
        print(f"📊 Account uses real netLiquidation: ${self.account_value:.2f}")
    
    def run_analysis(self):
        """Run the complete personal trading analysis"""
        print("🚀 Personal Trading System")
        print("=" * 50)
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Check market hours
        if not self.config.is_market_hours():
            print("⏰ Outside preferred trading hours")
            print(f"   Preferred: {self.config.TRADING_START_TIME} - {self.config.TRADING_END_TIME}")
            choice = input("Continue anyway? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                return
        
        # Step 1: Login to Webull
        if not self.is_logged_in:
            if not self.login_to_webull():
                return
        
        # Step 2: Get account information
        if not self.get_account_info():
            return
        
        # Step 3: Display current positions
        self.display_positions()
        
        # Step 3.5: Check fractional position monitoring
        choice = input("\nCheck fractional position exit levels? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            self.offer_fractional_monitoring()
        
        # Step 3.6: Offer protective stops for overnight positions
        overnight_positions = self.get_overnight_positions()
        if overnight_positions:
            print(f"\n🌙 OVERNIGHT POSITIONS DETECTED")
            print(f"Found {len(overnight_positions)} positions held overnight")
            
            choice = input("Review protective stop-loss orders? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                # Get trading PIN for stop orders
                trading_pin = getpass.getpass("Enter 6-digit Webull trading PIN (for stop orders): ")
                
                try:
                    # Authorize for stop order placement
                    print("🔑 Authorizing stop order placement...")
                    if self.wb.get_trade_token(trading_pin):
                        print("✅ Stop order authorization successful")
                        self.offer_protective_stops(overnight_positions)
                    else:
                        print("❌ Invalid trading PIN - skipping stop orders")
                except Exception as e:
                    print(f"❌ Stop order authorization failed: {e}")
        
        # Optional: Show position trends
        choice = input("\nView position trends? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            self.display_position_trends(days=7)
        
        # Check if we're at max positions for buys
        if len(self.positions) >= self.config.MAX_POSITIONS_TOTAL:
            print(f"\n⚠️  At maximum positions ({len(self.positions)}/{self.config.MAX_POSITIONS_TOTAL})")
            print("   Only sell signals will be considered")
        
        # Step 4: Determine scan universe
        scan_universe = self.get_scan_universe()
        
        print(f"\n🔍 SCAN UNIVERSE")
        print("=" * 30)
        print(f"Position stocks: {len(self.get_position_symbols())}")
        print(f"Watchlist stocks: {len(self.config.PERSONAL_WATCHLIST)}")
        print(f"Affordable stocks: {len(self.get_affordable_stocks())}")
        print(f"Total scan universe: {len(scan_universe)}")
        
        if len(scan_universe) == 0:
            print("❌ No stocks to analyze")
            return
        
        # Step 5: Run trading system analysis on our universe
        print(f"\n🤖 RUNNING ANALYSIS ON {len(scan_universe)} STOCKS")
        print("=" * 50)
        
        # Override the stock list for this analysis
        original_bb_list = StockLists.BOLLINGER_MEAN_REVERSION
        original_gap_list = StockLists.GAP_TRADING
        
        try:
            # Temporarily override stock lists
            StockLists.BOLLINGER_MEAN_REVERSION = scan_universe
            StockLists.GAP_TRADING = scan_universe
            
            # Run analysis
            results = self.trading_system.run_daily_analysis()
            
        finally:
            # Restore original lists
            StockLists.BOLLINGER_MEAN_REVERSION = original_bb_list
            StockLists.GAP_TRADING = original_gap_list
        
        # Step 6: Filter signals by our personal rules
        all_signals = results['buy_signals'] + results['sell_signals']
        filtered_signals = self.filter_signals_by_rules(all_signals)
        
        # Step 7: Display and process signals
        print(f"\n📋 PERSONAL TRADING SIGNALS")
        print("=" * 50)
        print(f"Strategy Used: {results['strategy_used']}")
        print(f"Market Condition: {results.get('market_condition', {}).get('condition', 'Unknown')}")
        print(f"Raw signals: {len(all_signals)}")
        print(f"Filtered signals: {len(filtered_signals)}")
        
        if not filtered_signals:
            print("✅ No trading signals meet your criteria today")
            self._display_summary(0)
            return
        
        # Sort by confidence
        filtered_signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Display signals summary
        buy_signals = [s for s in filtered_signals if s['signal_type'] == 'BUY']
        sell_signals = [s for s in filtered_signals if s['signal_type'] == 'SELL']
        
        print(f"💰 Buy signals: {len(buy_signals)}")
        print(f"💸 Sell signals: {len(sell_signals)}")
        
        # Process each signal
        executed_trades = 0
        for i, signal in enumerate(filtered_signals, 1):
            print(f"\n📊 Signal {i}/{len(filtered_signals)}")
            
            if self.confirm_trade(signal):
                if self.execute_trade(signal):
                    executed_trades += 1
                    # Refresh account info after successful trade
                    self.get_account_info()
                else:
                    print("❌ Trade failed")
                    
                # Ask if user wants to continue with remaining signals
                if i < len(filtered_signals):
                    continue_choice = input("Continue with remaining signals? (y/n): ").lower().strip()
                    if continue_choice not in ['y', 'yes']:
                        break
            else:
                print("⏭️  Trade skipped")
        
        # Final summary
        self._display_summary(executed_trades)
        
        # Final positions display
        if executed_trades > 0:
            print(f"\n💼 UPDATED POSITIONS")
            self.display_positions()

def main():
    """Main entry point"""
    try:
        personal_system = PersonalTradingSystem()
        personal_system.run_analysis()
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ System error: {e}")

if __name__ == "__main__":
    main()
