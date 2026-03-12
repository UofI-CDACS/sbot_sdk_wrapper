# CDACS StandardBot R01 Wrapper

A Python wrapper library for controlling the StandardBot R01 robot arm at the University of Idaho Facility (CDA).

This wrapper provides simplified, student-friendly interfaces for common robot operations including movement control, digital IO, camera operations, and gripper control.

## !!VERY IMPORTANT!! Package Version Requirements

> **WARNING: This wrapper REQUIRES a specific version of the standardbots package!**
> 
> **You MUST use: `standardbots==2.20241120.1`**
> 
> **DO NOT use any other version!** Other versions may have incompatible API changes that will break this wrapper.
> 
> Always install from `requirements.txt` to ensure correct versions:
> ```bash
> pip install -r requirements.txt
> ```
> 
> **Never run** `pip install standardbots` without the version specifier!

## Features

- **Movement Control**: Cartesian and joint-space positioning
- **Digital IO**: Read sensors and control outputs
- **Camera Integration**: Capture images from end-effector camera
- **Gripper Control**: Simple interface for OnRobot 2FG14 gripper
- **Modular Design**: Use individual modules or complete wrapper
- **Well-Documented**: Comprehensive docstrings and examples

## Roadmap

- Pictures for usuage of Teaching Pendant (how to find ip and token, etc)
- Individual Joint Control
- Modbus communications 
- More camera functions
- More IO functions

## Project Structure

```
sbot_sdk_wrapper/
├── src/
│   ├── cdacs_sbot_wrapper.py  # Main wrapper - USE THIS! (all functions)
│   ├── movement.py            # Robot movement functions (modular)
│   ├── io.py                  # Digital IO control (modular)
│   ├── camera.py              # Camera operations (modular)
│   └── gripper.py             # Gripper control (modular)
├── documentation/
│   ├── setup.md               # Installation and configuration
│   ├── movement.md            # Movement function documentation
│   ├── io.md                  # IO function documentation
│   ├── camera.md              # Camera function documentation
│   └── gripper.md             # Gripper function documentation
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Quick Start

### 1. Prerequisites

Before starting, make sure you have:
- **Python 3.8 or higher** installed on your computer
  - Check by running: `python --version` or `python3 --version`
  - If not installed, download from [python.org](https://www.python.org/downloads/)
- **Basic command line knowledge** (how to navigate directories)
- **Git** (optional, for cloning the repository)

### 2. Setting Up Your Python Environment

It's **highly recommended** to use a virtual environment to avoid conflicts with other Python projects. This creates an isolated space for this project's dependencies.

#### For Beginners: What is a Virtual Environment?

A virtual environment is like a separate "sandbox" for your Python project. It keeps all the packages and dependencies for this project separate from your other Python work. Think of it like having a dedicated toolbox for this specific robot project.

#### Step-by-Step Environment Setup

**Windows:**
```bash
# 1. Navigate to your project folder
cd path\to\sbot_sdk_wrapper

# 2. Create a virtual environment named 'venv'
python -m venv venv

# 3. Activate the virtual environment
venv\Scripts\activate

# You should see (venv) appear at the start of your command line
```

**macOS/Linux:**
```bash
# 1. Navigate to your project folder
cd path/to/sbot_sdk_wrapper

# 2. Create a virtual environment named 'venv'
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate

# You should see (venv) appear at the start of your command line
```

**What the commands mean:**
- `python -m venv venv` - Creates a new virtual environment folder called 'venv'
- `activate` - Turns on the virtual environment (must do this every time you open a new terminal)
- `(venv)` - This prefix shows your virtual environment is active

#### Deactivating the Environment

When you're done working:
```bash
deactivate
```

You'll need to activate the environment again next time you work on this project.

### 3. Installation

**CRITICAL: You MUST use requirements.txt to get the correct package versions!**

**With the virtual environment activated:**

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/UofI-CDACS/sbot_sdk_wrapper
cd sbot_sdk_wrapper

# Make sure your virtual environment is activated (you should see (venv) in your terminal)

# IMPORTANT: Install dependencies from requirements.txt
# This ensures you get standardbots==2.20241120.1 (the ONLY compatible version)
pip install -r requirements.txt

# Wait for all packages to download and install...
# This may take a few minutes
```

