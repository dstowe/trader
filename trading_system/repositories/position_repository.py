# repositories/position_repository.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from base_repository import BaseRepository

@dataclass
class PositionEntity:
    """Domain entity for positions"""
    id: Optional[int]
    account_id: str
    symbol: str
    quantity: float
    cost_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    last_updated: datetime

class PositionRepository(BaseRepository):
    """Repository for position data"""
    
    def save_positions(self, positions: List[PositionEntity]) -> int:
        """Bulk save positions"""
        command = """
            INSERT OR REPLACE INTO enhanced_position_history 
            (sync_date, account_id, account_type, symbol, quantity, cost_price, 
             current_price, market_value, unrealized_pnl, pnl_rate, last_open_time,
             account_value, settled_funds, is_fractional, is_buy_and_hold, enhanced_system)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        param_list = []
        for pos in positions:
            params = (
                pos.last_updated.strftime('%Y-%m-%d'),
                pos.account_id,
                'UNKNOWN',  # This should come from position entity
                pos.symbol,
                pos.quantity,
                pos.cost_price,
                pos.current_price,
                pos.market_value,
                pos.unrealized_pnl,
                0.0,  # pnl_rate calculation
                '',   # last_open_time
                0.0,  # account_value
                0.0,  # settled_funds
                1 if pos.quantity != int(pos.quantity) else 0,
                0,    # is_buy_and_hold
                1     # enhanced_system
            )
            param_list.append(params)
        
        return self.execute_many(command, param_list)
    
    def get_positions_by_account(self, account_id: str) -> List[PositionEntity]:
        """Get current positions for an account"""
        query = """
            SELECT account_id, symbol, quantity, cost_price, current_price,
                   market_value, unrealized_pnl, sync_date
            FROM enhanced_position_history 
            WHERE account_id = ? 
            AND sync_date = (SELECT MAX(sync_date) FROM enhanced_position_history WHERE account_id = ?)
        """
        rows = self.execute_query(query, (account_id, account_id))
        return [self._row_to_position_entity(row) for row in rows]
    
    def _row_to_position_entity(self, row: Dict) -> PositionEntity:
        """Convert database row to position entity"""
        return PositionEntity(
            id=None,
            account_id=row['account_id'],
            symbol=row['symbol'],
            quantity=row['quantity'],
            cost_price=row['cost_price'],
            current_price=row['current_price'],
            market_value=row['market_value'],
            unrealized_pnl=row['unrealized_pnl'],
            last_updated=datetime.fromisoformat(row['sync_date'])
        )
