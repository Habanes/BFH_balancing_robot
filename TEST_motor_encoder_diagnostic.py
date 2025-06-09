#!/usr/bin/env python3
"""
Diagnostic test to isolate PWM vs Encoder conflicts
Run this on the robot to identify the exact issue
"""

import time
import sys
from src.hardware.motorController import MotorController
from src.hardware.motorEncoder import MotorEncoder

def test_motors_only():
    """Test 1: Motors only - both should work"""
    print("\n" + "="*60)
    print("TEST 1: MOTORS ONLY (no encoders)")
    print("="*60)
    
    try:
        motor_left = MotorController(is_left=True)
        motor_right = MotorController(is_left=False)
        
        print("✓ Motor controllers created successfully")
        
        motor_left.start()
        motor_right.start()
        print("✓ Motors started")
        
        # Test both motors with slow speed
        for i in range(5):
            print(f"Setting motors to 0.3 speed... ({i+1}/5)")
            motor_left.set_speed(0.3)
            motor_right.set_speed(0.3)
            time.sleep(1)
            
            print(f"Setting motors to -0.3 speed... ({i+1}/5)")
            motor_left.set_speed(-0.3)
            motor_right.set_speed(-0.3)
            time.sleep(1)
        
        motor_left.set_speed(0.0)
        motor_right.set_speed(0.0)
        print("✓ Motors stopped")
        
        motor_left.stop()
        motor_right.stop()
        print("✓ TEST 1 PASSED: Both motors work without encoders")
        
    except Exception as e:
        print(f"✗ TEST 1 FAILED: {e}")
        return False
    
    return True

def test_encoders_only():
    """Test 2: Encoders only - should initialize without issues"""
    print("\n" + "="*60)
    print("TEST 2: ENCODERS ONLY (no motors)")
    print("="*60)
    
    try:
        encoder_left = MotorEncoder(is_left=True)
        encoder_right = MotorEncoder(is_left=False)
        print("✓ Encoder objects created successfully")
        
        # Reset and test encoder readings
        encoder_left.reset_travel_distance()
        encoder_right.reset_travel_distance()
        print("✓ Travel distances reset")
        
        # Read encoders multiple times
        for i in range(10):
            left_pos = encoder_left.get_steps()
            right_pos = encoder_right.get_steps()
            left_travel = encoder_left.update_travel_distance()
            right_travel = encoder_right.update_travel_distance()
            
            print(f"Reading {i+1}: L_pos={left_pos:.0f}, R_pos={right_pos:.0f}, L_travel={left_travel:.0f}, R_travel={right_travel:.0f}")
            time.sleep(0.1)
        
        print("✓ TEST 2 PASSED: Encoders work without motors")
        
    except Exception as e:
        print(f"✗ TEST 2 FAILED: {e}")
        return False
    
    return True

def test_motors_then_encoders():
    """Test 3: Motors first, then add encoders"""
    print("\n" + "="*60)
    print("TEST 3: MOTORS FIRST, THEN ADD ENCODERS")
    print("="*60)
    
    try:
        # First, create and test motors
        motor_left = MotorController(is_left=True)
        motor_right = MotorController(is_left=False)
        print("✓ Motor controllers created")
        
        motor_left.start()
        motor_right.start()
        print("✓ Motors started")
        
        # Test motors work
        motor_left.set_speed(0.2)
        motor_right.set_speed(0.2)
        print("✓ Motors running at 0.2 speed")
        time.sleep(2)
        
        # NOW add encoders while motors are running
        print("Now creating encoders while motors are running...")
        encoder_left = MotorEncoder(is_left=True)
        encoder_right = MotorEncoder(is_left=False)
        print("✓ Encoders created while motors running")
        
        # Test if motors still work
        print("Testing if motors still work after encoder creation...")
        motor_left.set_speed(-0.2)
        motor_right.set_speed(-0.2)
        print("✓ Motors still work after encoder creation")
        time.sleep(2)
        
        # Test encoder readings
        left_pos = encoder_left.get_steps()
        right_pos = encoder_right.get_steps()
        print(f"✓ Encoder readings: L={left_pos:.0f}, R={right_pos:.0f}")
        
        motor_left.set_speed(0.0)
        motor_right.set_speed(0.0)
        motor_left.stop()
        motor_right.stop()
        print("✓ TEST 3 PASSED: No conflict when adding encoders to running motors")
        
    except Exception as e:
        print(f"✗ TEST 3 FAILED: {e}")
        return False
    
    return True

