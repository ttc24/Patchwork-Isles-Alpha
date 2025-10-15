#!/usr/bin/env python3
"""
Performance optimization script for Patchwork Isles.
Analyzes and optimizes game loading times, memory usage, and responsiveness.
"""

import json
import time
import sys
import gc
from pathlib import Path
from typing import Dict, List, Any
import tracemalloc
import cProfile
import pstats
from io import StringIO

def print_section(title: str):
    """Print a section header."""
    print(f"\\n🔧 {title}")
    print("─" * (len(title) + 4))

def measure_world_loading_time():
    """Measure world.json loading performance."""
    print_section("World Loading Performance")
    
    world_path = Path("world/world.json")
    if not world_path.exists():
        print("❌ world.json not found")
        return
    
    # Measure loading time
    start_time = time.perf_counter()
    
    try:
        with open(world_path, 'r', encoding='utf-8') as f:
            world_data = json.load(f)
        
        end_time = time.perf_counter()
        loading_time = end_time - start_time
        
        # Analyze content
        nodes_count = len(world_data.get('nodes', {}))
        starts_count = len(world_data.get('starts', []))
        file_size = world_path.stat().st_size / 1024 / 1024  # MB
        
        print(f"✅ World loading: {loading_time:.3f}s")
        print(f"   File size: {file_size:.2f} MB")
        print(f"   Nodes: {nodes_count}")
        print(f"   Start options: {starts_count}")
        
        if loading_time > 1.0:
            print("⚠️  Loading time is high. Consider:")
            print("   • Splitting world.json into modules")
            print("   • Using lazy loading for large content sections")
        
        return loading_time, world_data
        
    except Exception as e:
        print(f"❌ Error loading world: {e}")
        return None, None

def measure_memory_usage():
    """Measure memory usage during game operations."""
    print_section("Memory Usage Analysis")
    
    # Start memory tracing
    tracemalloc.start()
    
    # Load world data
    loading_time, world_data = measure_world_loading_time()
    if not world_data:
        return
    
    # Simulate game operations
    start_time = time.perf_counter()
    
    # Simulate multiple node traversals
    nodes = world_data.get('nodes', {})
    node_keys = list(nodes.keys())[:100]  # Test first 100 nodes
    
    for node_key in node_keys:
        node = nodes.get(node_key, {})
        choices = node.get('choices', [])
        # Simulate choice processing
        for choice in choices:
            condition = choice.get('condition')
            effects = choice.get('effects', [])
    
    end_time = time.perf_counter()
    processing_time = end_time - start_time
    
    # Get memory statistics
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"✅ Memory usage:")
    print(f"   Current: {current / 1024 / 1024:.2f} MB")
    print(f"   Peak: {peak / 1024 / 1024:.2f} MB")
    print(f"   Processing time: {processing_time:.3f}s")
    
    if peak > 50 * 1024 * 1024:  # 50MB
        print("⚠️  High memory usage detected. Consider:")
        print("   • Implementing object pooling")
        print("   • Using generators for large data sets")
        print("   • Clearing unused data structures")

def profile_engine_performance():
    """Profile engine performance using cProfile."""
    print_section("Engine Performance Profiling")
    
    try:
        # Add engine to path
        sys.path.insert(0, str(Path("engine")))
        
        # Import engine components
        try:
            import engine_min
        except ImportError:
            print("❌ Could not import engine_min")
            return
        
        # Profile a typical game session startup
        profiler = cProfile.Profile()
        
        print("🔍 Profiling engine startup...")
        profiler.enable()
        
        # Simulate engine operations
        try:
            world_path = Path("world/world.json")
            if world_path.exists():
                with open(world_path, 'r', encoding='utf-8') as f:
                    world_data = json.load(f)
                
                # Simulate GameState creation
                profile_data = engine_min.default_profile()
                
                # This would normally create a GameState, but we'll skip
                # the full initialization to avoid UI interactions
                
        except Exception as e:
            print(f"⚠️  Profiling limited due to: {e}")
        
        profiler.disable()
        
        # Analyze results
        stats_stream = StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats('cumulative').print_stats(10)
        
        profile_output = stats_stream.getvalue()
        print("📊 Top performance bottlenecks:")
        
        # Extract meaningful lines
        lines = profile_output.split('\\n')
        for line in lines:
            if 'function calls' in line or 'seconds' in line:
                print(f"   {line.strip()}")
        
        # Show top functions
        relevant_lines = [line for line in lines if any(keyword in line.lower() 
                         for keyword in ['json', 'load', 'read', 'parse'])][:5]
        
        if relevant_lines:
            print("🎯 Key functions:")
            for line in relevant_lines:
                if line.strip():
                    print(f"   {line.strip()}")
        
    except Exception as e:
        print(f"❌ Profiling error: {e}")