**Verify Installation and Check Versions:**
```bash
# Test that packages installed correctly
python -c "import standardbots; import cv2; import numpy; print('Success! All packages installed.')"

# CRITICAL: Verify you have the correct standardbots version
python -c "import standardbots; print(f'standardbots version: {standardbots.__version__}')"

# You MUST see: standardbots version: 2.20241120.1
# If you see ANY other version, REINSTALL using requirements.txt!
```

If you see "Success! All packages installed." and the correct version, you're ready to go!

**Troubleshooting:**
- If `pip` command not found, try `pip3` instead
- If you get permission errors, make sure your virtual environment is activated
- On some systems you may need to use `python3` and `pip3` instead of `python` and `pip`
- **If you have the wrong standardbots version:**
  ```bash
  pip uninstall standardbots
  pip install -r requirements.txt
  ```

See [documentation/setup.md](documentation/setup.md) for detailed installation instructions and advanced setup options.

### 4. Configuration

Before you can control the robot, you need to tell the code where your robot is and how to connect to it.

**You'll need two pieces of information from either the teaching pendant or your lab instructor:**
1. **Robot IP Address** - The network address of your robot (looks like `10.8.4.11`)
2. **Authentication Token** - A secret password for your robot (looks like a random string)

**To configure the robot connection:**

1. Open the file you plan to use (see Usage Options below)
2. Find the section near the top that looks like this:

```python
sdk = StandardBotsRobot(
    url="http://10.8.4.11:3000",           # Robot's IP address
    token="8geqfqu0-qbbkig-ozwgr4-tl2xfj7", # Authentication token
    robot_kind=StandardBotsRobot.RobotKind.Live,
)
```

