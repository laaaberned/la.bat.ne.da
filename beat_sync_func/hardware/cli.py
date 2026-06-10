"""
CLI for hardware detection and optimization.
"""

import click
from loguru import logger
from beat_sync_func.hardware.detector import HardwareDetector
from beat_sync_func.hardware.optimizer import HardwareOptimizer
from beat_sync_func.hardware.benchmark import HardwareBenchmark


@click.group()
def hardware_cli():
    """Hardware detection and optimization commands."""
    pass


@hardware_cli.command()
def detect():
    """Detect system hardware."""
    detector = HardwareDetector()
    detector.detect()
    detector.print_summary()


@hardware_cli.command()
def optimize():
    """Show optimization recommendations."""
    detector = HardwareDetector()
    system_info = detector.detect()
    
    optimizer = HardwareOptimizer(system_info)
    tier = optimizer.tier
    profile = optimizer.generate_profile()
    
    print(f"\n💻 Hardware Tier: {tier.value}")
    print(f"\n🔧 Optimization Profile:")
    print(f"  Max Workers: {profile.max_workers}")
    print(f"  Batch Size: {profile.batch_size}")
    print(f"  Frame Samples: {profile.frame_sample_count}")
    print(f"  Use GPU: {profile.use_gpu}")
    print(f"  Mixed Precision: {profile.use_mixed_precision}")
    print(f"  Memory Limit: {profile.memory_limit_mb}MB")
    print(f"  Effect Quality: {profile.effect_quality}")
    print(f"  Render Threads: {profile.render_threads}")
    
    # Memory estimate
    memory = optimizer.get_memory_estimate(duration_seconds=60, num_clips=10)
    print(f"\n💾 Memory Estimate (60s video, 10 clips):")
    print(f"  Audio: {memory['audio']:.0f}MB")
    print(f"  Video: {memory['video']:.0f}MB")
    print(f"  Total: {memory['total']:.0f}MB")
    print(f"  Peak (est.): {memory['estimated_peak_mb']:.0f}MB")
    
    # Time estimate
    times = optimizer.get_processing_time_estimate(duration_seconds=60)
    print(f"\n⏱️  Processing Time Estimate (60s video):")
    print(f"  Audio Analysis: {times['audio_analysis']:.1f}s")
    print(f"  Video Analysis: {times['video_analysis']:.1f}s")
    print(f"  Timeline Generation: {times['timeline_generation']:.1f}s")
    print(f"  Effect Composition: {times['effect_composition']:.1f}s")
    print(f"  Rendering: {times['rendering']:.1f}s")
    print(f"  Total: {times['total']:.1f}s")


@hardware_cli.command()
def benchmark():
    """Run hardware benchmark."""
    results = HardwareBenchmark.full_benchmark()
    
    print(f"\nCPU: {results['cpu']['gflops']:.2f} GFLOPS")
    if results['gpu']['available']:
        print(f"GPU: {results['gpu']['gflops']:.2f} GFLOPS ({results['gpu']['device']})")
    print(f"Memory: {results['memory']['avg_bandwidth_gbps']:.2f} GB/s")


if __name__ == '__main__':
    hardware_cli()
