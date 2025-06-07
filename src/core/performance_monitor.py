"""Performance monitoring and optimization tools."""

import time
import psutil
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from functools import wraps
import json
import os
from datetime import datetime
import gc
import tracemalloc

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_before: float
    memory_after: float
    memory_peak: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self, enable_memory_tracking: bool = True, 
                 enable_cpu_tracking: bool = True,
                 save_to_file: bool = True,
                 output_dir: str = "logs"):
        """Initialize performance monitor.
        
        Args:
            enable_memory_tracking: Whether to track memory usage
            enable_cpu_tracking: Whether to track CPU usage
            save_to_file: Whether to save metrics to file
            output_dir: Directory to save performance logs
        """
        self.enable_memory_tracking = enable_memory_tracking
        self.enable_cpu_tracking = enable_cpu_tracking
        self.save_to_file = save_to_file
        self.output_dir = output_dir
        
        # Metrics storage
        self.metrics: List[PerformanceMetrics] = []
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Process monitoring
        self.process = psutil.Process()
        
        # Memory tracking
        if enable_memory_tracking:
            tracemalloc.start()
        
        # Create output directory
        if save_to_file:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Performance monitor initialized: memory={enable_memory_tracking}, "
                   f"cpu={enable_cpu_tracking}, save={save_to_file}")
    
    def start_operation(self, operation_name: str, **additional_data) -> str:
        """Start monitoring an operation.
        
        Args:
            operation_name: Name of the operation
            **additional_data: Additional data to track
            
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{operation_name}_{int(time.time() * 1000000)}"
        
        with self.lock:
            self.active_operations[operation_id] = {
                'name': operation_name,
                'start_time': time.time(),
                'memory_before': self._get_memory_usage(),
                'cpu_start': self._get_cpu_percent(),
                'additional_data': additional_data
            }
        
        logger.debug(f"Started monitoring operation: {operation_name} ({operation_id})")
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, 
                     error: Optional[str] = None, **additional_data) -> PerformanceMetrics:
        """End monitoring an operation.
        
        Args:
            operation_id: Operation ID from start_operation
            success: Whether the operation was successful
            error: Error message if operation failed
            **additional_data: Additional data to include
            
        Returns:
            Performance metrics for the operation
        """
        end_time = time.time()
        memory_after = self._get_memory_usage()
        
        with self.lock:
            if operation_id not in self.active_operations:
                logger.warning(f"Operation ID not found: {operation_id}")
                return None
            
            op_data = self.active_operations.pop(operation_id)
            
            # Calculate metrics
            duration = end_time - op_data['start_time']
            memory_peak = self._get_memory_peak()
            cpu_percent = self._get_cpu_percent()
            
            # Merge additional data
            all_additional_data = {**op_data['additional_data'], **additional_data}
            
            # Create metrics object
            metrics = PerformanceMetrics(
                operation_name=op_data['name'],
                start_time=op_data['start_time'],
                end_time=end_time,
                duration=duration,
                memory_before=op_data['memory_before'],
                memory_after=memory_after,
                memory_peak=memory_peak,
                cpu_percent=cpu_percent,
                success=success,
                error=error,
                additional_data=all_additional_data
            )
            
            # Store metrics
            self.metrics.append(metrics)
            
            # Save to file if enabled
            if self.save_to_file:
                self._save_metrics_to_file(metrics)
            
            logger.debug(f"Completed monitoring operation: {op_data['name']} "
                        f"(duration: {duration:.3f}s, memory: {memory_after:.1f}MB)")
            
            return metrics
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB.
        
        Returns:
            Memory usage in MB
        """
        if not self.enable_memory_tracking:
            return 0.0
        
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def _get_memory_peak(self) -> float:
        """Get peak memory usage in MB.
        
        Returns:
            Peak memory usage in MB
        """
        if not self.enable_memory_tracking or not tracemalloc.is_tracing():
            return 0.0
        
        try:
            current, peak = tracemalloc.get_traced_memory()
            return peak / 1024 / 1024
        except Exception:
            return 0.0
    
    def _get_cpu_percent(self) -> float:
        """Get current CPU usage percentage.
        
        Returns:
            CPU usage percentage
        """
        if not self.enable_cpu_tracking:
            return 0.0
        
        try:
            return self.process.cpu_percent()
        except Exception:
            return 0.0
    
    def _save_metrics_to_file(self, metrics: PerformanceMetrics):
        """Save metrics to file.
        
        Args:
            metrics: Performance metrics to save
        """
        try:
            filename = f"performance_{datetime.now().strftime('%Y%m%d')}.jsonl"
            filepath = os.path.join(self.output_dir, filename)
            
            metrics_dict = {
                'timestamp': datetime.now().isoformat(),
                'operation_name': metrics.operation_name,
                'duration': metrics.duration,
                'memory_before': metrics.memory_before,
                'memory_after': metrics.memory_after,
                'memory_peak': metrics.memory_peak,
                'cpu_percent': metrics.cpu_percent,
                'success': metrics.success,
                'error': metrics.error,
                'additional_data': metrics.additional_data
            }
            
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics_dict) + '\n')
                
        except Exception as e:
            logger.warning(f"Failed to save performance metrics: {e}")
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for all operations.
        
        Returns:
            Summary statistics dictionary
        """
        if not self.metrics:
            return {}
        
        # Group by operation name
        operations = {}
        for metric in self.metrics:
            name = metric.operation_name
            if name not in operations:
                operations[name] = []
            operations[name].append(metric)
        
        # Calculate statistics for each operation
        summary = {}
        for name, metrics_list in operations.items():
            durations = [m.duration for m in metrics_list]
            memory_usage = [m.memory_after - m.memory_before for m in metrics_list]
            success_count = sum(1 for m in metrics_list if m.success)
            
            summary[name] = {
                'total_calls': len(metrics_list),
                'success_rate': success_count / len(metrics_list) * 100,
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'total_duration': sum(durations),
                'avg_memory_change': sum(memory_usage) / len(memory_usage),
                'max_memory_usage': max(m.memory_after for m in metrics_list),
                'avg_cpu_percent': sum(m.cpu_percent for m in metrics_list) / len(metrics_list)
            }
        
        # Overall statistics
        all_durations = [m.duration for m in self.metrics]
        all_success = sum(1 for m in self.metrics if m.success)
        
        summary['overall'] = {
            'total_operations': len(self.metrics),
            'success_rate': all_success / len(self.metrics) * 100,
            'total_time': sum(all_durations),
            'avg_duration': sum(all_durations) / len(all_durations),
            'operations_per_second': len(self.metrics) / sum(all_durations) if sum(all_durations) > 0 else 0
        }
        
        return summary
    
    def get_slow_operations(self, threshold_seconds: float = 5.0) -> List[PerformanceMetrics]:
        """Get operations that took longer than threshold.
        
        Args:
            threshold_seconds: Duration threshold in seconds
            
        Returns:
            List of slow operations
        """
        return [m for m in self.metrics if m.duration > threshold_seconds]
    
    def get_memory_intensive_operations(self, threshold_mb: float = 100.0) -> List[PerformanceMetrics]:
        """Get operations that used more memory than threshold.
        
        Args:
            threshold_mb: Memory threshold in MB
            
        Returns:
            List of memory-intensive operations
        """
        return [m for m in self.metrics 
                if (m.memory_after - m.memory_before) > threshold_mb]
    
    def clear_metrics(self):
        """Clear all stored metrics."""
        with self.lock:
            self.metrics.clear()
            logger.info("Performance metrics cleared")
    
    def export_metrics(self, filename: str = None) -> str:
        """Export all metrics to JSON file.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_export_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_metrics': len(self.metrics),
            'summary': self.get_summary_statistics(),
            'metrics': [
                {
                    'operation_name': m.operation_name,
                    'start_time': m.start_time,
                    'duration': m.duration,
                    'memory_before': m.memory_before,
                    'memory_after': m.memory_after,
                    'memory_peak': m.memory_peak,
                    'cpu_percent': m.cpu_percent,
                    'success': m.success,
                    'error': m.error,
                    'additional_data': m.additional_data
                }
                for m in self.metrics
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Performance metrics exported to {filepath}")
        return filepath


def performance_monitor(monitor: PerformanceMonitor, operation_name: str = None):
    """Decorator for automatic performance monitoring.
    
    Args:
        monitor: PerformanceMonitor instance
        operation_name: Name of the operation (uses function name if None)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            operation_id = monitor.start_operation(op_name)
            
            try:
                result = func(*args, **kwargs)
                monitor.end_operation(operation_id, success=True)
                return result
            except Exception as e:
                monitor.end_operation(operation_id, success=False, error=str(e))
                raise
        
        return wrapper
    return decorator


class MemoryOptimizer:
    """Memory optimization utilities."""
    
    @staticmethod
    def optimize_memory():
        """Force garbage collection and memory optimization."""
        gc.collect()
        logger.debug("Memory optimization performed")
    
    @staticmethod
    def get_memory_info() -> Dict[str, float]:
        """Get detailed memory information.
        
        Returns:
            Memory information dictionary
        """
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024,
            'total_mb': psutil.virtual_memory().total / 1024 / 1024
        }
    
    @staticmethod
    def check_memory_threshold(threshold_percent: float = 80.0) -> bool:
        """Check if memory usage exceeds threshold.
        
        Args:
            threshold_percent: Memory usage threshold percentage
            
        Returns:
            True if memory usage exceeds threshold
        """
        memory_percent = psutil.virtual_memory().percent
        return memory_percent > threshold_percent
    
    @staticmethod
    def process_in_chunks(data: List[Any], chunk_size: int, 
                         processor: Callable[[List[Any]], Any]) -> List[Any]:
        """Process large datasets in chunks to optimize memory.
        
        Args:
            data: Data to process
            chunk_size: Size of each chunk
            processor: Function to process each chunk
            
        Returns:
            List of processed results
        """
        results = []
        
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            result = processor(chunk)
            results.append(result)
            
            # Force garbage collection after each chunk
            gc.collect()
        
        return results


class CacheManager:
    """Simple caching system for performance optimization."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """Initialize cache manager.
        
        Args:
            max_size: Maximum number of cached items
            ttl_seconds: Time to live for cached items
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        logger.info(f"Cache manager initialized: max_size={max_size}, ttl={ttl_seconds}s")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            if key not in self.cache:
                return None
            
            item = self.cache[key]
            
            # Check if expired
            if time.time() - item['timestamp'] > self.ttl_seconds:
                del self.cache[key]
                return None
            
            item['access_count'] += 1
            item['last_access'] = time.time()
            return item['value']
    
    def set(self, key: str, value: Any):
        """Set item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self.lock:
            # Remove oldest items if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            self.cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'last_access': time.time(),
                'access_count': 1
            }
    
    def _evict_oldest(self):
        """Evict oldest cache items."""
        if not self.cache:
            return
        
        # Sort by last access time and remove oldest 10%
        items = sorted(self.cache.items(), key=lambda x: x[1]['last_access'])
        evict_count = max(1, len(items) // 10)
        
        for i in range(evict_count):
            key = items[i][0]
            del self.cache[key]
    
    def clear(self):
        """Clear all cached items."""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Cache statistics dictionary
        """
        with self.lock:
            total_accesses = sum(item['access_count'] for item in self.cache.values())
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'total_accesses': total_accesses,
                'avg_accesses': total_accesses / len(self.cache) if self.cache else 0
            }