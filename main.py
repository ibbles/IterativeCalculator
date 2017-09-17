#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import re
import sys
import subprocess
import tempfile

from pathlib import Path

from PyQt4.QtGui import *
from PyQt4.QtCore import *

app = QApplication(sys.argv)
form = QFormLayout()

output = QTextEdit()
form.addRow(output)

input = QTextEdit()
form.addRow(input)

run = QPushButton("&Run")

current_script_filename = ""

def run_octave(script_filename):
    # Using a temporary file instead of the --eval Octave argument because
    # Octave get line numbering wrong when not reading from a file.
    status = subprocess.run(
        ["octave", "--no-gui", "-q", script_filename],
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
    global current_script_filename
    filename = current_script_filename
    save_script(filename)
    status = run_octave(filename)
    if status.returncode == 0:
        result = status.stdout.decode("utf-8")
        output.setText(result)
    else:
        error = status.stderr.decode("utf-8")
        output.setText(error)
        move_to_error(error)

run.clicked.connect(on_clicked)
form.addRow(run)


def save_script(filename):
    with open(filename, 'w') as file:
        file.write(input.toPlainText())


def clear_selection():
    output.setText("")
    input.setText("")
    scripts_list.setCurrentRow(-1, QItemSelectionModel.Deselect)

def load_script(filename):
    try:
        with open(filename, 'r') as file:
            global current_script_filename
            current_script_filename = filename
            script_contents = file.read()
            input.setText(script_contents)
            output.setText("")
            status = run_octave(filename)
            if status.returncode == 0:
                result = status.stdout.decode("utf-8")
                output.setText(result)
            else:
                error = status.stderr.decode("utf-8")
                output.setText(error)
                move_to_error(error)

    except Exception as e:
        clear_selection()
        output.setText(str(e))

def change_script(old_filename, new_filename):
    save_script(old_filename)
    load_script(new_filename)

def list_selection_changed(current, previous):
    if current is None:
        clear_selection()
    elif previous is None:
        load_script(current.text())
    else:
        change_script(previous.text(), current.text())

scripts_list = QListWidget()
dir = Path(".")
for file in dir.glob("*.m"):
    scripts_list.addItem(file.name)
scripts_list.currentItemChanged.connect(list_selection_changed)
form.addRow(scripts_list)

window = QWidget()
window.resize(800, 1024)
window.setWindowTitle("Calculator")
window.setLayout(form)
window.show()

input.setFocus()

scripts_list.setCurrentRow(0, QItemSelectionModel.Select)

sys.exit(app.exec_())
