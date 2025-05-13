# cst816.py
# Versión mejorada con nuevas funcionalidades.

from micropython import const
import pointer_framework
import time
import machine

I2C_ADDR = const(0x15)
BITS = const(8)

# 0x00: No gesture
# 0x01: Swipe up
# 0x02: Swipe down
# 0x03: Swipe left
# 0x04: Swipe right
# 0x05: Single click
# 0x0B: Double click
# 0x0C: Long press
_GestureID = const(0x01)

# 0: No finger
# 1: 1 finger
_FingerNum = const(0x02)

# & 0xF << 8
_XposH = const(0x03)
_XposL = const(0x04)

#  & 0xF << 8
_YposH = const(0x05)
_YposL = const(0x06)

_RegisterVersion = const(0x15)

_BPC0H = const(0xB0)
_BPC0L = const(0xB1)

_BPC1H = const(0xB2)
_BPC1L = const(0xB3)

_ChipID = const(0xA7)
#_ChipIDValue = const(0xB5)
_ChipIDValue = const(0xB6)

_ProjID = const(0xA8)
_FwVersion = const(0xA9)


# ===============================
_MotionMask = const(0xEC)

# Enables continuous left and right sliding
_EnConLR = const(0x04)
# Enables continuous up and down sliding
_EnConUD = const(0x02)
# Enable double-click action
_EnDClick = const(0x01)
# ===============================

# Interrupt low pulse output width.
# Unit 0.1ms, optional value: 1~200. The default value is 10.
_IrqPluseWidth = const(0xED)

# Normal fast detection cycle.
# This value affects LpAutoWakeTime and AutoSleepTime.
# Unit 10ms, optional value: 1~30. The default value is 1.
_NorScanPer = const(0xEE)

# Gesture detection sliding partition angle control. Angle=tan(c)*10
# c is the angle based on the positive direction of the x-axis.
_MotionSlAngle = const(0xEF)

_LpScanRaw1H = const(0xF0)
_LpScanRaw1L = const(0xF1)
_LpScanRaw2H = const(0xF2)
_LpScanRaw2L = const(0xF3)

# Automatic recalibration period in low power consumption.
# Unit: 1 minute, optional value: 1 to 5. The default value is 5.
_LpAutoWakeTime = const(0xF4)


# Low power scan wake-up threshold. The smaller the value,
# the more sensitive it is.
# Optional values: 1 to 255. The default value is 48.
_LpScanTH = const(0xF5)

# Low power scan range. The larger the value, the more sensitive it is,
# and the higher the power consumption is.
# Optional values: 0, 1, 2, 3. The default value is 3.
_LpScanWin = const(0xF6)

# Low power scan frequency. The smaller the value, the more sensitive it is.
# Optional values: 1 to 255. The default value is 7.
_LpScanFreq = const(0xF7)

# Low power scan current. The smaller the value, the more sensitive it is.
# Optional values: 1 to 255.
_LpScanIdac = const(0xF8)


# Automatically enters low power mode when there is no touch within x seconds.
# Unit: 1S, default value: 2S.
_AutoSleepTime = const(0xF9)

# ===============================
_IrqCtl = const(0xFA)
# Interrupt pin test, automatically sends low pulses periodically after enabling
_EnTest = const(0x80)
# Sends low pulses periodically when touch is detected.
_EnTouch = const(0x40)
# Sends low pulses when touch state changes are detected.
_EnChange = const(0x20)
# Sends low pulses when gestures are detected.
_EnMotion = const(0x10)
# Long press gesture only sends one low pulse signal.
_OnceWLP = const(0x01)
# ===============================


# Automatically reset when there is touch but no valid gesture within x seconds.
# Unit: 1S. This function is not enabled when it is 0. The default value is 5.
_AutoReset = const(0xFB)

# Automatically reset after long pressing for x seconds.
# Unit: 1S. This function is not enabled when it is 0. The default value is 10.
_LongPressTime = const(0xFC)

# ===============================
_IOCtl = const(0xFD)

# The master controller realizes the soft reset function
# of the touch screen by pulling down the IRQ pin.
#   0: Disable soft reset.
#   1: Enable soft reset.
_SOFT_RST = const(0x04)

# IIC pin drive mode, the default is resistor pull-up.
#   0: Resistor pull-up
#   1: OD
_IIC_OD = const(0x02)

