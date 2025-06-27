# strategies/policy_momentum.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, time, timedelta
import json

class PolicyMomentumStrategy:
    """
    Policy-Volatility Momentum Strategy
    
    Handles Fed-driven volatility and policy uncertainty through
    systematic momentum capture with enhanced risk controls
    """
    
    def __init__(self, config):
        self.config = config
        self.name = "PolicyMomentum"
        
        # Policy timing parameters
        self.policy_window_start = time(9, 30)
        self.policy_window_end = time(11, 30)  # First 2 hours for policy impact
        
        # Technical parameters
        self.min_policy_move = 0.03  # 3% minimum move on policy news
        self.volume_multiplier = 2.0  # 2x average volume required
        self.adx_threshold = 25      # ADX above 25 for trend strength
        
        # Policy event tracking
        self.fed_meeting_days = []  # Would be populated with Fed calendar
        self.fomc_announcement_times = [time(14, 0)]  # 2:00 PM ET typical
        
        # Risk management
        self.max_position_hold_hours = 4  # Maximum 4-hour holds
        self.policy_stop_multiplier = 1.5  # Wider stops for policy volatility
        self.max_risk_per_trade = 0.02    # 2% max risk
        
    def generate_signals(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """Generate policy momentum signals"""
        signals = []
        
        if len(data) < 30:
            return signals
            
        latest = data.iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')
        
        # Check if we're in policy-sensitive time window
        if not self._is_policy_window():
            return signals
            
        # Calculate technical indicators
        adx = self._calculate_adx(data)
        volume_ratio = self._calculate_volume_ratio(data)
        policy_move = self._detect_policy_move(data)
        
        # Check for policy momentum setup
        momentum_signal = self._check_policy_momentum(
            data, latest, adx, volume_ratio, policy_move)
        
        if momentum_signal:
            momentum_signal.update({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'price': latest['Close']
            })
            signals.append(momentum_signal)
            
        # Check for policy reversal setup
        reversal_signal = self._check_policy_reversal(
            data, latest, adx, volume_ratio, policy_move)
        
        if reversal_signal:
            reversal_signal.update({
                'symbol': symbol,
                'date': latest_date,
                'strategy': self.name,
                'price': latest['Close']
            })
            signals.append(reversal_signal)
            
        return signals
    
    def _is_policy_window(self) -> bool:
        """Check if we're in policy-sensitive trading window"""
        current_time = datetime.now().time()
        
        # Always active during morning policy window
        if self.policy_window_start <= current_time <= self.policy_window_end:
            return True
            
        # Active around FOMC announcement times
        for announce_time in self.fomc_announcement_times:
            window_start = (datetime.combine(datetime.today(), announce_time) - 
                          timedelta(minutes=30)).time()
            window_end = (datetime.combine(datetime.today(), announce_time) + 
                        timedelta(hours=2)).time()
            
            if window_start <= current_time <= window_end:
                return True
                
        return False
    
    def _calculate_adx(self, data: pd.DataFrame, periods: int = 14) -> float:
        """Calculate Average Directional Index (ADX) for trend strength"""
        if len(data) < periods * 2:
            return 0.0
            
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate Directional Movement
        plus_dm = (high - high.shift()).where((high - high.shift()) > (low.shift() - low), 0)
        minus_dm = (low.shift() - low).where((low.shift() - low) > (high - high.shift()), 0)
        
        # Smooth the values
        tr_smooth = tr.rolling(periods).mean()
        plus_dm_smooth = plus_dm.rolling(periods).mean()
        minus_dm_smooth = minus_dm.rolling(periods).mean()
        
        # Calculate Directional Indicators
        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)
        
        # Calculate ADX
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        adx = dx.rolling(periods).mean()
        
        return adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0.0
    
    def _calculate_volume_ratio(self, data: pd.DataFrame, periods: int = 20) -> float:
        """Calculate current volume vs average volume"""
        if len(data) < periods:
            return 1.0
            
        current_volume = data['Volume'].iloc[-1]
        avg_volume = data['Volume'].tail(periods).mean()
        
        return current_volume / avg_volume if avg_volume > 0 else 1.0
    
    def _detect_policy_move(self, data: pd.DataFrame) -> Dict:
        """Detect if recent price action suggests policy-driven move"""
        if len(data) < 5:
            return {'detected': False, 'magnitude': 0, 'direction': 'none'}
            
        # Look at recent 5-period move
        recent_data = data.tail(5)
        
        # Calculate move from first to last
        start_price = recent_data['Close'].iloc[0]
        current_price = recent_data['Close'].iloc[-1]
        move_pct = (current_price - start_price) / start_price
        
        # Check for sudden volume spike
        recent_volume = recent_data['Volume'].mean()
        historical_volume = data['Volume'].tail(20).mean()
        volume_spike = recent_volume / historical_volume > 1.5
        
        # Determine if this looks like policy move
        is_policy_move = (
            abs(move_pct) >= self.min_policy_move and
            volume_spike
        )
        
        return {
            'detected': is_policy_move,
            'magnitude': abs(move_pct),
            'direction': 'up' if move_pct > 0 else 'down',
            'volume_spike': volume_spike
        }
    
    def _check_policy_momentum(self, data: pd.DataFrame, latest: pd.Series,
                             adx: float, volume_ratio: float, 
                             policy_move: Dict) -> Optional[Dict]:
        """Check for policy momentum continuation setup"""
        
        # Must have strong trend and volume
        if adx < self.adx_threshold or volume_ratio < self.volume_multiplier:
            return None
            
        # Must have detected policy move
        if not policy_move['detected']:
            return None
            
        current_price = latest['Close']
        
        # Calculate momentum indicators
        rsi = self._calculate_rsi(data['Close'])
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(data['Close'])
        
        # Bullish momentum setup
        if (policy_move['direction'] == 'up' and
            current_price > bb_middle and
            50 < rsi < 80):  # Momentum but not overbought
            
            # Calculate risk/reward
            atr = self._calculate_atr(data)
            stop_price = current_price - (atr * self.policy_stop_multiplier)
            target_price = current_price + (atr * 3)  # 2:1 ratio with wider stop
            
            risk = current_price - stop_price
            reward = target_price - current_price
            
            if risk > 0 and (reward / risk) >= 1.5:  # Lower ratio for policy trades
                confidence = self._calculate_momentum_confidence(
                    adx, volume_ratio, policy_move, rsi)
                
                return {
                    'signal_type': 'BUY',
                    'confidence': confidence,
                    'metadata': json.dumps({
                        'pattern': 'policy_momentum_continuation',
                        'policy_move_magnitude': policy_move['magnitude'],
                        'policy_direction': policy_move['direction'],
                        'adx': adx,
                        'rsi': rsi,
                        'volume_ratio': volume_ratio,
                        'bb_position': (current_price - bb_lower) / (bb_upper - bb_lower),
                        'stop_price': stop_price,
                        'target_price': target_price,
                        'risk_reward_ratio': reward / risk,
                        'strategy_logic': 'policy_momentum_trend'
                    })
                }
                
        return None
    
    def _check_policy_reversal(self, data: pd.DataFrame, latest: pd.Series,
                             adx: float, volume_ratio: float,
                             policy_move: Dict) -> Optional[Dict]:
        """Check for policy-driven reversal setup"""
        
        # Must have volume confirmation
        if volume_ratio < self.volume_multiplier:
            return None
            
        # Must have detected strong policy move
        if not policy_move['detected'] or policy_move['magnitude'] < 0.05:
            return None
            
        current_price = latest['Close']
        
        # Calculate reversal indicators
        rsi = self._calculate_rsi(data['Close'])
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(data['Close'])
        
        # Look for oversold reversal after policy selloff
        if (policy_move['direction'] == 'down' and
            current_price <= bb_lower and
            rsi < 30):  # Oversold condition
            
            # Additional confirmation: look for bullish divergence or hammer
            recent_lows = data['Low'].tail(3).min()
            showing_support = current_price > recent_lows
            
            if showing_support:
                # Calculate risk/reward for reversal
                atr = self._calculate_atr(data)
                stop_price = current_price - (atr * 1.0)  # Tighter stop for reversals
                target_price = bb_middle  # Target back to middle band
                
                risk = current_price - stop_price
                reward = target_price - current_price
                
                if risk > 0 and (reward / risk) >= 2.0:
                    confidence = self._calculate_reversal_confidence(
                        volume_ratio, policy_move, rsi, current_price, bb_lower)
                    
                    return {
                        'signal_type': 'BUY',
                        'confidence': confidence,
                        'metadata': json.dumps({
                            'pattern': 'policy_reversal_oversold',
                            'policy_move_magnitude': policy_move['magnitude'],
                            'policy_direction': policy_move['direction'],
                            'rsi': rsi,
                            'volume_ratio': volume_ratio,
                            'bb_position': (current_price - bb_lower) / (bb_upper - bb_lower),
                            'showing_support': showing_support,
                            'stop_price': stop_price,
                            'target_price': target_price,
                            'risk_reward_ratio': reward / risk,
                            'strategy_logic': 'policy_reversal_oversold'
                        })
                    }
                    
        return None
    
    def _calculate_rsi(self, prices: pd.Series, periods: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < periods + 1:
            return 50.0
            
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(periods).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _calculate_bollinger_bands(self, prices: pd.Series, periods: int = 20, 
                                 std_dev: float = 2) -> tuple:
        """Calculate Bollinger Bands"""
        if len(prices) < periods:
            mid = prices.iloc[-1]
            return mid, mid, mid
            
        middle = prices.rolling(periods).mean()
        std = prices.rolling(periods).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper.iloc[-1], middle.iloc[-1], lower.iloc[-1]
    
    def _calculate_atr(self, data: pd.DataFrame, periods: int = 14) -> float:
        """Calculate Average True Range"""
        if len(data) < periods + 1:
            return 0.0
            
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        tr1 = high - low
        tr2 = (high - close.shift()).abs()
        tr3 = (low - close.shift()).abs()
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(periods).mean().iloc[-1]
        
        return atr if not pd.isna(atr) else 0.0
    
    def _calculate_momentum_confidence(self, adx: float, volume_ratio: float,
                                     policy_move: Dict, rsi: float) -> float:
        """Calculate confidence for momentum signals"""
        confidence = 0.5
        
        # Strong trend strength
        if adx > 40:
            confidence += 0.3
        elif adx > 30:
            confidence += 0.2
            
        # High volume confirmation
        if volume_ratio > 3.0:
            confidence += 0.2
        elif volume_ratio > 2.0:
            confidence += 0.1
            
        # Strong policy move
        if policy_move['magnitude'] > 0.05:
            confidence += 0.2
        elif policy_move['magnitude'] > 0.03:
            confidence += 0.1
            
        # RSI in momentum zone
        if 55 <= rsi <= 75:
            confidence += 0.1
            
        return min(confidence, 1.0)
    
    def _calculate_reversal_confidence(self, volume_ratio: float, policy_move: Dict,
                                     rsi: float, current_price: float, bb_lower: float) -> float:
        """Calculate confidence for reversal signals"""
        confidence = 0.5
        
        # Volume confirmation
        if volume_ratio > 2.5:
            confidence += 0.2
        elif volume_ratio > 2.0:
            confidence += 0.1
            
        # Strong oversold
        if rsi < 25:
            confidence += 0.3
        elif rsi < 30:
            confidence += 0.2
            
        # Extreme policy move creating opportunity
        if policy_move['magnitude'] > 0.06:
            confidence += 0.2
        elif policy_move['magnitude'] > 0.04:
            confidence += 0.1
            
        # Price near/below lower Bollinger Band
        distance_below_bb = (bb_lower - current_price) / current_price
        if distance_below_bb > 0.01:  # 1% below band
            confidence += 0.2
            
        return min(confidence, 1.0)
    
    def is_fed_day(self, date: datetime) -> bool:
        """Check if given date is a Fed meeting day"""
        # This would be populated with actual Fed calendar
        # For now, assume we check against known dates
        return date.date() in self.fed_meeting_days
    
    def calculate_position_size(self, account_value: float, entry_price: float,
                              stop_price: float, policy_volatility: bool = True) -> int:
        """Calculate position size with policy volatility adjustment"""
        base_risk = account_value * self.max_risk_per_trade
        
        # Reduce position size during high policy volatility
        if policy_volatility:
            base_risk *= 0.75  # 25% reduction for policy trades
            
        risk_per_share = entry_price - stop_price
        
        if risk_per_share <= 0:
            return 0
            
        shares = int(base_risk / risk_per_share)
        return max(shares, 1) if shares > 0 else 0