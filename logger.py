"""
Structured Logging and Monitoring System
Professional logging with performance tracking and alerting
"""

import logging
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import asyncio
import time
from config import config
from database import db


class StructuredLogger:
    """Professional structured logging system"""
    
    def __init__(self, name: str = "bot"):
        self.logger = logging.getLogger(name)
        self.setup_logger()
        
    def setup_logger(self):
        """Setup structured logging configuration"""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Console handler with structured format
        console_handler = logging.StreamHandler()
        console_formatter = StructuredFormatter()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_formatter = StructuredFormatter(include_extra=True)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self.logger.info(message, extra={'structured_data': kwargs})
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self.logger.warning(message, extra={'structured_data': kwargs})
    
    def error(self, message: str, exception: Exception = None, **kwargs):
        """Log error message with exception details"""
        if exception:
            kwargs['exception_type'] = type(exception).__name__
            kwargs['exception_message'] = str(exception)
            kwargs['traceback'] = traceback.format_exc()
        
        self.logger.error(message, extra={'structured_data': kwargs})
    
    def debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        self.logger.debug(message, extra={'structured_data': kwargs})


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def __init__(self, include_extra: bool = False):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record):
        """Format log record as structured JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add structured data if present
        if hasattr(record, 'structured_data'):
            log_entry['data'] = record.structured_data
        
        # Add extra fields if requested
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                              'pathname', 'filename', 'module', 'lineno', 
                              'funcName', 'created', 'msecs', 'relativeCreated', 
                              'thread', 'threadName', 'processName', 'process',
                              'structured_data']:
                    log_entry[f'extra_{key}'] = value
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics = {}
        self.logger = StructuredLogger("performance")
    
    def timing_decorator(self, func_name: str = None):
        """Decorator to measure function execution time"""
        def decorator(func):
            name = func_name or func.__name__
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self.record_timing(name, execution_time)
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.record_timing(name, execution_time, error=True)
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self.record_timing(name, execution_time)
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.record_timing(name, execution_time, error=True)
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def record_timing(self, operation: str, duration: float, error: bool = False):
        """Record timing metric"""
        metric_key = f"timing_{operation}"
        
        if metric_key not in self.metrics:
            self.metrics[metric_key] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'error_count': 0
            }
        
        metric = self.metrics[metric_key]
        metric['count'] += 1
        metric['total_time'] += duration
        metric['avg_time'] = metric['total_time'] / metric['count']
        metric['min_time'] = min(metric['min_time'], duration)
        metric['max_time'] = max(metric['max_time'], duration)
        
        if error:
            metric['error_count'] += 1
        
        # Log slow operations
        if duration > 5.0:  # More than 5 seconds
            self.logger.warning(
                f"Slow operation detected: {operation}",
                operation=operation,
                duration=duration,
                threshold=5.0
            )
    
    def increment_counter(self, counter_name: str, value: int = 1):
        """Increment a counter metric"""
        if counter_name not in self.metrics:
            self.metrics[counter_name] = 0
        self.metrics[counter_name] += value
        
        # Log significant events
        if self.metrics[counter_name] % 100 == 0:  # Every 100 increments
            self.logger.info(
                f"Counter milestone reached: {counter_name}",
                counter=counter_name,
                value=self.metrics[counter_name]
            )
    
    def gauge(self, gauge_name: str, value: float):
        """Set a gauge metric"""
        self.metrics[gauge_name] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics.clear()


class AlertManager:
    """Alert management system"""
    
    def __init__(self):
        self.alerts = []
        self.logger = StructuredLogger("alerts")
    
    def check_thresholds(self, metrics: Dict[str, Any]):
        """Check metrics against configured thresholds"""
        alerts = []
        
        # Check error rates
        if 'error_count' in metrics and 'total_operations' in metrics:
            error_rate = metrics['error_count'] / metrics['total_operations'] * 100
            if error_rate > 5.0:  # More than 5% error rate
                alerts.append({
                    'type': 'HIGH_ERROR_RATE',
                    'severity': 'WARNING',
                    'message': f'Error rate is {error_rate:.2f}% (threshold: 5%)',
                    'value': error_rate
                })
        
        # Check account health
        if 'disconnected_accounts' in metrics:
            disconnected_pct = metrics.get('disconnected_accounts', 0) / metrics.get('total_accounts', 1) * 100
            if disconnected_pct > 30:  # More than 30% accounts disconnected
                alerts.append({
                    'type': 'ACCOUNT_UNHEALTHY',
                    'severity': 'CRITICAL',
                    'message': f'{disconnected_pct:.1f}% of accounts are disconnected',
                    'value': disconnected_pct
                })
        
        # Check processing delays
        if 'avg_processing_time' in metrics:
            avg_time = metrics['avg_processing_time']
            if avg_time > 10.0:  # More than 10 seconds average
                alerts.append({
                    'type': 'HIGH_LATENCY',
                    'severity': 'WARNING',
                    'message': f'Average processing time is {avg_time:.2f}s',
                    'value': avg_time
                })
        
        # Process alerts
        for alert in alerts:
            self.process_alert(alert)
    
    def process_alert(self, alert: Dict[str, Any]):
        """Process and log alert"""
        self.alerts.append({
            **alert,
            'timestamp': datetime.now().isoformat()
        })
        
        # Log alert
        log_func = self.logger.error if alert['severity'] == 'CRITICAL' else self.logger.warning
        log_func(
            f"ALERT: {alert['type']} - {alert['message']}",
            alert_type=alert['type'],
            severity=alert['severity'],
            value=alert['value']
        )
        
        # Keep only recent alerts (last 100)
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_recent_alerts(self, hours: int = 24) -> list:
        """Get recent alerts"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        return [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']).timestamp() > cutoff_time
        ]


# Global instances
logger = StructuredLogger()
perf_monitor = PerformanceMonitor()
alert_manager = AlertManager()


# Convenience decorators
def timed(func_name: str = None):
    """Convenience decorator for timing"""
    return perf_monitor.timing_decorator(func_name)


def count_calls(counter_name: str):
    """Decorator to count function calls"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            perf_monitor.increment_counter(counter_name)
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            perf_monitor.increment_counter(counter_name)
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Integration with database for persistent logging
class DatabaseLogger:
    """Log events to database for analytics"""
    
    @staticmethod
    @timed("db_log_insert")
    async def log_event(event_type: str, severity: str, message: str, data: Dict = None):
        """Log event to database"""
        try:
            # This would insert into a logs table in the database
            db.save_statistic('logs', event_type, json.dumps({
                'severity': severity,
                'message': message,
                'data': data or {},
                'timestamp': datetime.now().isoformat()
            }))
        except Exception as e:
            # Don't let logging failures break the main application
            logger.error("Failed to log to database", exception=e)


# Initialize logging system
def setup_logging():
    """Initialize the complete logging system"""
    # Ensure database is ready
    try:
        # Test database connection by saving a startup log
        db.save_statistic('system', 'startup', datetime.now().isoformat())
        logger.info("Logging system initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize database logging: {e}")
    
    return logger, perf_monitor, alert_manager