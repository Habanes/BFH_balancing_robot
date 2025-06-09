#!/usr/bin/env python3
"""
Test script to find the optimal neutral pitch angle for the balancing robot.

This script continuously measures the IMU pitch angle and displays real-time statistics
to help determine the robot's neutral position when perfectly balanced.

Usage:
1. Place the robot in its neutral balanced position
2. Run this script
3. Let it collect data for a while (press Ctrl+C to stop)
4. Use the average value to update the angle_offset in configManager.py

The script shows:
- Current pitch reading
- Running average
- Standard deviation
- Min/Max values
- Sample count
"""

import sys
import os
import time
import signal
import statistics
from datetime import datetime

# Direct imports since we're now in the root directory
from src.hardware.imu import IMU
from src.config.configManager import global_config

class NeutralPitchFinder:
    def __init__(self):
        self.imu = None
        self.measurements = []
        self.running = True
        self.start_time = None
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\nShutdown requested...")
        self.running = False
        
    def initialize_imu(self):
        """Initialize the IMU sensor"""
        try:
            print("Initializing IMU...")
            self.imu = IMU()
            print("✓ IMU initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize IMU: {e}")
            return False
            
    def get_raw_pitch(self):
        """Get raw pitch without any offset applied"""
        try:
            # Read the raw pitch and remove the current offset to get true raw value
            pitch_with_offset = self.imu.read_pitch()
            raw_pitch = pitch_with_offset - global_config.imu_angle_offset
            return raw_pitch
        except Exception as e:
            print(f"Error reading IMU: {e}")
            return None
            
    def print_statistics(self):
        """Print current statistics"""
        if not self.measurements:
            return
            
        current_pitch = self.measurements[-1]
        avg = statistics.mean(self.measurements)
        std_dev = statistics.stdev(self.measurements) if len(self.measurements) > 1 else 0
        min_val = min(self.measurements)
        max_val = max(self.measurements)
        count = len(self.measurements)
        
        # Calculate elapsed time
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # Clear screen and print header
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 70)
        print("    BALANCING ROBOT - NEUTRAL PITCH ANGLE FINDER")
        print("=" * 70)
        print(f"Started: {datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S')}")
        print(f"Elapsed: {elapsed:.1f}s")
        print(f"Current offset in config: {global_config.imu_angle_offset:.2f}°")
        print("-" * 70)
        
        # Current measurement
        print(f"Current pitch (raw):     {current_pitch:8.2f}°")
        print(f"Current pitch (w/offset): {current_pitch + global_config.imu_angle_offset:8.2f}°")
        print()
        
        # Statistics
        print("STATISTICS (raw values):")
        print(f"  Samples collected:     {count:8d}")
        print(f"  Average:               {avg:8.2f}°")
        print(f"  Standard deviation:    {std_dev:8.2f}°")
        print(f"  Minimum:               {min_val:8.2f}°")
        print(f"  Maximum:               {max_val:8.2f}°")
        print(f"  Range:                 {max_val - min_val:8.2f}°")
        print()
        
        # Recommendations
        print("RECOMMENDATIONS:")
        if std_dev < 0.5:
            stability = "EXCELLENT"
        elif std_dev < 1.0:
            stability = "GOOD"
        elif std_dev < 2.0:
            stability = "FAIR"
        else:
            stability = "POOR"
            
        print(f"  Stability:             {stability} (σ = {std_dev:.2f}°)")
        
        if count >= 100:
            recommended_offset = -avg  # Negative because we want to offset TO zero
            print(f"  Recommended offset:    {recommended_offset:8.2f}°")
            print(f"  Current offset:        {global_config.imu_angle_offset:8.2f}°")
            
            offset_diff = recommended_offset - global_config.imu_angle_offset
            if abs(offset_diff) > 0.5:
                print(f"  Suggested adjustment:  {offset_diff:+8.2f}°")
                print(f"  → Update config to:    {recommended_offset:8.2f}°")
            else:
                print("  ✓ Current offset looks good!")
        else:
            remaining = 100 - count
            print(f"  Collect {remaining} more samples for recommendation")
            
        print()
        print("Press Ctrl+C to stop and save results")
        print("=" * 70)
        
    def save_results(self):
        """Save results to a file"""
        if not self.measurements:
            print("No measurements to save.")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"neutral_pitch_calibration_{timestamp}.txt"
        filepath = os.path.join("test", filename)
        
        try:
            with open(filepath, 'w') as f:
                f.write("NEUTRAL PITCH CALIBRATION RESULTS\n")
                f.write("=" * 50 + "\n")
                f.write(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duration: {time.time() - self.start_time:.1f} seconds\n")
                f.write(f"Samples: {len(self.measurements)}\n")
                f.write(f"Current config offset: {global_config.imu_angle_offset:.2f}°\n\n")
                
                avg = statistics.mean(self.measurements)
                std_dev = statistics.stdev(self.measurements) if len(self.measurements) > 1 else 0
                
                f.write("STATISTICS (raw values):\n")
                f.write(f"Average: {avg:.4f}°\n")
                f.write(f"Std Dev: {std_dev:.4f}°\n")
                f.write(f"Min: {min(self.measurements):.4f}°\n")
                f.write(f"Max: {max(self.measurements):.4f}°\n")
                f.write(f"Range: {max(self.measurements) - min(self.measurements):.4f}°\n\n")
                
                recommended_offset = -avg
                f.write(f"RECOMMENDED OFFSET: {recommended_offset:.4f}°\n\n")
                
                f.write("RAW MEASUREMENTS:\n")
                for i, measurement in enumerate(self.measurements):
                    f.write(f"{i+1:4d}: {measurement:.4f}°\n")
                    
            print(f"\n✓ Results saved to: {filepath}")
            
        except Exception as e:
            print(f"✗ Failed to save results: {e}")
            
    def run(self):
        """Main measurement loop"""
        print("BALANCING ROBOT - NEUTRAL PITCH ANGLE FINDER")
        print("=" * 50)
        print("\nInstructions:")
        print("1. Place the robot in its neutral balanced position")
        print("2. Ensure the robot is completely still")
        print("3. Let the script collect data (it will update continuously)")
        print("4. Press Ctrl+C when you have enough samples")
        print("\nStarting in 3 seconds...")
        
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
            
        if not self.initialize_imu():
            return False
            
        print("\nStarting measurements...")
        self.start_time = time.time()
        
        try:
            while self.running:
                pitch = self.get_raw_pitch()
                
                if pitch is not None:
                    self.measurements.append(pitch)
                    
                    # Print statistics every measurement
                    self.print_statistics()
                    
                    # Brief pause between measurements
                    time.sleep(0.1)
                else:
                    print("Failed to read IMU, retrying...")
                    time.sleep(0.5)
                    
        except KeyboardInterrupt:
            pass
            
        print("\n\nMeasurement completed!")
        
        if self.measurements:
            avg = statistics.mean(self.measurements)
            std_dev = statistics.stdev(self.measurements) if len(self.measurements) > 1 else 0
            
            print(f"\nFINAL RESULTS:")
            print(f"Samples collected: {len(self.measurements)}")
            print(f"Average raw pitch: {avg:.4f}°")
            print(f"Standard deviation: {std_dev:.4f}°")
            print(f"Current config offset: {global_config.imu_angle_offset:.2f}°")
            
            recommended_offset = -avg
            print(f"Recommended offset: {recommended_offset:.4f}°")
            
            offset_diff = recommended_offset - global_config.imu_angle_offset
            if abs(offset_diff) > 0.5:
                print(f"\n⚠️  RECOMMENDATION:")
                print(f"Update 'imu_angle_offset' in configManager.py to: {recommended_offset:.2f}")
                print(f"This will adjust the offset by {offset_diff:+.2f}°")
            else:
                print(f"\n✓ Current offset looks good! (difference: {offset_diff:+.2f}°)")
                
            # Save results
            self.save_results()
        
        return True

def main():
    """Main function"""
    finder = NeutralPitchFinder()
    success = finder.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
