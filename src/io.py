"""
==============================|
StandardBot IO Control Module |
==============================|

This module provides functions for reading and writing digital IO pins
on the StandardBot robot controller.

Functions:
    - read_specific_io(): Read the state of a specific IO pin
    - write_io(): Set the state of a specific IO pin
"""

from standardbots import StandardBotsRobot, models


# Initialize the StandardBot connection
# IMPORTANT: Update these values to match your robot's configuration
sdk = StandardBotsRobot(
    url="http://10.8.4.11:3000",  # Robot's IP address and port
    token="8geqfqu0-qbbkig-ozwgr4-tl2xfj7",  # Authentication token
    robot_kind=StandardBotsRobot.RobotKind.Live,  # Use Live for real robot
)


def read_specific_io(pin_name: str):
    """
    Read the state of a specific IO pin.

    Queries the robot controller for the current state of a named digital IO pin.
    Useful for reading sensors, limit switches, or other input devices.

    Args:
        pin_name (str): Name of the IO pin to read. Examples:
                        - "Input 1", "Input 2", etc. (digital inputs)
                        - "Output 0", "Output 1", etc. (digital outputs)
                        - "digital_in_0", "digital_out_0", etc. (alternate naming)

    Returns:
        str: State of the pin, either "high" or "low"
        None: If the pin is not found or an error occurs

    Example:
        >>> # Read a limit switch on Input 2
        >>> state = read_specific_io("Input 2")
        >>> if state == "high":
        ...     print("Limit switch activated")

        >>> # Poll a sensor until it activates
        >>> while read_specific_io("Input 1") != "high":
        ...     time.sleep(0.1)
        >>> print("Sensor triggered!")

    Note:
        Pin names are case-sensitive and must match the robot controller's
        configuration exactly.
    """
    with sdk.connection():
        response = sdk.io.status.get_io_state()

        try:
            data = response.ok()
            io_state = data.state

            if io_state and pin_name in io_state:
                state = io_state[pin_name]
                print(f"{pin_name}: {state}")
                return state
            else:
                print(f"{pin_name}: Not found in IO state")
                return None

        except Exception as e:
            print(
                f"Error reading IO: {response.data.message if hasattr(response.data, 'message') else e}"
            )
            return None


def write_io(pin_name: str, state: str):
    """
    Set the state of a specific IO pin.

    Controls a digital output pin on the robot controller. Use this to control
    external devices like pneumatic valves, lights, or relay switches.

    Args:
        pin_name (str): Name of the IO pin to control. Examples:
                        - "Output 0", "Output 1", "Output 2", etc.
                        - "digital_out_0", "digital_out_1", etc.
        state (str): Desired state, either "high" or "low" (case-insensitive)

    Returns:
        bool: True if the operation was successful, False otherwise

    Example:
        >>> # Turn on a pneumatic valve connected to Output 3
        >>> write_io("Output 3", "high")
        >>> time.sleep(2)
        >>> write_io("Output 3", "low")

        >>> # Control a door lock
        >>> if write_io("Output 4", "high"):
        ...     print("Door locked")

    Note:
        - Only output pins can be written; attempting to write to input pins
          will result in an error
        - State parameter is case-insensitive ("HIGH", "high", "High" all work)
        - Function validates state before sending command
    """
    if state.lower() not in ["high", "low"]:
        print(f"Invalid state: {state}. Must be 'high' or 'low'")
        return False

    with sdk.connection():
        # Create the update request with a dictionary of pin states
        update_request = models.IOStateUpdateRequest(state={pin_name: state.lower()})

        response = sdk.io.control.update_io_state(update_request)

        try:
            data = response.ok()
            print(f"Successfully set {pin_name} to {state}")

            # Print the resulting state
            if data.state:
                print(f"Resulting IO state: {data.state}")

            return True

        except Exception as e:
            print(
                f"Error writing IO: {response.data.message if hasattr(response.data, 'message') else e}"
            )
            return False
