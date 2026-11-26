#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Render a GTK widget gallery with the Pinstripe GTK theme into a PNG, headless.

Run it under a Broadway display so nothing appears on screen:

    broadwayd :7 &        GDK_BACKEND=broadway BROADWAY_DISPLAY=:7 python3 tools/gtk_gallery.py 3 out.png
    gtk4-broadwayd :8 &   GDK_BACKEND=broadway BROADWAY_DISPLAY=:8 python3 tools/gtk_gallery.py 4 out.png
"""
import os
import sys

import gi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "3"
OUT = sys.argv[2] if len(sys.argv) > 2 else f"gtk{VERSION}-gallery.png"
gi.require_version("Gtk", f"{VERSION}.0")
from gi.repository import GLib, Gtk  # noqa: E402

if VERSION == "4":
    gi.require_version("Gsk", "4.0")
    from gi.repository import Gdk, Gsk  # noqa: E402
    Gtk.init()
else:
    Gtk.IconTheme.get_default().prepend_search_path(os.path.join(ROOT, "icons"))

settings = Gtk.Settings.get_default()
settings.set_property("gtk-theme-name", "Pinstripe")
settings.set_property("gtk-font-name", sys.argv[3] if len(sys.argv) > 3 else "Luxi Sans 10")
settings.set_property("gtk-icon-theme-name", "Oxygen-Pinstripe")


def add(box, w):
    if VERSION == "4":
        box.append(w)
    else:
        box.pack_start(w, False, False, 0)


def build():
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    global HEADER
    hb = Gtk.HeaderBar()
    HEADER = hb
    if VERSION == "4":
        hb.set_decoration_layout("close,minimize,maximize:")
        hb.set_title_widget(Gtk.Label(label="Widget Gallery"))
        hb.set_show_title_buttons(True)
        return_hb = True
    else:
        hb.set_decoration_layout("close,minimize,maximize:")
        hb.set_title("Widget Gallery")
        hb.set_show_close_button(True)
    if VERSION != "4":
        add(outer, hb)

    body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    for m in ("start", "end", "top", "bottom"):
        getattr(body, f"set_margin_{m}")(16)
    add(outer, body)

    nb = Gtk.Notebook()
    grid = Gtk.Grid(column_spacing=12, row_spacing=8)
    for m in ("start", "end", "top", "bottom"):
        getattr(grid, f"set_margin_{m}")(12)
    check = Gtk.CheckButton(label="Checkbox")
    check.set_active(True)
    combo = Gtk.ComboBoxText()
    combo.append_text("Combo box")
    combo.append_text("Second")
    combo.set_active(0)
    if VERSION == "4":
        r1 = Gtk.CheckButton(label="Radio button")
        r2 = Gtk.CheckButton(label="Radio button")
        r2.set_group(r1)
    else:
        r1 = Gtk.RadioButton(label="Radio button")
        r2 = Gtk.RadioButton.new_with_label_from_widget(r1, "Radio button")
    r1.set_active(True)
    button = Gtk.Button(label="Button")
    spin = Gtk.SpinButton.new_with_range(0, 100, 1)
    entry = Gtk.Entry()
    entry.set_placeholder_text("Text Field")
    scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    scale.set_value(30)
    scale.set_draw_value(False)
    scale.set_hexpand(True)
    prog = Gtk.ProgressBar()
    prog.set_fraction(0.7)
    prog.set_valign(Gtk.Align.CENTER)
    row = Gtk.Box(spacing=12)
    add(row, button)
    add(row, spin)
    grid.attach(check, 0, 0, 1, 1)
    grid.attach(combo, 1, 0, 1, 1)
    grid.attach(r1, 0, 1, 1, 1)
    grid.attach(row, 1, 1, 1, 1)
    grid.attach(r2, 0, 2, 1, 1)
    grid.attach(entry, 1, 2, 1, 1)
    grid.attach(scale, 0, 3, 1, 1)
    grid.attach(prog, 1, 3, 1, 1)
    nb.append_page(grid, Gtk.Label(label="Tab 1"))
    nb.append_page(Gtk.Label(label="Second page"), Gtk.Label(label="Tab 2"))
    add(body, nb)

    # list with disclosure triangles, small-font headings, selection and a scroll bar
    store = Gtk.TreeStore(str, str)
    for n in ("Applications", "Documents", "Library", "Movies", "Music", "Pictures", "Public", "Sites"):
        it = store.append(None, [n, "Today, 7:17 PM"])
        store.append(it, ["Item", "Yesterday"])
    tree = Gtk.TreeView(model=store)
    for i, t in enumerate(("Name", "Date Modified")):
        col = Gtk.TreeViewColumn(t, Gtk.CellRendererText(), text=i)
        col.set_expand(i == 0)
        if i == 0:
            col.set_sort_indicator(True)
            col.set_sort_order(Gtk.SortType.ASCENDING)
        tree.append_column(col)
        if i == 0:
            hb = col.get_button()
            hb.get_style_context().add_class("sorted") if VERSION == "3" else hb.add_css_class("sorted")
    tree.expand_row(Gtk.TreePath.new_from_string("1"), False)
    tree.get_selection().select_path(Gtk.TreePath.new_from_string("2"))
    sw = Gtk.ScrolledWindow()
    sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
    if VERSION == "4":
        sw.set_child(tree)
        sw.set_has_frame(True)
        sw.set_overlay_scrolling(False)
    else:
        sw.add(tree)
        sw.set_shadow_type(Gtk.ShadowType.IN)
        sw.set_overlay_scrolling(False)
    sw.set_size_request(-1, 125)
    add(body, sw)

    # group box (frame with label) and matte bevel buttons (icon above label)
    lower = Gtk.Box(spacing=12)
    frame = Gtk.Frame(label="Icon Arrangement")
    frame.set_hexpand(True)
    fbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    if VERSION == "4":
        g1 = Gtk.CheckButton(label="None")
        g2 = Gtk.CheckButton(label="Always snap to grid")
        g2.set_group(g1)
        g2.set_active(True)
        frame.set_child(fbox)
    else:
        g1 = Gtk.RadioButton(label="None")
        g2 = Gtk.RadioButton.new_with_label_from_widget(g1, "Always snap to grid")
        g2.set_active(True)
        frame.add(fbox)
    add(fbox, g1)
    add(fbox, g2)
    if VERSION == "4":
        lower.append(frame)
    else:
        lower.pack_start(frame, True, True, 0)

    bevels = Gtk.Box(spacing=8)
    bevels.set_valign(Gtk.Align.CENTER)
    for idx, (ic, lbl) in enumerate((("document-print", "Print"), ("configure", "Settings"))):
        b = Gtk.ToggleButton()
        b.set_active(idx == 1)
        b.set_size_request(58, 57)
        vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        vb.set_valign(Gtk.Align.CENTER)
        if VERSION == "4":
            b.add_css_class("bevel")
            img = Gtk.Image.new_from_icon_name(ic)
            img.set_pixel_size(32)
            b.set_child(vb)
        else:
            b.get_style_context().add_class("bevel")
            img = Gtk.Image.new_from_icon_name(ic, Gtk.IconSize.DND)
            img.set_pixel_size(32)
            b.add(vb)
        add(vb, img)
        add(vb, Gtk.Label(label=lbl))
        add(bevels, b)
    add(lower, bevels)
    add(body, lower)

    buttons = Gtk.Box(spacing=12)
    buttons.set_halign(Gtk.Align.END)
    cancel = Gtk.Button(label="Cancel")
    ok = Gtk.Button(label="OK")
    ok.get_style_context().add_class("suggested-action") if VERSION == "3" else ok.add_css_class("suggested-action")
    add(buttons, cancel)
    add(buttons, ok)
    add(body, buttons)
    return outer


def save_gtk3(widget):
    win = Gtk.OffscreenWindow()
    win.add(widget)
    win.set_default_size(470, 520)
    win.show_all()

    def grab():
        pb = win.get_pixbuf()
        pb.savev(OUT, "png", [], [])
        Gtk.main_quit()
        return False
    GLib.timeout_add(600, grab)
    Gtk.main()


def save_gtk4(widget):
    loop = GLib.MainLoop()
    win = Gtk.Window()
    win.set_titlebar(HEADER)
    win.set_child(widget)
    win.set_default_size(470, 520)
    win.present()

    def grab():
        w, h = win.get_width(), win.get_height()
        paintable = Gtk.WidgetPaintable.new(win)
        snap = Gtk.Snapshot()
        paintable.snapshot(snap, w, h)
        node = snap.to_node()
        renderer = Gsk.CairoRenderer()
        renderer.realize_for_display(Gdk.Display.get_default())
        tex = renderer.render_texture(node, None)
        tex.save_to_png(OUT)
        renderer.unrealize()
        loop.quit()
        return False
    GLib.timeout_add(900, grab)
    loop.run()


if __name__ == "__main__":
    w = build()
    if VERSION == "4":
        save_gtk4(w)
    else:
        save_gtk3(w)
    print("wrote", OUT)
