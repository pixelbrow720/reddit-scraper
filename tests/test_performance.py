"""Tests for performance monitoring."""

import unittest
import tempfile
import os
import time
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.performance_monitor import PerformanceMonitor, performance_monitor, MemoryOptimizer, CacheManager


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for PerformanceMonitor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = PerformanceMonitor(
            enable_memory_tracking=True,
            enable_cpu_tracking=True,
            save_to_file=False,  # Don't save during tests
            output_dir=self.temp_dir
        )
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_start_end_operation(self):
        """Test starting and ending operation monitoring."""
        operation_id = self.monitor.start_operation("test_operation", test_param="value")
        
        self.assertIn(operation_id, self.monitor.active_operations)
        self.assertEqual(self.monitor.active_operations[operation_id]['name'], "test_operation")
        
        # Simulate some work
        time.sleep(0.1)
        
        metrics = self.monitor.end_operation(operation_id, success=True)
        
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.operation_name, "test_operation")
        self.assertTrue(metrics.success)
        self.assertGreater(metrics.duration, 0.05)  # Should be at least 0.05 seconds
        self.assertNotIn(operation_id, self.monitor.active_operations)
    
    def test_operation_failure(self):
        """Test handling operation failure."""
        operation_id = self.monitor.start_operation("failing_operation")
        
        metrics = self.monitor.end_operation(operation_id, success=False, error="Test error")
        
        self.assertFalse(metrics.success)
        self.assertEqual(metrics.error, "Test error")
    
    def test_performance_decorator(self):
        """Test performance monitoring decorator."""
        @performance_monitor(self.monitor, "decorated_function")
        def test_function(x, y):
            time.sleep(0.05)
            return x + y
        
        result = test_function(2, 3)
        
        self.assertEqual(result, 5)
        self.assertEqual(len(self.monitor.metrics), 1)
        self.assertEqual(self.monitor.metrics[0].operation_name, "decorated_function")
        self.assertTrue(self.monitor.metrics[0].success)
    
    def test_performance_decorator_exception(self):
        """Test performance decorator with exception."""
        @performance_monitor(self.monitor, "failing_function")
        def failing_function():
            time.sleep(0.05)
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            failing_function()
        
        self.assertEqual(len(self.monitor.metrics), 1)
        self.assertFalse(self.monitor.metrics[0].success)
        self.assertEqual(self.monitor.metrics[0].error, "Test error")
    
    def test_get_summary_statistics(self):
        """Test summary statistics generation."""
        # Add some test metrics
        for i in range(3):
            op_id = self.monitor.start_operation("test_op")
            time.sleep(0.01)
            self.monitor.end_operation(op_id, success=True)
        
        # Add a failed operation
        op_id = self.monitor.start_operation("test_op")
        self.monitor.end_operation(op_id, success=False, error="Test error")
        
        stats = self.monitor.get_summary_statistics()
        
        self.assertIn('test_op', stats)
        self.assertIn('overall', stats)
        
        test_op_stats = stats['test_op']
        self.assertEqual(test_op_stats['total_calls'], 4)
        self.assertEqual(test_op_stats['success_rate'], 75.0)  # 3/4 * 100
        
        overall_stats = stats['overall']
        self.assertEqual(overall_stats['total_operations'], 4)
        self.assertEqual(overall_stats['success_rate'], 75.0)
    
    def test_get_slow_operations(self):
        """Test getting slow operations."""
        # Add a fast operation
        op_id = self.monitor.start_operation("fast_op")
        time.sleep(0.01)
        self.monitor.end_operation(op_id, success=True)
        
        # Add a slow operation
        op_id = self.monitor.start_operation("slow_op")
        time.sleep(0.1)
        self.monitor.end_operation(op_id, success=True)
        
        slow_ops = self.monitor.get_slow_operations(threshold_seconds=0.05)
        
        self.assertEqual(len(slow_ops), 1)
        self.assertEqual(slow_ops[0].operation_name, "slow_op")
    
    def test_clear_metrics(self):
        """Test clearing metrics."""
        op_id = self.monitor.start_operation("test_op")
        self.monitor.end_operation(op_id, success=True)
        
        self.assertEqual(len(self.monitor.metrics), 1)
        
        self.monitor.clear_metrics()
        
        self.assertEqual(len(self.monitor.metrics), 0)


