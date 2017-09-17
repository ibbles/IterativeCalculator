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


#
# Gui widgets.
#

output = QTextEdit()
form.addRow(output)

input = QTextEdit()
form.addRow(input)

run = QPushButton("&Run")
form.addRow(run)

scripts_list = QListWidget()
dir = Path(".")
for file in dir.glob("*.m"):
    scripts_list.addItem(file.name)
form.addRow(scripts_list)


#
# State operations.
#

def get_filename():
    try:
        return scripts_list.currentItem().text()
    except:
        return None

def get_input():
    return input.toPlainText()

def set_input(input):
    input.setText(input)

def set_output(output):
    output.setText(output)


#
# Worker functions.
#

def move_to_position(line, col):
    cursor = input.textCursor()
    cursor.setPosition(0)
    cursor.movePosition(QTextCursor.Down, n = line)
    cursor.movePosition(QTextCursor.Right, n = col)
    input.setTextCursor(cursor)

def move_to_error(error_string):
    line_col = re.match(".*near line (.*) column (.*)", error_string)
    if line_col:
        try:
            # -1 becase cursor movements are 0-indexed but Octave line/col
            # numbering is not.
            line = int(line_col.group(1)) - 1
            col = int(line_col.group(2)) - 1
            move_to_position(line, col)
        except Exception as e:
            # Could not parse error message. That's fine, just cannot
            # helpfully place the cursor where the error is.
            pass

def run_octave(filename):
    status = subprocess.run(
        ["octave", "--no-gui", "-q", filename],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if status.returncode == 0:
        result = status.stdout.decode("utf-8")
        output.setText(result)
    else:
        error = status.stderr.decode("utf-8")
        output.setText(error)
        move_to_error(error)

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
            script_contents = file.read()
            input.setText(script_contents)
            run_octave(filename)
    except Exception as e:
        clear_selection()
        output.setText(str(e))

def change_script(old_filename, new_filename):
    save_script(old_filename)
    load_script(new_filename)


#
# GUI widget callbacks.
#

def on_clicked():
    filename = get_filename()
    if filename is None:
        output.setText("No script file selected.")
        return

    save_script(filename)
    run_octave(filename)




def list_selection_changed(current, previous):
    if current is None:
        clear_selection()
    elif previous is None:
        load_script(current.text())
    else:
        change_script(previous.text(), current.text())


run.clicked.connect(on_clicked)
scripts_list.currentItemChanged.connect(list_selection_changed)



window = QWidget()
window.resize(800, 1024)
window.setWindowTitle("Calculator")
window.setLayout(form)
window.show()

input.setFocus()

scripts_list.setCurrentRow(0, QItemSelectionModel.Select)

sys.exit(app.exec_())
