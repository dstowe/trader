# dependency_injection/container.py
from typing import Dict, Type, Any, Callable
from dataclasses import dataclass

@dataclass
class ServiceDefinition:
    """Service definition for dependency injection"""
    service_type: Type
    factory: Callable
    singleton: bool = True
    dependencies: list = None

class DIContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDefinition] = {}
        self._instances: Dict[Type, Any] = {}
    
    def register(self, service_type: Type, factory: Callable, 
                singleton: bool = True, dependencies: list = None):
        """Register a service"""
        self._services[service_type] = ServiceDefinition(
            service_type=service_type,
            factory=factory,
            singleton=singleton,
            dependencies=dependencies or []
        )
    
    def register_instance(self, service_type: Type, instance: Any):
        """Register an existing instance"""
        self._instances[service_type] = instance
    
    def get(self, service_type: Type) -> Any:
        """Get service instance"""
        # Return existing instance if singleton
        if service_type in self._instances:
            return self._instances[service_type]
        
        # Check if service is registered
        if service_type not in self._services:
            raise ValueError(f"Service {service_type} not registered")
        
        service_def = self._services[service_type]
        
        # Resolve dependencies
        dependencies = []
        for dep_type in service_def.dependencies:
            dependencies.append(self.get(dep_type))
        
        # Create instance
        instance = service_def.factory(*dependencies)
        
        # Store if singleton
        if service_def.singleton:
            self._instances[service_type] = instance
        
        return instance