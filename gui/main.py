import sys
from PySide6.QtWidgets import QApplication
from diagnostic_gui import DiagnosticGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DiagnosticGUI()
    gui.show()

    sys.exit(app.exec())