3. **Replace** the IP address and token with your robot's information:
   - Change `http://10.8.4.11:3000` to `http://YOUR_ROBOT_IP:3000`
   - Change the token string to your robot's token
   - Keep the `:3000` at the end of the URL (that's the port number)
   - Keep `RobotKind.Live` as-is (this tells it to use the real robot)

**Example:**
If your robot IP is `192.168.1.50` and token is `abc123-xyz789`:
```python
sdk = StandardBotsRobot(
    url="http://192.168.1.50:3000",
    token="abc123-xyz789",
    robot_kind=StandardBotsRobot.RobotKind.Live,
)
```

**Which files need updating?**
- If using **Option A** (main wrapper): Update only `src/cdacs_sbot_wrapper.py` (one file!)
- If using **Option B** (individual modules): Update each module you're using (`src/movement.py`, `src/io.py`, etc.)

**Don't have the robot info?** Ask your lab instructor or check the lab documentation.

See [documentation/setup.md](documentation/setup.md) for more configuration options.

### 5. Usage Options

#### Option A: Use the Main Wrapper (Recommended for Students)

Import everything from the main wrapper file - this gives you all functions in one place:

```python
from src.cdacs_sbot_wrapper import *

# Home the robot
home_robot()

# Open gripper
gripper_command("OPEN")

# Move to a position
move_robot_cartesian(0.5, 0.3, 0.4, 0.0, 0.707, 0.0, 0.707)

# Capture an image
img = capture_image()

# Close gripper
gripper_command("CLOSE")
```

**Why use this?** 
- Only one file to configure (update IP/token in one place)
- All functions available
- Simplest for beginners

#### Option B: Use Individual Modules (Advanced)

Import only what you need from specific modules:

```python
from src.movement import move_robot_joint, home_robot
from src.gripper import gripper_command

home_robot()
gripper_command("OPEN")
move_robot_joint(0.0, 0.5, -1.0, 0.0, 1.0, 0.0)
```

**Why use this?**
- Cleaner imports if you only need specific functionality
- Better for larger projects with many files
- Each module can have different robot configurations

## Your First Program

Let's write a simple program to test your robot connection!

**Step 1:** Create a new file called `test_robot.py` in your project folder

**Step 2:** Copy this code into the file:

```python
# Import all robot functions from the main wrapper
from src.cdacs_sbot_wrapper import *

# Print a message
print("Testing robot connection...")

# Try to get the robot's current position
# This will verify the robot is connected and responding
position = get_position_info()

if position:
    print("SUCCESS! Robot is connected and responding!")
    print("The robot returned its joint positions")
else:
    print("ERROR: Could not connect to robot")
    print("Check your IP address and token in the configuration")
```

**Step 3:** Run your program:

```bash
# Make sure your virtual environment is activated (you should see (venv))
python test_robot.py
```

**What should happen:**
- You should see "Testing robot connection..."
- Then see the robot's current joint positions printed
- Finally see "SUCCESS! Robot is connected and responding!"

**If it doesn't work:**
- Double-check your robot IP address and token are correct
- Make sure you're connected to the same network as the robot
- Verify the robot is powered on
- See the [Setup Guide](documentation/setup.md) for troubleshooting

**Next Steps:**
Once this works, you're ready to try the examples below!

## Basic Examples

### Example 1: Pick and Place

**Note**: Be careful when running this example.

```python
from src.cdacs_sbot_wrapper import *

# Start at home
home_robot()

# Open gripper
gripper_command("OPEN")

# Move to object
move_robot_cartesian(-0.64, -0.66, 0.27, 0.002, 0.717, -0.002, 0.697)

# Close gripper to grasp
gripper_command("CLOSE")

# Move to drop location
move_robot_cartesian(-0.5, 0.3, 0.4, 0.002, 0.717, -0.002, 0.697)

# Release object
gripper_command("OPEN")

# Return home
home_robot()
```

### Example 2: Read Sensor and Control Output

```python
from src.cdacs_sbot_wrapper import *

# Read a limit switch
sensor_state = read_specific_io("Input 1")

if sensor_state == "high":
    # Turn on pneumatic valve
    write_io("Output 3", "high")
else:
    # Turn off pneumatic valve
    write_io("Output 3", "low")
```

### Example 3: Vision-Based Task

```python
from src.cdacs_sbot_wrapper import *
import cv2 as cv

# Move camera to inspection position
move_robot_cartesian(0.5, 0.0, 0.5, 0.0, 1.0, 0.0, 0.0)

# Capture image
img = capture_image()

# Process image (example: find red objects)
hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
# ... your vision processing code ...
```

## Documentation

Detailed documentation for each module:

- **[Setup Guide](documentation/setup.md)** - Installation, configuration, and getting started
- **[Movement Functions](documentation/movement.md)** - Robot positioning and motion control
- **[IO Functions](documentation/io.md)** - Digital input/output operations
- **[Camera Functions](documentation/camera.md)** - Image capture and processing
- **[Gripper Functions](documentation/gripper.md)** - Gripper control operations

## API Reference

### Movement Module

| Function | Description |
|----------|-------------|
| `get_position_info()` | Get current joint angles and tooltip position |
| `move_robot_cartesian(x, y, z, i, j, k, l)` | Move to Cartesian position with quaternion orientation |
| `move_robot_joint(j1, j2, j3, j4, j5, j6)` | Move to specific joint angles |
| `home_robot()` | Return robot to home position |

### IO Module

| Function | Description |
|----------|-------------|
| `read_specific_io(pin_name)` | Read state of a digital IO pin |
| `write_io(pin_name, state)` | Set state of a digital output pin |

### Camera Module

| Function | Description |
|----------|-------------|
| `capture_image()` | Capture image from end-effector camera |

### Gripper Module

| Function | Description |
|----------|-------------|
| `gripper_command(STRING)` | Simple OPEN/CLOSE gripper control |
| `gripper_request(WIDTH, FORCE)` | Advanced gripper control with custom parameters |

## Frequently Asked Questions (Beginners)

### Q: Do I need to activate the virtual environment every time?

**A:** Yes! Every time you open a new terminal window, you need to activate the virtual environment before running your code:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```
You'll know it's active when you see `(venv)` at the start of your command line.

### Q: How do I run my Python program?

**A:** 
1. Make sure your virtual environment is activated
2. Navigate to your project folder
3. Run: `python your_program_name.py`

Example:
```bash
cd path/to/sbot_sdk_wrapper
source venv/bin/activate  # or venv\Scripts\activate on Windows
python test_robot.py
```

### Q: I get "ModuleNotFoundError: No module named 'standardbots'"

**A:** This usually means either:
1. Your virtual environment isn't activated (look for `(venv)` in your terminal)
2. You didn't install the requirements yet. Run: `pip install -r requirements.txt`

### Q: Can I use a different Python editor or IDE?

**A:** Yes! You can use any editor you like:
- **VS Code** (recommended) - Free, beginner-friendly, good for Python
- **Neovim/Vim/Terminal** (Advnaced) - If you are a chad, this is the way to go
- **Others** - If you know what you're doing, you can use any editor you like

Just make sure to configure your editor to use the virtual environment you created.

### Q: Where do I write my robot programs?

**A:** Create new `.py` files in your project folder:
```
sbot_sdk_wrapper/
├── src/              # Don't edit these (unless changing config)
├── my_program.py     # Create your programs here
├── test_robot.py     # Or here
└── lab_assignment.py # Or here
```

### Q: The robot isn't moving when I run my code

**A:** Check these common issues:
1. Is the robot powered on?
2. Are you connected to the robot's network?
3. Did you update the IP address and token in the configuration?
4. Is the emergency stop button released?
5. Did you call `home_robot()` first?
6. Did you unbrake the robot before moving it? (Wrapper takes care of this)

### Q: How do I stop my program if something goes wrong?

**A:** 
- **In terminal**: Press `Ctrl+C` to stop the Python program
- **On robot**: Press the **emergency stop button** (big red button)
- **If robot is stuck**: Contact your lab instructor/ Dawson / Trying to hand guide the robot

### Q: Do I need to understand all the code in the src/ folder?

**A:** No! The whole point of this wrapper is that you **don't** need to understand the internal details. Just:
1. Update the configuration (IP and token)
2. Import the functions you need
3. Use them in your programs

Think of it like using a TV remote - you don't need to understand how the TV works internally, just which buttons to press.
It may be helpful to read the [documentation](documentation/setup.md) to understand how the configuration works.

## Safety Notes

- Always ensure the robot workspace is clear before running programs
- Start with `home_robot()` to establish a known safe position
- Test movements at reduced speed when developing new programs
- Use emergency stop if robot behavior is unexpected
- Verify IO pin names match your robot's configuration
- **Never** reach into the robot's workspace while it's moving

## Requirements

**CRITICAL - Specific Versions Required:**

- **Python 3.8 or higher**
- **standardbots==2.20241120.1** (EXACT version required - DO NOT use any other version!)
- **opencv-python>=4.11.0.86**
- **numpy>=2.2.5**
- **pandas>=2.2.3**

**Installation:**
```bash
# ALWAYS install from requirements.txt to ensure correct versions
pip install -r requirements.txt

# NEVER run: pip install standardbots
# This will install the wrong version and break the wrapper!
```

See `requirements.txt` for the pinned dependency versions.

## Contributing

This project is maintained by CDACS at the University of Idaho. For questions or improvements, contact the lab.

## License

See LICENSE file for details.

## Support

For issues or questions:
- Check the documentation in the `documentation/` folder
- Review example code in this README
- Contact CDACS lab support (Dawson Burgess)

## Version

Current version: 1.0.0

Last updated: 2026

## Maintainers

- [Pegasus](https://github.com/pegasora) - Dawson Burgess
- University of Idaho
