# CST816 Touch Driver for MicroPython

A robust and extensible driver for the CST816S touch sensor chip, featuring advanced functionality while maintaining full backward compatibility with existing code.

## 🚀 Features

- ✅ **Full backward compatibility** with original implementations
- ✅ **Robust I2C error handling**
- ✅ **Multiple operating modes** (Default, Fast, Hardware)
- ✅ **Advanced gesture detection**
- ✅ **Flexible interrupt configuration**
- ✅ **Performance optimizations**
- ✅ **Built-in diagnostic tools**

# device test:
<p align="center"> 
ESP32-S3 1.46″ LCD touch Development Board (412×412)
</p>
<p align="center">
    <img lign="center" src="https://github.com/user-attachments/assets/6b205242-24e2-41fd-ad57-6ff417a90a40" width="600" height="500" />
</p>

<p align="center">


## 📋 Requirements

- MicroPython with I2C support
- `pointer_framework` (for GUI integration)
- CST816S touch sensor

## 🔧 Installation

1. Copy the `cst816.py` file to your MicroPython device
2. Ensure `pointer_framework` is available

```python
# Import the driver
from cst816 import CST816S
```

## 🚦 Basic Usage

### Simple Initialization

```python
import machine
from cst816 import CST816S

# Setup I2C
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=400000)

# Initialize touch sensor
touch = CST816S(
    device=i2c,
    reset_pin=9,  # Reset pin (optional)
    debug=True    # Enable debug messages
)
```

### Reading Coordinates

```python
# Classic method
coords = touch._get_coords()
if coords:
    state, x, y = coords
    print(f"Touch: {x}, {y}")

# Advanced method with more information
gesture_data = touch._get_gesture_data()
if gesture_data:
    print(f"Gesture: {gesture_data['gesture']}, Pos: ({gesture_data['x']}, {gesture_data['y']})")
```

## ⚙️ Operating Modes

### 1. Default Mode
```python
# Standard configuration (active by default)
touch._write_reg(touch._IrqCtl, touch._EnTouch | touch._EnChange)
```

### 2. Fast Mode
```python
# Software-based fast detection
touch.set_operating_mode_fast(notify_motion=True)
```

### 3. Hardware Mode
```python
# Full hardware capabilities
touch.set_operating_mode_hardware()
```

## 🎯 Gesture Management

### Configure Motion Detection

```python
# Enable continuous movements
touch.set_motion_mask(
    enable_continuous_lr=True,    # Horizontal sliding
    enable_continuous_ud=True,    # Vertical sliding
    enable_double_click=True      # Double click
)
```

### Configure Gesture Timings

```python
# Long press of 3 seconds
touch.set_long_press_time(3)

# Auto-reset after 5 seconds
touch.set_auto_reset_time(5)
```

## 💾 Power Management

### Auto-Sleep Control

```python
# Configure auto-sleep timeout
touch.auto_sleep_timeout = 5  # seconds

# Enable/disable auto-sleep
touch.auto_sleep = True

# Wake up manually
touch.wake_up()

# Configure wake-up sensitivity
touch.wake_up_threshold = 100  # 1-255 (higher = less sensitive)
touch.wake_up_scan_frequency = 10  # 1-255 (higher = more frequent)
```

### Temporary Suspension

```python
# Suspend during critical operations
touch.suspend()

# ... operations requiring precision ...

# Resume normal operation
touch.resume()
```

## 🔄 Reset and Recovery

### Hardware Reset

```python
# Physical reset using pin
touch.hw_reset()
```

### Software Reset

```python
# Complete software reset
touch.reset_chip_soft()
```

## 🛠️ Diagnostic Tools

### Chip Status

```python
# Get complete status
status = touch.get_chip_status()
print(status)

# Print formatted status
touch.print_chip_status()
```

### Hardware Information

```python
# Verify during initialization
# (automatically shown with debug=True)
```

## 📊 Gesture and State Codes

### Gestures (_GestureID)
- `0x00`: No gesture
- `0x01`: Swipe up
- `0x02`: Swipe down
- `0x03`: Swipe left
- `0x04`: Swipe right
- `0x05`: Single click
- `0x0B`: Double click
- `0x0C`: Long press

### Touch States
- `0`: No finger
- `1`: One finger
- `2`: Contact

## 💡 Advanced Examples

### Real-time Gesture Monitor

```python
import time

def gesture_monitor():
    while True:
        data = touch._get_gesture_data()
        if data:
            gesture = data['gesture']
            if gesture == 0x01:
                print("🔼 Swipe Up")
            elif gesture == 0x02:
                print("🔽 Swipe Down")
            elif gesture == 0x03:
                print("◀️ Swipe Left")
            elif gesture == 0x04:
                print("▶️ Swipe Right")
            elif gesture == 0x05:
                print("👆 Single Click")
            elif gesture == 0x0B:
                print("👆👆 Double Click")
            elif gesture == 0x0C:
                print("👈 Long Press")
        time.sleep_ms(10)

# Run monitor
gesture_monitor()
```

### Custom Configuration

