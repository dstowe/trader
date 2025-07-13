# repositories/signal_repository.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SignalEntity:
    """Domain entity for trading signals"""
    id: Optional[int]
    symbol: str
    strategy: str
    signal_type: str
    price: float
    confidence: float
    timestamp: datetime
    metadata: Optional[str] = None

class SignalRepository(BaseRepository):
    """Repository for trading signals"""
    
    def save_signal(self, signal: SignalEntity) -> int:
        """Save a trading signal"""
        command = """
            INSERT INTO signals 
            (symbol, date, strategy, signal_type, price, confidence, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            signal.symbol,
            signal.timestamp.strftime('%Y-%m-%d'),
            signal.strategy,
            signal.signal_type,
            signal.price,
            signal.confidence,
            signal.metadata
        )
        return self.execute_command(command, params)
    
    def get_signals_by_date(self, date: str, limit: int = 100) -> List[SignalEntity]:
        """Get signals for a specific date"""
        query = """
            SELECT id, symbol, strategy, signal_type, price, confidence, 
                   date, metadata, created_at
            FROM signals 
            WHERE date = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        rows = self.execute_query(query, (date, limit))
        return [self._row_to_entity(row) for row in rows]
    
    def get_signals_by_symbol(self, symbol: str, limit: int = 50) -> List[SignalEntity]:
        """Get recent signals for a symbol"""
        query = """
            SELECT id, symbol, strategy, signal_type, price, confidence, 
                   date, metadata, created_at
            FROM signals 
            WHERE symbol = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        rows = self.execute_query(query, (symbol, limit))
        return [self._row_to_entity(row) for row in rows]
    
    def _row_to_entity(self, row: Dict) -> SignalEntity:
        """Convert database row to entity"""
        return SignalEntity(
            id=row['id'],
            symbol=row['symbol'],
            strategy=row['strategy'],
            signal_type=row['signal_type'],
            price=row['price'],
            confidence=row['confidence'],
            timestamp=datetime.fromisoformat(row['created_at']),
            metadata=row['metadata']
        )