def test_encoders_then_motors():
    """Test 4: Encoders first, then add motors"""
    print("\n" + "="*60)
    print("TEST 4: ENCODERS FIRST, THEN ADD MOTORS")
    print("="*60)
    
    try:
        # First, create encoders
        encoder_left = MotorEncoder(is_left=True)
        encoder_right = MotorEncoder(is_left=False)
        print("✓ Encoders created first")
        
        # Test encoder readings
        left_pos = encoder_left.get_steps()
        right_pos = encoder_right.get_steps()
        print(f"✓ Initial encoder readings: L={left_pos:.0f}, R={right_pos:.0f}")
        
        # NOW add motors
        print("Now creating motors after encoders...")
        motor_left = MotorController(is_left=True)
        motor_right = MotorController(is_left=False)
        print("✓ Motor controllers created after encoders")
        
        motor_left.start()
        motor_right.start()
        print("✓ Motors started")
        
        # Test both systems together
        for i in range(3):
            print(f"Combined test {i+1}/3:")
            
            # Set motor speeds
            motor_left.set_speed(0.3)
            motor_right.set_speed(0.3)
            
            # Read encoders
            left_pos = encoder_left.get_steps()
            right_pos = encoder_right.get_steps()
            left_travel = encoder_left.update_travel_distance()
            right_travel = encoder_right.update_travel_distance()
            
            print(f"  Motors at 0.3, Encoders: L_pos={left_pos:.0f}, R_pos={right_pos:.0f}")
            time.sleep(1)
            
            motor_left.set_speed(-0.3)
            motor_right.set_speed(-0.3)
            time.sleep(1)
        
        motor_left.set_speed(0.0)
        motor_right.set_speed(0.0)
        motor_left.stop()
        motor_right.stop()
        print("✓ TEST 4 PASSED: No conflict when adding motors to existing encoders")
        
    except Exception as e:
        print(f"✗ TEST 4 FAILED: {e}")
        return False
    
    return True

def test_simultaneous_creation():
    """Test 5: Create everything simultaneously like in main.py"""
    print("\n" + "="*60)
    print("TEST 5: SIMULTANEOUS CREATION (like main.py)")
    print("="*60)
    
    try:
        # Create everything at once like in main.py
        motor_left = MotorController(is_left=True)
        motor_right = MotorController(is_left=False)
        encoder_left = MotorEncoder(is_left=True)
        encoder_right = MotorEncoder(is_left=False)
        print("✓ All objects created simultaneously")
        
        # Reset encoders
        encoder_left.reset_travel_distance()
        encoder_right.reset_travel_distance()
        print("✓ Encoder distances reset")
        
        # Start motors
        motor_left.start()
        motor_right.start()
        print("✓ Motors started")
        
        # Test loop similar to main.py
        for i in range(5):
            # Read sensors (like main loop)
            left_position = encoder_left.get_steps()
            right_position = encoder_right.get_steps()
            left_travel = encoder_left.update_travel_distance()
            right_travel = encoder_right.update_travel_distance()
            
            # Set motor commands (like main loop)
            speed = 0.2 if i % 2 == 0 else -0.2
            motor_left.set_speed(speed)
            motor_right.set_speed(speed)
            
            print(f"Loop {i+1}: Speed={speed}, L_pos={left_position:.0f}, R_pos={right_position:.0f}, Travel L/R={left_travel:.0f}/{right_travel:.0f}")
            time.sleep(1)
        
        motor_left.set_speed(0.0)
        motor_right.set_speed(0.0)
        motor_left.stop()
        motor_right.stop()
        print("✓ TEST 5 PASSED: Simultaneous creation works like main.py")
        
    except Exception as e:
        print(f"✗ TEST 5 FAILED: {e}")
        return False
    
    return True

def main():
    print("PWM vs ENCODER CONFLICT DIAGNOSTIC TEST")
    print("="*60)
    print("This test will help identify where the conflict occurs")
    print("Run this on the robot and report which tests pass/fail")
    
    tests = [
        ("Motors Only", test_motors_only),
        ("Encoders Only", test_encoders_only), 
        ("Motors Then Encoders", test_motors_then_encoders),
        ("Encoders Then Motors", test_encoders_then_motors),
        ("Simultaneous Creation", test_simultaneous_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            if not result:
                print(f"\n⚠️  STOPPING HERE - {test_name} failed")
                break
                
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted by user")
            break
        except Exception as e:
            print(f"\n⚠️  Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
            break
        
        # Small delay between tests
        print("\nWaiting 3 seconds before next test...")
        time.sleep(3)
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    # Analysis
    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)
    
    if len(results) == 0:
        print("No tests completed - check for import errors")
    elif results[0][1] == False:
        print("❌ Basic motor functionality broken - check motor hardware/drivers")
    elif results[1][1] == False:
        print("❌ Encoder initialization broken - check encoder hardware/GPIO")
    elif len(results) >= 3 and results[2][1] == False:
        print("❌ Adding encoders to running motors causes conflict")
        print("   → This suggests encoder init interferes with PWM")
    elif len(results) >= 4 and results[3][1] == False:
        print("❌ Adding motors to existing encoders causes conflict") 
        print("   → This suggests motor init interferes with encoder GPIO")
    elif len(results) >= 5 and results[4][1] == False:
        print("❌ Simultaneous creation causes conflict")
        print("   → This is the same pattern as main.py - timing issue?")
    else:
        print("✅ All tests passed - no obvious PWM/encoder conflict detected")
        print("   → Issue might be in main.py logic, not hardware conflict")

if __name__ == "__main__":
    main()