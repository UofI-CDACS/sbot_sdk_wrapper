# Camera Operations Documentation

This document covers image capture and processing using the robot's end-effector camera in the `camera.py` module.

## Table of Contents

1. [Overview](#overview)
2. [Camera Specifications](#camera-specifications)
3. [Function Reference](#function-reference)
4. [Usage Examples](#usage-examples)
5. [Image Processing Basics](#image-processing-basics)
6. [Best Practices](#best-practices)

## Overview

The camera module provides functions to capture images from the camera mounted on the robot's end-of-arm tooling (EOAT). Images are returned as NumPy arrays compatible with OpenCV for further processing.

### Import Statement

```python
from src.camera import capture_image
import cv2 as cv  # For image processing
import numpy as np  # For numerical operations
```

## Camera Specifications

### Default Camera Settings

The camera is configured with the following default settings:

| Setting | Value | Description |
|---------|-------|-------------|
| Brightness | 0 | Image brightness adjustment |
| Contrast | 50 | Image contrast level |
| Exposure | 250 | Exposure time (higher = brighter) |
| Sharpness | 50 | Edge enhancement level |
| Hue | 0 | Color hue adjustment |
| White Balance | 4600K | Color temperature |
| Auto White Balance | Enabled | Automatic color correction |

### Image Format

- **Format**: BGR (Blue-Green-Red) color space
- **Data Type**: NumPy array (uint8)
- **Dimensions**: Width × Height × 3 channels
- **File Output**: JPEG (.jpg)

**Note**: OpenCV uses BGR format, not RGB. Convert if needed for other libraries.

## Function Reference

### capture_image()

Capture a color image from the robot's end-effector camera.

**Parameters:** None

**Returns:**
- `numpy.ndarray`: Color image in BGR format (OpenCV compatible)
- `None`: If capture fails

**Side Effects:**
- Saves image to `camera_output.jpg` in current directory
- Prints response data to console

**Example:**
```python
img = capture_image()

if img is not None:
    print(f"Image captured: {img.shape}")  # e.g., (480, 640, 3)
    print(f"Image saved to: camera_output.jpg")
else:
    print("Failed to capture image")
```

**Image Properties:**
```python
# Get image dimensions
height, width, channels = img.shape

# Get image data type
dtype = img.dtype  # uint8 (0-255 per channel)

# Get image size in bytes
size_bytes = img.nbytes
```

## Usage Examples

### Example 1: Basic Image Capture

```python
from src.camera import capture_image
from src.movement import move_robot_cartesian

# Move camera to inspection position
move_robot_cartesian(0.5, 0.0, 0.4, 0.0, 1.0, 0.0, 0.0)

# Capture image
img = capture_image()

if img is not None:
    print("Image captured successfully")
    # Image automatically saved as 'camera_output.jpg'
```

### Example 2: Display Image

```python
from src.camera import capture_image
import cv2 as cv

# Capture image
img = capture_image()

if img is not None:
    # Display image in window
    cv.imshow('Robot Camera View', img)
    cv.waitKey(0)  # Wait for key press
    cv.destroyAllWindows()
```

### Example 3: Convert to Grayscale

```python
from src.camera import capture_image
import cv2 as cv

# Capture color image
img = capture_image()

if img is not None:
    # Convert to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # Save grayscale image
    cv.imwrite('camera_grayscale.jpg', gray)
    
    print(f"Grayscale image shape: {gray.shape}")  # (height, width)
```

### Example 4: Object Detection (Red Objects)

```python
from src.camera import capture_image
import cv2 as cv
import numpy as np

def detect_red_objects():
    """Detect red-colored objects in camera view"""
    
    # Capture image
    img = capture_image()
    if img is None:
        return None
    
    # Convert BGR to HSV color space
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    
    # Define range for red color in HSV
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    
    # Create mask for red objects
    mask = cv.inRange(hsv, lower_red, upper_red)
    
    # Find contours
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    # Draw contours on original image
    result = img.copy()
    cv.drawContours(result, contours, -1, (0, 255, 0), 2)
    
    # Save result
    cv.imwrite('detected_objects.jpg', result)
    
    print(f"Found {len(contours)} red objects")
    return contours

# Usage
contours = detect_red_objects()
```

### Example 5: QR Code Detection

```python
from src.camera import capture_image
import cv2 as cv

def read_qr_code():
    """Detect and decode QR code from camera"""
    
    # Capture image
    img = capture_image()
    if img is None:
        return None
    
    # Initialize QR code detector
    qr_detector = cv.QRCodeDetector()
    
    # Detect and decode
    data, bbox, _ = qr_detector.detectAndDecode(img)
    
    if data:
        print(f"QR Code detected: {data}")
        
        # Draw bounding box if detected
        if bbox is not None:
            bbox = bbox.astype(int)
            cv.polylines(img, [bbox], True, (0, 255, 0), 2)
            cv.imwrite('qr_code_detected.jpg', img)
        
        return data
    else:
        print("No QR code detected")
        return None

# Usage
qr_data = read_qr_code()
```

### Example 6: Vision-Guided Pick

```python
from src.camera import capture_image
from src.movement import move_robot_cartesian
from src.gripper import gripper_command
import cv2 as cv
import numpy as np

def vision_guided_pick():
    """
    Use camera to locate part and calculate pick position
    """
    # Move camera to overhead position
    camera_height = 0.5
    move_robot_cartesian(0.5, 0.0, camera_height, 0.0, 1.0, 0.0, 0.0)
    
    # Capture image
    img = capture_image()
    if img is None:
        print("Failed to capture image")
        return False
    
    # Convert to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # Apply threshold
    _, thresh = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        print("No objects detected")
        return False
    
    # Find largest contour (assumed to be the part)
    largest_contour = max(contours, key=cv.contourArea)
    
    # Calculate center of contour
    M = cv.moments(largest_contour)
    if M["m00"] == 0:
        print("Cannot calculate center")
        return False
    
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    # Convert pixel coordinates to robot coordinates
    # (Requires camera calibration - simplified here)
    img_height, img_width = img.shape[:2]
    
    # Assume field of view is 0.4m x 0.3m
    fov_width = 0.4
    fov_height = 0.3
    
    # Calculate offset from center
    offset_x = (cx - img_width/2) * (fov_width / img_width)
    offset_y = (cy - img_height/2) * (fov_height / img_height)
    
    # Calculate pick position
    pick_x = 0.5 + offset_x
    pick_y = 0.0 + offset_y
    pick_z = 0.2  # Height of part surface
    
    print(f"Part located at: ({pick_x:.3f}, {pick_y:.3f})")
    
    # Open gripper
    gripper_command("OPEN")
    
    # Move to pick position
    move_robot_cartesian(pick_x, pick_y, pick_z + 0.1, 0.0, 1.0, 0.0, 0.0)
    move_robot_cartesian(pick_x, pick_y, pick_z, 0.0, 1.0, 0.0, 0.0)
    
    # Close gripper
    gripper_command("CLOSE")
    
    # Lift part
    move_robot_cartesian(pick_x, pick_y, pick_z + 0.1, 0.0, 1.0, 0.0, 0.0)
    
    return True

# Usage
if vision_guided_pick():
    print("Part picked successfully")
```

### Example 7: Capture Multiple Images

```python
from src.camera import capture_image
from src.movement import move_robot_cartesian
import time

def capture_multiple_angles():
    """Capture images from multiple angles"""
    
    positions = [
        (0.5, 0.0, 0.4, 0.0, 1.0, 0.0, 0.0),   # Top view
        (0.5, 0.2, 0.3, 0.5, 0.5, 0.5, 0.5),   # Angle 1
        (0.5, -0.2, 0.3, -0.5, 0.5, -0.5, 0.5), # Angle 2
    ]
    
    images = []
    
    for i, pos in enumerate(positions):
        print(f"Capturing image {i+1}/{len(positions)}")
        
        # Move to position
        move_robot_cartesian(*pos)
        time.sleep(0.5)  # Let camera settle
        
        # Capture image
        img = capture_image()
        if img is not None:
            # Save with unique name
            cv.imwrite(f'camera_angle_{i+1}.jpg', img)
            images.append(img)
    
    print(f"Captured {len(images)} images")
    return images

# Usage
images = capture_multiple_angles()
```

## Image Processing Basics

### Common OpenCV Operations

#### Edge Detection
```python
img = capture_image()
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
edges = cv.Canny(gray, 100, 200)
cv.imwrite('edges.jpg', edges)
```

#### Blurring/Smoothing
```python
img = capture_image()
blurred = cv.GaussianBlur(img, (5, 5), 0)
cv.imwrite('blurred.jpg', blurred)
```

#### Thresholding
```python
img = capture_image()
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
_, binary = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
cv.imwrite('binary.jpg', binary)
```

#### Drawing on Images
```python
img = capture_image()

# Draw circle
cv.circle(img, (100, 100), 50, (0, 255, 0), 2)

# Draw rectangle
cv.rectangle(img, (200, 200), (300, 300), (255, 0, 0), 2)

# Add text
cv.putText(img, 'Robot View', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 
           1, (0, 0, 255), 2)

cv.imwrite('annotated.jpg', img)
```

## Best Practices

### 1. Allow Camera to Settle

```python
from src.movement import move_robot_cartesian
import time

# Move to position
move_robot_cartesian(x, y, z, i, j, k, l)

# Wait for motion to complete and camera to settle
time.sleep(0.5)

# Now capture
img = capture_image()
```

### 2. Consistent Lighting

- Use consistent lighting conditions
- Avoid shadows in workspace
- Consider adding LED ring light to camera

### 3. Error Checking

```python
img = capture_image()

if img is None:
    print("ERROR: Failed to capture image")
    return

if img.size == 0:
    print("ERROR: Empty image captured")
    return

# Continue with processing
```

### 4. Image Naming Convention

```python
import time

# Generate unique filename
timestamp = time.strftime("%Y%m%d_%H%M%S")
filename = f"capture_{timestamp}.jpg"

img = capture_image()
if img is not None:
    cv.imwrite(filename, img)
```

### 5. Camera Calibration

For accurate vision-guided positioning, calibrate your camera:

```python
# Simplified calibration example
# (Real calibration requires checkerboard patterns)

def calibrate_camera_fov():
    """
    Measure field of view by imaging known-size object
    """
    # Place object of known size (e.g., 10cm square)
    # at known distance from camera
    
    img = capture_image()
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # Detect object corners
    # Calculate pixels per meter
    # Store calibration data
    
    pass
```

## Troubleshooting

### Issue: Dark or overexposed images

**Solution**: Adjust exposure setting

```python
# Modify camera.py capture_image() function
# Increase exposure for brighter images (current: 250)
exposure=500  # Brighter

# Decrease for darker images
exposure=100  # Darker
```

### Issue: Blurry images

**Possible causes:**
- Camera moving during capture
- Focus issue
- Motion blur

**Solutions:**
1. Add settling time after movement
2. Check camera focus (may require physical adjustment)
3. Use faster shutter speed (lower exposure)

### Issue: Color calibration issues

**Solution**: Adjust white balance

```python
# In camera.py, modify CameraSettings:
autoWhiteBalance=False
whiteBalance=5000  # Adjust value (typical range: 2800-6500K)
```

### Issue: Image processing too slow

**Solutions:**
1. Resize image before processing:
```python
img = capture_image()
small = cv.resize(img, (320, 240))  # Process smaller image
```

2. Use grayscale when possible:
```python
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Faster processing
```

## Related Documentation

- [Movement Control](movement.md) - Position camera for imaging
- [Gripper Control](gripper.md) - Vision-guided grasping
- [IO Control](io.md) - Trigger external lighting

## Additional Resources

- OpenCV Tutorial: https://docs.opencv.org/master/d9/df8/tutorial_root.html
- NumPy Documentation: https://numpy.org/doc/stable/
- Image Processing Algorithms: Search for "computer vision" tutorials

---

**Last Updated**: March 2026  
**Module**: camera.py