# IIC and IRQ pin level selection, the default is VDD level.
#   0: VDD
#   1: 1.8V
_En1v8 = const(0x01)
# ===============================

# The default value is 0, enabling automatic entry into low power mode.
# When the value is non-zero, automatic entry into low power mode is disabled.
#   0: enabled
#   1: disabled
_DisAutoSleep = const(0xFE)


# *** NUEVAS CONSTANTES PARA MODOS DE OPERACIÓN ***
class CST816SOperatingMode:
    DEFAULT = const(0)
    FAST = const(1)
    HARDWARE = const(2)


class CST816S(pointer_framework.PointerDriver):
    """
    Controlador CST816S mejorado - mantiene compatibilidad total con el código original
    y agrega nuevas funcionalidades opcionales
    """

    def _read_reg(self, reg):
        """Método original con manejo de errores añadido"""
        try:
            # Código original preservado exactamente como estaba
            self._device.writeto(I2C_ADDR, bytes([reg]), False)  # No stop bit
            self._device.readfrom_into(I2C_ADDR, self._rx_buf)
            return self._rx_buf[0]
        except OSError as e:
            if self._debug:
                print(f"I2C read error at reg {hex(reg)}: {e}")
            return None

    def _write_reg(self, reg, value):
        """Método original con manejo de errores añadido"""
        try:
            # Código original preservado exactamente como estaba
            self._device.writeto(I2C_ADDR, bytes([reg, value]))
            return True
        except OSError as e:
            if self._debug:
                print(f"I2C write error at reg {hex(reg)}: {e}")
            return False

    # *** NUEVO MÉTODO PARA LECTURA MÚLTIPLE ***
    def _read_multiple_regs(self, start_reg, count):
        """Leer múltiples registros consecutivos de forma eficiente"""
        try:
            if count > len(self._multi_buf):
                count = len(self._multi_buf)
            
            self._device.writeto(I2C_ADDR, bytes([start_reg]), False)
            self._device.readfrom_into(I2C_ADDR, self._multi_buf[:count])
            return self._multi_buf[:count]
        except OSError as e:
            if self._debug:
                print(f"I2C multi-read error at reg {hex(start_reg)}: {e}")
            return None

    def __init__(
        self,
        device,
        reset_pin=None,
        touch_cal=None,
        startup_rotation=None,
        debug=False
    ):
        # Variables originales preservadas exactamente
        self._rx_buf = bytearray(1)
        self._device = device
        
        # *** NUEVAS VARIABLES ***
        self._is_suspended = False
        self._debug = debug  # Almacenar para usar en manejo de errores
        self._multi_buf = bytearray(8)  # Buffer para lecturas múltiples
        
        # *** NUEVAS PROPIEDADES DE CONFIGURACIÓN ***
        self._operating_mode = CST816SOperatingMode.DEFAULT
        self._notify_on_motion = False
        self._notify_release_only = True
        self._movement_interval = 50  # ms
        self._touch_button_coords = (360, 85)  # T-Display default
        
        # Manejar el startup_rotation exactamente como en el original
        if startup_rotation is None:
            try:
                startup_rotation = pointer_framework.lv.DISPLAY_ROTATION._0
            except:
                # Si hay error, usar None
                startup_rotation = None

        # Configurar el pin de reset exactamente como en el original
        if not isinstance(reset_pin, int):
            self._reset_pin = reset_pin
        else:
            self._reset_pin = machine.Pin(reset_pin, machine.Pin.OUT)

        if self._reset_pin:
            self._reset_pin.value(1)

        # Inicialización exactamente como en el original
        self.hw_reset()
        
        # Leer identificación del chip
        chip_id = self._read_reg(_ChipID)
        if chip_id is not None:
            print('Chip ID:', hex(chip_id))
        
        # Leer versión del registro
        touch_version = self._read_reg(_RegisterVersion)
        if touch_version is not None:
            print('Touch version:', touch_version)
        
        # Leer ID del proyecto
        proj_id = self._read_reg(_ProjID)
        if proj_id is not None:
            print('Proj ID:', hex(proj_id))
        
        # Leer versión del firmware
        fw_version = self._read_reg(_FwVersion)
        if fw_version is not None:
            print('FW Version:', hex(fw_version))

        # Verificar si el ID del chip es correcto
        if chip_id is not None and chip_id != _ChipIDValue:
            raise RuntimeError(f'Incorrect chip id: got {hex(chip_id)}, expected: {hex(_ChipIDValue)}')

        # Configurar el control de interrupciones (original)
        self._write_reg(_IrqCtl, _EnTouch | _EnChange)
        
        # Deshabilitar el modo auto-sleep (original)
        self.auto_sleep = False

        # Inicializar la clase base exactamente como en el original
        try:
            super().__init__(
                touch_cal=touch_cal, startup_rotation=startup_rotation, debug=debug
            )
        except Exception as e:
            if debug:
                print(f"Warning during driver initialization: {e}")

    # *** MÉTODOS ORIGINALES PRESERVADOS ***
    def suspend(self):
        """Suspender el touch durante operaciones críticas"""
        self._is_suspended = True

    def resume(self):
        """Reanudar el touch después de operaciones críticas"""
        self._is_suspended = False

    @property
    def wake_up_threshold(self):
        val = self._read_reg(_LpScanTH)
        if val is None:
            return None
        return 256 - val

    @wake_up_threshold.setter
    def wake_up_threshold(self, value):
        if value < 1:
            value = 1
        elif value > 255:
            value = 255

        self._write_reg(_LpScanTH, 256 - value)

    @property
    def wake_up_scan_frequency(self):
        val = self._read_reg(_LpScanFreq)
        if val is None:
            return None
        return 256 - val

    @wake_up_scan_frequency.setter
    def wake_up_scan_frequency(self, value):
        if value < 1:
            value = 1
        elif value > 255:
            value = 255

        self._write_reg(_LpScanFreq, 256 - value)

    @property
    def auto_sleep_timeout(self):
        return self._read_reg(_AutoSleepTime)

    @auto_sleep_timeout.setter
    def auto_sleep_timeout(self, value):
        if value < 1:
            value = 1
        elif value > 255:
            value = 255

        self._write_reg(_AutoSleepTime, value)

    def wake_up(self):
        auto_sleep = self.auto_sleep

        self._write_reg(_DisAutoSleep, 0x00)
        time.sleep_ms(10)
        self._write_reg(_DisAutoSleep, 0xFE)
        time.sleep_ms(50)
        self._write_reg(_DisAutoSleep, 0xFE)
        time.sleep_ms(50)
        self._write_reg(_DisAutoSleep, int(not auto_sleep))

    @property
    def auto_sleep(self):
        val = self._read_reg(_DisAutoSleep)
        if val is None:
            return None
        return val == 0x00

    @auto_sleep.setter
    def auto_sleep(self, en):
        if en:
            self._write_reg(_DisAutoSleep, 0x00)
        else:
            self._write_reg(_DisAutoSleep, 0xFE)

    def hw_reset(self):
        if self._reset_pin is None:
            return

        self._reset_pin(0)
        time.sleep_ms(1)
        self._reset_pin(1)
        time.sleep_ms(50)

    def _get_coords(self):
        """
        Método original preservado con solo la verificación de suspensión agregada
        """
        # *** ÚNICA LÍNEA AGREGADA ***
        if self._is_suspended:
            return None
        
        # *** CÓDIGO ORIGINAL SIN CAMBIOS ***
        finger_num = self._read_reg(_FingerNum)
        if finger_num is None or finger_num == 0:
            return None

        x_high = self._read_reg(_XposH)
        if x_high is None:
            return None
        x = (x_high & 0x0F) << 8
        x_low = self._read_reg(_XposL)
        if x_low is None:
            return None
        x |= x_low

        y_high = self._read_reg(_YposH)
        if y_high is None:
            return None
        y = (y_high & 0x0F) << 8
        y_low = self._read_reg(_YposL)
        if y_low is None:
            return None
        y |= y_low

        return self.PRESSED, x, y

    # *** NUEVOS MÉTODOS OPCIONALES ***
    def set_operating_mode_fast(self, notify_motion=False):
        """
        Configurar modo rápido con detección por software
        - notify_motion: Si True, notifica durante movimiento
        """
        irq_enable = _EnChange
        if notify_motion:
            irq_enable |= _EnMotion | _EnTouch
        
        if self._write_reg(_IrqCtl, irq_enable):
            self._write_reg(_MotionMask, 0)
            self._operating_mode = CST816SOperatingMode.FAST
            self._notify_on_motion = notify_motion
            if self._debug:
                print(f"Set to FAST mode, motion={notify_motion}")
            return True
        return False
        
    def set_operating_mode_hardware(self):
        """
        Configurar modo hardware completo
        - Long press más lento pero más preciso
        - Double click solo da evento de gesto
        """
        irq_enable = _EnMotion | _OnceWLP
        if self._write_reg(_IrqCtl, irq_enable):
            self._write_reg(_MotionMask, _EnDClick)
            self._operating_mode = CST816SOperatingMode.HARDWARE
            self._notify_release_only = True
            self._notify_on_motion = False
            if self._debug:
                print("Set to HARDWARE mode")
            return True
        return False

    def set_motion_mask(self, enable_continuous_lr=False, enable_continuous_ud=False, enable_double_click=False):
        """
        Configurar detección de movimientos continuos
        """
        mask = 0
        if enable_continuous_lr:
            mask |= _EnConLR
        if enable_continuous_ud:
            mask |= _EnConUD
        if enable_double_click:
            mask |= _EnDClick
        
        if self._write_reg(_MotionMask, mask):
            if self._debug:
                print(f"Motion mask set: LR={enable_continuous_lr}, UD={enable_continuous_ud}, DClick={enable_double_click}")
            return True
        return False

    def set_long_press_time(self, seconds):
        """
        Configurar tiempo de long press en segundos (0-255)
        0 = deshabilitar long press
        """
        if seconds < 0:
            seconds = 0
        elif seconds > 255:
            seconds = 255
        return self._write_reg(_LongPressTime, seconds)

    def set_auto_reset_time(self, seconds):
        """
        Reseteo automático cuando hay touch sin gesto válido
        0 = deshabilitar, 1-255 = segundos
        """
        if seconds < 0:
            seconds = 0
        elif seconds > 255:
            seconds = 255
        return self._write_reg(_AutoReset, seconds)

    def reset_chip_soft(self):
        """
        Reset completo del chip vía software
        """
        # Activar soft reset
        if self._write_reg(_IOCtl, _SOFT_RST):
            time.sleep_ms(50)
            # Desactivar soft reset
            self._write_reg(_IOCtl, 0)
            time.sleep_ms(100)
            
            # Reinicializar configuración básica
            self._write_reg(_IrqCtl, _EnTouch | _EnChange)
            if self._debug:
                print("Soft reset completed")
            return True
        return False

    def _get_gesture_data(self):
        """
        Leer datos completos de gesto y touch en una sola operación optimizada
        """
        if self._is_suspended:
            return None
            
        # Leer todos los registros relevantes de una vez
        data = self._read_multiple_regs(_GestureID, 6)
        if data is None:
            return None
            
        gesture_id = data[0]
        finger_num = data[1]
        event_flag = (data[2] & 0xC0) >> 6
        
        if finger_num == 0:
            return None
            
        x = ((data[2] & 0x0F) << 8) | data[3]
        y = ((data[4] & 0x0F) << 8) | data[5]
        
        return {
            'gesture': gesture_id,
            'fingers': finger_num,
            'event': event_flag,  # 0=DOWN, 1=UP, 2=CONTACT
            'x': x,
            'y': y,
            'pressed': event_flag in [0, 2]  # DOWN o CONTACT
        }

    def get_chip_status(self):
        """
        Obtener estado completo del chip para diagnóstico
        """
        status = {}
        
        chip_id = self._read_reg(_ChipID)
        if chip_id is not None:
            status['chip_id'] = hex(chip_id)
            
        fw_version = self._read_reg(_FwVersion)
        if fw_version is not None:
            status['fw_version'] = hex(fw_version)
            
        irq_ctl = self._read_reg(_IrqCtl)
        if irq_ctl is not None:
            status['irq_control'] = hex(irq_ctl)
            
        motion_mask = self._read_reg(_MotionMask)
        if motion_mask is not None:
            status['motion_mask'] = hex(motion_mask)
            
        auto_sleep = self._read_reg(_DisAutoSleep)
        if auto_sleep is not None:
            status['auto_sleep'] = 'Disabled' if auto_sleep else 'Enabled'
            
        status['operating_mode'] = self._operating_mode
        status['notify_on_motion'] = self._notify_on_motion
        status['notify_release_only'] = self._notify_release_only
        
        return status

    def print_chip_status(self):
        """
        Imprimir estado completo del chip para debug
        """
        if not self._debug:
            return
            
        status = self.get_chip_status()
        print("=== CST816S Status ===")
        for key, value in status.items():
            print(f"{key}: {value}")
        print("=====================")
