"""
PyDiagram - Command module

This module implements the Command pattern for undo/redo functionality.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable


class Command(ABC):
    """
    Abstract base class for all commands in the application.
    Implements the Command pattern for undo/redo functionality.
    """
    
    def __init__(self, description: str = ""):
        """
        Initialize a new command.
        
        Args:
            description: Human-readable description of the command
        """
        self._description = description
    
    @property
    def description(self) -> str:
        """Get the description of the command."""
        return self._description
    
    @abstractmethod
    def execute(self) -> None:
        """
        Execute the command.
        This method should perform the actual operation.
        """
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """
        Undo the command.
        This method should reverse the effects of execute().
        """
        pass
    
    def redo(self) -> None:
        """
        Redo the command.
        By default, this just calls execute() again.
        Override if a different behavior is needed.
        """
        self.execute()


class CommandManager:
    """
    Manages the execution, undoing, and redoing of commands.
    Maintains the command history and current position.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize a new command manager.
        
        Args:
            max_history: Maximum number of commands to keep in history
        """
        self._history: List[Command] = []
        self._position: int = -1
        self._max_history = max_history
        self._listeners: List[Callable[[str, Command], None]] = []
    
    def add_listener(self, listener: Callable[[str, Command], None]) -> None:
        """
        Add a listener to be notified of command events.
        
        Args:
            listener: Callback function that takes event_type and command
        """
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[str, Command], None]) -> None:
        """
        Remove a listener.
        
        Args:
            listener: The listener to remove
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _notify_listeners(self, event_type: str, command: Command) -> None:
        """
        Notify all listeners of a command event.
        
        Args:
            event_type: Type of event ('execute', 'undo', 'redo')
            command: The command involved
        """
        for listener in self._listeners:
            listener(event_type, command)
    
    def execute_command(self, command: Command) -> None:
        """
        Execute a command and add it to the history.
        
        Args:
            command: The command to execute
        """
        # If we're not at the end of the history, truncate it
        if self._position < len(self._history) - 1:
            self._history = self._history[:self._position + 1]
        
        # Execute the command
        command.execute()
        
        # Add to history
        self._history.append(command)
        self._position = len(self._history) - 1
        
        # Trim history if needed
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
            self._position = len(self._history) - 1
        
        # Notify listeners
        self._notify_listeners('execute', command)
    
    def undo(self) -> bool:
        """
        Undo the last executed command.
        
        Returns:
            True if a command was undone, False if there's nothing to undo
        """
        if self._position >= 0:
            command = self._history[self._position]
            command.undo()
            self._position -= 1
            self._notify_listeners('undo', command)
            return True
        return False
    
    def redo(self) -> bool:
        """
        Redo the last undone command.
        
        Returns:
            True if a command was redone, False if there's nothing to redo
        """
        if self._position < len(self._history) - 1:
            self._position += 1
            command = self._history[self._position]
            command.redo()
            self._notify_listeners('redo', command)
            return True
        return False
    
    def can_undo(self) -> bool:
        """
        Check if there are commands that can be undone.
        
        Returns:
            True if there are commands to undo, False otherwise
        """
        return self._position >= 0
    
    def can_redo(self) -> bool:
        """
        Check if there are commands that can be redone.
        
        Returns:
            True if there are commands to redo, False otherwise
        """
        return self._position < len(self._history) - 1
    
    def get_undo_description(self) -> Optional[str]:
        """
        Get the description of the command that would be undone.
        
        Returns:
            Description of the command or None if there's nothing to undo
        """
        if self.can_undo():
            return self._history[self._position].description
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """
        Get the description of the command that would be redone.
        
        Returns:
            Description of the command or None if there's nothing to redo
        """
        if self.can_redo():
            return self._history[self._position + 1].description
        return None
    
    def clear_history(self) -> None:
        """Clear the command history."""
        self._history.clear()
        self._position = -1
