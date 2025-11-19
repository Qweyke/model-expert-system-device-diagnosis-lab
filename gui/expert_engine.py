from experta import *
from PySide6.QtCore import QObject, Signal, QEventLoop


class Device(Fact):
    power = Field(str, default="unknown")
    led_color = Field(str, default="unknown")
    internal_state = Field(str, default="unknown")

    allowed_vals = {
        "power": ["on", "off"],
        "led_color": ["red", "green", "yellow", "blue", "none"],
        "internal_state": ["errfile", "erraddress"],
    }


class DeviceDiagnosisEngine(KnowledgeEngine, QObject):
    """
    Expert system engine.
    Emits signals to GUI instead of calling it directly.
    """

    signal_request_input = Signal(str, list)
    signal_diagnosis_ready = Signal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        KnowledgeEngine.__init__(self)

        self.loop = None
        self.last_answer = None

    def provide_answer(self, slot, value):
        """Called by GUI to provide user input."""
        self.last_answer = value.lower()
        if self.loop and self.loop.isRunning():
            self.loop.quit()

    def ask_value(self, slot):
        """Emit signal to GUI and wait for answer."""
        allowed = Device.allowed_vals[slot]
        self.signal_request_input.emit(slot, allowed)
        self.loop = QEventLoop()
        self.loop.exec()
        if self.last_answer is None:
            return "unknown"

        return self.last_answer

    # ------------------- Facts -------------------
    @DefFacts()
    def start_facts(self):
        yield Device()

    # ------------------- Rules -------------------
    @Rule(AS.dev << Device(power="unknown"))
    def rule_power(self, dev):
        v = self.ask_value("power")
        self.modify(dev, power=v)

    @Rule(AS.dev << Device(power="on", led_color="unknown"))
    def rule_led(self, dev):
        v = self.ask_value("led_color")
        self.modify(dev, led_color=v)

    @Rule(AS.dev << Device(power="on", led_color="yellow", internal_state="unknown"))
    def rule_internal(self, dev):
        v = self.ask_value("internal_state")
        self.modify(dev, internal_state=v)

    # ------------------- Diagnoses -------------------
    @Rule(Device(power="off"))
    def diag_off(self):
        self.signal_diagnosis_ready.emit("Connect the power supply to the device")
        self.halt()

    @Rule(Device(power="on", led_color="red"))
    def diag_red(self):
        self.signal_diagnosis_ready.emit(
            "CPU malfunction detected. Send for reballing."
        )
        self.halt()

    @Rule(Device(power="on", led_color="green"))
    def diag_green(self):
        self.signal_diagnosis_ready.emit("Device fully operational — OK.")
        self.halt()

    @Rule(Device(power="on", led_color="yellow", internal_state="errfile"))
    def diag_yellow_errfile(self):
        self.signal_diagnosis_ready.emit("Flash error — reflash device with Stable.bin")
        self.halt()

    @Rule(Device(power="on", led_color="yellow", internal_state="erraddress"))
    def diag_yellow_erraddr(self):
        self.signal_diagnosis_ready.emit(
            "Bootloader address fault — reflash device with Recovery.bin"
        )
        self.halt()

    @Rule(Device(power="on", led_color="blue"))
    def diag_blue(self):
        self.signal_diagnosis_ready.emit("Firmware update process detected")
        self.halt()

    @Rule(Device(power="on", led_color="none"))
    def diag_none(self):
        self.signal_diagnosis_ready.emit(
            "Hardware fault detected — send board for physical diagnostics"
        )
        self.halt()
