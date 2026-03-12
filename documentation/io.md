# Digital IO Control Documentation

This document covers digital input/output control functions in the `io.py` module.

## Table of Contents

1. [Overview](#overview)
2. [IO Pin Naming](#io-pin-naming)
3. [Function Reference](#function-reference)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)
6. [Common Applications](#common-applications)

## Overview

The IO module provides functions to read digital inputs (sensors, switches) and control digital outputs (valves, lights, relays) connected to the robot controller.

### Import Statement

```python
from src.io import read_specific_io, write_io
```

### IO States

All digital IO pins have two states:
- **"high"**: Logic high (~24V or ~5V depending on controller)
- **"low"**: Logic low (0V, ground)

## IO Pin Naming

### StandardBot Controller Pin Names

The robot controller uses specific naming conventions for IO pins:

#### Input Pins (Read-only)
```
"Input 1", "Input 2", "Input 3", ..., "Input N"
```
Also may appear as:
```
"digital_in_0", "digital_in_1", "digital_in_2", ...
```

#### Output Pins (Read/Write)
```
"Output 0", "Output 1", "Output 2", ..., "Output N"
```
Also may appear as:
```
"digital_out_0", "digital_out_1", "digital_out_2", ...
```

**Important:** Pin names are case-sensitive!

### Finding Available Pins

To discover available IO pins on your robot:

```python
from standardbots import StandardBotsRobot

# Initialize SDK (use your robot's credentials)
sdk = StandardBotsRobot(url="...", token="...", robot_kind=...)

# Get all IO states
with sdk.connection():
    response = sdk.io.status.get_io_state()
    data = response.ok()
    
    print("Available IO pins:")
    for pin_name, state in data.state.items():
        print(f"  {pin_name}: {state}")
```

## Function Reference

### read_specific_io(pin_name)

Read the current state of a digital input or output pin.

**Parameters:**
- `pin_name` (str): Name of the IO pin (e.g., "Input 1", "Output 3")

**Returns:**
- `str`: "high" or "low" if successful
- `None`: If pin not found or error occurs

**Example:**
```python
state = read_specific_io("Input 2")
if state == "high":
    print("Sensor activated!")
elif state == "low":
    print("Sensor not activated")
else:
    print("Error reading sensor")
```

**Common Use Cases:**
- Reading limit switches
- Checking sensor states
- Monitoring safety interlocks
- Detecting part presence

---

### write_io(pin_name, state)

Set the state of a digital output pin.

**Parameters:**
- `pin_name` (str): Name of the output pin (e.g., "Output 0", "Output 4")
- `state` (str): Desired state ("high" or "low", case-insensitive)

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
# Turn on pneumatic valve
success = write_io("Output 3", "high")
if success:
    print("Valve opened")
    
# Turn off valve
write_io("Output 3", "low")
```

**Common Use Cases:**
- Controlling pneumatic valves
- Activating relays
- Controlling indicator lights
- Triggering external equipment

## Usage Examples

### Example 1: Simple Sensor Reading

```python
from src.io import read_specific_io

# Read a limit switch
limit_switch = read_specific_io("Input 1")

if limit_switch == "high":
    print("Part detected at station")
else:
    print("No part at station")
```

### Example 2: Waiting for Sensor Activation

```python
from src.io import read_specific_io
import time

def wait_for_sensor(pin_name, timeout=30):
    """
    Wait for a sensor to activate (go high)
    
    Args:
        pin_name: Name of input pin
        timeout: Maximum wait time in seconds
    
    Returns:
        bool: True if sensor activated, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        state = read_specific_io(pin_name)
        if state == "high":
            return True
        time.sleep(0.1)  # Check every 100ms
    
    return False

# Usage
print("Waiting for part sensor...")
if wait_for_sensor("Input 2", timeout=10):
    print("Part detected!")
else:
    print("Timeout - no part detected")
```

### Example 4: Safety Interlock System

```python
from src.io import read_specific_io, write_io
from src.movement import move_robot_cartesian

def check_safety_interlocks():
    """
    Check all safety interlocks before allowing robot motion
    
    Returns:
        bool: True if all safety conditions met
    """
    # Check door closed (Input 3)
    door_closed = read_specific_io("Input 3") == "high"
    
    # Check emergency stop not pressed (Input 4)
    estop_ok = read_specific_io("Input 4") == "low"
    
    # Check light curtain clear (Input 5)
    curtain_clear = read_specific_io("Input 5") == "high"
    
    if not door_closed:
        print("SAFETY: Door is open!")
        return False
    
    if not estop_ok:
        print("SAFETY: Emergency stop activated!")
        return False
    
    if not curtain_clear:
        print("SAFETY: Light curtain blocked!")
        return False
    
    return True

def safe_move(x, y, z, i, j, k, l):
    """Move robot only if safety interlocks are satisfied"""
    if check_safety_interlocks():
        # Turn on "robot moving" indicator light
        write_io("Output 1", "high")
        
        move_robot_cartesian(x, y, z, i, j, k, l)
        
        # Turn off indicator
        write_io("Output 1", "low")
    else:
        print("Movement aborted - safety interlock failure")

# Usage
safe_move(0.5, 0.3, 0.4, 0.0, 0.707, 0.0, 0.707)
```


### Example 6: Machine Tending with Handshaking

```python
from src.io import read_specific_io, write_io
import time

def cnc_machine_tending():
    """
    Coordinate with CNC machine using IO handshaking
    
    Robot IO:
        Output 1: Robot ready signal to CNC
        Output 2: Part loaded signal
        Input 7: CNC cycle complete signal
    
    Sequence:
        1. Signal robot ready
        2. Load part
        3. Wait for CNC cycle complete
        4. Unload part
    """
    print("Machine tending cycle started")
    
    # Signal to CNC: Robot is ready
    write_io("Output 1", "high")
    print("Signaled: Robot ready")
    
    # Load part (assuming pick/place functions exist)
    load_part_to_cnc()
    
    # Signal to CNC: Part is loaded
    write_io("Output 2", "high")
    print("Signaled: Part loaded")
    
    # Wait for CNC to signal cycle complete
    print("Waiting for CNC cycle to complete...")
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if read_specific_io("Input 7") == "high":
            print("CNC cycle complete!")
            break
        time.sleep(0.5)
    else:
        print("ERROR: CNC cycle timeout!")
        return False
    
    # Unload part
    unload_part_from_cnc()
    
    # Reset signals
    write_io("Output 1", "low")
    write_io("Output 2", "low")
    
    print("Machine tending cycle complete")
    return True

def load_part_to_cnc():
    # Implementation of part loading
    pass

def unload_part_from_cnc():
    # Implementation of part unloading
    pass

# Usage
cnc_machine_tending()
```

## Best Practices

### 1. Input Debouncing

Mechanical switches may "bounce," causing multiple rapid state changes. Implement debouncing:

```python
import time

def read_debounced(pin_name, stable_time=0.05):
    """
    Read input with debouncing
    
    Args:
        pin_name: Name of input pin
        stable_time: Time signal must be stable (seconds)
    
    Returns:
        str: Stable state ("high" or "low")
    """
    # Read initial state
    state = read_specific_io(pin_name)
    start = time.time()
    
    # Wait for stable state
    while time.time() - start < stable_time:
        new_state = read_specific_io(pin_name)
        if new_state != state:
            # State changed, restart timer
            state = new_state
            start = time.time()
        time.sleep(0.01)
    
    return state
```

### 2. Error Handling

Always check return values:

```python
# Good practice
state = read_specific_io("Input 1")
if state is None:
    print("ERROR: Could not read Input 1")
    # Handle error appropriately
elif state == "high":
    # Process high state
    pass

# Bad practice (no error checking)
if read_specific_io("Input 1") == "high":  # Could fail if state is None
    pass
```

### 3. State Verification

Verify outputs were set correctly:

```python
def safe_write_io(pin_name, desired_state, verify=True):
    """Write IO with optional verification"""
    success = write_io(pin_name, desired_state)
    
    if not success:
        print(f"ERROR: Failed to write {pin_name}")
        return False
    
    if verify:
        time.sleep(0.05)  # Allow time for output to settle
        actual_state = read_specific_io(pin_name)
        if actual_state != desired_state:
            print(f"WARNING: {pin_name} state mismatch")
            return False
    
    return True
```

### 4. Documentation

Document your IO wiring clearly:

```python
# IO Configuration for Cell Station 1
# ====================================
# INPUTS:
#   Input 1: Part presence sensor (photoelectric, NPN, normally low)
#   Input 2: Door closed limit switch (mechanical, normally low)
#   Input 3: Emergency stop (NC contact, low when pressed)
#
# OUTPUTS:
#   Output 0: Status light green (high = on)
#   Output 1: Status light red (high = on)
#   Output 2: Pneumatic valve extend (high = extend)
```

## Common Applications

### Machine Tending
- Load/unload parts from CNC machines
- Coordinate cycles with machine signals
- Monitor door interlocks

### Assembly
- Detect part presence
- Control fastening tools
- Verify assembly steps with sensors

### Material Handling
- Conveyor belt control
- Part ejection
- Buffer zone management

### Quality Inspection
- Trigger measurement equipment
- Coordinate with vision systems
- Sort parts based on sensor feedback

## Troubleshooting

### Issue: Sensor always reads "low"

**Possible causes:**
- Sensor not powered
- Wiring disconnected
- Wrong pin name
- Sensor type mismatch (NPN vs PNP)

**Solutions:**
1. Verify pin name is correct
2. Check sensor has power
3. Use multimeter to verify sensor output
4. Consult wiring diagrams

### Issue: Output won't change state

**Possible causes:**
- Wrong pin name
- Output pin configured as input
- Load exceeding output rating
- Wiring issue

**Solutions:**
1. Verify pin name in code
2. Check robot controller configuration
3. Verify load is within specs (typically 2A max)
4. Test with multimeter

### Issue: Intermittent readings

**Possible causes:**
- Loose wiring
- Electrical noise
- Inadequate debouncing

**Solutions:**
1. Check all connections
2. Add shielded cables for long runs
3. Implement debouncing in code
4. Add delay between reads

## Related Documentation

- [Movement Control](movement.md) - Coordinate IO with motion
- [Gripper Control](gripper.md) - Verify gripping with sensors
- [Setup Guide](setup.md) - IO hardware configuration

---

**Last Updated**: March 2026  
**Module**: io.py
