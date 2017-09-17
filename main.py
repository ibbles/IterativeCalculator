#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# Create an PyQT4 application object.
app = QApplication(sys.argv)

# The QWidget widget is the base class of all user interface objects in PyQt4.
window = QWidget()

# Set window size.
window.resize(320, 240)

# Set window title
window.setWindowTitle("Calculator")

form = QFormLayout()

output = QTextEdit(window)
output.setText("Result will be shown here.")
form.addRow(output)

input = QTextEdit()
input.setText("Type here.")
form.addRow(input)

run = QPushButton("Run")
def on_clicked():
    print("Clicked")
    output.setText("Run!")
run.clicked.connect(on_clicked)
form.addRow(run)


window.connect(QShortcut(QKeySequence("Alt+r"), window), SIGNAL('activated()'), on_clicked)

window.setLayout(form)

window.show()



sys.exit(app.exec_())
