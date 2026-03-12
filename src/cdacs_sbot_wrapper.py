"""
=========================|
CDACS StandardBot Wrapper|
=========================|

A Python wrapper for controlling the StandardBot R01 robot arm at the University
of Idaho Facility (CDA). This essentially provides a simplified interface for
controlling the robot's movement, IO, camera, and gripper. All individual modules
are included in this file for ease of use.

This module provides simplified interfaces for:
- Robot movement (cartesian and joint space)
- IO pin control (reading and writing digital signals)
- Camera operations (capturing images from end effector)
- Gripper control (OnRobot 2FG14 gripper)

Requirements:
    - standardbots Python SDK (specific version pinned in requirements.txt)
    - OpenCV (cv2)
    - NumPy

Configuration:
    You will need to update the robot URL and token below to match your
    robot's IP address and authentication token. See documentation for details.
"""

import base64

import cv2 as cv
import numpy as np
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
        # Log to ensure the values are correct
        position_request = models.ArmPositionUpdateRequest(
            kind=models.ArmPositionUpdateRequestKindEnum.JointRotation,
            joint_rotation=arm_rotations,
        )
        sdk.movement.position.set_arm_position(position_request).ok()


def capture_image():
    """
    Capture an image from the robot's end-of-arm-tooling (EOAT) camera.

    Captures a color image using the built-in camera mounted on the robot's
    end effector. The image is automatically saved to 'camera_output.jpg' and
    returned as a NumPy array for further processing.

    Camera Settings:
        - Brightness: 0
        - Contrast: 50
        - Exposure: 250
        - Sharpness: 50
        - Hue: 0
        - White Balance: 4600K (auto white balance enabled)

    Returns:
        numpy.ndarray: Color image as BGR array (OpenCV format), suitable for
                       image processing operations. Returns None if capture fails.

    Side Effects:
        Saves the captured image to 'camera_output.jpg' in the current directory.

    Example:
        >>> img = capture_image()
        >>> if img is not None:
        ...     # Process the image with OpenCV
        ...     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        ...     cv.imshow('Captured Image', img)

    Note:
        Requires camera to be properly connected and configured on the robot.
    """
    body = models.CameraFrameRequest(
        camera_settings=models.CameraSettings(
            brightness=0,
            contrast=50,
            exposure=250,
            sharpness=50,
            hue=0,
            whiteBalance=4600,
            autoWhiteBalance=True,
        )
    )

    with sdk.connection():
        response = sdk.camera.data.get_color_frame(body)

        print(f"Result Data: {response.data}")
        response.ok()
        raw_data = response.response.data

        # extract
        base64_data = raw_data.decode().split(",")[1]

        # decode
        image_data = base64.b64decode(base64_data)

    # convert to numpy array
    np_data = np.frombuffer(image_data, np.uint8)

    # read image
    img = cv.imdecode(np_data, cv.IMREAD_COLOR)

    # make copy
    cv.imwrite("camera_output.jpg", img)

    # returns image for usage in code
    return img


def read_specific_io(pin_name: str):
    """
    Read the state of a specific IO pin.

    Args:
        pin_name: Name of the IO pin (e.g., "digital_out_0", "digital_in_1")

    Returns:
        str: State of the pin ("high" or "low"), or None if not found
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

    Args:
        pin_name: Name of the IO pin (e.g., "Output 0")
        state: Desired state ("high" or "low")

    Returns:
        bool: True if successful, False otherwise
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

    Note:
        The gripper always moves inward (closing direction) to the target width.
        Ensure the target width is achievable and won't damage workpieces.
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

    Note:
        Commands are case-sensitive. Use exactly "OPEN" or "CLOSE".
    
    IMPORTANT - Robot-Specific Calibration:
        The CLOSE width value (0.026m) varies between robots. If you hear a
        "locking" sound, experience slow performance, or see gripper communication
        errors, increase the CLOSE width below (line 381):
        
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
