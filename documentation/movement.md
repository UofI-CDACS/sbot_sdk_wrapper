# Movement Control Documentation

This document covers all robot movement functions in the `movement.py` module.

## Table of Contents

1. [Overview](#overview)
2. [Coordinate Systems](#coordinate-systems)
3. [Function Reference](#function-reference)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)
6. [Common Issues](#common-issues)

## Overview

The movement module provides functions to control the StandardBot R01 robot arm in both Cartesian space and joint space. Understanding when to use each type of movement is crucial for effective robot programming.

### Import Statement

```python
from src.movement import get_position_info, move_robot_cartesian, move_robot_joint, home_robot
```

## Coordinate Systems

### Cartesian Coordinates (X, Y, Z)

The robot uses a right-handed Cartesian coordinate system:

- **X-axis**: Forward/backward (positive = forward)
- **Y-axis**: Left/right (positive = left)
- **Z-axis**: Up/down (positive = up)
- **Origin**: Robot base center

Units: Meters

Example positions:
```
Base center: (0.0, 0.0, 0.0)
Forward 0.5m, left 0.3m, up 0.4m: (0.5, 0.3, 0.4)
```

### Orientation (Quaternions)

Orientation is specified using quaternions (i, j, k, l), where:
- i, j, k: Vector components
- l (or w): Scalar component

Common orientations:
- **Downward facing**: (0.0, 1.0, 0.0, 0.0)
- **Forward facing**: (0.707, 0.0, 0.0, 0.707)
- **90° rotation**: Varies based on axis

**Tip**: Use `get_position_info()` to record orientations from teach positions.

### Joint Space (J1-J6)

Six revolute joints control the robot:

| Joint | Description | Typical Range |
|-------|-------------|---------------|
| J1 | Base rotation | -2π to 2π rad |
| J2 | Shoulder | -π to π rad |
| J3 | Elbow | -π to π rad |
| J4 | Wrist 1 (roll) | -2π to 2π rad |
| J5 | Wrist 2 (pitch) | -π to π rad |
| J6 | Wrist 3 (yaw) | -2π to 2π rad |

Units: Radians (π rad ≈ 3.14159 rad = 180°)

## Function Reference

### get_position_info()

Get the current robot position and joint angles.

**Returns:**
- `tuple`: Six joint angles (j1, j2, j3, j4, j5, j6) in radians
- `None`: If error occurs

**Prints:**
- Joint rotations for all 6 joints
- Tooltip position (x, y, z) in meters
- Tooltip orientation (quaternion i, j, k, l)

**Example:**
```python
joints = get_position_info()
if joints:
    j1, j2, j3, j4, j5, j6 = joints
    print(f"Base rotation (J1): {j1} radians")
```

**Use Cases:**
- Recording positions for playback
- Verifying robot location
- Debugging movement issues
- Teaching positions manually

---

### move_robot_cartesian(x, y, z, i, j, k, l)

Move the robot tooltip to a Cartesian position with specified orientation.

**Parameters:**
- `x` (float): X position in meters
- `y` (float): Y position in meters
- `z` (float): Z position in meters
- `i` (float): Quaternion i component
- `j` (float): Quaternion j component
- `k` (float): Quaternion k component
- `l` (float): Quaternion l/w component

**Returns:** None

**Behavior:**
- Automatically unbrakes robot
- Plans motion path to target
- Executes movement
- Blocks until movement complete

**Example:**
```python
# Move to position 0.5m forward, 0.3m left, 0.4m up
# with specific orientation
move_robot_cartesian(
    x=0.5,
    y=0.3,
    z=0.4,
    i=0.002,
    j=0.717,
    k=-0.002,
    l=0.697
)
```

**Use Cases:**
- Precise positioning for assembly
- Following straight-line paths
- Maintaining constant orientation
- Pick and place operations

---

### move_robot_joint(j1, j2, j3, j4, j5, j6)

Move the robot to specified joint angles.

**Parameters:**
- `j1` (float): Joint 1 angle in radians
- `j2` (float): Joint 2 angle in radians
- `j3` (float): Joint 3 angle in radians
- `j4` (float): Joint 4 angle in radians
- `j5` (float): Joint 5 angle in radians
- `j6` (float): Joint 6 angle in radians

**Returns:** None

**Behavior:**
- Automatically unbrakes robot
- Moves joints along shortest path
- Movement may not be linear in Cartesian space
- Blocks until movement complete

**Example:**
```python
# Move to specific joint configuration
move_robot_joint(
    j1=0.0,
    j2=0.5,
    j3=-1.0,
    j4=0.0,
    j5=1.5,
    j6=-3.14
)
```

**Use Cases:**
- Avoiding singularities
- Clearing obstacles
- Reaching positions unreachable in Cartesian mode
- Faster movements between positions

---

### home_robot()

Move robot to predefined home position.

**Parameters:** None

**Returns:** None

**Home Position:**
- J1: 0.0 rad (0°)
- J2: 0.0 rad (0°)
- J3: -1.5 rad (-85.9°)
- J4: 0.0 rad (0°)
- J5: 1.5 rad (85.9°)
- J6: -3.14 rad (-180°)

**Example:**
```python
# Return to home position
home_robot()
```

**Use Cases:**
- Program start/end position
- Safe position for tool changes
- Recovery from errors
- Consistent starting point

## Usage Examples

### Example 1: Recording and Replaying Positions

```python
from src.movement import get_position_info, move_robot_cartesian

# Manually move robot to desired position using teach pendant
print("Move robot to position 1, then press Enter")
input()
pos1 = get_position_info()

print("Move robot to position 2, then press Enter")
input()
pos2 = get_position_info()

# Later, replay the positions
# Note: get_position_info returns joints, but we want Cartesian
# Better approach: extract full position data in custom function
```

### Example 2: Linear Motion Pattern

```python
from src.movement import move_robot_cartesian, home_robot

# Start at home
home_robot()

# Define orientation (downward facing)
i, j, k, l = 0.002, 0.717, -0.002, 0.697

# Move in a square pattern at constant height
height = 0.3

# Position 1
move_robot_cartesian(0.4, 0.2, height, i, j, k, l)

# Position 2
move_robot_cartesian(0.4, -0.2, height, i, j, k, l)

# Position 3
move_robot_cartesian(0.6, -0.2, height, i, j, k, l)

# Position 4
move_robot_cartesian(0.6, 0.2, height, i, j, k, l)

# Return to start
home_robot()
```

### Example 3: Joint-Based Movement for Speed

```python
from src.movement import move_robot_joint, home_robot
import time

# Start at home
home_robot()

# Quick joint movements between positions
positions = [
    (0.0, 0.5, -1.0, 0.0, 1.5, 0.0),
    (0.5, 0.5, -1.0, 0.0, 1.5, 0.0),
    (0.5, 0.0, -1.5, 0.0, 1.5, 0.0),
]

for pos in positions:
    move_robot_joint(*pos)
    time.sleep(0.5)  # Brief pause at each position

home_robot()
```


## Best Practices

### Movement Planning

1. **Always start with home_robot()**
   - Establishes known starting point
   - Ensures safe initial configuration

2. **Use Cartesian movements for straight lines**
   - Better for precision tasks
   - Maintains orientation
   - More predictable paths

3. **Use joint movements for speed**
   - Faster between distant points
   - Avoids singularities
   - More energy efficient

### Safety

1. **Check workspace boundaries**
   ```python
   # Define safe workspace
   X_MIN, X_MAX = 0.2, 0.8
   Y_MIN, Y_MAX = -0.4, 0.4
   Z_MIN, Z_MAX = 0.1, 0.6
   
   def is_position_safe(x, y, z):
       return (X_MIN <= x <= X_MAX and
               Y_MIN <= y <= Y_MAX and
               Z_MIN <= z <= Z_MAX)
   ```

2. **Use approach heights**
   - Always approach from above
   - Prevents collisions
   - Provides clearance

3. **Add delays between movements**
   ```python
   import time
   
   move_robot_cartesian(x1, y1, z1, i, j, k, l)
   time.sleep(0.5)  # Let robot settle
   move_robot_cartesian(x2, y2, z2, i, j, k, l)
   ```

### Debugging

1. **Print positions before moving**
   ```python
   print(f"Moving to: X={x}, Y={y}, Z={z}")
   move_robot_cartesian(x, y, z, i, j, k, l)
   ```

2. **Verify movements**
   ```python
   move_robot_cartesian(x, y, z, i, j, k, l)
   new_pos = get_position_info()
   print(f"Arrived at: {new_pos}")
   ```

3. **Test at reduced speed** (if supported by SDK)

## Common Issues

### Issue: Robot won't move

**Causes:**
- Brakes engaged (function auto-unbrakes, but may fail)
- Position out of reach
- Joint limits exceeded
- Emergency stop active

**Solutions:**
```python
# Manual brake release (if needed)
from standardbots import StandardBotsRobot

with sdk.connection():
    sdk.movement.brakes.unbrake().ok()
```

### Issue: Unexpected path

**Problem:** Robot takes curved path instead of straight line

**Cause:** Using `move_robot_joint()` for Cartesian paths

**Solution:** Use `move_robot_cartesian()` for straight-line motion

### Issue: Position unreachable

**Problem:** Robot returns error or doesn't move

**Causes:**
- Position outside workspace
- Singular configuration
- Orientation impossible to achieve

**Solutions:**
1. Check position is within reach (~0.8m radius)
2. Adjust orientation
3. Try joint-space movement
4. Use `get_position_info()` to find reachable positions

### Issue: Jerky motion

**Problem:** Robot moves in steps or jerks

**Causes:**
- Commands sent too rapidly
- Network latency
- System load

**Solutions:**
```python
import time

# Add delays between movements
move_robot_cartesian(x1, y1, z1, i, j, k, l)
time.sleep(0.5)
move_robot_cartesian(x2, y2, z2, i, j, k, l)
```

## Related Documentation

- [IO Control](io.md) - Coordinate movements with sensors
- [Gripper Control](gripper.md) - Combine with pick/place
- [Camera Operations](camera.md) - Vision-guided positioning

---

**Last Updated**: March 2026  
**Module**: movement.py