def optimize_world_structure():
    """Analyze and suggest world.json optimizations."""
    print_section("World Structure Optimization")
    
    world_path = Path("world/world.json")
    if not world_path.exists():
        print("❌ world.json not found")
        return
    
    try:
        with open(world_path, 'r', encoding='utf-8') as f:
            world_data = json.load(f)
        
        nodes = world_data.get('nodes', {})
        
        # Analyze node complexity
        complex_nodes = []
        large_text_nodes = []
        many_choices_nodes = []
        
        for node_id, node_data in nodes.items():
            if not isinstance(node_data, dict):
                continue
                
            text = node_data.get('text', '')
            choices = node_data.get('choices', [])
            
            # Check for complexity indicators
            if len(text) > 1000:
                large_text_nodes.append((node_id, len(text)))
            
            if len(choices) > 8:
                many_choices_nodes.append((node_id, len(choices)))
            
            # Overall complexity score
            complexity = len(text) + len(choices) * 100
            if complexity > 2000:
                complex_nodes.append((node_id, complexity))
        
        print(f"📊 World structure analysis:")
        print(f"   Total nodes: {len(nodes)}")
        print(f"   Complex nodes: {len(complex_nodes)}")
        print(f"   Large text nodes: {len(large_text_nodes)}")
        print(f"   Many choices nodes: {len(many_choices_nodes)}")
        
        # Suggestions
        if complex_nodes:
            print("\\n💡 Optimization suggestions:")
            print("   • Consider breaking complex nodes into smaller scenes")
            print("   • Use continuation nodes for long text passages")
            print("   • Group related choices into sub-menus")
        
        if large_text_nodes:
            print("   • Large text blocks found - consider pagination")
            
        if many_choices_nodes:
            print("   • High choice count nodes - consider categorization")
        
        # Check for potential memory issues
        total_text_length = sum(len(node.get('text', '')) for node in nodes.values())
        avg_text_length = total_text_length / len(nodes) if nodes else 0
        
        print(f"\\n📝 Content metrics:")
        print(f"   Total text: {total_text_length:,} characters")
        print(f"   Average per node: {avg_text_length:.0f} characters")
        
        if avg_text_length > 500:
            print("   ⚠️  Consider text compression or lazy loading")
        
    except Exception as e:
        print(f"❌ World analysis error: {e}")

def check_module_loading():
    """Check if modular content loading is beneficial."""
    print_section("Module Loading Analysis")
    
    modules_dir = Path("world/modules")
    if modules_dir.exists():
        module_files = list(modules_dir.glob("*.json"))
        print(f"✅ Found {len(module_files)} content modules")
        
        # Test module loading performance
        total_load_time = 0
        total_size = 0
        
        for module_file in module_files[:10]:  # Test first 10
            start_time = time.perf_counter()
            try:
                with open(module_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                end_time = time.perf_counter()
                load_time = end_time - start_time
                total_load_time += load_time
                total_size += module_file.stat().st_size
            except Exception:
                continue
        
        if module_files:
            avg_load_time = total_load_time / min(len(module_files), 10)
            avg_size = total_size / min(len(module_files), 10) / 1024  # KB
            
            print(f"   Average module load time: {avg_load_time:.4f}s")
            print(f"   Average module size: {avg_size:.1f} KB")
            
            if avg_load_time < 0.001:
                print("   ✅ Module loading is efficient")
            else:
                print("   ⚠️  Consider module optimization")
        
    else:
        print("ℹ️  No modules directory found")
        print("   Consider splitting world.json for better performance")

def run_performance_benchmarks():
    """Run comprehensive performance benchmarks."""
    print("🏁 Patchwork Isles Performance Analysis")
    print("=" * 50)
    
    # Force garbage collection before tests
    gc.collect()
    
    # Run all performance tests
    measure_world_loading_time()
    measure_memory_usage()
    check_module_loading()
    optimize_world_structure()
    profile_engine_performance()
    
    print_section("Performance Summary")
    print("✅ Performance analysis complete!")
    print("\\n💡 General optimization tips:")
    print("   • Use lazy loading for large content")
    print("   • Implement content caching")
    print("   • Consider module-based architecture")
    print("   • Optimize JSON parsing and validation")
    print("   • Monitor memory usage during long sessions")

def create_optimization_report():
    """Create a detailed optimization report."""
    report_path = Path("performance_report.txt")
    
    print(f"\\n📄 Creating optimization report: {report_path}")
    
    # Redirect stdout to capture output
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        run_performance_benchmarks()
        report_content = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    
    # Save report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"Patchwork Isles Performance Report\\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n")
        f.write("=" * 50 + "\\n\\n")
        f.write(report_content)
    
    print(f"✅ Report saved to: {report_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        create_optimization_report()
    else:
        run_performance_benchmarks()