// SPDX-License-Identifier: GPL-2.0-or-later
#include "gel.h"

#include <QLinearGradient>
#include <QPainterPath>
#include <cmath>

namespace Pinstripe
{
namespace
{
QGradientStops stops(std::initializer_list<std::pair<qreal, QColor>> l)
{
    QGradientStops s;
    for (const auto &[pos, c] : l)
        s.append({pos, c});
    return s;
}

QColor lerp(const QColor &a, const QColor &b, qreal t)
{
    return QColor::fromRgbF(a.redF() + (b.redF() - a.redF()) * t,
                            a.greenF() + (b.greenF() - a.greenF()) * t,
                            a.blueF() + (b.blueF() - a.blueF()) * t,
                            a.alphaF() + (b.alphaF() - a.alphaF()) * t);
}

QColor colorAt(const QGradientStops &s, qreal pos)
{
    if (s.isEmpty())
        return {};
    if (pos <= s.first().first)
        return s.first().second;
    for (int i = 1; i < s.size(); ++i) {
        if (pos <= s[i].first) {
            const qreal t = (pos - s[i - 1].first) / qMax(1e-6, s[i].first - s[i - 1].first);
            return lerp(s[i - 1].second, s[i].second, t);
        }
    }
    return s.last().second;
}

QGradientStops mapStops(const QGradientStops &s, QColor (*f)(const QColor &))
{
    QGradientStops out;
    for (const auto &st : s)
        out.append({st.first, f(st.second)});
    return out;
}

Gel blueGel()
{
    // Sampled from the 20px pop-up end cap (Figure 7-8) and the selected tab (Figure 7-23):
    // a pale lens on top, a sharp edge into saturated blue at ~45%, brightening to cyan.
    Gel g;
    g.rimTop = QColor(26, 44, 112);
    g.rimBottom = QColor(62, 92, 140);
    g.body = stops({{0.00, QColor(92, 140, 214)},
                    {0.42, QColor(98, 162, 238)},
                    {0.50, QColor(107, 176, 246)},
                    {0.62, QColor(141, 205, 255)},
                    {0.80, QColor(163, 228, 255)},
                    {1.00, QColor(180, 242, 255)}});
    g.lens = stops({{0.00, QColor(228, 234, 247)},
                    {0.18, QColor(189, 211, 239)},
                    {0.55, QColor(150, 191, 234)},
                    {1.00, QColor(131, 181, 236)}});
    return g;
}

Gel clearGel()
{
    // Sampled from the clear "Cancel" push button and unselected tab artwork.
    Gel g;
    g.rimTop = QColor(108, 108, 112);
    g.rimBottom = QColor(150, 150, 156);
    g.body = stops({{0.00, QColor(200, 202, 206)},
                    {0.42, QColor(201, 204, 210)},
                    {0.55, QColor(209, 214, 220)},
                    {0.80, QColor(228, 233, 238)},
                    {1.00, QColor(247, 248, 250)}});
    g.lens = stops({{0.00, QColor(253, 253, 254)},
                    {0.35, QColor(236, 238, 242)},
                    {1.00, QColor(222, 225, 230)}});
    return g;
}
}

QColor graphite(const QColor &c)
{
    // The 10.2 Graphite appearance: same gels, blue-grey instead of blue.
    const qreal l = 0.30 * c.redF() + 0.59 * c.greenF() + 0.11 * c.blueF();
    return QColor::fromRgbF(qBound(0.0, l * 0.90, 1.0), qBound(0.0, l * 0.95, 1.0), qBound(0.0, l * 1.06, 1.0), c.alphaF());
}

Gel tint(Gel g, Appearance appearance)
{
    if (appearance == Appearance::Graphite) {
        g.rimTop = graphite(g.rimTop);
        g.rimBottom = graphite(g.rimBottom);
        g.body = mapStops(g.body, graphite);
        g.lens = mapStops(g.lens, graphite);
    }
    return g;
}

Gel gel(GelKind kind, Appearance appearance)
{
    switch (kind) {
    case GelKind::Clear:
        return clearGel();
    case GelKind::TabSelected: {
        // sampled column of the selected "Mouse" / "Appearance" tab (HIG Figures 7-23, 8-2):
        // sky-blue top lens, dip at ~24%, brightening to icy cyan where it merges into the accent strip
        Gel g;
        g.rimTop = QColor(21, 43, 108);
        g.rimBottom = QColor(0, 87, 174);
        g.body = stops({{0.00, QColor(136, 176, 226)},
                        {0.24, QColor(114, 158, 212)},
                        {0.55, QColor(148, 192, 238)},
                        {0.82, QColor(182, 224, 255)},
                        {0.95, QColor(206, 246, 255)},
                        {1.00, QColor(178, 222, 244)}});
        g.lens = stops({{0.00, QColor(198, 224, 248)}, {0.50, QColor(176, 208, 240)}, {1.00, QColor(152, 192, 232)}});
        return tint(g, appearance);
    }
    case GelKind::TabClear: {
        // sampled column of the unselected "Trackpad" / "Settings" tab (HIG Figures 7-23, 8-2)
        Gel g;
        g.rimTop = QColor(118, 118, 122);
        g.rimBottom = QColor(140, 140, 144);
        g.body = stops({{0.00, QColor(214, 215, 218)},
                        {0.26, QColor(194, 196, 200)},
                        {0.60, QColor(214, 216, 220)},
                        {0.88, QColor(242, 244, 246)},
                        {1.00, QColor(252, 253, 255)}});
        g.lens = stops({{0.00, QColor(250, 250, 252)}, {0.50, QColor(236, 237, 240)}, {1.00, QColor(220, 222, 226)}});
        return g;
    }
    case GelKind::Progress: {
        // rows of the 16px large progress bar fill (HIG Figure 7-27): medium blue on top, a dip
        // to deep blue at half height, rising to cyan; no separate white lens
        Gel g;
        g.rimTop = QColor(47, 85, 150);
        g.rimBottom = QColor(90, 140, 200);
        static const int rows[15][3] = {{90, 135, 212}, {130, 175, 229}, {143, 187, 234}, {144, 186, 236}, {131, 178, 232},
                                        {110, 165, 229}, {85, 150, 223}, {74, 145, 227}, {82, 156, 241}, {95, 170, 251},
                                        {104, 180, 255}, {116, 192, 254}, {125, 202, 255}, {131, 204, 255}, {143, 196, 236}};
        for (int i = 0; i < 15; ++i)
            g.body.append({i / 14.0, QColor(rows[i][0], rows[i][1], rows[i][2])});
        return tint(g, appearance);
    }
    case GelKind::Thumb: {
        // columns across the 10.2 scroll thumb, averaged over its length (HIG Figure "Sample Window")
        Gel g;
        g.rimTop = QColor(24, 55, 115);
        g.rimBottom = QColor(68, 93, 110);
        // piecewise-constant so each pixel column keeps its measured colour (the sharp dip after
        // the lens is what makes the thumb read as a cylinder)
        static const int cols[11][3] = {{122, 159, 215}, {143, 185, 238}, {140, 184, 236}, {128, 180, 238}, {79, 142, 216}, {93, 162, 239},
                                        {111, 178, 249}, {128, 195, 253}, {141, 209, 254}, {160, 220, 253}, {164, 206, 232}};
        for (int i = 0; i < 11; ++i) {
            const QColor col(cols[i][0], cols[i][1], cols[i][2]);
            g.body.append({i / 11.0 + (i ? 0.001 : 0.0), col});
            g.body.append({(i + 1) / 11.0, col});
        }
        g.lens = stops({{0.0, QColor(124, 161, 217)}, {0.35, QColor(143, 185, 238)}, {1.0, QColor(130, 181, 238)}});
        return tint(g, appearance);
    }
    case GelKind::Pressed: {
        Gel g = gel(GelKind::Colored, appearance);
        auto darker = [](const QColor &c) {
            return c.darker(118);
        };
        for (auto &s : g.body)
            s.second = darker(s.second);
        for (auto &s : g.lens)
            s.second = darker(s.second);
        return g;
    }
    case GelKind::Colored:
    default: {
        return tint(blueGel(), appearance);
    }
    }
}

Gel mix(const Gel &a, const Gel &b, qreal t)
{
    Gel g;
    g.rimTop = lerp(a.rimTop, b.rimTop, t);
    g.rimBottom = lerp(a.rimBottom, b.rimBottom, t);
    for (const auto &s : a.body)
        g.body.append({s.first, lerp(s.second, colorAt(b.body, s.first), t)});
    for (const auto &s : a.lens)
        g.lens.append({s.first, lerp(s.second, colorAt(b.lens, s.first), t)});
    return g;
}

void paintGel(QPainter *p, const QRectF &rect, const Gel &g, const GelOptions &o)
{
    p->save();
    p->setRenderHint(QPainter::Antialiasing, true);
    p->setPen(Qt::NoPen);

    const bool vertical = o.orientation == Qt::Vertical;
    const qreal thickness = vertical ? rect.width() : rect.height();
    const qreal radius = o.radius < 0 ? thickness / 2.0 : o.radius;

    if (o.shadow) {
        // soft shadow: mostly below, a little around (the HIG buttons sit in a grey halo)
        p->setBrush(QColor(0, 0, 0, 12));
        p->drawRoundedRect(rect.adjusted(-0.8, -0.2, 0.8, 2.6), radius + 0.8, radius + 0.8);
        p->setBrush(QColor(0, 0, 0, 22));
        p->drawRoundedRect(rect.adjusted(-0.3, 0.6, 0.3, 1.8), radius + 0.3, radius + 0.3);
        p->setBrush(QColor(0, 0, 0, 30));
        p->drawRoundedRect(rect.translated(0, 1.0), radius, radius);
    }

    // rim
    {
        QLinearGradient rim(rect.topLeft(), vertical ? rect.topRight() : rect.bottomLeft());
        rim.setColorAt(0, g.rimTop);
        rim.setColorAt(1, g.rimBottom);
        p->setBrush(rim);
        p->drawRoundedRect(rect, radius, radius);
    }

    // body
    const QRectF inner = rect.adjusted(1, 1, -1, -1);
    const qreal innerRadius = qMax<qreal>(0, radius - 1);
    {
        QLinearGradient body(inner.topLeft(), vertical ? inner.topRight() : inner.bottomLeft());
        body.setStops(g.body);
        p->setBrush(body);
        p->drawRoundedRect(inner, innerRadius, innerRadius);
    }

    // lens: inset from the end caps, rounded at its ends, sharp lower edge
    if (o.lensHeight > 0 && !g.lens.isEmpty()) {
        const qreal len = vertical ? inner.height() : inner.width();
        const qreal th = vertical ? inner.width() : inner.height();
        const qreal lensTh = th * o.lensHeight;
        qreal inset = o.lensInset >= 0 ? o.lensInset : qMin(th * 0.30, len * 0.18);
        QRectF lens;
        if (vertical)
            lens = QRectF(inner.left() + 0.5, inner.top() + inset, lensTh, inner.height() - 2 * inset);
        else
            lens = QRectF(inner.left() + inset, inner.top() + 0.5, inner.width() - 2 * inset, lensTh);
        QLinearGradient lg(lens.topLeft(), vertical ? lens.topRight() : lens.bottomLeft());
        lg.setStops(g.lens);
        p->setBrush(lg);
        const qreal lr = qMin(lensTh, innerRadius) * 0.95;
        QPainterPath path;
        path.addRoundedRect(lens, lr, lr);
        p->setClipRect(inner.adjusted(0, 0, 0, 0), Qt::IntersectClip);
        p->drawPath(path);
    }
    p->restore();
}

QPixmap windowStripes()
{
    static QPixmap pm;
    if (pm.isNull()) {
        QImage img(16, 4, QImage::Format_RGB32);
        const int rows[4] = {255, 238, 230, 238};
        for (int y = 0; y < 4; ++y)
            for (int x = 0; x < 16; ++x)
                img.setPixel(x, y, qRgb(rows[y], rows[y], rows[y]));
        pm = QPixmap::fromImage(img);
    }
    return pm;
}

QPixmap menuStripes(int alpha)
{
    QImage img(16, 4, QImage::Format_ARGB32_Premultiplied);
    const int rows[4] = {255, 249, 238, 249};
    for (int y = 0; y < 4; ++y)
        for (int x = 0; x < 16; ++x) {
            const int v = rows[y] * alpha / 255;
            img.setPixel(x, y, qRgba(v, v, v, alpha));
        }
    return QPixmap::fromImage(img);
}

QColor menuHighlight(Appearance appearance)
{
    const QColor c(66, 116, 198);
    return appearance == Appearance::Graphite ? graphite(c) : c;
}

void paintSelection(QPainter *p, const QRectF &rect, Appearance appearance, qreal radius)
{
    auto c = [appearance](int r, int g, int b, int a = 255) {
        QColor col(r, g, b, a);
        return appearance == Appearance::Graphite ? graphite(col) : col;
    };
    p->save();
    p->setRenderHint(QPainter::Antialiasing, radius > 0);
    p->setPen(Qt::NoPen);
    QPainterPath shape;
    shape.addRoundedRect(rect, radius, radius);
    p->setClipPath(shape, Qt::IntersectClip);

    // fixed-height lens and glow (11px / 8px, as in the Plasma style) around a striped body,
    // so a tall icon tile and a menu row carry the same gel
    p->fillRect(rect, c(40, 108, 218));

    // pinstripes through the gel (same 4px rhythm as the window: 255, 238, 230, 238)
    const int rowDark[4] = {0, 44, 66, 44};
    for (qreal y = std::floor(rect.top()); y < rect.bottom(); y += 1.0) {
        const int row = (int(y) % 4 + 4) % 4;
        if (rowDark[row])
            p->fillRect(QRectF(rect.left(), y, rect.width(), 1.0), c(0, 26, 100, rowDark[row]));
        else
            p->fillRect(QRectF(rect.left(), y, rect.width(), 1.0), QColor(255, 255, 255, 34));
    }

    const qreal lensH = qMin<qreal>(11.0, rect.height() * 0.5);
    const QRectF lens(rect.left(), rect.top(), rect.width(), lensH);
    QLinearGradient lg(lens.topLeft(), lens.bottomLeft());
    lg.setColorAt(0.0, QColor(255, 255, 255, 170));
    lg.setColorAt(0.25, QColor(255, 255, 255, 105));
    lg.setColorAt(1.0, QColor(255, 255, 255, 30));
    p->fillRect(lens, lg);

    const qreal glowH = qMin<qreal>(8.0, rect.height() * 0.4);
    const QRectF glow(rect.left(), rect.bottom() - glowH, rect.width(), glowH);
    QLinearGradient gg(glow.topLeft(), glow.bottomLeft());
    gg.setColorAt(0.0, c(128, 202, 255, 0));
    gg.setColorAt(1.0, c(128, 202, 255, 200));
    p->fillRect(glow, gg);

    // fine rim: darker on top, a bright line just inside the bottom
    p->fillRect(QRectF(rect.left(), rect.top(), rect.width(), 1.0), c(24, 66, 160, 230));
    p->fillRect(QRectF(rect.left(), rect.bottom() - 2.0, rect.width(), 1.0), c(170, 225, 255, 150));
    p->fillRect(QRectF(rect.left(), rect.bottom() - 1.0, rect.width(), 1.0), c(40, 92, 180, 200));
    p->restore();
}
}
