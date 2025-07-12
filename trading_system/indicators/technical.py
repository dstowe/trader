# indicators/technical.py
import pandas as pd
import numpy as np
from typing import Tuple, Dict

class TechnicalIndicators:
    """Technical indicator calculations including gap analysis"""
    
    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, 
                       num_std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        middle_band = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, 
            window: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = high - low
        high_close = (high - close.shift()).abs()
        low_close = (low - close.shift()).abs()
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=window).mean()
        return atr
    
    @staticmethod
    def calculate_all_indicators(data: pd.DataFrame, 
                               bb_period: int = 20, 
                               rsi_period: int = 14) -> pd.DataFrame:
        """Calculate all indicators for a dataset"""
        result = data.copy()
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.bollinger_bands(
            data['Close'], bb_period)
        result['bb_upper'] = bb_upper
        result['bb_middle'] = bb_middle
        result['bb_lower'] = bb_lower
        
        # RSI
        result['rsi'] = TechnicalIndicators.rsi(data['Close'], rsi_period)
        
        # ATR
        result['atr'] = TechnicalIndicators.atr(
            data['High'], data['Low'], data['Close'])
        
        return result
    
    @staticmethod
    def detect_gaps(data: pd.DataFrame) -> pd.Series:
        """
        Detect gaps by comparing open price to previous close
        
        Returns:
            Series with gap percentages (positive for gap up, negative for gap down)
        """
        if len(data) < 2:
            return pd.Series(dtype=float, index=data.index)
        
        prev_close = data['Close'].shift(1)
        current_open = data['Open']
        gap_percent = (current_open - prev_close) / prev_close
        
        return gap_percent
    
    @staticmethod
    def gap_volume_ratio(data: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Calculate volume ratio for gap days
        
        Returns:
            Series with current volume / average volume ratio
        """
        avg_volume = data['Volume'].rolling(window=window).mean()
        volume_ratio = data['Volume'] / avg_volume
        
        return volume_ratio
    
    @staticmethod
    def classify_gap(gap_percent: float, volume_ratio: float = 1.0) -> Dict[str, any]:
        """
        Classify gap by size and strength
        
        Args:
            gap_percent: Gap size as percentage (e.g., 0.02 for 2% gap up)
            volume_ratio: Current volume vs average volume
            
        Returns:
            Dictionary with gap classification
        """
        gap_size = abs(gap_percent)
        gap_direction = 'UP' if gap_percent > 0 else 'DOWN'
        
        # Size classification
        if gap_size < 0.01:
            size_class = 'SMALL'
        elif gap_size < 0.03:
            size_class = 'MEDIUM'
        elif gap_size < 0.05:
            size_class = 'LARGE'
        else:
            size_class = 'EXTREME'
        
        # Volume strength
        if volume_ratio > 2.0:
            volume_strength = 'VERY_HIGH'
        elif volume_ratio > 1.5:
            volume_strength = 'HIGH'
        elif volume_ratio > 1.0:
            volume_strength = 'NORMAL'
        else:
            volume_strength = 'LOW'
        
        # Overall gap quality
        quality_score = 0
        if size_class in ['MEDIUM', 'LARGE']:
            quality_score += 3
        elif size_class == 'SMALL':
            quality_score += 1
        
        if volume_strength in ['HIGH', 'VERY_HIGH']:
            quality_score += 2
        elif volume_strength == 'NORMAL':
            quality_score += 1
        
        if quality_score >= 4:
            quality = 'HIGH'
        elif quality_score >= 2:
            quality = 'MEDIUM'
        else:
            quality = 'LOW'
        
        return {
            'gap_percent': gap_percent,
            'gap_size': gap_size,
            'direction': gap_direction,
            'size_class': size_class,
            'volume_ratio': volume_ratio,
            'volume_strength': volume_strength,
            'quality': quality,
            'quality_score': quality_score
        }
    
    @staticmethod
    def gap_fill_progress(data: pd.DataFrame, gap_open: float, prev_close: float) -> float:
        """
        Calculate how much of a gap has been filled during the day
        
        Args:
            data: Intraday data for current trading session
            gap_open: Opening price (gap level)
            prev_close: Previous day's closing price
            
        Returns:
            Float between 0-1 representing gap fill percentage
        """
        if len(data) == 0:
            return 0.0
        
        current_price = data['Close'].iloc[-1]
        gap_size = abs(gap_open - prev_close)
        
        if gap_size == 0:
            return 0.0
        
        if gap_open > prev_close:  # Gap up
            fill_amount = max(0, gap_open - current_price)
        else:  # Gap down
            fill_amount = max(0, current_price - gap_open)
        
        fill_percentage = min(fill_amount / gap_size, 1.0)
        return fill_percentage
    
    @staticmethod
    def calculate_all_indicators_with_gaps(data: pd.DataFrame, 
                                         bb_period: int = 20, 
                                         rsi_period: int = 14,
                                         volume_window: int = 20) -> pd.DataFrame:
        """Calculate all indicators including gap analysis"""
        result = TechnicalIndicators.calculate_all_indicators(data, bb_period, rsi_period)
        
        # Add gap indicators
        result['gap_percent'] = TechnicalIndicators.detect_gaps(data)
        result['volume_ratio'] = TechnicalIndicators.gap_volume_ratio(data, volume_window)
        
        # Add gap size and direction columns
        result['gap_size'] = result['gap_percent'].abs()
        result['gap_direction'] = result['gap_percent'].apply(
            lambda x: 'UP' if x > 0 else 'DOWN' if x < 0 else 'NONE'
        )
        
        # Add gap significance flag (gaps > 1%)
        result['significant_gap'] = result['gap_size'] > 0.01
        
        return result
