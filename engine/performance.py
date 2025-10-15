#!/usr/bin/env python3
"""
Performance monitoring and benchmarking for Patchwork Isles engine.
Provides profiling, benchmarking, and memory monitoring capabilities.
"""

import json
import logging
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
import sys
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger("patchwork_isles.performance")


@dataclass
class PerformanceMetric:
    """Represents a single performance measurement."""
    name: str
    value: float
    unit: str
    timestamp: str
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""
    name: str
    duration_seconds: float
    memory_peak_mb: float
    memory_current_mb: float
    metrics: List[PerformanceMetric]
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "metrics": [m.to_dict() for m in self.metrics]
        }


class PerformanceMonitor:
    """Monitor and collect performance metrics."""
    
    def __init__(self):
        self.metrics = []
        self.start_time = None
        self.memory_tracer_active = False
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        tracemalloc.start()
        self.memory_tracer_active = True
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return summary."""
        if not self.memory_tracer_active:
            logger.warning("Monitoring not active")
            return {}
        
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.memory_tracer_active = False
        
        summary = {
            "duration_seconds": duration,
            "memory_peak_mb": peak / 1024 / 1024,
            "memory_current_mb": current / 1024 / 1024,
            "metrics_collected": len(self.metrics)
        }
        
        logger.info(f"Monitoring stopped: {summary}")
        return summary
    
    def record_metric(self, name: str, value: float, unit: str, context: Dict[str, Any] = None):
        """Record a performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now().isoformat(),
            context=context or {}
        )
        self.metrics.append(metric)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system performance info."""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available"}
        
        try:
            process = psutil.Process()
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "system_cpu_percent": psutil.cpu_percent(),
                "system_memory_percent": psutil.virtual_memory().percent
            }
        except Exception as e:
            logger.warning(f"Could not get system info: {e}")
            return {}
    
    @contextmanager
    def timed_operation(self, operation_name: str, context: Dict[str, Any] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        start_memory = self._get_current_memory()
        
        try:
            yield
            success = True
            error = None
        except Exception as e:
            success = False
            error = str(e)
            raise
        finally:
            end_time = time.time()
            end_memory = self._get_current_memory()
            
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            
            self.record_metric(
                f"{operation_name}_duration",
                duration,
                "seconds",
                {**(context or {}), "success": success, "error": error}
            )
            
            if memory_delta != 0:
                self.record_metric(
                    f"{operation_name}_memory_delta",
                    memory_delta,
                    "mb",
                    context
                )
    
    def _get_current_memory(self) -> float:
        """Get current memory usage in MB."""
        if not PSUTIL_AVAILABLE:
            return 0
        try:
            return psutil.Process().memory_info().rss / 1024 / 1024
        except:
            return 0


class GameBenchmark:
    """Benchmark game engine operations."""
    
    def __init__(self, world_data: Dict[str, Any]):
        self.world_data = world_data
        self.monitor = PerformanceMonitor()
    
    def benchmark_world_loading(self, world_path: Path) -> BenchmarkResult:
        """Benchmark world data loading performance."""
        self.monitor.start_monitoring()
        metrics = []
        error = None
        
        try:
            with self.monitor.timed_operation("world_load"):
                start_time = time.time()
                with open(world_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                load_time = time.time() - start_time
                
                # Record specific metrics
                self.monitor.record_metric("file_size", world_path.stat().st_size, "bytes")
                self.monitor.record_metric("nodes_count", len(data.get("nodes", {})), "count")
                self.monitor.record_metric("starts_count", len(data.get("starts", [])), "count")
                
            success = True
        except Exception as e:
            success = False
            error = str(e)
        
        summary = self.monitor.stop_monitoring()
        
        return BenchmarkResult(
            name="world_loading",
            duration_seconds=summary.get("duration_seconds", 0),
            memory_peak_mb=summary.get("memory_peak_mb", 0),
            memory_current_mb=summary.get("memory_current_mb", 0),
            metrics=self.monitor.metrics,
            success=success,
            error=error
        )
    
    def benchmark_node_traversal(self, num_steps: int = 100) -> BenchmarkResult:
        """Benchmark node traversal performance."""
        self.monitor.start_monitoring()
        error = None
        
        try:
            # Simulate traversing nodes
            nodes = self.world_data.get("nodes", {})
            if not nodes:
                raise ValueError("No nodes available for traversal")
            
            node_ids = list(nodes.keys())
            
            with self.monitor.timed_operation("node_traversal", {"steps": num_steps}):
                for i in range(num_steps):
                    # Pick a random node and access its data
                    node_id = node_ids[i % len(node_ids)]
                    node_data = nodes[node_id]
                    
                    # Access common fields to simulate real usage
                    choices = node_data.get("choices", [])
                    text = node_data.get("text", "")
                    
                    # Record per-step metrics occasionally
                    if i % 10 == 0:
                        self.monitor.record_metric("choices_in_node", len(choices), "count", 
                                                 {"node_id": node_id, "step": i})
            
            success = True
        except Exception as e:
            success = False
            error = str(e)
        
        summary = self.monitor.stop_monitoring()
        
        return BenchmarkResult(
            name="node_traversal",
            duration_seconds=summary.get("duration_seconds", 0),
            memory_peak_mb=summary.get("memory_peak_mb", 0),
            memory_current_mb=summary.get("memory_current_mb", 0),
            metrics=self.monitor.metrics,
            success=success,
            error=error
        )
    
    def benchmark_save_operations(self, num_saves: int = 10) -> BenchmarkResult:
        """Benchmark save/load operations."""
        try:
            from engine.engine_min import GameState, default_profile
            from engine.settings import Settings
        except ImportError:
            # Handle case when running as script
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from engine.engine_min import GameState, default_profile
            from engine.settings import Settings
        import tempfile
        
        self.monitor.start_monitoring()
        error = None
        
        try:
            # Set up game state
            profile = default_profile()
            settings = Settings()
            temp_dir = tempfile.mkdtemp()
            profile_path = os.path.join(temp_dir, "benchmark_profile.json")
            
            game_state = GameState(self.world_data, profile, profile_path, settings)
            
            # Benchmark save operations
            with self.monitor.timed_operation("save_operations", {"num_saves": num_saves}):
                for i in range(num_saves):
                    # Modify game state to make saves different
                    game_state.player["flags"][f"benchmark_flag_{i}"] = True
                    game_state.player["inventory"].append(f"benchmark_item_{i}")
                    
                    # Time individual save
                    start_time = time.time()
                    # Simulate save operation (simplified)
                    save_data = {
                        "player": game_state.player,
                        "current_node": game_state.current_node,
                        "history": game_state.history[:10]  # Limit history for benchmark
                    }
                    save_json = json.dumps(save_data, indent=2)
                    save_time = time.time() - start_time
                    
                    self.monitor.record_metric("individual_save_time", save_time, "seconds",
                                             {"save_number": i, "save_size": len(save_json)})
            
            # Cleanup
            try:
                os.remove(profile_path)
                os.rmdir(temp_dir)
            except:
                pass
                
            success = True
        except Exception as e:
            success = False
            error = str(e)
        
        summary = self.monitor.stop_monitoring()
        
        return BenchmarkResult(
            name="save_operations",
            duration_seconds=summary.get("duration_seconds", 0),
            memory_peak_mb=summary.get("memory_peak_mb", 0),
            memory_current_mb=summary.get("memory_current_mb", 0),
            metrics=self.monitor.metrics,
            success=success,
            error=error
        )
    
    def benchmark_choice_processing(self, num_choices: int = 1000) -> BenchmarkResult:
        """Benchmark choice condition evaluation."""
        self.monitor.start_monitoring()
        error = None
        
        try:
            # Find nodes with choices that have conditions
            nodes_with_conditions = []
            for node_id, node_data in self.world_data.get("nodes", {}).items():
                choices = node_data.get("choices", [])
                for choice in choices:
                    if choice.get("condition"):
                        nodes_with_conditions.append((node_id, choice))
                        break
            
            if not nodes_with_conditions:
                # Create test conditions if none exist
                test_conditions = [
                    {"type": "has_tag", "value": "Scout"},
                    {"type": "has_item", "value": "test_item"},
                    {"type": "rep_at_least", "faction": "Test Faction", "value": 1}
                ]
                nodes_with_conditions = [(f"test_node_{i}", {"condition": cond}) 
                                       for i, cond in enumerate(test_conditions)]
            
            with self.monitor.timed_operation("choice_processing", {"num_choices": num_choices}):
                for i in range(num_choices):
                    node_id, choice = nodes_with_conditions[i % len(nodes_with_conditions)]
                    condition = choice.get("condition", {})
                    
                    # Simulate condition evaluation
                    condition_type = condition.get("type")
                    condition_value = condition.get("value")
                    
                    # Record processing time for different condition types
                    start_time = time.time()
                    
                    # Simplified condition evaluation
                    if condition_type == "has_tag":
                        result = condition_value in ["Scout", "Emissary"]  # Simulate check
                    elif condition_type == "has_item":
                        result = condition_value == "test_item"
                    elif condition_type == "rep_at_least":
                        result = True  # Simulate reputation check
                    else:
                        result = False
                    
                    eval_time = time.time() - start_time
                    
                    if i % 100 == 0:  # Record every 100th evaluation
                        self.monitor.record_metric("condition_eval_time", eval_time, "seconds",
                                                 {"type": condition_type, "result": result})
            
            success = True
        except Exception as e:
            success = False
            error = str(e)
        
        summary = self.monitor.stop_monitoring()
        
        return BenchmarkResult(
            name="choice_processing",
            duration_seconds=summary.get("duration_seconds", 0),
            memory_peak_mb=summary.get("memory_peak_mb", 0),
            memory_current_mb=summary.get("memory_current_mb", 0),
            metrics=self.monitor.metrics,
            success=success,
            error=error
        )


def run_performance_suite(world_path: Path) -> Dict[str, Any]:
    """
    Run a comprehensive performance benchmark suite.
    
    Args:
        world_path: Path to world.json file
    
    Returns:
        Dictionary with all benchmark results
    """
    print("Loading world data for benchmarking...")
    with open(world_path, 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    benchmark = GameBenchmark(world_data)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "world_path": str(world_path),
        "world_size_mb": world_path.stat().st_size / 1024 / 1024,
        "benchmarks": {}
    }
    
    # Run benchmarks
    benchmarks_to_run = [
        ("world_loading", lambda: benchmark.benchmark_world_loading(world_path)),
        ("node_traversal", lambda: benchmark.benchmark_node_traversal(100)),
        ("save_operations", lambda: benchmark.benchmark_save_operations(5)),
        ("choice_processing", lambda: benchmark.benchmark_choice_processing(500))
    ]
    
    for name, benchmark_func in benchmarks_to_run:
        print(f"Running {name} benchmark...")
        try:
            result = benchmark_func()
            results["benchmarks"][name] = result.to_dict()
            print(f"  ✓ {name}: {result.duration_seconds:.3f}s, {result.memory_peak_mb:.1f}MB peak")
        except Exception as e:
            print(f"  ✗ {name} failed: {e}")
            results["benchmarks"][name] = {
                "success": False,
                "error": str(e),
                "duration_seconds": 0,
                "memory_peak_mb": 0
            }
    
    # Summary statistics
    successful_benchmarks = [b for b in results["benchmarks"].values() if b.get("success", False)]
    total_time = sum(b["duration_seconds"] for b in successful_benchmarks)
    max_memory = max((b["memory_peak_mb"] for b in successful_benchmarks), default=0)
    
    results["summary"] = {
        "total_benchmarks": len(benchmarks_to_run),
        "successful_benchmarks": len(successful_benchmarks),
        "total_time_seconds": total_time,
        "max_memory_mb": max_memory,
        "success_rate": len(successful_benchmarks) / len(benchmarks_to_run) if benchmarks_to_run else 0
    }
    
    return results


def save_performance_report(results: Dict[str, Any], output_path: Path):
    """Save performance report to file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        f.write('\n')
    print(f"Performance report saved to {output_path}")


if __name__ == "__main__":
    # Basic performance test when run directly
    world_path = Path(__file__).parent.parent / "world" / "world.json"
    if world_path.exists():
        results = run_performance_suite(world_path)
        
        # Save report
        report_path = Path(__file__).parent.parent / "logs" / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        save_performance_report(results, report_path)
    else:
        print(f"World file not found at {world_path}")