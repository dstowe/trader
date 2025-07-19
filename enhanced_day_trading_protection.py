# enhanced_day_trading_protection.py
"""
Enhanced Day Trading Protection with Live Webull Integration
Prevents day trading violations by checking actual Webull trade history
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

class EnhancedDayTradingProtection:
    """
    Enhanced day trading protection that integrates with live Webull data
    to prevent violations from manual trades made outside the automated system
    """
    
    def __init__(self, wb, config, logger=None):
        self.wb = wb
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Cache for today's trades (refreshed periodically)
        self._todays_trades_cache = None
        self._cache_timestamp = None
        self._cache_duration_minutes = 5  # Refresh cache every 5 minutes
    
    def fetch_todays_webull_trades(self, account_id: str = None) -> List[Dict]:
        """
        Fetch all trades from Webull for today across all accounts or specific account
        
        Returns:
            List of trade dictionaries with standardized format
        """
        try:
            all_trades = []
            today = datetime.now().date()
            
            # Check cache first
            if self._is_cache_valid():
                self.logger.debug("Using cached today's trades")
                return self._todays_trades_cache
            
            self.logger.info("🔍 Fetching today's trades from Webull...")
            
            # Get trade history from Webull
            # We'll get recent orders and activities to capture all trades
            
            # Method 1: Get recent order history
            try:
                history_orders = self.wb.get_history_orders(status='All', count=50)
                
                for order in history_orders.get('data', []):
                    order_date = self._parse_webull_date(order.get('createTime', ''))
                    
                    if order_date and order_date.date() == today:
                        # Only include filled orders
                        if order.get('status') in ['Filled', 'Partially Filled']:
                            standardized_trade = self._standardize_webull_order(order)
                            if standardized_trade:
                                all_trades.append(standardized_trade)
                                
            except Exception as e:
                self.logger.warning(f"Could not fetch order history: {e}")
            
            # Method 2: Get account activities (more comprehensive)
            try:
                activities = self.wb.get_activities(index=1, size=100)
                
                for activity in activities.get('data', []):
                    activity_date = self._parse_webull_date(activity.get('time', ''))
                    
                    if activity_date and activity_date.date() == today:
                        # Only include trade activities
                        if activity.get('type') in ['trade', 'Trade']:
                            standardized_trade = self._standardize_webull_activity(activity)
                            if standardized_trade:
                                # Avoid duplicates
                                if not self._is_duplicate_trade(standardized_trade, all_trades):
                                    all_trades.append(standardized_trade)
                                    
            except Exception as e:
                self.logger.warning(f"Could not fetch activities: {e}")
            
            # Cache the results
            self._todays_trades_cache = all_trades
            self._cache_timestamp = datetime.now()
            
            self.logger.info(f"📊 Found {len(all_trades)} trades today from Webull")
            
            # Log summary for debugging
            if all_trades:
                symbols_traded = set(trade['symbol'] for trade in all_trades)
                self.logger.debug(f"Symbols traded today: {', '.join(symbols_traded)}")
            
            return all_trades
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching today's Webull trades: {e}")
            return []
    
    def _is_cache_valid(self) -> bool:
        """Check if cached trades are still valid"""
        if not self._todays_trades_cache or not self._cache_timestamp:
            return False
        
        cache_age = datetime.now() - self._cache_timestamp
        return cache_age.total_seconds() < (self._cache_duration_minutes * 60)
    
    def _parse_webull_date(self, date_str: str) -> Optional[datetime]:
        """Parse Webull date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Try different Webull date formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If none worked, try parsing as timestamp
            try:
                timestamp = float(date_str) / 1000  # Webull often uses milliseconds
                return datetime.fromtimestamp(timestamp)
            except (ValueError, TypeError):
                pass
            
        except Exception as e:
            self.logger.debug(f"Could not parse date '{date_str}': {e}")
        
        return None
    
    def _standardize_webull_order(self, order: Dict) -> Optional[Dict]:
        """Convert Webull order to standardized trade format"""
        try:
            ticker = order.get('ticker', {})
            symbol = ticker.get('symbol', '')
            
            if not symbol:
                return None
            
            return {
                'symbol': symbol,
                'action': order.get('action', ''),  # BUY, SELL
                'quantity': float(order.get('filledQuantity', 0)),
                'price': float(order.get('avgFilledPrice', 0)),
                'timestamp': order.get('createTime', ''),
                'order_id': order.get('orderId', ''),
                'source': 'webull_order',
                'account_id': getattr(self.wb, '_account_id', ''),
                'status': order.get('status', '')
            }
            
        except Exception as e:
            self.logger.debug(f"Could not standardize order: {e}")
            return None
    
    def _standardize_webull_activity(self, activity: Dict) -> Optional[Dict]:
        """Convert Webull activity to standardized trade format"""
        try:
            # Activities have different structure than orders
            symbol = activity.get('symbol', '')
            
            if not symbol:
                return None
            
            # Determine action from activity description
            description = activity.get('description', '').lower()
            action = 'BUY' if 'buy' in description or 'bought' in description else 'SELL'
            
            return {
                'symbol': symbol,
                'action': action,
                'quantity': float(activity.get('quantity', 0)),
                'price': float(activity.get('price', 0)),
                'timestamp': activity.get('time', ''),
                'activity_id': activity.get('id', ''),
                'source': 'webull_activity',
                'account_id': getattr(self.wb, '_account_id', ''),
                'description': activity.get('description', '')
            }
            
        except Exception as e:
            self.logger.debug(f"Could not standardize activity: {e}")
            return None
    
    def _is_duplicate_trade(self, new_trade: Dict, existing_trades: List[Dict]) -> bool:
        """Check if trade is already in the list"""
        for existing in existing_trades:
            if (existing['symbol'] == new_trade['symbol'] and
                existing['action'] == new_trade['action'] and
                abs(existing['quantity'] - new_trade['quantity']) < 0.001 and
                abs(existing['price'] - new_trade['price']) < 0.01):
                return True
        return False
    
    def enhanced_day_trading_check(self, symbol: str, signal_type: str, 
                                 account_id: str = None) -> Tuple[bool, str, Dict]:
        """
        Enhanced day trading check using live Webull data
        
        Args:
            symbol: Stock symbol to check
            signal_type: 'BUY' or 'SELL'
            account_id: Specific account ID (optional)
            
        Returns:
            Tuple of (can_execute, reason, trade_context)
        """
        try:
            # First check if day trading is allowed
            if self.config.ALLOW_DAY_TRADING:
                return True, "Day trading allowed in config", {}
            
            # Get today's actual trades from Webull
            todays_trades = self.fetch_todays_webull_trades(account_id)
            
            # Filter trades for this symbol
            symbol_trades = [t for t in todays_trades if t['symbol'] == symbol]
            
            if not symbol_trades:
                return True, "No trades found for this symbol today", {}
            
            # Analyze the trades for day trading implications
            trade_context = self._analyze_symbol_trades(symbol_trades, signal_type)
            
            # Apply day trading rules
            can_execute, reason = self._apply_day_trading_rules(
                signal_type, trade_context, symbol
            )
            
            return can_execute, reason, trade_context
            
        except Exception as e:
            self.logger.error(f"❌ Error in enhanced day trading check: {e}")
            # Default to cautious approach
            return False, f"Day trading check failed: {e}", {}
    
    def _analyze_symbol_trades(self, symbol_trades: List[Dict], proposed_signal: str) -> Dict:
        """
        Analyze all trades for a symbol today to understand day trading implications
        
        Returns:
            Dictionary with trade analysis context
        """
        context = {
            'total_trades': len(symbol_trades),
            'buy_trades': [],
            'sell_trades': [],
            'net_position_change': 0,
            'would_create_day_trade': False,
            'day_trade_type': None,
            'can_buy_more': True,
            'can_sell_more': True,
            'reasons': []
        }
        
        # Categorize trades
        for trade in symbol_trades:
            if trade['action'] == 'BUY':
                context['buy_trades'].append(trade)
                context['net_position_change'] += trade['quantity']
            elif trade['action'] == 'SELL':
                context['sell_trades'].append(trade)
                context['net_position_change'] -= trade['quantity']
        
        # Check if proposed signal would create day trade
        if context['buy_trades'] and proposed_signal == 'SELL':
            context['would_create_day_trade'] = True
            context['day_trade_type'] = 'BUY_then_SELL'
            context['reasons'].append(f"Would sell after buying today ({len(context['buy_trades'])} buy(s))")
        
        elif context['sell_trades'] and proposed_signal == 'BUY':
            context['would_create_day_trade'] = True
            context['day_trade_type'] = 'SELL_then_BUY'
            context['reasons'].append(f"Would buy after selling today ({len(context['sell_trades'])} sell(s))")
        
        # Determine what actions are still allowed
        if context['buy_trades']:
            # If we bought today, we can buy more but can't sell (day trade)
            context['can_sell_more'] = False
            context['reasons'].append("Cannot sell - would create day trade (bought today)")
        
        if context['sell_trades']:
            # If we sold today, we can sell more but can't buy (day trade)
            # UNLESS we're not going short (i.e., we still have position to sell)
            context['can_buy_more'] = False
            context['reasons'].append("Cannot buy - would create day trade (sold today)")
            
            # However, we can still sell more if we have position
            # This requires checking current position
        
        return context
    
    def _apply_day_trading_rules(self, signal_type: str, context: Dict, symbol: str) -> Tuple[bool, str]:
        """
        Apply day trading rules based on trade context
        
        Returns:
            Tuple of (can_execute, reason)
        """
        # Rule 1: If this would create a day trade, block it
        if context['would_create_day_trade']:
            return False, f"DAY TRADE BLOCKED: {context['day_trade_type']} - {'; '.join(context['reasons'])}"
        
        # Rule 2: Check specific signal type permissions
        if signal_type == 'BUY' and not context['can_buy_more']:
            return False, f"BUY BLOCKED: {'; '.join(context['reasons'])}"
        
        if signal_type == 'SELL' and not context['can_sell_more']:
            # Special case: Check if we're trying to short sell
            if not context['buy_trades']:  # No buys today, so this might be short selling
                if not self.config.ALLOW_SHORT_SELLING:
                    return False, "SELL BLOCKED: Would be short selling (not allowed in config)"
        
        # Rule 3: All checks passed
        return True, "No day trading violation detected"
    
    def get_current_position(self, symbol: str, account_id: str = None) -> Dict:
        """
        Get current position for symbol from Webull
        
        Returns:
            Dictionary with position info or empty dict if no position
        """
        try:
            positions = self.wb.get_positions()
            
            for position in positions:
                if position.get('ticker', {}).get('symbol') == symbol:
                    return {
                        'symbol': symbol,
                        'quantity': float(position.get('position', 0)),
                        'cost_price': float(position.get('costPrice', 0)),
                        'current_price': float(position.get('lastPrice', 0)),
                        'market_value': float(position.get('marketValue', 0)),
                        'unrealized_pnl': float(position.get('unrealizedProfitLoss', 0)),
                        'last_open_time': position.get('lastOpenTime', '')
                    }
            
            return {}  # No position found
            
        except Exception as e:
            self.logger.error(f"❌ Error getting current position for {symbol}: {e}")
            return {}
    
    def enhanced_should_execute_signal(self, signal, current_positions=None, 
                                     account_value=0.0, account_id=None) -> Tuple[bool, str]:
        """
        Enhanced signal execution check with live Webull day trading protection
        
        This replaces the original should_execute_signal method with enhanced protection
        """
        symbol = signal.symbol
        signal_type = signal.signal_type
        
        # First run the original config-based checks
        original_check, original_reason = self.config.should_execute_signal(
            signal, current_positions, account_value
        )
        
        if not original_check:
            return False, original_reason
        
        # Now run enhanced day trading check with live Webull data
        can_execute, dt_reason, trade_context = self.enhanced_day_trading_check(
            symbol, signal_type, account_id
        )
        
        if not can_execute:
            # Log the trade context for debugging
            if trade_context.get('total_trades', 0) > 0:
                self.logger.info(f"🚫 Day trade blocked for {symbol}:")
                self.logger.info(f"   Today's trades: {trade_context['total_trades']}")
                self.logger.info(f"   Buys: {len(trade_context.get('buy_trades', []))}")
                self.logger.info(f"   Sells: {len(trade_context.get('sell_trades', []))}")
                self.logger.info(f"   Proposed: {signal_type}")
            
            return False, f"ENHANCED DAY TRADING PROTECTION: {dt_reason}"
        
        # Additional check: Verify position exists for SELL signals
        if signal_type == 'SELL':
            current_position = self.get_current_position(symbol, account_id)
            
            if not current_position or current_position.get('quantity', 0) <= 0:
                if not self.config.ALLOW_SHORT_SELLING:
                    return False, "SELL BLOCKED: No position to sell and short selling disabled"
        
        return True, "Enhanced checks passed"
    
    def get_day_trading_summary(self) -> Dict:
        """
        Get summary of today's trading activity for monitoring
        
        Returns:
            Summary dictionary
        """
        try:
            todays_trades = self.fetch_todays_webull_trades()
            
            summary = {
                'total_trades': len(todays_trades),
                'symbols_traded': len(set(t['symbol'] for t in todays_trades)),
                'buy_count': len([t for t in todays_trades if t['action'] == 'BUY']),
                'sell_count': len([t for t in todays_trades if t['action'] == 'SELL']),
                'potential_day_trades': 0,
                'symbols_with_day_trade_risk': [],
                'last_updated': datetime.now().isoformat()
            }
            
            # Analyze each symbol for day trade potential
            symbols = set(t['symbol'] for t in todays_trades)
            
            for symbol in symbols:
                symbol_trades = [t for t in todays_trades if t['symbol'] == symbol]
                has_buy = any(t['action'] == 'BUY' for t in symbol_trades)
                has_sell = any(t['action'] == 'SELL' for t in symbol_trades)
                
                if has_buy and has_sell:
                    summary['potential_day_trades'] += 1
                    summary['symbols_with_day_trade_risk'].append(symbol)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error generating day trading summary: {e}")
            return {'error': str(e)}