```python
class TouchConfig:
    def __init__(self, touch_driver):
        self.touch = touch_driver
    
    def setup_gaming_mode(self):
        """Optimized configuration for games"""
        self.touch.set_operating_mode_fast(notify_motion=True)
        self.touch.auto_sleep = False
        self.touch.set_long_press_time(1)  # Fast long press
        
    def setup_power_save_mode(self):
        """Configuration for power saving"""
        self.touch.set_operating_mode_hardware()
        self.touch.auto_sleep = True
        self.touch.auto_sleep_timeout = 2
        self.touch.wake_up_threshold = 200  # Less sensitive
```

## 🐛 Troubleshooting

### Common Issues

1. **No touch detection**
   ```python
   # Check I2C connections
   touch.print_chip_status()
   
   # Try reset
   touch.hw_reset()
   ```

2. **Erratic detection**
   ```python
   # Adjust sensitivity
   touch.wake_up_threshold = 150
   
   # Reduce noise
   touch.set_operating_mode_hardware()
   ```

3. **Performance issues**
   ```python
   # Use fast mode
   touch.set_operating_mode_fast(notify_motion=False)
   
   # Suspend during critical operations
   touch.suspend()
   # ... critical operation ...
   touch.resume()
   ```

## 📈 Optimizations

### Multiple Reads
```python
# Driver automatically uses multiple reads for better performance
data = touch._get_gesture_data()  # Reads 6 registers at once
```

### Read Buffers
```python
# Internal buffers to reduce allocations
# - self._rx_buf: 1-byte buffer for simple reads
# - self._multi_buf: 8-byte buffer for multiple reads
```

## 🤝 Contributing

Contributions are welcome. Please:

1. Maintain compatibility with existing code
2. Add tests for new functionality
3. Update documentation
4. Follow existing code style

## 📄 License

This code is under the MIT license.

---

## 📚 Additional Documentation

### CST816S Registers

| Register | Address | Function |
|----------|---------|----------|
| _GestureID | 0x01 | Detected gesture ID |
| _FingerNum | 0x02 | Number of fingers |
| _XposH/L | 0x03/0x04 | X coordinate |
| _YposH/L | 0x05/0x06 | Y coordinate |
| _MotionMask | 0xEC | Motion mask |
| _IrqCtl | 0xFA | Interrupt control |

### Recommended Configurations

```python
# For GUI applications
touch.set_operating_mode_fast(notify_motion=False)

# For drawing applications
touch.set_operating_mode_fast(notify_motion=True)

# For low-power applications
touch.set_operating_mode_hardware()
```

## 📝 API Reference

### Core Methods

#### `__init__(device, reset_pin=None, touch_cal=None, startup_rotation=None, debug=False)`
Initialize the CST816S driver.

**Parameters:**
- `device`: I2C device object
- `reset_pin`: Reset pin number or Pin object (optional)
- `touch_cal`: Touch calibration data (optional)
- `startup_rotation`: Display rotation (optional)
- `debug`: Enable debug output (default: False)

#### `_get_coords()`
Get current touch coordinates.

**Returns:**
- `None` if no touch
- `(state, x, y)` tuple if touch detected

#### `_get_gesture_data()`
Get comprehensive gesture and touch data.

**Returns:**
- `None` if no touch
- Dictionary with gesture information

### Power Management

#### `auto_sleep`
Property to enable/disable auto-sleep mode.

#### `auto_sleep_timeout`
Property to set auto-sleep timeout in seconds.

#### `wake_up_threshold`
Property to set wake-up sensitivity (1-255).

#### `wake_up_scan_frequency`
Property to set wake-up scan frequency (1-255).

#### `wake_up()`
Manually wake up the device from sleep.

### Operating Modes

#### `set_operating_mode_fast(notify_motion=False)`
Configure fast mode with software detection.

#### `set_operating_mode_hardware()`
Configure hardware mode for maximum precision.

### Gesture Configuration

#### `set_motion_mask(enable_continuous_lr=False, enable_continuous_ud=False, enable_double_click=False)`
Configure motion detection mask.

#### `set_long_press_time(seconds)`
Set long press duration in seconds.

#### `set_auto_reset_time(seconds)`
Set auto-reset timeout in seconds.

### Reset and Recovery

#### `hw_reset()`
Perform hardware reset using reset pin.

#### `reset_chip_soft()`
Perform software reset.

### Diagnostic Tools

#### `get_chip_status()`
Get complete chip status information.

**Returns:**
- Dictionary with status information

#### `print_chip_status()`
Print formatted chip status (requires debug=True).

### Suspension

#### `suspend()`
Temporarily suspend touch detection.

#### `resume()`
Resume touch detection after suspension.

## 🔍 Event Flags

When using `_get_gesture_data()`, the `event` field contains:
- `0`: Finger down
- `1`: Finger up
- `2`: Contact (finger moving)

## ⚡ Performance Tips

1. **Use appropriate operating mode** for your application
2. **Suspend during critical operations** to avoid interference
3. **Configure motion mask** to reduce unnecessary interrupts
4. **Adjust auto-sleep settings** based on your power requirements
5. **Use debug mode** only during development

## 🔧 Hardware Notes

- The CST816S operates at 3.3V
- I2C address is fixed at 0x15
- Reset pin is active-low
- IRQ pin can be configured for different interrupt types

## 📊 Performance Characteristics

| Mode | Response Time | Power Usage | Precision |
|------|---------------|-------------|-----------|
| Default | Medium | Medium | Good |
| Fast | Fastest | Higher | Good |
| Hardware | Slower | Lower | Excellent |
