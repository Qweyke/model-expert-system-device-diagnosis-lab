from experta import *
import sys


class Device(Fact):
    """Terminal-device status"""

    power = Field(str, default="unknown")
    led_color = Field(str, default="unknown")
    internal_state = Field(str, default="unknown")

    allowed_vals = {
        "power": ["on", "off", "unknown"],
        "led_color": ["red", "green", "yellow", "blue", "none", "unknown"],
        "internal_state": ["errfile", "erraddress", "unknown"],
    }


def ask_slot_value_with_validation(slot):
    allowed = Device.allowed_vals.get(slot)
    if not allowed:
        print(f"Slot {slot} has no allowed values.")
        sys.exit(1)

    while True:
        print(f"What's the status of {slot}: {allowed}?")
        user_input = input(">>> ").lower().strip()
        if user_input in allowed:
            return user_input
        print(f"Validate answer: Fail / Allowed answers are: {allowed}")


class DeviceDiagnosisEngine(KnowledgeEngine):

    @DefFacts()
    def _initial_fact(self):
        yield Device()

    # --------------------------
    # INTERACTIVE RULES
    # --------------------------

    @Rule(AS.dev << Device(power="unknown"))
    def check_power(self, dev):
        user_input = ask_slot_value_with_validation("power")
        self.modify(dev, power=user_input)

    @Rule(AS.dev << Device(power="on", led_color="unknown"))
    def check_led_color(self, dev):
        user_input = ask_slot_value_with_validation("led_color")
        self.modify(dev, led_color=user_input)

    @Rule(AS.dev << Device(power="on", led_color="yellow", internal_state="unknown"))
    def check_internal_state(self, dev):
        user_input = ask_slot_value_with_validation("internal_state")
        self.modify(dev, internal_state=user_input)

    # --------------------------
    # DIAGNOSES
    # --------------------------

    @Rule(Device(power="off"))
    def diagnose_no_power(self):
        print("Diagnosis: Connect the power supply to device")
        self.halt()

    @Rule(Device(power="on", led_color="none"))
    def diagnose_led_none(self):
        print(
            "Diagnosis: Hardware fault detected - send the board for physical diagnostics"
        )
        self.halt()

    @Rule(Device(power="on", led_color="red"))
    def diagnose_led_red(self):
        print("Diagnosis: CPU malfunction - send the board for CPU reballing")
        self.halt()

    @Rule(Device(power="on", led_color="yellow", internal_state="errfile"))
    def diagnose_led_yellow_errfile(self):
        print("Diagnosis: Flash error - reflash device with Stable.bin image")
        self.halt()

    @Rule(Device(power="on", led_color="yellow", internal_state="erraddress"))
    def diagnose_led_yellow_erraddr(self):
        print(
            "Diagnosis: Bootloader address fault - reflash device with Recovery.bin image"
        )
        self.halt()

    @Rule(Device(power="on", led_color="green"))
    def diagnose_led_green_ok(self):
        print("Diagnosis: Device fully operational - ready for casing")
        self.halt()

    @Rule(Device(power="on", led_color="blue"))
    def diagnose_led_blue(self):
        print("Diagnosis: Firmware update process detected")
        self.halt()


def start():
    engine = DeviceDiagnosisEngine()
    engine.reset()
    engine.run()


if __name__ == "__main__":
    start()
