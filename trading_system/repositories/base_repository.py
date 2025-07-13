# repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import sqlite3
from contextlib import contextmanager

class DatabaseConnection:
    """Database connection manager with proper resource handling"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        else:
            conn.commit()
        finally:
            conn.close()

class BaseRepository(ABC):
    """Base repository with common database operations"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SELECT query and return results"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_command(self, command: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE and return affected rows"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(command, params)
            return cursor.rowcount
    
    def execute_many(self, command: str, param_list: List[tuple]) -> int:
        """Execute command with multiple parameter sets"""
        with self.db.get_connection() as conn:
            cursor = conn.executemany(command, param_list)
            return cursor.rowcount