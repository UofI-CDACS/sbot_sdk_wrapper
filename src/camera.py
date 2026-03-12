"""
=========================|
StandardBot Camera Module|
=========================|

This module provides functions for capturing images from the robot's
end-of-arm-tooling (EOAT) camera.

Functions:
    - capture_image(): Capture and process image from EOAT camera

More to come soon...
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

        >>> # Capture image and apply edge detection
        >>> img = capture_image()
        >>> edges = cv.Canny(img, 100, 200)
        >>> cv.imwrite('edges.jpg', edges)

        >>> # Use for object detection or computer vision
        >>> img = capture_image()
        >>> # Apply your vision algorithms here...

    Note:
        - Requires camera to be properly connected and configured on the robot
        - Image is returned in OpenCV BGR format (not RGB)
        - Camera settings can be adjusted by modifying the CameraSettings object
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

        # extract base64 data from response
        base64_data = raw_data.decode().split(",")[1]

        # decode base64 to bytes
        image_data = base64.b64decode(base64_data)

    # convert to numpy array
    np_data = np.frombuffer(image_data, np.uint8)

    # decode image from numpy array
    img = cv.imdecode(np_data, cv.IMREAD_COLOR)

    # save image to file
    cv.imwrite("camera_output.jpg", img)

    # returns image for usage in code
    return img
