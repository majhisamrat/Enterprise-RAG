"""
Backward compatibility forwarder for app configuration.
Main configuration is maintained in app.config.settings.
"""
from app.config.settings import Settings, settings

__all__ = ["Settings", "settings"]