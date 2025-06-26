# quick_daily_check.py
"""
Quick Daily Trading Check
- Fast login and position overview
- Shows top 3 signals without execution
- Perfect for morning market check
"""

import sys
import os
import getpass
from datetime import datetime
from typing import List, Dict

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_system import TradingSystem, StockLists
from trading_system.webull.webull import webull
from trading_system.database.models import DatabaseManager
from trading_system.config.settings import TradingConfig

class QuickDailyCheck:
    """Quick daily market check without trade execution"""
    
    def __init__(self):
        self.config = TradingConfig()
        self.wb = webull()
        self.trading_system = TradingSystem()
        self.db = DatabaseManager(self.config.DATABASE_PATH)
        
        self.account_data = None
        self.positions = []
        self.settled_funds = 0.0
        self.account_value = 0.0
        
    def quick_login(self):
        """Quick login - try saved credentials first"""
        print("🔐 Quick Login")
        
        # Try to use saved credentials if available
        # In a real implementation, you might save encrypted credentials
        username = input("Webull username/email: ")
        password = getpass.getpass("Webull password: ")
        
        try:
            login_result = self.wb.login(username, password)
            if 'accessToken' in login_result:
                print("✅ Logged in")
                return True
            else:
                print("❌ Login failed")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def get_positions_quick(self):
        """Quick position check"""
        try:
            self.account_data = self.wb.get_account()
            
            # Get settled funds
            for member in self.account_data['accountMembers']:
                if member['key'] == 'settledFunds':
                    self.settled_funds = float(member['value'])
                    break
            
            # Use netLiquidation as account value
            if 'netLiquidation' in self.account_data:
                self.account_value = float(self.account_data['netLiquidation'])
            else:
                # Fallback
                for member in self.account_data['accountMembers']:
                    if member['key'] == 'totalMarketValue':
                        self.account_value = float(member['value'])
                        break
            
            # Get positions
            self.positions = []
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
            
            # Quick sync to database (positions only, no verbose output)
            self._sync_positions_quietly()
            
            return True
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return False
    
    def _sync_positions_quietly(self):
        """Quietly sync positions without verbose output"""
        if not self.positions:
            return
        
        try:
            # Create table if needed
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
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(sync_date, symbol)
                    )
                ''')
            
            sync_date = datetime.now().strftime('%Y-%m-%d')
            
            for pos in self.positions:
                try:
                    with self.db as conn:
                        conn.execute('''
                            INSERT OR REPLACE INTO position_history 
                            (sync_date, symbol, quantity, cost_price, current_price, 
                             market_value, unrealized_pnl, pnl_rate, last_open_time,
                             account_value, settled_funds)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            sync_date, pos['symbol'], pos['quantity'], pos['cost_price'],
                            pos['current_price'], pos['market_value'], pos['unrealized_pnl'],
                            pos['pnl_rate'], pos['last_open_time'], self.account_value, self.settled_funds
                        ))
                except:
                    pass  # Quietly ignore sync errors in quick check
                    
        except:
            pass  # Quietly ignore sync errors in quick check
    
    def display_quick_summary(self):
        """Display quick position summary"""
        print(f"\n💼 ACCOUNT SUMMARY")
        print("=" * 40)
        print(f"🏦 Net Liquidation: ${self.account_value:.2f}")
        
        if not self.positions:
            cash_pct = (self.settled_funds / self.account_value * 100) if self.account_value > 0 else 0
            print(f"📭 No positions ({cash_pct:.1f}% cash)")
        else:
            total_pnl = sum(pos['unrealized_pnl'] for pos in self.positions)
            total_position_value = sum(pos['market_value'] for pos in self.positions)
            
            # Sort by P&L for quick view
            sorted_positions = sorted(self.positions, key=lambda x: x['unrealized_pnl'], reverse=True)
            
            for pos in sorted_positions:
                pnl_emoji = "🟢" if pos['unrealized_pnl'] >= 0 else "🔴"
                pnl_pct = pos['pnl_rate'] * 100
                pos_pct = (pos['market_value'] / self.account_value * 100) if self.account_value > 0 else 0
                print(f"{pos['symbol']:6s} {pnl_emoji} ${pos['unrealized_pnl']:+6.2f} ({pnl_pct:+5.1f}%) [{pos_pct:4.1f}%]")
            
            total_emoji = "🟢" if total_pnl >= 0 else "🔴"
            positions_pct = (total_position_value / self.account_value * 100) if self.account_value > 0 else 0
            cash_pct = (self.settled_funds / self.account_value * 100) if self.account_value > 0 else 0
            
            print(f"{'TOTAL':6s} {total_emoji} ${total_pnl:+6.2f} | Pos:{positions_pct:.1f}% Cash:{cash_pct:.1f}%")
        
        print(f"💰 Available: ${self.settled_funds:.2f}")
    
    def get_top_signals(self, max_signals=3):
        """Get top trading signals without execution"""
        # Create scan universe (positions + affordable stocks)
        position_symbols = [pos['symbol'] for pos in self.positions]
        
        # Get affordable stocks (simplified check)
        affordable = []
        sample_stocks = StockLists.BOLLINGER_MEAN_REVERSION[:20]  # Check top 20 only for speed
        
        for symbol in sample_stocks:
            try:
                data = self.db.get_stock_data(symbol, 1)
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    if price <= self.settled_funds:
                        affordable.append(symbol)
            except:
                continue
        
        scan_universe = list(set(position_symbols + affordable))[:30]  # Limit to 30 for speed
        
        if not scan_universe:
            return []
        
        # Override stock lists temporarily
        original_bb = StockLists.BOLLINGER_MEAN_REVERSION
        original_gap = StockLists.GAP_TRADING
        
        try:
            StockLists.BOLLINGER_MEAN_REVERSION = scan_universe
            StockLists.GAP_TRADING = scan_universe
            
            # Run quick analysis
            results = self.trading_system.run_daily_analysis()
            
        finally:
            StockLists.BOLLINGER_MEAN_REVERSION = original_bb
            StockLists.GAP_TRADING = original_gap
        
        # Combine and sort signals
        all_signals = results['buy_signals'] + results['sell_signals']
        all_signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return all_signals[:max_signals]
    
    def display_signals(self, signals):
        """Display top signals"""
        print(f"\n🎯 TOP SIGNALS")
        print("=" * 40)
        
        if not signals:
            print("📭 No signals today")
            return
        
        for i, signal in enumerate(signals, 1):
            action_emoji = "💰" if signal['signal_type'] == 'BUY' else "💸"
            confidence_bar = "█" * int(signal.get('confidence', 0) * 10)
            
            print(f"{i}. {action_emoji} {signal['signal_type']} {signal['symbol']}")
            print(f"   Price: ${signal['price']:.2f}")
            print(f"   Confidence: {confidence_bar} {signal.get('confidence', 0):.1%}")
            
            # Show position info for sells
            if signal['signal_type'] == 'SELL':
                for pos in self.positions:
                    if pos['symbol'] == signal['symbol']:
                        print(f"   Current P&L: ${pos['unrealized_pnl']:+.2f}")
                        break
            print()
    
    def run_quick_check(self):
        """Run the complete quick daily check"""
        print("⚡ QUICK DAILY CHECK")
        print("=" * 30)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Quick login
        if not self.quick_login():
            return
        
        # Get positions
        if not self.get_positions_quick():
            return
        
        # Display summary
        self.display_quick_summary()
        
        # Get and display top signals
        print(f"\n🔍 Scanning market...")
        signals = self.get_top_signals(3)
        self.display_signals(signals)
        
        print(f"\n✅ Quick check complete!")
        if signals:
            print(f"💡 Run 'python personal_trading_system.py' for full analysis")

def main():
    try:
        checker = QuickDailyCheck()
        checker.run_quick_check()
    except KeyboardInterrupt:
        print("\n⏹️  Check interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()