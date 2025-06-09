#!/usr/bin/env python3
"""
No-Encoder Timing Test
Tests 200Hz main loop without encoder interference

This test will confirm whether encoders are the bottleneck causing timing issues.
If 200Hz works well without encoders, we know the encoder integration needs optimization.
"""

import time
import statistics
from src.hardware.imu import IMU
from src.config.configManager import global_config

def test_no_encoder_timing():
    """Test 200Hz main loop without any encoder reads."""
    
    print("=== NO-ENCODER TIMING TEST ===")
    print(f"Testing pure IMU-only control loop")
    print(f"Main loop rate: {global_config.main_loop_rate} Hz")
    print(f"Main loop interval: {global_config.main_loop_interval:.4f} s ({global_config.main_loop_interval*1000:.1f} ms)")
    print(f"Expected safety margin: {5.0/0.73:.1f}x over average IMU read time")
    print()
    
    # Initialize IMU only
    try:
        imu = IMU()
        print("✅ IMU initialized successfully")
    except Exception as e:
        print(f"❌ IMU initialization failed: {e}")
        return
    
    # Test parameters
    test_duration = 15  # seconds - longer test for better statistics
    target_iterations = int(test_duration * global_config.main_loop_rate)
    
    print(f"Running {target_iterations} iterations over {test_duration} seconds...")
    print("This simulates the core balance control loop WITHOUT encoders")
    print("Press Ctrl+C to stop early if needed")
    print()
    
    # Timing measurements
    loop_times = []
    imu_times = []
    total_iteration_times = []
    iteration_count = 0
    
    start_time = time.time()
    last_iteration_time = start_time
    
    try:
        for i in range(target_iterations):
            iteration_start = time.time()
            
            # Measure IMU read time (critical path)
            imu_start = time.time()
            tilt_angle = imu.read_pitch()
            imu_end = time.time()
            imu_time = (imu_end - imu_start) * 1000  # Convert to ms
            
            # Simulate minimal balance control processing
            # This represents the essential PID computation
            target_torque = tilt_angle * 0.1  # Simple proportional control
            torque_left = max(min(target_torque - 0.05, 1.0), -1.0)  # Clipping
            torque_right = max(min(target_torque + 0.05, 1.0), -1.0)
            
            # Sleep for target interval
            sleep_start = time.time()
            time.sleep(global_config.main_loop_interval)
            sleep_end = time.time()
            
            # Calculate timing metrics
            iteration_end = time.time()
            total_iteration_time = (iteration_end - iteration_start) * 1000
            loop_time = (iteration_end - last_iteration_time) * 1000
            
            # Store measurements
            loop_times.append(loop_time)
            imu_times.append(imu_time)
            total_iteration_times.append(total_iteration_time)
            
            last_iteration_time = iteration_end
            iteration_count += 1
            
            # Progress update every 3 seconds
            if i % (global_config.main_loop_rate * 3) == 0 and i > 0:
                elapsed = time.time() - start_time
                avg_loop = statistics.mean(loop_times[-200:])  # Last 200 iterations
                avg_imu = statistics.mean(imu_times[-200:])
                avg_total = statistics.mean(total_iteration_times[-200:])
                print(f"Progress: {elapsed:.1f}s | Loop: {avg_loop:.1f}ms | IMU: {avg_imu:.2f}ms | Total: {avg_total:.1f}ms | Angle: {tilt_angle:.1f}°")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    
    # Calculate final statistics
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
        avg_imu_ms = statistics.mean(imu_times)
        max_imu_ms = max(imu_times)
        
        print(f"Performance Analysis:")
        print(f"  Target interval: {target_interval_ms:.1f} ms")
        print(f"  Average accuracy: {(target_interval_ms/avg_loop_ms)*100:.1f}%")
        print(f"  IMU overhead: {(avg_imu_ms/target_interval_ms)*100:.1f}% of budget")
        print(f"  Max IMU spike: {max_imu_ms:.2f}ms ({(max_imu_ms/target_interval_ms)*100:.0f}% of budget)")
        print(f"  Safety margin: {target_interval_ms/max_loop_ms:.1f}x")
        
        # Stability assessment
        rate_stable = abs(actual_rate - global_config.main_loop_rate) < 5  # Within 5Hz
        timing_stable = max_loop_ms < target_interval_ms * 1.2  # Within 20%
        imu_reasonable = max_imu_ms < target_interval_ms * 0.8  # IMU < 80% of budget
        
        print(f"\n=== ASSESSMENT ===")
        print(f"Rate stability: {'✅' if rate_stable else '❌'} {'GOOD' if rate_stable else 'POOR'}")
        print(f"Timing stability: {'✅' if timing_stable else '❌'} {'GOOD' if timing_stable else 'POOR'}")
        print(f"IMU performance: {'✅' if imu_reasonable else '❌'} {'GOOD' if imu_reasonable else 'BOTTLENECK'}")
        
        if rate_stable and timing_stable and imu_reasonable:
            print(f"\n🎉 SUCCESS: 200Hz operation is STABLE without encoders!")
            print(f"   The encoder integration is the bottleneck.")
            print(f"   Recommendation: Implement async encoder reading or optimize I2C.")
        elif timing_stable and imu_reasonable:
            print(f"\n✅ MOSTLY GOOD: Timing is stable but rate accuracy needs work")
            print(f"   200Hz is viable, minor tuning needed")
        elif imu_reasonable:
            print(f"\n⚠️  TIMING ISSUES: IMU is fine but overall timing unstable")
            print(f"   Consider 150Hz or optimize sleep timing")
        else:
            print(f"\n❌ IMU BOTTLENECK: Even without encoders, IMU reads are too slow")
            print(f"   Need IMU optimization or lower frequencies")


if __name__ == "__main__":
    test_no_encoder_timing()