# Integration with automated_system.py
class EnhancedAutomatedTradingSystemWithDayTradeProtection:
    """
    Integration example showing how to use the enhanced day trading protection
    """
    
    def __init__(self):
        # ... existing initialization code ...
        
        # Add enhanced day trading protection
        self.day_trade_protection = EnhancedDayTradingProtection(
            self.wb, self.config, self.logger
        )
    
    def filter_signals_for_account(self, signals: List, account) -> List:
        """
        Enhanced signal filtering with live day trading protection
        """
        filtered_signals = []
        
        for signal in signals:
            # Use enhanced day trading check instead of basic one
            should_execute, reason = self.day_trade_protection.enhanced_should_execute_signal(
                signal, 
                current_positions=[pos['symbol'] for pos in account.positions],
                account_value=account.net_liquidation,
                account_id=account.account_id
            )
            
            if not should_execute:
                self.logger.debug(f"⚠️ {account.account_type}: Filtered {signal.symbol} - {reason}")
                continue
            
            # Apply other filters (position sizing, etc.)
            # ... existing filtering logic ...
            
            filtered_signals.append(signal)
        
        return filtered_signals
    
    def run_enhanced_automated_analysis(self):
        """
        Enhanced main analysis method with day trading protection
        """
        # ... existing code ...
        
        # Add day trading summary to logging
        try:
            dt_summary = self.day_trade_protection.get_day_trading_summary()
            self.logger.info("📊 Day Trading Summary:")
            self.logger.info(f"   Total trades today: {dt_summary['total_trades']}")
            self.logger.info(f"   Symbols traded: {dt_summary['symbols_traded']}")
            self.logger.info(f"   Potential day trades: {dt_summary['potential_day_trades']}")
            
            if dt_summary['symbols_with_day_trade_risk']:
                self.logger.warning(f"   ⚠️ Day trade risk symbols: {dt_summary['symbols_with_day_trade_risk']}")
        
        except Exception as e:
            self.logger.warning(f"Could not generate day trading summary: {e}")
        
        # ... continue with existing analysis ...

