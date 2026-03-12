# Setup and Configuration Guide

This guide will help you install and configure the CDACS StandardBot wrapper for your development environment.

## CRITICAL: Package Version Requirements

> **WARNING: This wrapper REQUIRES a specific version of the standardbots package!**
> 
> **You MUST use: `standardbots==2.20241120.1`**
> 
> **DO NOT install any other version!** The wrapper is designed for this specific SDK version and other versions will cause compatibility issues and break functionality.
> 
> Always install using `requirements.txt` to ensure the correct version:
> ```bash
> pip install -r requirements.txt
> ```

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Robot Configuration](#robot-configuration)
4. [Network Setup](#network-setup)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Hardware Requirements

- StandardBot R01 robot arm
- Network connection to robot controller
- Computer with Python 3.8 or higher
- (Optional) OnRobot 2FG14 gripper
- (Optional) End-effector camera

### Software Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Knowledge Requirements

- Basic Python programming
- Understanding of robot coordinate systems
- Familiarity with command line/terminal

## Installation

### Step 1: Clone the Repository

```bash
# Navigate to your projects directory
cd ~/Projects

# Clone the repository
git clone https://github.com/UofI-CDACS/sbot_sdk_wrapper
cd sbot_sdk_wrapper
```

### Step 2: Install Python Dependencies

The project requires several Python packages **with specific versions**.

**CRITICAL: You MUST install from requirements.txt to get the correct versions!**

```bash
# Install all required packages with correct versions
pip install -r requirements.txt

# NEVER run: pip install standardbots
# This will install the wrong version and WILL break the wrapper!
```

The `requirements.txt` includes:
- **`standardbots==2.20241120.1`** - EXACT version required (SDK dated 2024-11-20)
- `opencv-python>=4.11.0.86` - For camera image processing
- `numpy>=2.2.5` - For numerical operations
- `pandas>=2.2.3` - For data handling

### Step 3: Verify Installation and Versions

Check that packages are installed correctly **with the correct versions**:

```bash
# Check all packages imported
python3 -c "import standardbots; import cv2; import numpy; print('All packages installed successfully!')"

# CRITICAL: Verify standardbots version
python3 -c "import standardbots; print(f'standardbots version: {standardbots.__version__}')"
```

**You MUST see:** `standardbots version: 2.20241120.1`

**If you see ANY other version number:**
```bash
# Uninstall the wrong version
pip uninstall standardbots

# Reinstall from requirements.txt
pip install -r requirements.txt

# Verify again
python3 -c "import standardbots; print(standardbots.__version__)"
```

## Robot Configuration

### Finding Your Robot's IP Address

1. Access the robot's teach pendant or control interface
2. Navigate to Network Settings
3. Note the IP address (typically format: `10.8.4.XX` or `192.168.1.XX`)
4. Note the port (default: `3000`)

### Getting Your Authentication Token

1. Contact the CDACS lab administrator or view the Teaching Pendant for your authentication token
2. Each robot has a unique token for security
3. Keep your token confidential

### Updating Configuration in Code

You need to update the robot configuration in each module you use. The configuration appears at the top of each file:

#### Option 1: Update Individual Modules

If using individual modules (movement.py, io.py, camera.py, gripper.py), update each file:

```python
sdk = StandardBotsRobot(
    url="http://YOUR_ROBOT_IP:3000",      # Update this line
    token="YOUR_AUTH_TOKEN",               # Update this line
    robot_kind=StandardBotsRobot.RobotKind.Live,
)
```

Example:
```python
sdk = StandardBotsRobot(
    url="http://10.8.4.11:3000",
    token="8geqfqu0-qbbkig-ozwgr4-tl2xfj7",
    robot_kind=StandardBotsRobot.RobotKind.Live,
)
```

#### Option 2: Use Environment Variables (Advanced)

For better security, use environment variables:

1. Create a `.env` file in your project root:
```bash
ROBOT_URL=http://10.8.4.11:3000
ROBOT_TOKEN=your_token_here
```

2. Modify the SDK initialization:
```python
import os
from standardbots import StandardBotsRobot

sdk = StandardBotsRobot(
    url=os.getenv("ROBOT_URL"),
    token=os.getenv("ROBOT_TOKEN"),
    robot_kind=StandardBotsRobot.RobotKind.Live,
)
```

## Network Setup

### Connecting to the Robot

The robot controller must be accessible on your network:

#### Lab Network (UFOI)

1. Connect your computer to the lab network (Nile Robot)
2. Verify you can ping the robot:
   ```bash
   ping 10.8.4.11
   ```
3. If successful, you should see responses

## Verification

### Test Basic Connection

Create a test file `test_connection.py`:

```python
from src.movement import get_position_info

print("Testing connection to robot...")
result = get_position_info()

if result:
    print("SUCCESS! Connection established.")
    print(f"Joint positions: {result}")
else:
    print("FAILED! Could not connect to robot.")
```

Run the test:
```bash
python test_connection.py
```

### Test Each Module

#### Test Movement

```python
from src.movement import home_robot

print("Testing movement...")
home_robot()
print("Movement test complete!")
```

#### Test IO

```python
from src.io import read_specific_io

print("Testing IO...")
state = read_specific_io("Input 1")
print(f"Input 1 state: {state}")
```

#### Test Camera

```python
from src.camera import capture_image

print("Testing camera...")
img = capture_image()
if img is not None:
    print(f"Image captured! Size: {img.shape}")
```

#### Test Gripper

```python
from src.gripper import gripper_command

print("Testing gripper...")
gripper_command("OPEN")
print("Gripper opened successfully!")
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to robot

**Solutions**:
1. Verify robot IP address is correct
2. Check network connectivity: `ping <robot_ip>`
3. Verify firewall isn't blocking connection
4. Confirm robot controller is powered on
5. Check authentication token is correct

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'standardbots'`

**Solution**:
```bash
# IMPORTANT: Install from requirements.txt to get the correct version!
pip install -r requirements.txt

# DO NOT run: pip install standardbots
# This will install the wrong version!
```

**Problem**: `ModuleNotFoundError: No module named 'cv2'`

**Solution**:
```bash
pip install opencv-python
# Or install all dependencies: pip install -r requirements.txt
```

### Authentication Errors

**Problem**: Authentication failed or token rejected

**Solutions**:
1. Verify token is copied correctly (no extra spaces)
2. Confirm token hasn't expired
3. Contact lab administrator for new token

### Camera Issues

**Problem**: Camera not capturing images

**Solutions**:
1. Verify camera is physically connected to robot
2. Check camera settings in robot configuration
3. Ensure camera has power
4. Try adjusting camera settings (exposure, brightness)

### Gripper Issues

**Problem**: Gripper not responding

**Solutions**:
1. Verify gripper is properly connected to robot
2. Check gripper model matches configuration (OnRobot 2FG14)
3. Ensure gripper is receiving power
4. Verify gripper initialization in robot controller

### Position/Movement Errors

**Problem**: Robot won't move or returns error

**Solutions**:
1. Ensure position is within robot's reachable workspace
2. Check for joint limit violations
3. Verify robot brakes are released
4. Clear any error states on robot controller
5. Ensure no obstacles in robot's path

## Next Steps

Once setup is complete:

1. Review the [Movement Documentation](movement.md) to learn robot positioning
2. Explore [IO Documentation](io.md) for sensor integration
3. Check [Camera Documentation](camera.md) for vision applications
4. See [Gripper Documentation](gripper.md) for manipulation tasks

## Getting Help

If you encounter issues not covered here:

1. Check error messages carefully
2. Review robot controller logs
3. Consult StandardBot official documentation
4. Contact CDACS lab support

## Additional Resources

- StandardBot Official Documentation: [Link to docs]
- Python Tutorial: https://docs.python.org/3/tutorial/
- OpenCV Documentation: https://docs.opencv.org/
- NumPy Documentation: https://numpy.org/doc/

---

**Last Updated**: March 2026  
**Version**: 1.0.0
