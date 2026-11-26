// SPDX-License-Identifier: GPL-2.0-or-later
//
// Aqua "gel" painting. Colour stops are sampled from the pixel artwork in Apple's
// June 2002 Aqua Human Interface Guidelines (pop-up menu end cap, tab, push button,
// scroll thumb), so the gradients follow the real 10.2 controls.

#pragma once

#include <QColor>
#include <QGradientStops>
#include <QPainter>
#include <QPixmap>
#include <QRectF>

namespace Pinstripe
{
enum class Appearance { Blue, Graphite };

struct Gel {
    QColor rimTop, rimBottom; // 1px outline
    QGradientStops body; // whole inner area, top to bottom
    QGradientStops lens; // specular highlight over the top ~42%
};

enum class GelKind {
    Clear, // all ordinary push buttons, unselected tabs, check boxes off
    Colored, // default button, selected tab, check boxes on, thumbs, pop-up caps
    Pressed, // a clear button while pressed (acquires colour, a little darker)
    TabSelected, // flatter, lighter gel used by tabs (Figure 7-23)
    TabClear,
    Thumb, // scroll bar thumb: more saturated, narrow medium-blue lens
    Progress, // determinate progress fill (HIG Figure 7-27), rows measured from the artwork
};

Gel gel(GelKind kind, Appearance appearance);

// Blend a gel towards another (used for the default button's pulse).
Gel mix(const Gel &a, const Gel &b, qreal t);

struct GelOptions {
    qreal radius = -1; // -1: fully rounded (capsule / circle)
    Qt::Orientation orientation = Qt::Horizontal; // Vertical: gradient runs left to right
    bool shadow = true; // soft drop shadow under the control
    qreal lensInset = -1; // horizontal inset of the lens; -1: automatic
    qreal lensHeight = 0.42; // fraction of the inner height
};

void paintGel(QPainter *p, const QRectF &rect, const Gel &g, const GelOptions &o = {});

// 4px pinstripe tile (255, 238, 230, 238), measured from 10.2 windows in the HIG artwork.
QPixmap windowStripes();
// Menus are a little lighter (255, 249, 236, 249).
QPixmap menuStripes(int alpha = 255);

// Menu / list selection blue, sampled from the HIG menu artwork.
QColor menuHighlight(Appearance appearance);

QColor graphite(const QColor &c);

// Selection highlight: a glossy blue gel with the pinstripes showing through it.
void paintSelection(QPainter *p, const QRectF &rect, Appearance appearance, qreal radius = 0);
}