class TestMemoryOptimizer(unittest.TestCase):
    """Test cases for MemoryOptimizer."""
    
    def test_get_memory_info(self):
        """Test getting memory information."""
        memory_info = MemoryOptimizer.get_memory_info()
        
        self.assertIn('rss_mb', memory_info)
        self.assertIn('vms_mb', memory_info)
        self.assertIn('percent', memory_info)
        self.assertIn('available_mb', memory_info)
        self.assertIn('total_mb', memory_info)
        
        # Check that values are reasonable
        self.assertGreater(memory_info['rss_mb'], 0)
        self.assertGreater(memory_info['total_mb'], 0)
    
    def test_check_memory_threshold(self):
        """Test memory threshold checking."""
        # Test with very high threshold (should return False)
        result = MemoryOptimizer.check_memory_threshold(99.0)
        self.assertFalse(result)
        
        # Test with very low threshold (should return True)
        result = MemoryOptimizer.check_memory_threshold(1.0)
        self.assertTrue(result)
    
    def test_process_in_chunks(self):
        """Test processing data in chunks."""
        data = list(range(100))
        
        def sum_chunk(chunk):
            return sum(chunk)
        
        results = MemoryOptimizer.process_in_chunks(data, chunk_size=25, processor=sum_chunk)
        
        self.assertEqual(len(results), 4)  # 100 / 25 = 4 chunks
        self.assertEqual(sum(results), sum(data))  # Total should be the same


class TestCacheManager(unittest.TestCase):
    """Test cases for CacheManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = CacheManager(max_size=3, ttl_seconds=1)
    
    def test_set_and_get(self):
        """Test setting and getting cache values."""
        self.cache.set("key1", "value1")
        
        result = self.cache.get("key1")
        self.assertEqual(result, "value1")
    
    def test_get_nonexistent_key(self):
        """Test getting non-existent key."""
        result = self.cache.get("nonexistent")
        self.assertIsNone(result)
    
    def test_ttl_expiration(self):
        """Test TTL expiration."""
        self.cache.set("key1", "value1")
        
        # Should be available immediately
        result = self.cache.get("key1")
        self.assertEqual(result, "value1")
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired now
        result = self.cache.get("key1")
        self.assertIsNone(result)
    
    def test_max_size_eviction(self):
        """Test eviction when max size is reached."""
        # Fill cache to max size
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # Add one more item (should trigger eviction)
        self.cache.set("key4", "value4")
        
        # Cache should still have max_size items
        stats = self.cache.get_stats()
        self.assertLessEqual(stats['size'], 3)
    
    def test_access_count(self):
        """Test access count tracking."""
        self.cache.set("key1", "value1")
        
        # Access multiple times
        self.cache.get("key1")
        self.cache.get("key1")
        self.cache.get("key1")
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['total_accesses'], 3)
    
    def test_clear_cache(self):
        """Test clearing cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['size'], 2)
        
        self.cache.clear()
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['size'], 0)
    
    def test_get_stats(self):
        """Test getting cache statistics."""
        self.cache.set("key1", "value1")
        self.cache.get("key1")
        
        stats = self.cache.get_stats()
        
        self.assertIn('size', stats)
        self.assertIn('max_size', stats)
        self.assertIn('total_accesses', stats)
        self.assertIn('avg_accesses', stats)
        
        self.assertEqual(stats['size'], 1)
        self.assertEqual(stats['max_size'], 3)
        self.assertEqual(stats['total_accesses'], 1)


if __name__ == '__main__':
    unittest.main()