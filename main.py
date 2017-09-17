#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import subprocess
import tempfile

from PyQt4.QtGui import *
from PyQt4.QtCore import *

app = QApplication(sys.argv)
form = QFormLayout()

output = QTextEdit()
form.addRow(output)

input = QTextEdit()
form.addRow(input)

run = QPushButton("&Run")

def run_octave(string):
    file = tempfile.NamedTemporaryFile(mode='w')
    file.write(string)
    file.flush()
    file_name = file.name
    result = subprocess.run(
        ["octave", "-q", file_name],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    file.close()
    return result

def on_clicked():
    result = run_octave(input.toPlainText())
    if result.returncode == 0:
        output.setText(result.stdout.decode("utf-8"))
    else:
        output.setText(result.stderr.decode("utf-8"))

run.clicked.connect(on_clicked)
form.addRow(run)

window = QWidget()
window.resize(800, 1024)
window.setWindowTitle("Calculator")
window.setLayout(form)
window.show()

input.setFocus()

sys.exit(app.exec_())
