#!/usr/bin/python3
from gi.repository import Gtk, Gdk
import subprocess

def f_g_c(filename):
    with open(filename) as f:
        return f.read().strip()

def prepareRow(title):
    row = Gtk.ListBoxRow()
    row.set_selectable(False)
    row.set_activatable(False)

    label1 = Gtk.Label(title)
    label1.set_justify(Gtk.Justification.RIGHT)

    grid = Gtk.Table(1,16,True)

    box = Gtk.Box()
    box.pack_start(Gtk.Label(''),True,True,0)
    box.add(label1)
    box.set_margin_end(9)

    grid.attach(box,2,7,0,1)

    return grid

def TextRow(title, f, camelCase=False, frmt='%s', run=False, plain=False):
    grid = prepareRow(title)

    if run:
        labelText = subprocess.check_output(f) if not camelCase else subprocess.check_output(f).title()
        labelText = labelText.decode('utf-8').strip()[1:-1]
    elif plain:
        labelText = frmt % f if not camelCase else f.title()
    else:
        labelText = frmt % f_g_c(f) if not camelCase else f_g_c(f).title()

    label1 = Gtk.Label(labelText)
    box = Gtk.Box()
    box.add(label1)
    box.set_margin_start(9)

    grid.attach(box,7,12,0,1)

    return grid

def PercentageRow(title, percent, subtitle):
    grid = prepareRow(title)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    vbox.set_margin_start(9)

    grid.attach(vbox,7,12,0,1)

    label1 = Gtk.Label(subtitle)
    progressBar = Gtk.ProgressBar()
    progressBar.set_fraction(percent)

    box = Gtk.Box()
    box.add(label1)

    vbox.pack_start(progressBar, True, True, 0)
    vbox.pack_start(box, True, True, 0)

    return grid
