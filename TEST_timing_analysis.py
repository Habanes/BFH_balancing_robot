#!/usr/bin/env python3
"""
Timing Analysis Test for Control Loop Performance
Measures how long different operations take and their impact on loop timing
"""

import time
import statistics
from src.hardware.motorController import MotorController
from src.hardware.motorEncoder import MotorEncoder
from src.hardware.imu import IMU
from src.config.configManager import global_config

def measure_operation_times():
    """Measure how long each operation takes"""
    print("TIMING ANALYSIS FOR BALANCING ROBOT")
    print("="*60)
    
    # Initialize components
    print("Initializing components...")
    imu = IMU()
    motor_left = MotorController(is_left=True)
    motor_right = MotorController(is_left=False)
    encoder_left = MotorEncoder(is_left=True)
    encoder_right = MotorEncoder(is_left=False)
    
    motor_left.start()
    motor_right.start()
    print("✓ Components initialized")
    
    # Test parameters
    num_tests = 1000
    
    # === Test 1: IMU Read Times ===
    print(f"\n1. IMU Read Times ({num_tests} samples):")
    imu_times = []
    for _ in range(num_tests):
        start = time.perf_counter()
        pitch = imu.read_pitch()
        end = time.perf_counter()
        imu_times.append((end - start) * 1000)  # Convert to ms
    
    print(f"   Average: {statistics.mean(imu_times):.4f} ms")
    print(f"   Min:     {min(imu_times):.4f} ms")
    print(f"   Max:     {max(imu_times):.4f} ms")
    print(f"   StdDev:  {statistics.stdev(imu_times):.4f} ms")
    
    # === Test 2: Single Encoder Read Times ===
    print(f"\n2. Single Encoder Read Times ({num_tests} samples):")
    encoder_times = []
    for _ in range(num_tests):
        start = time.perf_counter()
        pos = encoder_left.get_steps()
        end = time.perf_counter()
        encoder_times.append((end - start) * 1000)
    
    print(f"   Average: {statistics.mean(encoder_times):.4f} ms")
    print(f"   Min:     {min(encoder_times):.4f} ms")
    print(f"   Max:     {max(encoder_times):.4f} ms")
    print(f"   StdDev:  {statistics.stdev(encoder_times):.4f} ms")
    
    # === Test 3: All Encoder Operations ===
    print(f"\n3. All Encoder Operations (4 reads) ({num_tests} samples):")
    all_encoder_times = []
    for _ in range(num_tests):
        start = time.perf_counter()
        left_pos = encoder_left.get_steps()
        right_pos = encoder_right.get_steps()
        left_travel = encoder_left.update_travel_distance()
        right_travel = encoder_right.update_travel_distance()
        end = time.perf_counter()
        all_encoder_times.append((end - start) * 1000)
    
    print(f"   Average: {statistics.mean(all_encoder_times):.4f} ms")
    print(f"   Min:     {min(all_encoder_times):.4f} ms")
    print(f"   Max:     {max(all_encoder_times):.4f} ms")
    print(f"   StdDev:  {statistics.stdev(all_encoder_times):.4f} ms")
    
    # === Test 4: Motor Command Times ===
    print(f"\n4. Motor Command Times ({num_tests} samples):")
    motor_times = []
    for _ in range(num_tests):
        start = time.perf_counter()
        motor_left.set_speed(0.1)
        motor_right.set_speed(0.1)
        end = time.perf_counter()
        motor_times.append((end - start) * 1000)
    
    print(f"   Average: {statistics.mean(motor_times):.4f} ms")
    print(f"   Min:     {min(motor_times):.4f} ms")
    print(f"   Max:     {max(motor_times):.4f} ms")
    print(f"   StdDev:  {statistics.stdev(motor_times):.4f} ms")
    
    # === Test 5: Full Loop Simulation ===
    print(f"\n5. Complete Loop Simulation ({num_tests} samples):")
    loop_times = []
    for _ in range(num_tests):
        start = time.perf_counter()
        
        # Read IMU
        pitch = imu.read_pitch()
        
        # Read all encoders
        left_pos = encoder_left.get_steps()
        right_pos = encoder_right.get_steps()
        left_travel = encoder_left.update_travel_distance()
        right_travel = encoder_right.update_travel_distance()
        
        # Simple PID calculation (simulate)
        target_torque = pitch * 0.03  # Simple proportional
        
        # Set motors
        motor_left.set_speed(target_torque)
        motor_right.set_speed(target_torque)
        
        end = time.perf_counter()
        loop_times.append((end - start) * 1000)
    
    print(f"   Average: {statistics.mean(loop_times):.4f} ms")
    print(f"   Min:     {min(loop_times):.4f} ms")
    print(f"   Max:     {max(loop_times):.4f} ms")
    print(f"   StdDev:  {statistics.stdev(loop_times):.4f} ms")
    
    # === Analysis ===
    print("\n" + "="*60)
    print("TIMING ANALYSIS")
    print("="*60)
    
    target_10khz = 0.1  # 0.1ms for 10kHz
    target_5khz = 0.2   # 0.2ms for 5kHz
    target_1khz = 1.0   # 1.0ms for 1kHz
    
    avg_loop_time = statistics.mean(loop_times)
    max_loop_time = max(loop_times)
    
    print(f"Current Configuration:")
    print(f"  Main loop target: {global_config.main_loop_rate}Hz ({global_config.main_loop_interval*1000:.3f}ms)")
    print(f"")
    print(f"Measured Performance:")
    print(f"  Average loop time: {avg_loop_time:.4f}ms")
    print(f"  Maximum loop time: {max_loop_time:.4f}ms")
    print(f"")
    print(f"Loop Rate Analysis:")
    
    if max_loop_time <= target_10khz:
        print(f"  ✅ 10kHz (0.1ms) - EXCELLENT: Max time {max_loop_time:.4f}ms fits comfortably")
    elif avg_loop_time <= target_10khz:
        print(f"  ⚠️  10kHz (0.1ms) - RISKY: Avg {avg_loop_time:.4f}ms OK, but max {max_loop_time:.4f}ms over budget")
    else:
        print(f"  ❌ 10kHz (0.1ms) - TOO FAST: Avg {avg_loop_time:.4f}ms exceeds budget")
    
    if max_loop_time <= target_5khz:
        print(f"  ✅ 5kHz (0.2ms) - GOOD: Max time {max_loop_time:.4f}ms fits well")
    elif avg_loop_time <= target_5khz:
        print(f"  ⚠️  5kHz (0.2ms) - MODERATE: Avg {avg_loop_time:.4f}ms OK, max {max_loop_time:.4f}ms tight")
    else:
        print(f"  ❌ 5kHz (0.2ms) - TOO FAST: Avg {avg_loop_time:.4f}ms exceeds budget")
    
    if max_loop_time <= target_1khz:
        print(f"  ✅ 1kHz (1.0ms) - SAFE: Max time {max_loop_time:.4f}ms has plenty of headroom")
    else:
        print(f"  ❌ 1kHz (1.0ms) - STILL TOO FAST: Max {max_loop_time:.4f}ms exceeds even 1kHz budget!")
    
    print(f"\nRecommendations:")
    if max_loop_time > target_5khz:
        print(f"  🔧 Reduce main loop to 1-2kHz for stable timing")
        print(f"  🔧 Read encoders at lower frequency (500Hz-1kHz)")
    elif max_loop_time > target_10khz:
        print(f"  🔧 Current 5kHz main loop rate is good")
        print(f"  🔧 Keep encoder reads at 1kHz as implemented")
    else:
        print(f"  ✅ System can handle high-frequency operation")
    
    # === Component breakdown ===
    print(f"\nOperation Time Breakdown:")
    print(f"  IMU read:           {statistics.mean(imu_times):.4f}ms ({statistics.mean(imu_times)/avg_loop_time*100:.1f}%)")
    print(f"  Single encoder:     {statistics.mean(encoder_times):.4f}ms")
    print(f"  All encoders (4x):  {statistics.mean(all_encoder_times):.4f}ms ({statistics.mean(all_encoder_times)/avg_loop_time*100:.1f}%)")
    print(f"  Motor commands:     {statistics.mean(motor_times):.4f}ms ({statistics.mean(motor_times)/avg_loop_time*100:.1f}%)")
    
    motor_left.stop()
    motor_right.stop()

if __name__ == "__main__":
    measure_operation_times()
