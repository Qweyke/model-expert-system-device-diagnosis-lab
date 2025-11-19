import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QHBoxLayout,
    QFrame,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal
from expert_engine import DeviceDiagnosisEngine


class DiagnosticGUI(QWidget):
    signal_input_ready = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telematics Terminal Diagnostics")

        icon_path = os.path.join(os.path.dirname(__file__), "wizard.png")
        self.setWindowIcon(QIcon(icon_path))

        self.setMinimumSize(600, 400)

        self._layout = QVBoxLayout(self)

        # --- HEADER ---
        header = QLabel("DEVICE DIAGNOSTICS")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold; margin: 10px;")
        self._layout.addWidget(header)

        # --- STATUS PANEL ---
        status_container = QFrame()
        status_container.setFrameShape(QFrame.Box)
        status_container.setStyleSheet("padding: 10px;")
        status_layout = QVBoxLayout(status_container)

        self.label_hint = QLabel("Press 'Start Diagnosis'")
        self.label_hint.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: black;"
        )
        status_layout.addWidget(self.label_hint)

        self.label_step = QLabel("Step: Waiting to start...")
        self.label_step.setStyleSheet("font-size: 14px; color: gray;")
        status_layout.addWidget(self.label_step)

        self._layout.addWidget(status_container)

        # --- INPUT PANEL ---
        input_container = QFrame()
        input_container.setFrameShape(QFrame.Box)
        input_container.setStyleSheet("padding: 10px;")
        input_layout = QHBoxLayout(input_container)

        self.combo = QComboBox()
        self.combo.setEnabled(False)
        input_layout.addWidget(QLabel("Select value:"))
        input_layout.addWidget(self.combo)

        self.confirm_btn = QPushButton("Confirm")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self._confirm_input)
        input_layout.addWidget(self.confirm_btn)

        self._layout.addWidget(input_container)

        # --- CONTROL BUTTONS ---
        ctrl_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start Diagnosis")
        self.start_btn.clicked.connect(self._start_pressed)
        ctrl_layout.addWidget(self.start_btn)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setEnabled(False)
        self.reset_btn.clicked.connect(self._reset_pressed)
        ctrl_layout.addWidget(self.reset_btn)

        self._layout.addLayout(ctrl_layout)

        # State
        self.current_slot = None
        self.engine = None

    def closeEvent(self, event):
        if hasattr(self, "engine") and self.engine:
            if (
                hasattr(self.engine, "loop")
                and self.engine.loop
                and self.engine.loop.isRunning()
            ):
                self.engine.loop.quit()
            self.engine.halt()
        event.accept()

    # ---------------- GUI slots ----------------

    def _start_pressed(self):
        self.start_btn.setEnabled(False)
        self.reset_btn.setEnabled(True)
        self.label_step.setText("Diagnosis running...")
        self.label_hint.setText("Awaiting next step")

        # create engine now
        self.engine = DeviceDiagnosisEngine(parent=self)

        self.engine.signal_request_input.connect(self.on_request_input)
        self.engine.signal_diagnosis_ready.connect(self.on_diagnosis_ready)

        self.signal_input_ready.connect(self.engine.provide_answer)

        self.engine.reset()
        self.engine.run()

    def _reset_pressed(self):
        if self.engine:
            self.engine.reset()
        self.start_btn.setEnabled(True)
        self.reset_btn.setEnabled(False)
        self.combo.setEnabled(False)
        self.confirm_btn.setEnabled(False)
        self.label_step.setText("Step: Waiting to start...")
        self.label_hint.setText("Press 'Start Diagnosis'")

    def _confirm_input(self):
        if self.current_slot:
            value = self.combo.currentText()
            self.combo.setEnabled(False)
            self.confirm_btn.setEnabled(False)
            self.signal_input_ready.emit(self.current_slot, value)

    # ---------------- Slots for engine signals ----------------

    def on_request_input(self, slot, allowed_vals):
        self.current_slot = slot
        self.combo.clear()
        self.combo.addItems(allowed_vals)
        self.combo.setEnabled(True)
        self.confirm_btn.setEnabled(True)

        self.label_step.setText(f"Step: Set {slot}")
        self.label_hint.setText(f"Choose value for '{slot}'")

    def on_diagnosis_ready(self, text):
        self.label_step.setText("Diagnosis complete")
        self.label_hint.setText(text)
        self.combo.setEnabled(False)
        self.confirm_btn.setEnabled(False)
        self.reset_btn.setEnabled(True)
