"""
===================================|
StandardBot Gripper Control Module |
===================================|

This module provides functions for controlling the OnRobot 2FG14 gripper
attached to the StandardBot robot arm.

Functions:
    - gripper_request(): Low-level gripper control with custom width and force
    - gripper_command(): High-level gripper control (OPEN/CLOSE)
"""

from standardbots import StandardBotsRobot, models


# Initialize the StandardBot connection
# IMPORTANT: Update these values to match your robot's configuration
sdk = StandardBotsRobot(
    url="http://10.8.4.11:3000",  # Robot's IP address and port
    token="8geqfqu0-qbbkig-ozwgr4-tl2xfj7",  # Authentication token
    robot_kind=StandardBotsRobot.RobotKind.Live,  # Use Live for real robot
)


def gripper_request(WIDTH, FORCE):
    """
    Send a direct control command to the OnRobot 2FG14 gripper.

    Controls the gripper to move to a specific width with a specified gripping
    force. This is a low-level function; consider using gripper_command() for
    simpler open/close operations.

    Args:
        WIDTH (float): Target grip width in meters. Valid range is typically
                       0.026m (fully closed) to 0.11m (fully open)
        FORCE (float): Gripping force in Newtons. Typical range is 10-140N

    Raises:
        Exception: If gripper command fails, prints error message

    Example:
        >>> # Close gripper to 50mm width with 20N force
        >>> gripper_request(0.05, 20.0)

        >>> # Gentle grip for fragile objects
        >>> gripper_request(0.04, 15.0)

        >>> # Strong grip for heavy objects
        >>> gripper_request(0.03, 100.0)

    Note:
        - The gripper always moves inward (closing direction) to the target width
        - Ensure the target width is achievable and won't damage workpieces
        - Force is limited by the gripper's maximum capability (140N)
        - Adjust force based on object material and fragility
    """
    with sdk.connection():
        response = sdk.equipment.control_gripper(
            models.GripperCommandRequest(
                kind=models.GripperKindEnum.Onrobot2Fg14,
                onrobot_2fg14=models.OnRobot2FG14GripperCommandRequest(
                    grip_direction=models.LinearGripDirectionEnum.Inward,
                    target_grip_width=models.LinearUnit(
                        value=WIDTH, unit_kind=models.LinearUnitKind.Meters
                    ),
                    target_force=models.ForceUnit(
                        value=FORCE,
                        unit_kind=models.ForceUnitKind.Newtons,
                    ),
                    control_kind=models.OnRobot2FG14ControlKindEnum.Move,
                ),
            )
        )

    try:
        data = response.ok()

    except Exception:
        print(f"ERROR! Exception: {response.data.message}")


def gripper_command(STRING):
    """
    Simple command interface to open or close the gripper.

    Provides a high-level interface for common gripper operations using
    predefined positions and forces. This is the recommended method for
    most gripper control tasks.

    Args:
        STRING (str): Command string, either "OPEN" or "CLOSE" (case-sensitive)

    Gripper Configurations:
        - OPEN: Moves to 110mm width (0.11m) with 10N force
        - CLOSE: Moves to 26mm width (0.026m) with 10N force

    Example:
        >>> # Open the gripper before picking up an object
        >>> gripper_command("OPEN")
        >>> move_robot_cartesian(x, y, z, i, j, k, l)
        >>> gripper_command("CLOSE")  # Close to grasp object

        >>> # Pick and place workflow
        >>> gripper_command("OPEN")
        >>> # Move to object
        >>> move_to_pickup_position()
        >>> gripper_command("CLOSE")
        >>> # Move to drop-off location
        >>> move_to_dropoff_position()
        >>> gripper_command("OPEN")

    Note:
        - Commands are case-sensitive. Use exactly "OPEN" or "CLOSE"
        - Force is set to a gentle 10N to avoid damaging most objects
        - For custom width/force, use gripper_request() instead

    IMPORTANT - Robot-Specific Calibration:
        The CLOSE width value (0.026m) varies between robots. If you hear a
        "locking" sound, experience slow performance, or see gripper communication
        errors, increase the CLOSE width below (line 126):
        
        Try: 0.028, 0.030, or 0.032 until gripper closes smoothly.
        
        Example adjustment:
            gripper_request(0.030, 10.0)  # Instead of 0.026
        
        This is normal - save your robot's calibrated value for future use.
    """
    if STRING == "OPEN":
        print("OPENING GRIPPER")
        gripper_request(0.11, 10.0)
    if STRING == "CLOSE":
        print("CLOSING GRIPPER")
        gripper_request(0.026, 10.0)  # ADJUST THIS VALUE if gripper makes locking sounds
