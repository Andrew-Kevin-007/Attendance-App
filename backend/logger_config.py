"""Structured logging configuration for Face Attendance System"""
import logging
import sys
from datetime import datetime
from typing import Any, Dict
import json


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in structured JSON format.
    Easier for log aggregation and analysis tools.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        # Add custom fields if present
        for key in ['user_id', 'employee_id', 'endpoint', 'method', 'status_code', 'duration_ms']:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        
        return json.dumps(log_data)


class SimpleFormatter(logging.Formatter):
    """
    Simple human-readable formatter for development.
    """
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


def setup_logging(app_name: str = 'face_attendance', 
                  log_level: str = 'INFO',
                  use_json: bool = False,
                  log_file: str = None) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        app_name: Name of the application logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use structured JSON logging
        log_file: Optional path to log file
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Choose formatter
    formatter = StructuredFormatter() if use_json else SimpleFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to create log file handler: {e}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def log_request(logger: logging.Logger, 
                endpoint: str,
                method: str,
                user_id: str = None,
                status_code: int = None,
                duration_ms: float = None) -> None:
    """
    Log an HTTP request with structured data.
    
    Args:
        logger: Logger instance
        endpoint: API endpoint path
        method: HTTP method
        user_id: Optional user identifier
        status_code: Response status code
        duration_ms: Request duration in milliseconds
    """
    extra = {
        'endpoint': endpoint,
        'method': method
    }
    
    if user_id:
        extra['user_id'] = user_id
    if status_code:
        extra['status_code'] = status_code
    if duration_ms:
        extra['duration_ms'] = round(duration_ms, 2)
    
    log_level = logging.INFO
    if status_code:
        if status_code >= 500:
            log_level = logging.ERROR
        elif status_code >= 400:
            log_level = logging.WARNING
    
    message = f"{method} {endpoint}"
    if status_code:
        message += f" - {status_code}"
    if duration_ms:
        message += f" ({duration_ms:.2f}ms)"
    
    logger.log(log_level, message, extra=extra)


def log_face_recognition(logger: logging.Logger,
                         action: str,
                         employee_id: int = None,
                         employee_name: str = None,
                         confidence: float = None,
                         success: bool = True) -> None:
    """
    Log a face recognition event.
    
    Args:
        logger: Logger instance
        action: Action performed (register, recognize, etc.)
        employee_id: Employee ID
        employee_name: Employee name
        confidence: Recognition confidence score
        success: Whether the action succeeded
    """
    extra = {
        'action': action,
        'success': success
    }
    
    if employee_id:
        extra['employee_id'] = employee_id
    if employee_name:
        extra['employee_name'] = employee_name
    if confidence:
        extra['confidence'] = round(confidence, 4)
    
    message = f"Face {action}"
    if employee_name:
        message += f" - {employee_name}"
    if confidence:
        message += f" (confidence: {confidence:.2f})"
    
    logger.info(message, extra=extra)


def log_security_event(logger: logging.Logger,
                       event_type: str,
                       user_id: str = None,
                       ip_address: str = None,
                       details: str = None) -> None:
    """
    Log a security-related event.
    
    Args:
        logger: Logger instance
        event_type: Type of security event (failed_login, rate_limit, etc.)
        user_id: User identifier
        ip_address: IP address of the request
        details: Additional details
    """
    extra = {
        'event_type': event_type,
        'category': 'security'
    }
    
    if user_id:
        extra['user_id'] = user_id
    if ip_address:
        extra['ip_address'] = ip_address
    
    message = f"Security event: {event_type}"
    if details:
        message += f" - {details}"
    
    logger.warning(message, extra=extra)
