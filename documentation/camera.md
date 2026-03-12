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
