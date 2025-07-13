# commands/base_command.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class CommandResult:
    """Standardized command result"""
    success: bool
    data: Any = None
    error_message: str = ""
    execution_time: float = 0.0

class Command(ABC):
    """Base command interface"""
    
    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command"""
        pass
    
    @abstractmethod
    def can_execute(self) -> bool:
        """Check if command can be executed"""
        pass
    
    def get_description(self) -> str:
        """Get human-readable description of command"""
        return self.__class__.__name__
    