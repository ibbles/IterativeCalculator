#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import subprocess

from PyQt4.QtGui import *
from PyQt4.QtCore import *

app = QApplication(sys.argv)
form = QFormLayout()

output = QTextEdit()
form.addRow(output)

input = QTextEdit()
input.setText("a = 1 / 3")
form.addRow(input)

run = QPushButton("Run")
def on_clicked():
    result = subprocess.run(
        ["octave", "-q", "--eval", input.toPlainText()],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        output.setText(result.stdout.decode("utf-8"))
    else:
        output.setText(result.stderr.decode("utf-8"))
run.clicked.connect(on_clicked)
form.addRow(run)


window = QWidget()
shortcut = QShortcut(QKeySequence("Alt+r"), window)
window.connect(shortcut, SIGNAL('activated()'), on_clicked)
window.resize(800, 1024)
window.setWindowTitle("Calculator")
window.setLayout(form)
window.show()

sys.exit(app.exec_())
