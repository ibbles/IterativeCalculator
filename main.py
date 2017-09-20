#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os
import re
import sys
import shutil
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
if scripts_list.count() == 0:
    scripts_list.addItem("default.m")
    with open("default.m", 'w'):
        pass
form.addRow(scripts_list)

create_script_button = QPushButton("&Create script")
form.addRow(create_script_button)

reload_timer = QTimer(app)
reload_timer.setInterval(1000)
reload_timer.setSingleShot(True)


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

def find_script_index(filename):
    for i in range(scripts_list.count()):
        item = scripts_list.item(i)
        if item.text() == filename:
            return i
    return None

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

def try_run_octave(filename):
    status = subprocess.run(
        ["octave", "--no-gui", "-q", filename], stdout=subprocess.PIPE)
    if status.returncode == 0:
        result = status.stdout.decode("utf-8")
        output.setText(result)
        return True
    else:
        return False

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
            return True
    except Exception as e:
        clear_selection()
        output.setText(str(e))
        list_index = find_script_index(filename)
        if not list_index is None:
            scripts_list.takeItem(list_index)
        return False

def change_script(old_filename, new_filename):
    save_script(old_filename)
    load_script(new_filename)

def create_script():
    filename, ok = QInputDialog.getText(None, "Script filename:", "name")
    if not ok:
        return

    print("Creating file '" + filename + "'.")
    for i in range(scripts_list.count()):
        item = scripts_list.item(i)
        if item.text() == filename:
            print("Already have item named '" + item.text() + "'.")
            scripts_list.setCurrentRow(i)
            return
    # Did not have a file with that name already.
    try:
        open(filename, 'r')
        # File exists but wasn't in our list. Add it.
        scripts_list.addItem(filename)
        scripts_list.setCurrentRow(scripts_list.count() - 1)
    except:
        try:
            open(filename, 'w')
            # File did not exist, but we've created it. Add to list.
            scripts_list.addItem(filename)
            scripts_list.setCurrentRow(scripts_list.count() - 1)
        except:
            print("Could not create file " + filename + "'.")


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

def on_create_script():
    create_script()

def on_text_changed():
    reload_timer.start()

def on_timer_exipred():
    filename = get_filename()
    if filename is None:
        return
    save_script(filename)
    try_run_octave(filename)

def on_quit():
    filename = get_filename()
    if not filename is None:
        save_script(filename)

run.clicked.connect(on_clicked)
scripts_list.currentItemChanged.connect(list_selection_changed)
create_script_button.clicked.connect(on_create_script)
input.textChanged.connect(on_text_changed)
reload_timer.timeout.connect(on_timer_exipred)
app.aboutToQuit.connect(on_quit)

window = QWidget()
window.resize(800, 730)
window.setWindowTitle("Calculator")
window.setLayout(form)
window.show()

input.setFocus()

scripts_list.setCurrentRow(0, QItemSelectionModel.Select)

sys.exit(app.exec_())
