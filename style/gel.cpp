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
        // sampled column of the selected "Fonts" tab
        Gel g;
        g.rimTop = QColor(0, 87, 174);
        g.rimBottom = QColor(40, 110, 190);
        g.body = stops({{0.0, QColor(120, 184, 236)}, {0.45, QColor(86, 178, 235)}, {0.70, QColor(124, 207, 255)}, {1.0, QColor(172, 240, 255)}});
        g.lens = stops({{0.0, QColor(170, 210, 238)}, {0.5, QColor(150, 199, 231)}, {1.0, QColor(160, 205, 236)}});
        return tint(g, appearance);
    }
    case GelKind::TabClear: {
        // sampled column of the unselected "Appearance" tab
        Gel g;
        g.rimTop = QColor(118, 118, 120);
        g.rimBottom = QColor(140, 140, 142);
        g.body = stops({{0.0, QColor(214, 214, 216)}, {0.45, QColor(198, 198, 200)}, {0.70, QColor(206, 206, 208)}, {1.0, QColor(226, 226, 228)}});
        g.lens = stops({{0.0, QColor(232, 232, 234)}, {0.5, QColor(224, 224, 226)}, {1.0, QColor(214, 214, 216)}});
        return g;
    }
    case GelKind::Thumb: {
        // sampled row across the 10.2 scroll thumb (lens on the left, glow on the right)
        Gel g;
        g.rimTop = QColor(25, 57, 116);
        g.rimBottom = QColor(72, 95, 120);
        g.body = stops({{0.0, QColor(110, 160, 222)}, {0.36, QColor(96, 155, 223)}, {0.50, QColor(110, 176, 244)}, {0.70, QColor(139, 206, 255)}, {0.90, QColor(178, 235, 255)}, {1.0, QColor(170, 214, 238)}});
        g.lens = stops({{0.0, QColor(170, 200, 238)}, {0.35, QColor(146, 190, 239)}, {1.0, QColor(139, 188, 244)}});
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
    {
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

    // body: deep blue under the lens, saturated in the middle, glowing cyan at the bottom
    QLinearGradient body(rect.topLeft(), rect.bottomLeft());
    body.setColorAt(0.00, c(74, 132, 222));
    body.setColorAt(0.48, c(38, 104, 214));
    body.setColorAt(0.52, c(44, 116, 226));
    body.setColorAt(0.80, c(84, 162, 246));
    body.setColorAt(1.00, c(128, 202, 255));
    p->fillRect(rect, body);

    // pinstripes through the gel (same 4px rhythm as the window: 255, 238, 230, 238)
    // light row lifted, the two middle rows darkened, so the stripes read clearly through the blue
    const int rowDark[4] = {0, 44, 66, 44};
    for (qreal y = std::floor(rect.top()); y < rect.bottom(); y += 1.0) {
        const int row = (int(y) % 4 + 4) % 4;
        if (rowDark[row])
            p->fillRect(QRectF(rect.left(), y, rect.width(), 1.0), c(0, 26, 100, rowDark[row]));
        else
            p->fillRect(QRectF(rect.left(), y, rect.width(), 1.0), QColor(255, 255, 255, 34));
    }

    // wet lens over the top half
    const QRectF lens(rect.left(), rect.top(), rect.width(), rect.height() * 0.48);
    QLinearGradient lg(lens.topLeft(), lens.bottomLeft());
    lg.setColorAt(0.0, QColor(255, 255, 255, 170));
    lg.setColorAt(0.25, QColor(255, 255, 255, 105));
    lg.setColorAt(1.0, QColor(255, 255, 255, 38));
    p->fillRect(lens, lg);

    // fine rim: darker on top, a bright line just inside the bottom
    p->fillRect(QRectF(rect.left(), rect.top(), rect.width(), 1.0), c(24, 66, 160, 230));
    p->fillRect(QRectF(rect.left(), rect.bottom() - 2.0, rect.width(), 1.0), c(170, 225, 255, 150));
    p->fillRect(QRectF(rect.left(), rect.bottom() - 1.0, rect.width(), 1.0), c(40, 92, 180, 200));
    p->restore();
}
}
