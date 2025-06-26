# simplified_trading_example.py
"""
Simplified trading script focusing on automatic strategy selection
between Bollinger Band mean reversion and gap trading only
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Clean imports
from trading_system import TradingSystem, StockLists

def main():
    """Run automatic trading analysis with BB and Gap strategies only"""
    
    print("🚀 Auto Trading System - BB & Gap Focus")
    print("=" * 50)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Initialize the system
    system = TradingSystem()
    
    # ========================================================================
    # 1. Show available stock universes
    # ========================================================================
    
    print(f"\n📊 Stock Universe Sizes:")
    print(f"  • Bollinger Band Mean Reversion: {len(StockLists.BOLLINGER_MEAN_REVERSION)} stocks")
    print(f"  • Gap Trading Universe: {len(StockLists.GAP_TRADING)} stocks")
    print(f"  • Combined Universe: {len(set(StockLists.BOLLINGER_MEAN_REVERSION + StockLists.GAP_TRADING))} unique stocks")
    
    # ========================================================================
    # 2. Run automatic strategy selection
    # ========================================================================
    
    print("\n" + "="*50)
    print("🤖 AUTOMATIC STRATEGY SELECTION")
    print("="*50)
    
    # Let the system automatically choose between BB and Gap based on market conditions
    results = system.run_daily_analysis()
    
    print(f"\n✅ Auto-Selected Strategy: {results['strategy_used']}")
    print(f"📈 Stocks Analyzed: {len(results['stock_universe'])}")
    print(f"🎯 Total Signals: {results['total_signals']}")
    print(f"💰 Buy Signals: {len(results['buy_signals'])}")
    print(f"💸 Sell Signals: {len(results['sell_signals'])}")
    
    # Show market conditions that influenced the choice
    if 'market_analysis' in results:
        market = results['market_analysis']
        print(f"\n📊 Market Conditions:")
        print(f"  • VIX Level: {market.get('vix_level', 'N/A')}")
        print(f"  • Market Trend: {market.get('trend', 'N/A')}")
        print(f"  • Volatility: {market.get('volatility', 'N/A')}")
        print(f"  • Condition: {market.get('condition', 'N/A')}")
    
    # ========================================================================
    # 3. Display trading signals
    # ========================================================================
    
    print("\n" + "="*50)
    print("📋 TRADING SIGNALS")
    print("="*50)
    
    # Show buy signals
    if results['buy_signals']:
        print(f"\n💰 BUY SIGNALS ({len(results['buy_signals'])}):")
        print("-" * 30)
        
        # Sort by confidence and show top signals
        top_buys = sorted(results['buy_signals'], key=lambda x: x['confidence'], reverse=True)
        
        for i, signal in enumerate(top_buys[:10], 1):  # Top 10 buy signals
            print(f"{i:2d}. {signal['symbol']:6s} - ${signal['price']:7.2f} | "
                  f"Conf: {signal['confidence']:5.1%} | "
                  f"Reason: {signal.get('reason', 'N/A')}")
            
            # Show gap-specific info if available
            if 'gap_size' in signal:
                gap_info = f"Gap: {signal['gap_size']:+5.1%} ({signal.get('gap_type', 'Unknown')})"
                print(f"     └─ {gap_info}")
    else:
        print("\n💰 No buy signals found today")
    
    # Show sell signals
    if results['sell_signals']:
        print(f"\n💸 SELL SIGNALS ({len(results['sell_signals'])}):")
        print("-" * 30)
        
        # Sort by confidence and show top signals
        top_sells = sorted(results['sell_signals'], key=lambda x: x['confidence'], reverse=True)
        
        for i, signal in enumerate(top_sells[:10], 1):  # Top 10 sell signals
            print(f"{i:2d}. {signal['symbol']:6s} - ${signal['price']:7.2f} | "
                  f"Conf: {signal['confidence']:5.1%} | "
                  f"Reason: {signal.get('reason', 'N/A')}")
    else:
        print("\n💸 No sell signals found today")
    
    # ========================================================================
    # 4. Strategy comparison (if you want to see both)
    # ========================================================================
    
    print("\n" + "="*50)
    print("🔬 STRATEGY COMPARISON")
    print("="*50)
    
    # Force test both strategies to compare
    print("\n🧪 Testing both strategies for comparison...")
    
    # Test Bollinger Band strategy
    bb_results = system.run_daily_analysis(
        strategy_override='BollingerMeanReversion',
        stock_list_override='BollingerMeanReversion'
    )
    
    # Test Gap Trading strategy  
    gap_results = system.run_daily_analysis(
        strategy_override='GapTrading',
        stock_list_override='GapTrading'
    )
    
    print(f"\n📊 Strategy Performance Today:")
    print(f"  Bollinger Bands: {len(bb_results['buy_signals'])} buys, {len(bb_results['sell_signals'])} sells")
    print(f"  Gap Trading:     {len(gap_results['buy_signals'])} buys, {len(gap_results['sell_signals'])} sells")
    
    # Show which one the system automatically selected vs manual test
    auto_strategy = results['strategy_used']
    print(f"\n🎯 System chose: {auto_strategy}")
    
    if auto_strategy == 'BollingerMeanReversion':
        print("  └─ Favoring mean reversion in current market conditions")
    elif auto_strategy == 'GapTrading':
        print("  └─ Favoring gap opportunities in current volatility")
    
    # ========================================================================
    # 5. Quick summary for daily use
    # ========================================================================
    
    print("\n" + "="*50)
    print("📝 DAILY SUMMARY")
    print("="*50)
    
    total_opportunities = len(results['buy_signals']) + len(results['sell_signals'])
    
    print(f"Strategy Selected: {results['strategy_used']}")
    print(f"Total Opportunities: {total_opportunities}")
    print(f"Market Condition: {results.get('market_analysis', {}).get('condition', 'Unknown')}")
    
    if results['buy_signals']:
        best_buy = max(results['buy_signals'], key=lambda x: x['confidence'])
        print(f"Best Buy Opportunity: {best_buy['symbol']} at ${best_buy['price']:.2f} ({best_buy['confidence']:.1%})")
    
    if results['sell_signals']:
        best_sell = max(results['sell_signals'], key=lambda x: x['confidence'])
        print(f"Best Sell Opportunity: {best_sell['symbol']} at ${best_sell['price']:.2f} ({best_sell['confidence']:.1%})")
    
    return results

def quick_daily_check():
    """Ultra-simplified version for quick daily checks"""
    
    print("\n🎯 QUICK DAILY CHECK")
    print("="*25)
    
    system = TradingSystem()
    results = system.run_daily_analysis()
    
    print(f"Strategy: {results['strategy_used']}")
    print(f"Signals: {len(results['buy_signals'])} buys, {len(results['sell_signals'])} sells")
    
    # Show only top 3 opportunities
    all_signals = results['buy_signals'] + results['sell_signals']
    if all_signals:
        print("\nTop opportunities:")
        top_signals = sorted(all_signals, key=lambda x: x['confidence'], reverse=True)[:3]
        for signal in top_signals:
            action = "BUY" if signal in results['buy_signals'] else "SELL"
            print(f"  {action} {signal['symbol']} @ ${signal['price']:.2f} ({signal['confidence']:.1%})")
    else:
        print("No signals today - market may be trending or low volatility")
    
    return results

if __name__ == "__main__":
    # Run the main analysis
    try:
        main_results = main()
        
        print("\n" + "="*60)
        
        # Quick version for copy/paste to other tools
        quick_results = quick_daily_check()
        
        print(f"\n✅ Analysis Complete at {datetime.now().strftime('%H:%M')}")
        print("📊 Ready for trading decisions!")
        
    except Exception as e:
        print(f"\n❌ Error running analysis: {e}")
        print("Check your data connection and try again.")