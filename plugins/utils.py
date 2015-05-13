#!/usr/bin/python3
from gi.repository import Gtk, Gdk
import subprocess

def f_g_c(filename):
    with open(filename) as f:
        try: return f.read().strip()
        except: return ''

def prepareRow(title):
    label1 = Gtk.Label(title)
    label1.set_justify(Gtk.Justification.RIGHT)
    label1.set_alignment(1,0)

    grid = Gtk.Box(True, orientation=Gtk.Orientation.HORIZONTAL)
    grid.pack_start(label1,True, True, 9)
    grid.props.hexpand = True

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
    #box.set_margin_start(9)

    grid.pack_start(box,True, True, 9)

    return grid

def PercentageRow(title, percent, subtitle):
    grid = prepareRow(title)

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    grid.pack_start(vbox,True, True, 9)

    label1 = Gtk.Label(subtitle)
    progressBar = Gtk.ProgressBar()
    progressBar.set_fraction(percent)
    progressBar.set_margin_right(45)

    box = Gtk.Box()
    box.add(label1)

    vbox.pack_start(progressBar, True, True, 0)
    vbox.pack_start(box, True, True, 0)

    return grid
