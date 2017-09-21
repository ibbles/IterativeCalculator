#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#


# IterativeCalculator is an Octave script editor that displays the Octave output
# as the user types. The intended use case is for quick throw-away exploratory
# computations where the problem isn't understood well enough for the Octave
# shell and creating files and re-running Octave by hand several times is too
# much overhead.


import os
import re
import sys
import shutil
import subprocess

from pathlib import Path

from PyQt4.QtGui import *
from PyQt4.QtCore import *

# The subprocess library what change in Python 3.5 to include 'run'
# which is preferred over call.
try:
    subprocess.run
    have_run = True
except AttributeError:
    have_run = False

app = QApplication(sys.argv)
form = QFormLayout()


#
# Gui widgets.
#

output = QTextEdit()
output.setReadOnly(True)
form.addRow(output)

input = QTextEdit()
form.addRow(input)

run = QPushButton("&Run")
form.addRow(run)

scripts_list = QListWidget()
form.addRow(scripts_list)

create_script_button = QPushButton("&Create script")
form.addRow(create_script_button)

reload_timer = QTimer(app)
reload_timer.setInterval(1000)
reload_timer.setSingleShot(True)

# Load scripts that already exists.
# Create a default script if none existed.
dir = Path(".")
for file in dir.glob("*.m"):
    scriptname = file.name[:-len(".m")]
    scripts_list.addItem(scriptname)
if scripts_list.count() == 0:
    scripts_list.addItem("default")
    with open("default.m", 'w'):
        pass


#
# State operations.
#

def get_scriptname():
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

def find_script_index(scriptname):
    for i in range(scripts_list.count()):
        item = scripts_list.item(i)
        if item.text() == scriptname:
            return i
    return None


def move_to_position(line, col):
    cursor = input.textCursor()
    cursor.setPosition(0)
    cursor.movePosition(QTextCursor.Down, n=line)
    cursor.movePosition(QTextCursor.Right, n=col)
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


def run_octave(scriptname):
    if have_run:
        status = subprocess.run(
            ["octave", "--no-gui", "-q", scriptname+".m"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if status.returncode == 0:
            result = status.stdout.decode("utf-8")
            output.setText(result)
        else:
            error = status.stderr.decode("utf-8")
            output.setText(error)
            move_to_error(error)
    else:
        process = subprocess.Popen(
            ["octave", "--no-gui", "-q", scriptname+".m"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if process.returncode == 0:
            result = out.decode("utf-8")
            output.setText(result)
        else:
            error = err.decode("utf-8")
            output.setText(error)
            move_to_error(error)

def try_run_octave(scriptname):
    if have_run:
        status = subprocess.run(
            ["octave", "--no-gui", "-q", scriptname+".m"], stdout=subprocess.PIPE)
        if status.returncode == 0:
            result = status.stdout.decode("utf-8")
            output.setText(result)
            return True
        else:
            return False
    else:
        process = subprocess.Popen(
            ["octave", "--no-gui", "-q", scriptname+".m"], stdout=subprocess.PIPE)
        out, err = process.communicate()
        if process.returncode == 0:
            result = out.decode("utf-8")
            output.setText(result)
            return True
        else:
            return False


def save_script(scriptname):
    with open(scriptname+".m", 'w') as file:
        file.write(input.toPlainText())


def clear_selection():
    output.setText("")
    input.setText("")
    scripts_list.setCurrentRow(-1, QItemSelectionModel.Deselect)


def load_script(scriptname):
    try:
        with open(scriptname+".m", 'r') as file:
            script_contents = file.read()
            input.setText(script_contents)
            run_octave(scriptname)
            return True
    except Exception as e:
        clear_selection()
        output.setText(str(e))
        list_index = find_script_index(scriptname)
        if list_index is not None:
            scripts_list.takeItem(list_index)
        return False


def change_script(old_scriptname, new_scriptname):
    save_script(old_scriptname)
    load_script(new_scriptname)


def create_script():
    scriptname, ok = QInputDialog.getText(None, "Script name:", "name")
    if not ok:
        return

    for i in range(scripts_list.count()):
        item = scripts_list.item(i)
        if item.text() == scriptname:
            # The script already exists. Select it.
            scripts_list.setCurrentRow(i)
            return

    # Did not have a script with that name already.
    try:
        with open(scriptname+".m", 'r'):
            pass
        # File exists but wasn't in our list. Add it.
        scripts_list.addItem(scriptname)
        scripts_list.setCurrentRow(scripts_list.count() - 1)
    except:
        try:
            with open(scriptname+".m", 'w'):
                pass
            # File did not exist, but we have created it. Add to list.
            scripts_list.addItem(scriptname)
            scripts_list.setCurrentRow(scripts_list.count() - 1)
        except:
            output.setText("Could not create file " + scriptname+".m" + "'.")


#
# GUI widget callbacks.
#

def on_run_clicked():
    scriptname = get_scriptname()
    if scriptname is None:
        output.setText("No script file selected.")
        return
    save_script(scriptname)
    run_octave(scriptname)


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


def on_timer_expired():
    scriptname = get_scriptname()
    if scriptname is None:
        return
    save_script(scriptname)
    try_run_octave(scriptname)


def on_quit():
    scriptname = get_scriptname()
    if scriptname is not None:
        save_script(scriptname)


run.clicked.connect(on_run_clicked)
scripts_list.currentItemChanged.connect(list_selection_changed)
create_script_button.clicked.connect(on_create_script)
input.textChanged.connect(on_text_changed)
reload_timer.timeout.connect(on_timer_expired)
app.aboutToQuit.connect(on_quit)


#
# Application finalization.
#

window = QWidget()
window.resize(800, 730)
window.setWindowTitle("Calculator")
window.setLayout(form)
window.show()

scripts_list.setCurrentRow(0, QItemSelectionModel.Select)

input.setFocus()

sys.exit(app.exec_())
