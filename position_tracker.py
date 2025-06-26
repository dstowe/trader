# position_tracker.py
"""
Position History Tracker
View historical position data, P&L trends, and portfolio analytics
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trading_system.database.models import DatabaseManager
from trading_system.config.settings import TradingConfig

class PositionTracker:
    """Track and analyze position history from database"""
    
    def __init__(self):
        self.config = TradingConfig()
        self.db = DatabaseManager(self.config.DATABASE_PATH)
    
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
    
    def display_portfolio_summary(self, days=30):
        """Display portfolio performance summary"""
        history = self.get_position_history(days=days)
        
        if not history:
            print("📭 No position history found")
            return
        
        print(f"\n📊 PORTFOLIO SUMMARY (Last {days} days)")
        print("=" * 60)
        
        # Group by date
        from collections import defaultdict
        by_date = defaultdict(list)
        for entry in history:
            by_date[entry['sync_date']].append(entry)
        
        dates = sorted(by_date.keys())
        if len(dates) >= 2:
            # Compare first and last day
            first_day = by_date[dates[0]]
            last_day = by_date[dates[-1]]
            
            first_total = sum(entry['market_value'] for entry in first_day)
            last_total = sum(entry['market_value'] for entry in last_day)
            
            first_pnl = sum(entry['unrealized_pnl'] for entry in first_day)
            last_pnl = sum(entry['unrealized_pnl'] for entry in last_day)
            
            portfolio_change = last_total - first_total
            pnl_change = last_pnl - first_pnl
            
            print(f"📈 Portfolio Value Change:")
            print(f"  {dates[0]}: ${first_total:.2f} (P&L: ${first_pnl:+.2f})")
            print(f"  {dates[-1]}: ${last_total:.2f} (P&L: ${last_pnl:+.2f})")
            
            change_emoji = "🟢" if portfolio_change >= 0 else "🔴"
            pnl_emoji = "🟢" if pnl_change >= 0 else "🔴"
            
            print(f"  Change: {change_emoji} ${portfolio_change:+.2f}")
            print(f"  P&L Change: {pnl_emoji} ${pnl_change:+.2f}")
        
        # Show current positions summary
        if dates:
            current_date = dates[-1]
            current_positions = by_date[current_date]
            
            print(f"\n💼 Current Positions ({current_date}):")
            print("-" * 40)
            
            # Sort by market value
            current_positions.sort(key=lambda x: x['market_value'], reverse=True)
            
            for pos in current_positions:
                pnl_emoji = "🟢" if pos['unrealized_pnl'] >= 0 else "🔴"
                pnl_pct = pos['pnl_rate'] * 100
                
                print(f"{pos['symbol']:6s} | {pos['quantity']:>6.0f} shares | "
                      f"${pos['market_value']:>8.2f} | "
                      f"{pnl_emoji} ${pos['unrealized_pnl']:>+7.2f} ({pnl_pct:>+5.1f}%)")
    
    def display_position_trends(self, symbol=None, days=14):
        """Display position P&L trends"""
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
                print("-" * 30)
                
                # Sort by date
                symbol_history.sort(key=lambda x: x['sync_date'])
                
                for entry in symbol_history:
                    pnl_emoji = "🟢" if entry['unrealized_pnl'] >= 0 else "🔴"
                    pnl_pct = entry['pnl_rate'] * 100
                    print(f"{entry['sync_date']}: {pnl_emoji} ${entry['unrealized_pnl']:+8.2f} "
                          f"({pnl_pct:+6.1f}%) | ${entry['current_price']:>7.2f}")
                
                # Show trend analysis
                if len(symbol_history) >= 2:
                    first = symbol_history[0]
                    last = symbol_history[-1]
                    
                    pnl_change = last['unrealized_pnl'] - first['unrealized_pnl']
                    price_change = last['current_price'] - first['current_price']
                    price_change_pct = (price_change / first['current_price']) * 100
                    
                    trend_emoji = "🟢" if pnl_change >= 0 else "🔴"
                    print(f"\nTrend: {trend_emoji} P&L change: ${pnl_change:+.2f}")
                    print(f"Price change: ${price_change:+.2f} ({price_change_pct:+.1f}%)")
        else:
            # Show summary by date
            from collections import defaultdict
            by_date = defaultdict(list)
            for entry in history:
                by_date[entry['sync_date']].append(entry)
            
            for date in sorted(by_date.keys(), reverse=True):
                total_pnl = sum(entry['unrealized_pnl'] for entry in by_date[date])
                total_value = sum(entry['market_value'] for entry in by_date[date])
                position_count = len(by_date[date])
                
                pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
                
                print(f"{date}: {pnl_emoji} ${total_pnl:+8.2f} | "
                      f"${total_value:>10.2f} total | {position_count} positions")
    
    def find_best_worst_performers(self, days=30):
        """Find best and worst performing positions"""
        history = self.get_position_history(days=days)
        
        if not history:
            print("📭 No position history found")
            return
        
        # Group by symbol and get latest entry for each
        from collections import defaultdict
        by_symbol = defaultdict(list)
        for entry in history:
            by_symbol[entry['symbol']].append(entry)
        
        # Get most recent entry for each symbol
        latest_positions = []
        for symbol, entries in by_symbol.items():
            latest = max(entries, key=lambda x: x['sync_date'])
            latest_positions.append(latest)
        
        if not latest_positions:
            return
        
        # Sort by P&L percentage
        latest_positions.sort(key=lambda x: x['pnl_rate'], reverse=True)
        
        print(f"\n🏆 BEST & WORST PERFORMERS (Last {days} days)")
        print("=" * 50)
        
        print("🥇 Top Performers:")
        for pos in latest_positions[:3]:
            pnl_pct = pos['pnl_rate'] * 100
            print(f"  {pos['symbol']:6s}: 🟢 ${pos['unrealized_pnl']:+8.2f} ({pnl_pct:+6.1f}%)")
        
        print("\n🥉 Bottom Performers:")
        for pos in latest_positions[-3:]:
            pnl_pct = pos['pnl_rate'] * 100
            emoji = "🟢" if pos['unrealized_pnl'] >= 0 else "🔴"
            print(f"  {pos['symbol']:6s}: {emoji} ${pos['unrealized_pnl']:+8.2f} ({pnl_pct:+6.1f}%)")
    
    def export_position_history(self, filename=None, days=30):
        """Export position history to CSV"""
        history = self.get_position_history(days=days)
        
        if not history:
            print("📭 No position history to export")
            return
        
        if not filename:
            filename = f"position_history_{datetime.now().strftime('%Y%m%d')}.csv"
        
        try:
            df = pd.DataFrame(history)
            df.to_csv(filename, index=False)
            print(f"📊 Exported {len(history)} records to {filename}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def run_analysis(self):
        """Run complete position analysis"""
        print("📊 Position History Tracker")
        print("=" * 40)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        while True:
            print(f"\n📋 ANALYSIS OPTIONS:")
            print("1. Portfolio Summary")
            print("2. Position Trends (All)")
            print("3. Position Trends (Specific Symbol)")
            print("4. Best/Worst Performers")
            print("5. Export to CSV")
            print("6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                days = int(input("Days to analyze (default 30): ") or 30)
                self.display_portfolio_summary(days)
                
            elif choice == '2':
                days = int(input("Days to analyze (default 14): ") or 14)
                self.display_position_trends(days=days)
                
            elif choice == '3':
                symbol = input("Enter symbol: ").upper().strip()
                days = int(input("Days to analyze (default 14): ") or 14)
                self.display_position_trends(symbol, days)
                
            elif choice == '4':
                days = int(input("Days to analyze (default 30): ") or 30)
                self.find_best_worst_performers(days)
                
            elif choice == '5':
                days = int(input("Days to export (default 30): ") or 30)
                filename = input("Filename (Enter for auto): ").strip() or None
                self.export_position_history(filename, days)
                
            elif choice == '6':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice")

def main():
    try:
        tracker = PositionTracker()
        tracker.run_analysis()
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()