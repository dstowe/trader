# services/data_service.py
class DataService:
    """Service layer that coordinates repository operations"""
    
    def __init__(self, signal_repo: SignalRepository, position_repo: PositionRepository):
        self.signal_repo = signal_repo
        self.position_repo = position_repo
    
    def save_trading_signals(self, signals: List[SignalEntity]) -> int:
        """Save multiple trading signals"""
        saved_count = 0
        for signal in signals:
            try:
                self.signal_repo.save_signal(signal)
                saved_count += 1
            except Exception as e:
                # Log error but continue processing other signals
                print(f"Failed to save signal for {signal.symbol}: {e}")
        return saved_count
    
    def get_account_summary(self, account_id: str) -> Dict:
        """Get comprehensive account summary"""
        positions = self.position_repo.get_positions_by_account(account_id)
        
        total_value = sum(pos.market_value for pos in positions)
        total_pnl = sum(pos.unrealized_pnl for pos in positions)
        
        return {
            'account_id': account_id,
            'total_positions': len(positions),
            'total_market_value': total_value,
            'total_unrealized_pnl': total_pnl,
            'positions': positions
        }