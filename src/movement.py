"""
============================|
StandardBot Movement Module |
============================|

This module provides functions for controlling robot movement in both
Cartesian and joint space.

Functions:
    - get_position_info(): Get current robot position and joint angles
    - move_robot_cartesian(): Move to Cartesian position with orientation
    - move_robot_joint(): Move to specific joint angles
    - home_robot(): Return robot to home position
"""

from standardbots import StandardBotsRobot, models


# Initialize the StandardBot connection
# IMPORTANT: Update these values to match your robot's configuration
sdk = StandardBotsRobot(
    url="http://10.8.4.11:3000",  # Robot's IP address and port
    token="8geqfqu0-qbbkig-ozwgr4-tl2xfj7",  # Authentication token
    robot_kind=StandardBotsRobot.RobotKind.Live,  # Use Live for real robot
)


def get_position_info():
    """
    Get the current position and orientation of the robot arm.

    Retrieves both joint angles and Cartesian tooltip position/orientation.
    Unbrakes the robot before querying position data.

    Returns:
        tuple: A tuple of 6 joint angles (j1, j2, j3, j4, j5, j6) in radians,
               or None if an error occurs.

    Prints:
        - Joint rotations for all 6 joints
        - Tooltip position (x, y, z) in meters
        - Tooltip orientation (quaternion i, j, k, l)

    Example:
        >>> joints = get_position_info()
        >>> if joints:
        ...     j1, j2, j3, j4, j5, j6 = joints
        ...     print(f"Joint 1 angle: {j1} radians")
    """
    with sdk.connection():
        sdk.movement.brakes.unbrake().ok()
        response = sdk.movement.position.get_arm_position()

        try:
            data = response.ok()
            j_1, j_2, j_3, j_4, j_5, j_6 = data.joint_rotations
            position = data.tooltip_position.position
            orientation = data.tooltip_position.orientation
            joints = data.joint_rotations

            print(f"Joints: {joints}")
            print(f"Got Position: {position}")
            print(f"Got orientation: {orientation}")

            return j_1, j_2, j_3, j_4, j_5, j_6

        except Exception:
            print(response.data.message)


def move_robot_cartesian(x, y, z, i, j, k, l):
    """
    Move the robot tooltip to a specified Cartesian position and orientation.

    Uses Cartesian coordinates (x, y, z) and quaternion orientation (i, j, k, l)
    to define the target pose. The robot will automatically plan and execute
    the motion path.

    Args:
        x (float): Target X position in meters
        y (float): Target Y position in meters
        z (float): Target Z position in meters
        i (float): Quaternion i component (orientation)
        j (float): Quaternion j component (orientation)
        k (float): Quaternion k component (orientation)
        l (float): Quaternion l component (scalar/w)

    Example:
        >>> # Move to position (0.5m, 0.3m, 0.4m) with specific orientation
        >>> move_robot_cartesian(0.5, 0.3, 0.4, 0.0, 0.707, 0.0, 0.707)

    Note:
        Automatically unbrakes the robot before movement. Ensure the target
        position is within the robot's reachable workspace.
    """
    with sdk.connection():
        sdk.movement.brakes.unbrake().ok()
        sdk.movement.position.move(
            position=models.Position(
                unit_kind=models.LinearUnitKind.Meters,
                x=x,
                y=y,
                z=z,
            ),
            orientation=models.Orientation(
                kind=models.OrientationKindEnum.Quaternion,
                quaternion=models.Quaternion(i, j, k, l),
            ),
        ).ok()


def move_robot_joint(j1, j2, j3, j4, j5, j6):
    """
    Move the robot to specified joint angles.

    Directly controls each joint's angle, providing precise control over the
    robot's configuration. This is useful when you need to reach a specific
    joint configuration or avoid singularities.

    Args:
        j1 (float): Joint 1 angle in radians (base rotation)
        j2 (float): Joint 2 angle in radians (shoulder)
        j3 (float): Joint 3 angle in radians (elbow)
        j4 (float): Joint 4 angle in radians (wrist 1)
        j5 (float): Joint 5 angle in radians (wrist 2)
        j6 (float): Joint 6 angle in radians (wrist 3)

    Example:
        >>> # Move to home position
        >>> move_robot_joint(0.0, 0.0, -1.5, 0.0, 1.5, -3.14)

    Note:
        Automatically unbrakes the robot before movement. Ensure joint angles
        are within valid ranges to avoid collision or joint limits.
    """
    with sdk.connection():
        sdk.movement.brakes.unbrake().ok()
        arm_rotations = models.ArmJointRotations(joints=(j1, j2, j3, j4, j5, j6))
        position_request = models.ArmPositionUpdateRequest(
            kind=models.ArmPositionUpdateRequestKindEnum.JointRotation,
            joint_rotation=arm_rotations,
        )
        sdk.movement.position.set_arm_position(position_request).ok()


def home_robot():
    """
    Move the robot to its home (default) position.

    Moves all joints to a predefined home configuration that is safe and
    provides good clearance. This position should be used at the start and
    end of programs, or when recovering from an error state.

    Home Position Joint Angles:
        - Joint 1: 0.0 rad
        - Joint 2: 0.0 rad
        - Joint 3: -1.5 rad (-85.9 degrees)
        - Joint 4: 0.0 rad
        - Joint 5: 1.5 rad (85.9 degrees)
        - Joint 6: -3.14 rad (-180 degrees)

    Example:
        >>> # Start of program
        >>> home_robot()
        >>> # ... perform tasks ...
        >>> home_robot()  # Return to home at end

    Note:
        Ensure the robot's workspace is clear before homing, as the robot
        will move along the shortest joint-space path to this position.
    """
    print("HOMING: Running home routine")
    move_robot_joint(0.0, 0.0, -1.5, 0.0, 1.5, -3.14)
