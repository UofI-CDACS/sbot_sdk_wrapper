# Gripper Control Documentation

This document covers gripper control functions for the OnRobot 2FG14 gripper in the `gripper.py` module.

> **Quick Fix**: If your gripper makes a "locking" sound or has communication errors, see [Gripper Locking Sound Issue](#issue-gripper-makes-locking-sound--communication-errors) in the Common Issues section.

## Table of Contents

1. [Overview](#overview)
2. [Gripper Specifications](#gripper-specifications)
3. [Function Reference](#function-reference)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)
6. [Common Issues](#common-issues)

## Overview

The gripper module provides control functions for the OnRobot 2FG14 parallel-jaw gripper mounted on the robot's end effector. The gripper can be controlled with either simple OPEN/CLOSE commands or precise width and force specifications.

### Import Statement

```python
from src.gripper import gripper_command, gripper_request
```

## Gripper Specifications

### OnRobot 2FG14 Specifications

| Specification | Value |
|---------------|-------|
| Model | OnRobot 2FG14 |
| Stroke (Max Opening) | 110 mm (0.11 m) |
| Min Grip Width | 26 mm (0.026 m) |
| Gripping Force Range | 10-140 N |
| Payload | Up to 14 kg |
| Grip Type | Parallel jaw, internal/external |

### Default Configurations

The wrapper provides two preset configurations:

| Command | Width | Force | Use Case |
|---------|-------|-------|----------|
| OPEN | 110 mm (0.11 m) | 10 N | Ready to grasp |
| CLOSE | 26 mm (0.026 m) | 10 N | Light gripping |

**Note**: 10N is a gentle force suitable for most objects. Adjust using `gripper_request()` for specific needs.

**Important - Robot-Specific Calibration**: The CLOSE width value (0.026m) may need adjustment between different robots. See [Calibration Note](#calibration-note) below for symptoms and solutions.

## Function Reference

### gripper_command(STRING)

Simple high-level interface for common gripper operations.

**Parameters:**
- `STRING` (str): Command string - either "OPEN" or "CLOSE" (case-sensitive)

**Returns:** None

**Example:**
```python
# Open gripper
gripper_command("OPEN")

# Close gripper
gripper_command("CLOSE")
```

**Use Cases:**
- Simple pick and place operations
- Quick open/close without custom parameters
- Student-friendly interface

**Calibration Note:**
The CLOSE command uses a default width of 0.026m (26mm), but this value varies between robots. If you experience:
- Gripper making a "locking" sound when closing
- Robot slowing down during gripper operations
- Communication errors with the gripper
- Gripper appearing to struggle or jam

**Solution**: Increase the CLOSE width value in the source code. Edit `gripper.py` or `gripper_command()`:

```python
# Original (may be too tight for some robots)
gripper_request(0.026, 10.0)

# Try increasing by 1-2mm
gripper_request(0.028, 10.0)  # or
gripper_request(0.030, 10.0)
```

Test incrementally until the gripper closes smoothly without making locking sounds or triggering communication errors.

---

### gripper_request(WIDTH, FORCE)

Low-level gripper control with custom width and force parameters.

**Parameters:**
- `WIDTH` (float): Target grip width in meters (0.026 to 0.11)
- `FORCE` (float): Gripping force in Newtons (10 to 140)

**Returns:** None

**Raises:**
- Prints error message if command fails

**Example:**
```python
# Grip with 50mm width and 30N force
gripper_request(0.05, 30.0)

# Gentle grip for fragile objects
gripper_request(0.04, 15.0)

# Strong grip for heavy objects
gripper_request(0.03, 100.0)
```

**Use Cases:**
- Precise control for specific parts
- Adapting to object size
- Fragile or heavy object handling

## Usage Examples

### Example 1: Basic Pick and Place

```python
from src.gripper import gripper_command
from src.movement import move_robot_cartesian, home_robot

# Start at home
home_robot()

# Open gripper
gripper_command("OPEN")

# Move to pick position
move_robot_cartesian(0.5, 0.2, 0.3, 0.0, 1.0, 0.0, 0.0)

# Lower to part
move_robot_cartesian(0.5, 0.2, 0.25, 0.0, 1.0, 0.0, 0.0)

# Close gripper to grasp
gripper_command("CLOSE")

# Lift part
move_robot_cartesian(0.5, 0.2, 0.3, 0.0, 1.0, 0.0, 0.0)

# Move to place position
move_robot_cartesian(0.4, -0.2, 0.3, 0.0, 1.0, 0.0, 0.0)

# Lower to surface
move_robot_cartesian(0.4, -0.2, 0.25, 0.0, 1.0, 0.0, 0.0)

# Open gripper to release
gripper_command("OPEN")

# Lift away
move_robot_cartesian(0.4, -0.2, 0.3, 0.0, 1.0, 0.0, 0.0)

# Return home
home_robot()
```

### Example 2: Gripping Different Sized Objects

```python
from src.gripper import gripper_request

def grip_object(object_diameter_mm):
    """
    Grip object with appropriate width and force
    
    Args:
        object_diameter_mm: Diameter of object in millimeters
    """
    # Convert mm to meters and add small clearance
    grip_width = (object_diameter_mm / 1000.0) - 0.002  # 2mm clearance
    
    # Clamp to gripper limits
    grip_width = max(0.026, min(grip_width, 0.11))
    
    # Determine force based on size (larger = more force)
    if object_diameter_mm < 40:
        force = 20.0  # Light force for small objects
    elif object_diameter_mm < 70:
        force = 50.0  # Medium force
    else:
        force = 80.0  # Higher force for large objects
    
    print(f"Gripping {object_diameter_mm}mm object")
    print(f"  Width: {grip_width*1000:.1f}mm, Force: {force}N")
    
    gripper_request(grip_width, force)

# Usage for different objects
grip_object(30)   # Small part
grip_object(60)   # Medium part
grip_object(90)   # Large part
```

### Example 3: Adaptive Gripping with Verification

```python
from src.gripper import gripper_request, gripper_command
from src.io import read_specific_io
import time

def verified_grip(target_width, force, sensor_pin="Input 10"):
    """
    Grip with force and verify using sensor
    
    Args:
        target_width: Desired grip width in meters
        force: Gripping force in Newtons
        sensor_pin: IO pin connected to grip sensor
    
    Returns:
        bool: True if grip verified, False otherwise
    """
    # Attempt grip
    gripper_request(target_width, force)
    
    # Wait for gripper to settle
    time.sleep(0.5)
    
    # Check grip sensor (if equipped)
    # Assumes sensor goes HIGH when object is gripped
    sensor_state = read_specific_io(sensor_pin)
    
    if sensor_state == "high":
        print("Grip verified - object detected")
        return True
    else:
        print("WARNING: Grip not verified - no object detected")
        return False

# Usage
if verified_grip(0.05, 30.0):
    # Continue with operation
    pass
else:
    # Handle grip failure
    gripper_command("OPEN")
    print("Retrying pick...")
```

### Example 4: Fragile Object Handling

```python
from src.gripper import gripper_request
from src.movement import move_robot_cartesian
import time

def handle_fragile_object():
    """
    Gentle handling routine for fragile objects
    """
    # Use very light force to avoid damage
    FRAGILE_FORCE = 12.0  # Just above minimum
    
    # Open wide
    gripper_request(0.11, FRAGILE_FORCE)
    time.sleep(0.3)
    
    # Move to object
    move_robot_cartesian(0.5, 0.0, 0.35, 0.0, 1.0, 0.0, 0.0)
    move_robot_cartesian(0.5, 0.0, 0.30, 0.0, 1.0, 0.0, 0.0)
    
    # Close very gently around object
    # Assume object is 50mm diameter
    gripper_request(0.048, FRAGILE_FORCE)
    time.sleep(0.5)
    
    # Slow, gentle lift
    move_robot_cartesian(0.5, 0.0, 0.32, 0.0, 1.0, 0.0, 0.0)
    time.sleep(0.5)
    move_robot_cartesian(0.5, 0.0, 0.35, 0.0, 1.0, 0.0, 0.0)
    
    print("Fragile object secured")

# Usage
handle_fragile_object()
```

### Example 5: Multi-Part Assembly

```python
from src.gripper import gripper_command, gripper_request
from src.movement import move_robot_cartesian, home_robot
import time

def assemble_parts():
    """
    Pick and assemble multiple parts with different grip requirements
    """
    home_robot()
    
    # Part 1: Base plate (large, sturdy)
    print("Picking base plate...")
    gripper_command("OPEN")
    move_robot_cartesian(0.4, 0.3, 0.25, 0.0, 1.0, 0.0, 0.0)
    gripper_request(0.08, 60.0)  # Strong grip
    time.sleep(0.3)
    
    # Move to assembly position
    move_robot_cartesian(0.5, 0.0, 0.22, 0.0, 1.0, 0.0, 0.0)
    gripper_command("OPEN")
    time.sleep(0.3)
    
    # Part 2: Small component (delicate)
    print("Picking small component...")
    move_robot_cartesian(0.4, -0.3, 0.25, 0.0, 1.0, 0.0, 0.0)
    gripper_request(0.035, 15.0)  # Gentle grip
    time.sleep(0.3)
    
    # Place on base plate
    move_robot_cartesian(0.5, 0.0, 0.24, 0.0, 1.0, 0.0, 0.0)
    gripper_command("OPEN")
    
    home_robot()
    print("Assembly complete")

# Usage
assemble_parts()
```

### Example 6: Parallel Operations

```python
from src.gripper import gripper_command
from src.movement import move_robot_joint
import time

def rapid_sort_operation():
    """
    Rapidly pick and place multiple parts
    """
    pick_positions = [
        (0.0, 0.5, -1.0, 0.0, 1.5, 0.0),
        (0.5, 0.5, -1.0, 0.0, 1.5, 0.0),
        (1.0, 0.5, -1.0, 0.0, 1.5, 0.0),
    ]
    
    place_positions = [
        (0.0, 0.0, -1.5, 0.0, 1.5, 0.0),
        (0.5, 0.0, -1.5, 0.0, 1.5, 0.0),
        (1.0, 0.0, -1.5, 0.0, 1.5, 0.0),
    ]
    
    for pick_pos, place_pos in zip(pick_positions, place_positions):
        # Open and move to pick
        gripper_command("OPEN")
        move_robot_joint(*pick_pos)
        time.sleep(0.2)
        
        # Grip
        gripper_command("CLOSE")
        time.sleep(0.3)
        
        # Move to place
        move_robot_joint(*place_pos)
        time.sleep(0.2)
        
        # Release
        gripper_command("OPEN")
        time.sleep(0.2)
    
    print(f"Sorted {len(pick_positions)} parts")

# Usage
rapid_sort_operation()
```

### Example 7: Grip Force Testing

```python
from src.gripper import gripper_request
import time

def test_grip_forces():
    """
    Test different grip forces to find optimal setting
    """
    forces = [15, 30, 50, 75, 100]
    width = 0.05  # 50mm
    
    print("Testing grip forces...")
    print("Manually check grip quality for each force level")
    
    for force in forces:
        print(f"\nApplying {force}N force...")
        gripper_request(width, force)
        time.sleep(2)
        
        input(f"Press Enter to test next force level...")
    
    # Return to safe state
    gripper_request(0.11, 10.0)
    print("\nTest complete")

# Usage (interactive)
test_grip_forces()
```

## Best Practices

### 1. Always Open Before Moving

```python
# Good practice
gripper_command("OPEN")
move_robot_cartesian(x, y, z, i, j, k, l)
gripper_command("CLOSE")

# Bad practice (may catch on obstacles)
gripper_command("CLOSE")
move_robot_cartesian(x, y, z, i, j, k, l)  # Moving with closed gripper
```

### 2. Add Delays After Grip Commands

```python
import time

# Allow gripper to complete motion
gripper_command("OPEN")
time.sleep(0.3)  # Wait for gripper to open

gripper_command("CLOSE")
time.sleep(0.3)  # Wait for gripper to close
```

### 3. Match Force to Object

```python
# Fragile objects
gripper_request(width, 15.0)

# Normal objects
gripper_request(width, 30.0)

# Heavy objects
gripper_request(width, 80.0)

# Maximum force (use cautiously)
gripper_request(width, 140.0)
```

### 4. Calculate Grip Width

```python
def calculate_grip_width(object_diameter_mm, clearance_mm=2):
    """
    Calculate grip width with safety margin
    
    Args:
        object_diameter_mm: Object diameter in mm
        clearance_mm: Safety clearance in mm
    
    Returns:
        float: Grip width in meters
    """
    width_m = (object_diameter_mm - clearance_mm) / 1000.0
    
    # Clamp to gripper limits
    return max(0.026, min(width_m, 0.11))

# Usage
width = calculate_grip_width(45)  # 45mm object
gripper_request(width, 30.0)
```

### 5. Error Recovery

```python
from src.gripper import gripper_command
import time

def safe_grip_with_retry(max_attempts=3):
    """Retry gripping with error recovery"""
    
    for attempt in range(max_attempts):
        try:
            gripper_command("CLOSE")
            time.sleep(0.5)
            
            # Verify grip (implementation depends on sensors)
            if grip_is_successful():
                return True
            else:
                print(f"Grip attempt {attempt + 1} failed, retrying...")
                gripper_command("OPEN")
                time.sleep(0.5)
        except Exception as e:
            print(f"Error during grip: {e}")
            gripper_command("OPEN")
            time.sleep(0.5)
    
    return False

def grip_is_successful():
    # Implement verification logic
    # e.g., check force sensor, position sensor, or IO
    return True
```

## Common Issues

### Issue: Gripper doesn't close completely

**Possible causes:**
- Object too large for specified width
- Insufficient force
- Object slipping

**Solutions:**
1. Check object size:
```python
# Measure object and adjust width
gripper_request(0.06, 50.0)  # Wider opening
```

2. Increase force:
```python
gripper_request(0.05, 60.0)  # More force
```

### Issue: Gripper damages objects

**Cause:** Excessive gripping force

**Solution:**
```python
# Reduce force significantly
gripper_request(0.05, 12.0)  # Minimum safe force

# Or use CLOSE command (uses gentle 10N)
gripper_command("CLOSE")
```

### Issue: Gripper not responding

**Possible causes:**
- Gripper not powered
- Communication error
- Emergency stop active

**Solutions:**
1. Check gripper power connection
2. Verify gripper is configured in robot controller
3. Check for error messages in controller
4. Reset gripper (power cycle if needed)

### Issue: Gripper makes "locking" sound / Communication errors

**Symptoms:**
- Grinding or "locking" noise when gripper closes
- Robot slows down during gripper operations
- Error messages about gripper communication
- Gripper appears to struggle or jam when closing

**Root Cause:**
The CLOSE command default width (0.026m/26mm) is attempting to close the gripper beyond its mechanical limit for your specific robot. This varies between robots due to manufacturing tolerances, calibration differences, or wear.

**Solution - Adjust CLOSE Width:**

1. **Locate the gripper_command function** in your code:
   - If using modular files: `src/gripper.py` (line ~125)
   - If using complete wrapper: `src/cdacs_sbot_wrapper.py` (line ~380)

2. **Find the CLOSE command**:
```python
if STRING == "CLOSE":
    print("CLOSING GRIPPER")
    gripper_request(0.026, 10.0)  # <-- This line
```

3. **Increase the width value incrementally**:
```python
# Start by adding 1-2mm (0.001-0.002m)
gripper_request(0.028, 10.0)  # Try 28mm first

# If still locking, increase more
gripper_request(0.030, 10.0)  # Try 30mm

# Continue until gripper closes smoothly
gripper_request(0.032, 10.0)  # Or 32mm if needed
```

4. **Test the new value**:
```python
gripper_command("OPEN")
time.sleep(0.5)
gripper_command("CLOSE")  # Should now close smoothly without locking sounds
time.sleep(0.5)
```

5. **Verify gripping still works**:
   - Ensure the new width can still grip your objects
   - If too wide, objects may slip
   - Find the balance between avoiding locking and maintaining grip

**Typical Values by Robot:**
- Robot A might need: 0.026m (26mm)
- Robot B might need: 0.029m (29mm)
- Robot C might need: 0.032m (32mm)

**Note**: This is normal and expected. Save your robot-specific value in comments for future reference:
```python
# Robot #3 calibration: CLOSE width = 0.030m (tested 2026-03-12)
gripper_request(0.030, 10.0)
```

### Issue: Inconsistent gripping

**Possible causes:**
- Part positioning variation
- Gripper not settling before moving
- Insufficient clearance

**Solutions:**
```python
import time

# Add settling time
gripper_command("CLOSE")
time.sleep(0.5)  # Let gripper fully close

# Increase clearance
gripper_request(0.055, 30.0)  # More clearance than calculated
```

### Issue: Object slips during movement

**Causes:**
- Insufficient grip force
- Object too heavy
- Acceleration too high

**Solutions:**
1. Increase grip force:
```python
gripper_request(0.05, 80.0)  # Stronger grip
```

2. Slow down movements (requires SDK motion planning parameters)

3. Verify object weight is within payload capacity

## Gripper Maintenance

### Regular Checks

1. **Inspect jaws for wear or damage**
   - Check for deformation
   - Ensure jaws are parallel

2. **Clean gripper surfaces**
   - Remove debris from jaws
   - Clean mounting surface

3. **Verify mounting**
   - Check mounting bolts are tight
   - Ensure no play in connection

4. **Test full range of motion**
```python
# Open to maximum
gripper_request(0.11, 10.0)
time.sleep(1)

# Close to minimum
gripper_request(0.026, 10.0)
time.sleep(1)

# Check for smooth operation
```

## Advanced Topics

### Custom Gripper Jaws

The OnRobot 2FG14 supports custom jaw inserts:

- Soft jaws for delicate parts
- Serrated jaws for better grip
- Shaped jaws for specific parts

When using custom jaws, adjust:
- Grip width calculations (account for jaw thickness)
- Grip force (softer jaws may require less force)

### Force Feedback

If gripper is equipped with force feedback:

```python
# Pseudo-code (requires SDK force feedback support)
def adaptive_grip(target_width, max_force):
    """Increase force until object is secure"""
    for force in range(15, max_force, 5):
        gripper_request(target_width, force)
        time.sleep(0.3)
        
        # Read force sensor (implementation depends on setup)
        if object_is_secure():
            print(f"Optimal force found: {force}N")
            return force
    
    return max_force
```

## Related Documentation

- [Movement Control](movement.md) - Coordinate gripper with motion
- [IO Control](io.md) - Use sensors to verify gripping
- [Camera Operations](camera.md) - Vision-guided grasping

---

**Last Updated**: March 2026  
**Module**: gripper.py  
**Gripper Model**: OnRobot 2FG14
