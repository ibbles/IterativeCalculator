#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import re
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
with open("script.m", 'r') as file:
    input.setText(file.read())

run = QPushButton("&Run")

def run_octave(string):
    # Using a temporary file instead of the --eval Octave argument because
    # Octave get line numbering wrong when not reading from a file.
    with open('script.m', 'w') as file:
        file.write(string)
        file.flush()
        file_name = file.name
        status = subprocess.run(
            ["octave", "--no-gui", "-q", file_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return status

def move_to_error(error_string):
        line_col = re.match(".*near line (.*) column (.*)", error_string)
        if line_col:
            try:
                # -1 becase cursor movements are 0-indexed but Octave line/col
                # numbering is not.
                line = int(line_col.group(1)) - 1
                col = int(line_col.group(2)) - 1
                cursor = input.textCursor()
                cursor.setPosition(0)
                cursor.movePosition(QTextCursor.Down, n = line - 1)
                cursor.movePosition(QTextCursor.Right, n = col - 1)
                input.setTextCursor(cursor)
            except:
                # Could not parse error message. That's fine, just cannot
                # helfully place the cursor where the error is.
                pass

def on_clicked():
    script = input.toPlainText()
    status = run_octave(script)
    if status.returncode == 0:
        result = status.stdout.decode("utf-8")
        output.setText(result)
    else:
        error = status.stderr.decode("utf-8")
        output.setText(error)
        move_to_error(error)

run.clicked.connect(on_clicked)
form.addRow(run)

window = QWidget()
window.resize(800, 1024)
window.setWindowTitle("Calculator")
window.setLayout(form)
window.show()

input.setFocus()

sys.exit(app.exec_())
