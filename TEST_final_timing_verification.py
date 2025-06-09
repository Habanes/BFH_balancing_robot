#!/usr/bin/env python3
"""
Final Timing Verification Test
Tests the ultra-conservative 50Hz main loop configuration

Based on timing analysis results:
- IMU reads: 0.67ms average
- Max delays: 1200ms worst case
- Conservative approach: 50Hz (20ms interval) = 30x safety margin

This test validates that the new configuration can maintain stable timing.
"""

import time
import statistics
from src.hardware.imu import IMU
from src.config.configManager import global_config

def test_ultra_conservative_timing():
    """Test the new 50Hz configuration with real hardware."""
    
    print("=== FINAL TIMING VERIFICATION TEST ===")
    print(f"Main loop rate: {global_config.main_loop_rate} Hz")
    print(f"Main loop interval: {global_config.main_loop_interval:.4f} s ({global_config.main_loop_interval*1000:.1f} ms)")
    print(f"Expected safety margin: {20/0.67:.1f}x over average IMU read time")
    print()
    
    # Initialize IMU
    try:
        imu = IMU()
        print("✅ IMU initialized successfully")
    except Exception as e:
        print(f"❌ IMU initialization failed: {e}")
        return
    
    # Test parameters
    test_duration = 10  # seconds
    target_iterations = int(test_duration * global_config.main_loop_rate)
    
    print(f"Running {target_iterations} iterations over {test_duration} seconds...")
    print("Press Ctrl+C to stop early if needed")
    print()
    
    # Timing measurements
    loop_times = []
    imu_times = []
    sleep_times = []
    iteration_count = 0
    
    start_time = time.time()
    last_iteration_time = start_time
    
    try:
        for i in range(target_iterations):
            iteration_start = time.time()
            
            # Measure IMU read time
            imu_start = time.time()
            tilt_angle = imu.get_tilt_angle()
            imu_end = time.time()
            imu_time = (imu_end - imu_start) * 1000  # Convert to ms
            
            # Simulate minimal processing (like in main loop)
            target_torque = tilt_angle * 0.1  # Simple proportional control simulation
            
            # Calculate sleep time
            sleep_start = time.time()
            time.sleep(global_config.main_loop_interval)
            sleep_end = time.time()
            sleep_time = (sleep_end - sleep_start) * 1000
            
            # Calculate total loop time
            iteration_end = time.time()
            loop_time = (iteration_end - last_iteration_time) * 1000
            
            # Store measurements
            loop_times.append(loop_time)
            imu_times.append(imu_time)
            sleep_times.append(sleep_time)
            
            last_iteration_time = iteration_end
            iteration_count += 1
            
            # Progress update every 2 seconds
            if i % (global_config.main_loop_rate * 2) == 0 and i > 0:
                elapsed = time.time() - start_time
                avg_loop = statistics.mean(loop_times[-100:])  # Last 100 iterations
                avg_imu = statistics.mean(imu_times[-100:])
                print(f"Progress: {elapsed:.1f}s | Avg loop: {avg_loop:.1f}ms | Avg IMU: {avg_imu:.2f}ms | Angle: {tilt_angle:.1f}°")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    
    # Calculate statistics
    end_time = time.time()
    total_time = end_time - start_time
    actual_rate = iteration_count / total_time
    
    print(f"\n=== RESULTS ===")
    print(f"Completed {iteration_count} iterations in {total_time:.2f} seconds")
    print(f"Actual rate: {actual_rate:.1f} Hz (target: {global_config.main_loop_rate} Hz)")
    print(f"Rate accuracy: {(actual_rate/global_config.main_loop_rate)*100:.1f}%")
    print()
    
    if loop_times:
        print(f"Loop timing (ms):")
        print(f"  Average: {statistics.mean(loop_times):.2f}")
        print(f"  Median:  {statistics.median(loop_times):.2f}")
        print(f"  Min:     {min(loop_times):.2f}")
        print(f"  Max:     {max(loop_times):.2f}")
        print(f"  Std dev: {statistics.stdev(loop_times):.2f}")
        print()
        
        print(f"IMU read timing (ms):")
        print(f"  Average: {statistics.mean(imu_times):.3f}")
        print(f"  Median:  {statistics.median(imu_times):.3f}")
        print(f"  Min:     {min(imu_times):.3f}")
        print(f"  Max:     {max(imu_times):.3f}")
        print(f"  Std dev: {statistics.stdev(imu_times):.3f}")
        print()
        
        # Performance analysis
        target_interval_ms = global_config.main_loop_interval * 1000
        avg_loop_ms = statistics.mean(loop_times)
        max_loop_ms = max(loop_times)
        
        print(f"Performance Analysis:")
        print(f"  Target interval: {target_interval_ms:.1f} ms")
        print(f"  Average timing accuracy: {(target_interval_ms/avg_loop_ms)*100:.1f}%")
        print(f"  Worst case safety margin: {target_interval_ms/max_loop_ms:.1f}x")
        
        # Check if timing is stable
        if max_loop_ms < target_interval_ms * 1.1:  # Within 10% of target
            print(f"  ✅ TIMING STABLE - Max deviation: {((max_loop_ms/target_interval_ms)-1)*100:.1f}%")
        else:
            print(f"  ⚠️  TIMING UNSTABLE - Max deviation: {((max_loop_ms/target_interval_ms)-1)*100:.1f}%")
        
        # Overall assessment
        stability_ok = max_loop_ms < target_interval_ms * 1.2
        accuracy_ok = abs(actual_rate - global_config.main_loop_rate) < 2
        
        print(f"\n=== FINAL ASSESSMENT ===")
        if stability_ok and accuracy_ok:
            print("✅ CONFIGURATION READY FOR TESTING")
            print("   Ultra-conservative timing should provide stable robot operation")
        elif stability_ok:
            print("⚠️  CONFIGURATION MOSTLY STABLE")
            print("   Rate accuracy issues, but timing stability is good")
        else:
            print("❌ CONFIGURATION NEEDS FURTHER ADJUSTMENT")
            print("   Timing instability detected - consider even lower rates")

if __name__ == "__main__":
    test_ultra_conservative_timing()
