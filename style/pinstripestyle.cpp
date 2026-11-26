// SPDX-License-Identifier: GPL-2.0-or-later
//
// Pinstripe widget style. Measurements follow Apple's June 2002 Aqua Human Interface
// Guidelines (chapter 7, "Controls"); colours are sampled from that document's artwork.

#include <QPainterPath>

#include "pinstripestyle.h"

#include <QAbstractScrollArea>
#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QDialogButtonBox>
#include <QLabel>
#include <QLineEdit>
#include <QMenu>
#include <QPainter>
#include <QProgressBar>
#include <QPushButton>
#include <QRadioButton>
#include <QScrollBar>
#include <QSlider>
#include <QSpinBox>
#include <QStyleFactory>
#include <QStyleOption>
#include <QTabBar>
#include <QTimerEvent>
#include <QToolButton>
#include <QtMath>

#include <KWindowShadow>
#include <KWindowShadowTile>

#include <array>
#include <cmath>

namespace Pinstripe
{
namespace
{
// HIG, chapter 7
constexpr int ButtonHeight = 20; // push buttons, pop-up menus, combo boxes (fixed)
constexpr int ButtonEndCap = 14;
constexpr int ButtonMinWidth = 69; // OK / Cancel
constexpr int ShadowSpace = 2; // drop shadow below gel controls
constexpr int IndicatorSize = 18; // check box / radio button incl. shadow
constexpr int PopupTextInset = 9;
constexpr int PopupCapWidth = 20;
constexpr int TabHeight = 23;
constexpr int TabTextInset = 12;
constexpr int TabAccentBar = 6; // plus a 3px shadow drawn inside the pane
constexpr int TextFieldHeight = 22;
constexpr int ScrollBarWidth = 15;
constexpr int ScrollArrowLength = 16;
constexpr int SliderThumb = 15; // 15x15 round, 15x18 pointed
constexpr int SliderThumbPointed = 18;
constexpr int ProgressHeight = 16; // HIG Figure 7-27: large progress bar
constexpr int MenuItemHeight = 19;
constexpr int MenuSeparatorHeight = 12;
constexpr int LittleArrowsWidth = 13;
constexpr int LittleArrowsHeight = 23;

const QColor Ink(0, 0, 0);
const QColor GlyphInk(18, 20, 32);

bool windowActive(const QStyleOption *opt)
{
    return opt->state & QStyle::State_Active;
}

bool enabled(const QStyleOption *opt)
{
    return opt->state & QStyle::State_Enabled;
}

Gel popupBodyGel()
{
    // the white body of a pop-up menu button
    Gel g;
    g.rimTop = QColor(102, 102, 106);
    g.rimBottom = QColor(142, 142, 146);
    g.body = {{0.0, QColor(232, 232, 234)}, {0.45, QColor(226, 226, 229)}, {0.55, QColor(222, 223, 226)}, {0.85, QColor(240, 240, 242)}, {1.0, QColor(252, 252, 253)}};
    g.lens = {{0.0, QColor(255, 255, 255)}, {1.0, QColor(244, 244, 246)}};
    return g;
}

Gel trackGel()
{
    // light groove for progress bars
    Gel g;
    g.rimTop = QColor(130, 130, 134);
    g.rimBottom = QColor(170, 170, 174);
    g.body = {{0.0, QColor(206, 206, 210)}, {0.45, QColor(214, 214, 218)}, {0.55, QColor(226, 226, 230)}, {1.0, QColor(250, 250, 252)}};
    g.lens = {{0.0, QColor(248, 248, 250)}, {1.0, QColor(230, 230, 234)}};
    return g;
}

QColor alpha(QColor c, int a)
{
    c.setAlpha(a);
    return c;
}

// HIG chapter 10: small system font is 11pt next to the 13pt system font
QFont smallFont(const QFont &f)
{
    QFont s = f;
    if (f.pointSizeF() > 0)
        s.setPointSizeF(f.pointSizeF() * 11.0 / 13.0);
    else if (f.pixelSize() > 0)
        s.setPixelSize(qRound(f.pixelSize() * 11.0 / 13.0));
    return s;
}

// HIG chapter 10: the label font is 10pt (bevel button labels)
QFont labelFont(const QFont &f)
{
    QFont s = f;
    if (f.pointSizeF() > 0)
        s.setPointSizeF(f.pointSizeF() * 10.0 / 13.0);
    else if (f.pixelSize() > 0)
        s.setPixelSize(qRound(f.pixelSize() * 10.0 / 13.0));
    return s;
}

QFont widgetFont(const QWidget *w)
{
    return w ? w->font() : QApplication::font();
}

enum class Side { North, South, West, East };

Side tabSide(QTabBar::Shape shape)
{
    switch (shape) {
    case QTabBar::RoundedSouth:
    case QTabBar::TriangularSouth:
        return Side::South;
    case QTabBar::RoundedWest:
    case QTabBar::TriangularWest:
        return Side::West;
    case QTabBar::RoundedEast:
    case QTabBar::TriangularEast:
        return Side::East;
    default:
        return Side::North;
    }
}

bool vertical(Side s)
{
    return s == Side::West || s == Side::East;
}

// Traffic-light gels (same colours as the Oxygen Traffic Lights decoration)
void paintLight(QPainter *p, const QRectF &r, int kind, bool active, bool hover, bool pressed)
{
    static const QColor deep[3] = {QColor(176, 18, 10), QColor(194, 128, 0), QColor(44, 134, 18)};
    static const QColor mid[3] = {QColor(242, 70, 56), QColor(247, 193, 36), QColor(108, 203, 58)};
    static const QColor light[3] = {QColor(255, 184, 168), QColor(255, 242, 176), QColor(216, 248, 168)};
    static const QColor rim[3] = {QColor(128, 12, 6), QColor(140, 90, 0), QColor(29, 90, 10)};
    p->save();
    p->setRenderHint(QPainter::Antialiasing, true);
    const QPointF c = r.center();
    const qreal rad = qMin(r.width(), r.height()) / 2.0 - 0.5;
    QColor d = deep[kind], m = mid[kind], l = light[kind], rm = rim[kind];
    if (!active && !hover) {
        // inactive windows show hollow grey gels
        d = QColor(160, 160, 164);
        m = QColor(214, 214, 218);
        l = QColor(250, 250, 252);
        rm = QColor(120, 120, 124);
    }
    if (pressed) {
        d = d.darker(130);
        m = m.darker(125);
    }
    p->setBrush(QColor(0, 0, 0, 30));
    p->setPen(Qt::NoPen);
    p->drawEllipse(c + QPointF(0, 0.8), rad, rad);
    QRadialGradient body(c + QPointF(0, rad * 0.55), rad * 1.45);
    body.setColorAt(0.0, l);
    body.setColorAt(0.45, m);
    body.setColorAt(1.0, d);
    p->setBrush(body);
    p->setPen(QPen(rm, 1.0));
    p->drawEllipse(c, rad, rad);
    QLinearGradient lens(QPointF(c.x(), c.y() - rad), QPointF(c.x(), c.y()));
    lens.setColorAt(0, QColor(255, 255, 255, 240));
    lens.setColorAt(1, QColor(255, 255, 255, 30));
    p->setPen(Qt::NoPen);
    p->setBrush(lens);
    p->drawEllipse(QRectF(c.x() - rad * 0.68, c.y() - rad * 0.92, rad * 1.36, rad * 0.9));
    if (hover) {
        p->setPen(QPen(QColor(60, 10, 0, 200), qMax(1.0, rad * 0.22), Qt::SolidLine, Qt::RoundCap));
        const qreal g = rad * 0.45;
        if (kind == 0) {
            p->drawLine(c + QPointF(-g * 0.8, -g * 0.8), c + QPointF(g * 0.8, g * 0.8));
            p->drawLine(c + QPointF(g * 0.8, -g * 0.8), c + QPointF(-g * 0.8, g * 0.8));
        } else {
            p->drawLine(c + QPointF(-g, 0), c + QPointF(g, 0));
            if (kind == 2)
                p->drawLine(c + QPointF(0, -g), c + QPointF(0, g));
        }
    }
    p->restore();
}

// 10.2 title bar: pinstripes darkening towards the bottom, a dark line below
void paintTitleBar(QPainter *p, const QRect &r, bool active)
{
    p->save();
    for (int y = r.top(); y <= r.bottom(); ++y) {
        const int rows[4] = {255, 238, 230, 238};
        int v = rows[(y - r.top()) % 4] - (r.height() > 1 ? 26 * (y - r.top()) / (r.height() - 1) : 0);
        if (!active)
            v = 240 + (v - 240) / 2;
        p->fillRect(QRect(r.left(), y, r.width(), 1), QColor(v, v, v));
    }
    p->fillRect(QRect(r.left(), r.bottom(), r.width(), 1), active ? QColor(127, 127, 127) : QColor(160, 160, 160));
    p->restore();
}

// Aqua bevel button (HIG Figures 7-14, 7-15): a curved glass cushion with a crisp top specular
// lens, cool silver mid-tone dip, bright white bottom reflection, and dark charcoal bottom rim.
// Pressed or toggled on, it becomes a smoked-grey glass cushion that keeps its lens and glow.
void paintBevel(QPainter *p, const QRectF &rect, bool down, qreal radius = 4.5)
{
    p->save();
    p->setRenderHint(QPainter::Antialiasing, true);
    const QRectF r = rect.adjusted(0.5, 0.5, -0.5, -1.5);
    p->setPen(Qt::NoPen);
    p->setBrush(QColor(0, 0, 0, 16));
    p->drawRoundedRect(r.translated(0, 2.0).adjusted(-0.3, 0, 0.3, 0), radius + 0.3, radius + 0.3);
    p->setBrush(QColor(0, 0, 0, 38));
    p->drawRoundedRect(r.translated(0, 1.0), radius, radius);

    QLinearGradient face(r.topLeft(), r.bottomLeft());
    if (down) {
        face.setColorAt(0.00, QColor(192, 195, 202));
        face.setColorAt(0.26, QColor(184, 188, 196));
        face.setColorAt(0.32, QColor(166, 170, 178));
        face.setColorAt(0.65, QColor(172, 176, 184));
        face.setColorAt(0.88, QColor(192, 196, 203));
        face.setColorAt(1.00, QColor(208, 212, 218));
    } else {
        face.setColorAt(0.00, QColor(236, 238, 243));
        face.setColorAt(0.26, QColor(228, 231, 238));
        face.setColorAt(0.32, QColor(216, 220, 228));
        face.setColorAt(0.62, QColor(226, 229, 235));
        face.setColorAt(0.86, QColor(244, 246, 249));
        face.setColorAt(1.00, QColor(255, 255, 255));
    }
    QPainterPath clip;
    clip.addRoundedRect(r, radius, radius);
    p->setBrush(face);
    p->drawPath(clip);

    p->save();
    p->setClipPath(clip, Qt::IntersectClip);
    // curved glass pillow shading along the left and right edges
    {
        QLinearGradient sides(r.topLeft(), r.topRight());
        const QColor edge = down ? QColor(86, 92, 106, 62) : QColor(150, 158, 174, 58);
        const QColor mid(edge.red(), edge.green(), edge.blue(), 0);
        const qreal w = qMax<qreal>(1.0, r.width());
        const qreal e = qMin<qreal>(0.18, 6.0 / w);
        sides.setColorAt(0.0, edge);
        sides.setColorAt(e, mid);
        sides.setColorAt(1.0 - e, mid);
        sides.setColorAt(1.0, edge);
        p->setBrush(sides);
        p->drawRect(r);
    }
    // upward bounce reflection at the bottom of the glass cushion
    {
        QRadialGradient glow(QPointF(r.center().x(), r.bottom()), qMax(r.width() * 0.58, r.height() * 0.45));
        glow.setColorAt(0.0, down ? QColor(238, 242, 250, 155) : QColor(255, 255, 255, 235));
        glow.setColorAt(0.55, down ? QColor(238, 242, 250, 55) : QColor(255, 255, 255, 110));
        glow.setColorAt(1.0, QColor(255, 255, 255, 0));
        p->setBrush(glow);
        p->drawRect(QRectF(r.left(), r.center().y(), r.width(), r.height() * 0.5));
    }
    // rounded top specular lens with a crisp lower edge
    {
        const qreal lensH = qBound<qreal>(5.0, r.height() * 0.30, 11.0);
        const qreal inset = qMin<qreal>(2.5, r.width() * 0.12);
        const QRectF lens(r.left() + inset, r.top() + 0.8, r.width() - 2 * inset, lensH);
        QLinearGradient lg(lens.topLeft(), lens.bottomLeft());
        if (down) {
            lg.setColorAt(0.0, QColor(240, 244, 250, 215));
            lg.setColorAt(0.6, QColor(216, 220, 228, 155));
            lg.setColorAt(1.0, QColor(198, 202, 210, 95));
        } else {
            lg.setColorAt(0.0, QColor(255, 255, 255, 248));
            lg.setColorAt(0.58, QColor(250, 251, 254, 215));
            lg.setColorAt(1.0, QColor(242, 245, 250, 165));
        }
        p->setBrush(lg);
        const qreal lr = qMin(lensH * 0.5, qMax<qreal>(1.5, radius - 1.0));
        p->drawRoundedRect(lens, lr, lr);
    }
    p->restore();

    QLinearGradient rim(r.topLeft(), r.bottomLeft());
    rim.setColorAt(0.0, down ? QColor(104, 106, 112) : QColor(152, 154, 160));
    rim.setColorAt(0.8, down ? QColor(88, 90, 96) : QColor(124, 126, 132));
    rim.setColorAt(1.0, down ? QColor(74, 76, 82) : QColor(82, 84, 90));
    p->setPen(QPen(QBrush(rim), 1.0));
    p->setBrush(Qt::NoBrush);
    p->drawPath(clip);
    p->restore();
}
}

Style::Style(Appearance appearance)
    : QProxyStyle(QStyleFactory::create(QStringLiteral("Fusion")))
    , m_appearance(appearance)
{
    setObjectName(appearance == Appearance::Graphite ? QStringLiteral("Pinstripe Graphite") : QStringLiteral("Pinstripe"));
}

Gel Style::coloredGel() const
{
    return gel(GelKind::Colored, m_appearance);
}

Gel Style::buttonGel(const QStyleOption *opt, bool isDefault, bool sunken) const
{
    if (sunken)
        return gel(GelKind::Pressed, m_appearance);
    if (isDefault && windowActive(opt) && enabled(opt)) {
        // the default button pulses between full colour and a paler, brighter colour
        const qreal t = 0.5 - 0.5 * qCos(m_phase * 2 * M_PI / 1.7);
        Gel pale = mix(coloredGel(), gel(GelKind::Clear, m_appearance), 0.55);
        return mix(coloredGel(), pale, t * 0.75);
    }
    return gel(GelKind::Clear, m_appearance);
}

// ---------------------------------------------------------------- polish

void Style::polish(QPalette &palette)
{
    QProxyStyle::polish(palette);
    // pinstripes only make sense on a light window colour
    const QColor window = palette.color(QPalette::Active, QPalette::Window);
    if (window.lightness() > 200) {
        for (auto group : {QPalette::Active, QPalette::Inactive, QPalette::Disabled}) {
            QBrush b(palette.color(group, QPalette::Window), windowStripes());
            palette.setBrush(group, QPalette::Window, b);
        }
    }
}

void Style::polish(QWidget *w)
{
    QProxyStyle::polish(w);
    if (qobject_cast<QPushButton *>(w) || qobject_cast<QCheckBox *>(w) || qobject_cast<QRadioButton *>(w) || qobject_cast<QComboBox *>(w)
        || qobject_cast<QAbstractSpinBox *>(w) || qobject_cast<QSlider *>(w) || qobject_cast<QScrollBar *>(w) || qobject_cast<QTabBar *>(w)
        || qobject_cast<QToolButton *>(w)) {
        w->setAttribute(Qt::WA_Hover);
    }
    if (qobject_cast<QMenu *>(w)) {
        w->setAttribute(Qt::WA_TranslucentBackground);
    }
    if (qobject_cast<QPushButton *>(w) || qobject_cast<QProgressBar *>(w)) {
        m_animated.append(w);
        updateAnimationTimer();
    }
    // menus, help tags and pop-up lists cast the soft Aqua drop shadow
    if (qobject_cast<QMenu *>(w) || w->inherits("QTipLabel") || w->inherits("QComboBoxPrivateContainer"))
        w->installEventFilter(this);
    // help tags use the small system font (HIG chapter 10) and 6px horizontal padding (Figure 14-1)
    if (w->inherits("QTipLabel")) {
        w->setFont(smallFont(w->font()));
        w->setContentsMargins(4, 0, 4, 0);
    }
    // alerts: message in the emphasized system font, informative text in the small system font
    if (auto *label = qobject_cast<QLabel *>(w)) {
        if (label->objectName() == QLatin1String("qt_msgbox_label")) {
            QFont f = label->font();
            f.setBold(true);
            label->setFont(f);
        } else if (label->objectName() == QLatin1String("qt_msgbox_informativelabel")) {
            label->setFont(smallFont(label->font()));
        }
    }
}

void Style::unpolish(QWidget *w)
{
    m_animated.removeAll(w);
    w->removeEventFilter(this);
    removeShadow(w);
    if (qobject_cast<QMenu *>(w))
        w->setAttribute(Qt::WA_TranslucentBackground, false);
    QProxyStyle::unpolish(w);
}

void Style::updateAnimationTimer()
{
    m_animated.removeAll(nullptr);
    if (m_animated.isEmpty())
        m_timer.stop();
    else if (!m_timer.isActive())
        m_timer.start(40, this);
}

namespace
{
// Soft drop shadow, heavier below (offset 3px down), as under 10.2 menus and windows.
constexpr int ShadowSize = 14;
constexpr int ShadowOffset = 3;

std::array<KWindowShadowTile::Ptr, 8> shadowTiles()
{
    static std::array<KWindowShadowTile::Ptr, 8> tiles;
    if (tiles[0])
        return tiles;
    const int n = 2 * ShadowSize + 1;
    QImage img(n, n, QImage::Format_ARGB32_Premultiplied);
    img.fill(Qt::transparent);
    const double sigma = ShadowSize / 2.6;
    for (int y = 0; y < n; ++y) {
        for (int x = 0; x < n; ++x) {
            const double dx = std::abs(x - ShadowSize);
            const double dy = std::abs(y - (ShadowSize + ShadowOffset));
            const double d2 = dx * dx + dy * dy;
            const int a = qBound(0, int(std::lround(92.0 * std::exp(-d2 / (2 * sigma * sigma)))), 255);
            img.setPixel(x, y, qPremultiply(qRgba(0, 0, 0, a)));
        }
    }
    const int s = ShadowSize;
    const QRect rects[8] = {QRect(0, 0, s, s), QRect(s, 0, 1, s), QRect(s + 1, 0, s, s), QRect(s + 1, s, s, 1),
                            QRect(s + 1, s + 1, s, s), QRect(s, s + 1, 1, s), QRect(0, s + 1, s, s), QRect(0, s, s, 1)};
    for (int i = 0; i < 8; ++i) {
        tiles[i] = KWindowShadowTile::Ptr::create();
        tiles[i]->setImage(img.copy(rects[i]));
    }
    return tiles;
}
}

void Style::installShadow(QWidget *w)
{
    if (!w->windowHandle() || m_shadows.contains(w))
        return;
    const auto t = shadowTiles();
    auto *shadow = new KWindowShadow(w);
    shadow->setTopLeftTile(t[0]);
    shadow->setTopTile(t[1]);
    shadow->setTopRightTile(t[2]);
    shadow->setRightTile(t[3]);
    shadow->setBottomRightTile(t[4]);
    shadow->setBottomTile(t[5]);
    shadow->setBottomLeftTile(t[6]);
    shadow->setLeftTile(t[7]);
    shadow->setPadding(QMargins(ShadowSize, ShadowSize, ShadowSize, ShadowSize));
    shadow->setWindow(w->windowHandle());
    if (shadow->create())
        m_shadows.insert(w, shadow);
    else
        delete shadow;
}

void Style::removeShadow(QWidget *w)
{
    if (auto *shadow = m_shadows.take(w))
        delete shadow;
}

bool Style::eventFilter(QObject *obj, QEvent *event)
{
    if (auto *w = qobject_cast<QWidget *>(obj)) {
        if (event->type() == QEvent::Show)
            installShadow(w);
        else if (event->type() == QEvent::Hide || event->type() == QEvent::Destroy)
            removeShadow(w);
    }
    return QProxyStyle::eventFilter(obj, event);
}

void Style::timerEvent(QTimerEvent *event)
{
    if (event->timerId() != m_timer.timerId()) {
        QProxyStyle::timerEvent(event);
        return;
    }
    m_phase += 0.04;
    m_animated.removeAll(nullptr);
    for (const auto &w : std::as_const(m_animated)) {
        if (!w->isVisible())
            continue;
        if (auto b = qobject_cast<QPushButton *>(w.data())) {
            if ((b->isDefault() || (b->autoDefault() && b->hasFocus())) && b->isEnabled() && b->isActiveWindow() && !b->isDown())
                b->update();
        } else if (auto pb = qobject_cast<QProgressBar *>(w.data())) {
            if (pb->isEnabled() && (pb->maximum() == pb->minimum() || pb->value() > pb->minimum()))
                pb->update();
        }
    }
    if (m_animated.isEmpty())
        m_timer.stop();
}

// ---------------------------------------------------------------- helpers

void Style::paintGelPath(QPainter *p, const QPainterPath &path, const QRectF &r, const Gel &g, Qt::Orientation o, bool shadow, const QPainterPath *rimPath) const
{
    p->save();
    p->setRenderHint(QPainter::Antialiasing, true);
    p->setPen(Qt::NoPen);
    if (shadow) {
        p->setBrush(QColor(0, 0, 0, 34));
        p->drawPath(path.translated(0, 1));
        p->setBrush(QColor(0, 0, 0, 14));
        p->drawPath(path.translated(0, 2));
    }
    const bool vertical = o == Qt::Vertical;
    QLinearGradient body(r.topLeft(), vertical ? r.topRight() : r.bottomLeft());
    body.setStops(g.body);
    p->setBrush(body);
    p->drawPath(path);

    p->setClipPath(path, Qt::IntersectClip);
    const qreal th = vertical ? r.width() : r.height();
    const qreal lensTh = qMin<qreal>(th * 0.32, 7.5);
    QRectF lens = vertical ? QRectF(r.left() + 1, r.top() + 2.5, lensTh, r.height() - 5) : QRectF(r.left() + 2.5, r.top() + 1, r.width() - 5, lensTh);
    QLinearGradient lg(lens.topLeft(), vertical ? lens.topRight() : lens.bottomLeft());
    lg.setStops(g.lens);
    p->setBrush(lg);
    const qreal lr = lensTh * 0.45;
    p->drawRoundedRect(lens, lr, lr);
    p->setClipping(false);

    QLinearGradient rim(r.topLeft(), vertical ? r.topRight() : r.bottomLeft());
    rim.setColorAt(0, g.rimTop);
    rim.setColorAt(1, g.rimBottom);
    p->setBrush(Qt::NoBrush);
    p->setPen(QPen(QBrush(rim), 1.0));
    p->drawPath(rimPath ? *rimPath : path);
    p->restore();
}

void Style::drawArrow(QPainter *p, const QRectF &r, Qt::ArrowType type, const QColor &c) const
{
    // solid Aqua triangles, 7px across
    p->save();
    p->setRenderHint(QPainter::Antialiasing, true);
    p->setPen(Qt::NoPen);
    p->setBrush(c);
    const QPointF ctr = r.center();
    const qreal s = qMin<qreal>(7.0, qMin(r.width(), r.height()) - 2) / 2.0;
    QPolygonF poly;
    switch (type) {
    case Qt::UpArrow:
        poly << QPointF(ctr.x() - s, ctr.y() + s * 0.6) << QPointF(ctr.x() + s, ctr.y() + s * 0.6) << QPointF(ctr.x(), ctr.y() - s * 0.75);
        break;
    case Qt::DownArrow:
        poly << QPointF(ctr.x() - s, ctr.y() - s * 0.6) << QPointF(ctr.x() + s, ctr.y() - s * 0.6) << QPointF(ctr.x(), ctr.y() + s * 0.75);
        break;
    case Qt::LeftArrow:
        poly << QPointF(ctr.x() + s * 0.6, ctr.y() - s) << QPointF(ctr.x() + s * 0.6, ctr.y() + s) << QPointF(ctr.x() - s * 0.75, ctr.y());
        break;
    case Qt::RightArrow:
    default:
        poly << QPointF(ctr.x() - s * 0.6, ctr.y() - s) << QPointF(ctr.x() - s * 0.6, ctr.y() + s) << QPointF(ctr.x() + s * 0.75, ctr.y());
        break;
    }
    p->drawPolygon(poly);
    p->restore();
}

void Style::drawTextField(const QRect &rect, const QStyleOption *opt, QPainter *p, bool focus) const
{
    // HIG: 22px field, white, with a 3px shadow inside the box; blue focus ring.
    p->save();
    p->setRenderHint(QPainter::Antialiasing, false);
    const QRect r = rect.adjusted(2, 2, -2, -2);
    if (focus && enabled(opt)) {
        p->setRenderHint(QPainter::Antialiasing, true);
        const QColor ring = m_appearance == Appearance::Graphite ? QColor(130, 140, 160) : QColor(94, 146, 228);
        p->setPen(QPen(alpha(ring, 120), 3.0));
        p->setBrush(Qt::NoBrush);
        p->drawRoundedRect(QRectF(r).adjusted(-0.5, -0.5, 0.5, 0.5), 2, 2);
        p->setPen(QPen(alpha(ring, 200), 1.2));
        p->drawRoundedRect(QRectF(r).adjusted(-0.6, -0.6, 0.6, 0.6), 1.5, 1.5);
        p->setRenderHint(QPainter::Antialiasing, false);
    }
    p->fillRect(r, opt->palette.brush(QPalette::Base));
    // inner shadow
    QLinearGradient top(r.topLeft(), r.topLeft() + QPoint(0, 3));
    top.setColorAt(0, QColor(0, 0, 0, 52));
    top.setColorAt(1, QColor(0, 0, 0, 0));
    p->fillRect(QRect(r.left(), r.top(), r.width(), 3), top);
    p->fillRect(QRect(r.left(), r.top(), 1, r.height()), QColor(0, 0, 0, 14));
    p->fillRect(QRect(r.right(), r.top(), 1, r.height()), QColor(0, 0, 0, 14));
    // border: darker on top, as in the HIG artwork
    p->setPen(QColor(112, 112, 116));
    p->drawLine(r.topLeft(), r.topRight());
    p->setPen(QColor(158, 158, 162));
    p->drawLine(r.topLeft() + QPoint(0, 1), r.bottomLeft());
    p->drawLine(r.topRight() + QPoint(0, 1), r.bottomRight());
    p->setPen(QColor(184, 184, 188));
    p->drawLine(r.bottomLeft() + QPoint(1, 0), r.bottomRight() - QPoint(1, 0));
    p->restore();
}

void Style::drawLittleArrows(const QRect &r, const QStyleOption *opt, QPainter *p, bool upPressed, bool downPressed, bool upEnabled, bool downEnabled) const
{
    // HIG "little arrows": a 13x23 capsule split in two
    const QRectF cap(r.center().x() - LittleArrowsWidth / 2.0 + 0.5, r.center().y() - LittleArrowsHeight / 2.0 + 0.5, LittleArrowsWidth - 1, LittleArrowsHeight - 2);
    GelOptions o;
    o.radius = 6.0;
    o.lensInset = 1.5;
    o.lensHeight = 0.22;
    paintGel(p, cap, gel(GelKind::Clear, m_appearance), o);
    p->save();
    p->setRenderHint(QPainter::Antialiasing, true);
    QPainterPath clip;
    clip.addRoundedRect(cap.adjusted(1, 1, -1, -1), 5, 5);
    p->setClipPath(clip);
    const QRectF up(cap.left(), cap.top(), cap.width(), cap.height() / 2.0);
    const QRectF down(cap.left(), cap.center().y(), cap.width(), cap.height() / 2.0);
    if (upPressed)
        p->fillRect(up, QColor(0, 0, 60, 60));
    if (downPressed)
        p->fillRect(down, QColor(0, 0, 60, 60));
    p->setClipping(false);
    p->setPen(QPen(QColor(110, 110, 116), 1.0));
    p->drawLine(QPointF(cap.left() + 1, cap.center().y()), QPointF(cap.right() - 1, cap.center().y()));
    p->restore();
    const QColor ink = enabled(opt) ? GlyphInk : QColor(150, 150, 150);
    drawArrow(p, up.adjusted(2, 2, -2, 0), Qt::UpArrow, upEnabled ? ink : QColor(160, 160, 160));
    drawArrow(p, down.adjusted(2, 0, -2, -2), Qt::DownArrow, downEnabled ? ink : QColor(160, 160, 160));
}

// ---------------------------------------------------------------- primitives

void Style::drawPrimitive(PrimitiveElement pe, const QStyleOption *opt, QPainter *p, const QWidget *w) const
{
    switch (pe) {
    case PE_IndicatorCheckBox:
    case PE_IndicatorRadioButton: {
        const bool radio = pe == PE_IndicatorRadioButton;
        const bool on = opt->state & State_On;
        const bool tri = opt->state & State_NoChange;
        const bool sunken = opt->state & State_Sunken;
        const QRectF box(opt->rect.x() + (opt->rect.width() - 14) / 2.0, opt->rect.y() + (opt->rect.height() - 16) / 2.0, 14, 14);
        Gel g = (on || tri) ? (windowActive(opt) ? coloredGel() : gel(GelKind::Clear, m_appearance)) : gel(GelKind::Clear, m_appearance);
        if (sunken)
            g = gel(GelKind::Pressed, m_appearance);
        GelOptions o;
        o.radius = radio ? -1 : 3.0;
        o.lensInset = radio ? 2.5 : 1.5;
        o.lensHeight = 0.46;
        p->save();
        if (!enabled(opt))
            p->setOpacity(0.5);
        paintGel(p, box, g, o);
        p->setRenderHint(QPainter::Antialiasing, true);
        if (radio && (on || tri)) {
            p->setPen(Qt::NoPen);
            p->setBrush(GlyphInk);
            p->drawEllipse(box.center() + QPointF(0, 0.3), 2.6, 2.6);
        } else if (tri) {
            p->setPen(QPen(GlyphInk, 2.2, Qt::SolidLine, Qt::RoundCap));
            p->drawLine(QPointF(box.left() + 4, box.center().y()), QPointF(box.right() - 4, box.center().y()));
        } else if (on) {
            // the Aqua check overshoots the box at the top right
            QPainterPath check;
            check.moveTo(box.left() + 3.2, box.top() + 7.2);
            check.lineTo(box.left() + 6.3, box.top() + 11.4);
            check.cubicTo(box.left() + 8.0, box.top() + 6.0, box.left() + 10.5, box.top() + 1.5, box.left() + 15.5, box.top() - 2.2);
            p->setPen(QPen(GlyphInk, 1.9, Qt::SolidLine, Qt::RoundCap, Qt::RoundJoin));
            p->setBrush(Qt::NoBrush);
            p->drawPath(check);
        }
        p->restore();
        return;
    }

    case PE_PanelButtonCommand:
    case PE_PanelButtonBevel: {
        paintBevel(p, QRectF(opt->rect), opt->state & (State_Sunken | State_On));
        return;
    }

    case PE_PanelButtonTool: {
        const bool sunken = opt->state & (State_Sunken | State_On);
        const bool autoRaise = opt->state & State_AutoRaise;
        if (autoRaise) {
            // toolbar items have no frame in Aqua; only darken while pressed
            if (sunken) {
                p->save();
                p->setRenderHint(QPainter::Antialiasing, true);
                p->setPen(Qt::NoPen);
                p->setBrush(QColor(0, 0, 0, 46));
                p->drawRoundedRect(QRectF(opt->rect).adjusted(1, 1, -1, -1), 4, 4);
                p->restore();
            }
            return;
        }
        paintBevel(p, QRectF(opt->rect), sunken);
        return;
    }

    case PE_FrameDefaultButton:
    case PE_FrameButtonBevel:
    case PE_FrameButtonTool:
        return;

    case PE_FrameFocusRect:
        // Aqua shows keyboard focus with a ring on text fields and lists only
        return;

    case PE_PanelLineEdit: {
        const auto *f = qstyleoption_cast<const QStyleOptionFrame *>(opt);
        if (w && (qobject_cast<const QAbstractSpinBox *>(w->parentWidget()) || qobject_cast<const QComboBox *>(w->parentWidget()))) {
            p->fillRect(opt->rect, opt->palette.brush(QPalette::Base));
            return;
        }
        if (f && f->lineWidth > 0)
            drawTextField(opt->rect, opt, p, opt->state & State_HasFocus);
        else
            p->fillRect(opt->rect, opt->palette.brush(QPalette::Base));
        return;
    }
    case PE_FrameLineEdit:
        return;

    case PE_Frame:
    case PE_FrameWindow: {
        // list and text view frames: a fine grey line, darker on top
        p->save();
        const QRect r = opt->rect.adjusted(0, 0, -1, -1);
        p->setPen(QColor(150, 150, 154));
        p->drawRect(r);
        p->setPen(QColor(118, 118, 122));
        p->drawLine(r.topLeft(), r.topRight());
        p->restore();
        return;
    }

    case PE_FrameGroupBox: {
        // 10.2 group box: a fine etched line (grey, with white just inside), square corners,
        // on the same pinstripes as the window (HIG Figures 8-2 to 8-4)
        p->save();
        const QRect r = opt->rect.adjusted(0, 0, -1, -1);
        p->setPen(QColor(0, 0, 0, 62));
        p->setBrush(Qt::NoBrush);
        p->drawRect(r.adjusted(0, 0, -1, -1));
        p->setPen(QColor(255, 255, 255, 200));
        p->drawRect(r.adjusted(1, 1, 0, 0));
        p->restore();
        return;
    }

    case PE_FrameTabWidget: {
        const auto *tw = qstyleoption_cast<const QStyleOptionTabWidgetFrame *>(opt);
        if (!tw)
            break;
        // blue accent bar along the tabs' side, then the pane with a soft inner shadow
        const Side side = tabSide(tw->shape);
        const QRect r = opt->rect;
        QRect bar, pane;
        switch (side) {
        case Side::North:
            bar = QRect(r.left(), r.top(), r.width(), TabAccentBar);
            pane = r.adjusted(0, TabAccentBar, 0, 0);
            break;
        case Side::South:
            bar = QRect(r.left(), r.bottom() - TabAccentBar + 1, r.width(), TabAccentBar);
            pane = r.adjusted(0, 0, 0, -TabAccentBar);
            break;
        case Side::West:
            bar = QRect(r.left(), r.top(), TabAccentBar, r.height());
            pane = r.adjusted(TabAccentBar, 0, 0, 0);
            break;
        case Side::East:
            bar = QRect(r.right() - TabAccentBar + 1, r.top(), TabAccentBar, r.height());
            pane = r.adjusted(0, 0, -TabAccentBar, 0);
            break;
        }
        p->save();
        p->fillRect(pane.adjusted(1, 1, -1, -1), QColor(0, 0, 0, 8));
        QPoint from = side == Side::North ? pane.topLeft() : side == Side::South ? pane.bottomLeft() : side == Side::West ? pane.topLeft() : pane.topRight();
        QPoint dir = side == Side::North ? QPoint(0, 6) : side == Side::South ? QPoint(0, -6) : side == Side::West ? QPoint(6, 0) : QPoint(-6, 0);
        QLinearGradient sh(from, from + dir);
        sh.setColorAt(0, QColor(0, 0, 0, 40));
        sh.setColorAt(1, QColor(0, 0, 0, 0));
        p->fillRect(pane.adjusted(1, 1, -1, -1), sh);
        p->setPen(QColor(0, 0, 0, 52));
        p->setBrush(Qt::NoBrush);
        p->drawRect(pane.adjusted(0, 0, -1, -1));
        // accent bar rows measured from HIG Figure 7-23 (outer edge first), then a grey shadow
        static const QColor blueRows[6] = {QColor(0, 87, 174), QColor(162, 215, 240), QColor(168, 209, 238), QColor(81, 176, 234), QColor(121, 204, 255), QColor(172, 239, 255)};
        static const QColor shadowRows[3] = {QColor(98, 98, 98), QColor(147, 147, 147), QColor(226, 226, 226, 200)};
        const bool active = windowActive(opt);
        auto rowRect = [&](int i) {
            switch (side) {
            case Side::North:
                return QRect(bar.left(), bar.top() + i, bar.width(), 1);
            case Side::South:
                return QRect(bar.left(), bar.bottom() - i, bar.width(), 1);
            case Side::West:
                return QRect(bar.left() + i, bar.top(), 1, bar.height());
            case Side::East:
                default:
                return QRect(bar.right() - i, bar.top(), 1, bar.height());
            }
        };
        for (int i = 0; i < 6; ++i) {
            QColor c = blueRows[i];
            if (!active)
                c = graphite(c).lighter(115);
            else if (m_appearance == Appearance::Graphite)
                c = graphite(c);
            p->fillRect(rowRect(i), c);
        }
        for (int i = 0; i < 3; ++i)
            p->fillRect(rowRect(6 + i), shadowRows[i]);
        p->restore();
        return;
    }
    case PE_FrameTabBarBase: {
        // standalone QTabBar (not inside a QTabWidget): draw the 6-row Aqua accent bar along its base
        if (w && qobject_cast<const QTabWidget *>(w->parentWidget()))
            return;
        const auto *tbb = qstyleoption_cast<const QStyleOptionTabBarBase *>(opt);
        if (!tbb)
            return;
        const Side side = tabSide(tbb->shape);
        static const QColor blueRows[6] = {QColor(0, 87, 174), QColor(162, 215, 240), QColor(168, 209, 238), QColor(81, 176, 234), QColor(121, 204, 255), QColor(172, 239, 255)};
        const bool active = windowActive(opt);
        p->save();
        for (int i = 0; i < 6 && i < (vertical(side) ? opt->rect.width() : opt->rect.height()); ++i) {
            QColor c = blueRows[i];
            if (!active)
                c = graphite(c).lighter(115);
            else if (m_appearance == Appearance::Graphite)
                c = graphite(c);
            QRect rr;
            switch (side) {
            case Side::North: rr = QRect(opt->rect.left(), opt->rect.top() + i, opt->rect.width(), 1); break;
            case Side::South: rr = QRect(opt->rect.left(), opt->rect.bottom() - i, opt->rect.width(), 1); break;
            case Side::West: rr = QRect(opt->rect.left() + i, opt->rect.top(), 1, opt->rect.height()); break;
            case Side::East: rr = QRect(opt->rect.right() - i, opt->rect.top(), 1, opt->rect.height()); break;
            }
            p->fillRect(rr, c);
        }
        p->restore();
        return;
    }

    case PE_PanelMenu:
    case PE_FrameMenu: {
        if (pe == PE_FrameMenu)
            return;
        p->save();
        p->setRenderHint(QPainter::Antialiasing, true);
        const bool translucent = w && w->testAttribute(Qt::WA_TranslucentBackground);
        const qreal radius = translucent ? 5.0 : 0.0;
        p->setPen(QColor(0, 0, 0, 46));
        p->setBrush(QBrush(menuStripes(translucent ? 244 : 255)));
        p->drawRoundedRect(QRectF(opt->rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius);
        p->restore();
        return;
    }
    case PE_PanelMenuBar:
        return;

    case PE_PanelTipLabel: {
        p->save();
        p->fillRect(opt->rect, opt->palette.brush(QPalette::ToolTipBase));
        p->setPen(QColor(0, 0, 0, 90));
        p->drawRect(opt->rect.adjusted(0, 0, -1, -1));
        p->restore();
        return;
    }

    case PE_IndicatorArrowUp:
    case PE_IndicatorArrowDown:
    case PE_IndicatorArrowLeft:
    case PE_IndicatorArrowRight: {
        const Qt::ArrowType t = pe == PE_IndicatorArrowUp ? Qt::UpArrow : pe == PE_IndicatorArrowDown ? Qt::DownArrow : pe == PE_IndicatorArrowLeft ? Qt::LeftArrow : Qt::RightArrow;
        drawArrow(p, opt->rect, t, enabled(opt) ? opt->palette.color(QPalette::ButtonText) : QColor(150, 150, 150));
        return;
    }

    case PE_IndicatorBranch: {
        if (!(opt->state & State_Children))
            return;
        // disclosure triangle (HIG Figure 7-34): flat mid-grey, no outline
        p->save();
        p->setRenderHint(QPainter::Antialiasing, true);
        const QPointF c = QRectF(opt->rect).center();
        QPolygonF tri;
        if (opt->state & State_Open)
            tri << c + QPointF(-4.0, -2.2) << c + QPointF(4.0, -2.2) << c + QPointF(0, 3.2);
        else
            tri << c + QPointF(-2.2, -4.0) << c + QPointF(3.2, 0) << c + QPointF(-2.2, 4.0);
        p->setPen(Qt::NoPen);
        p->setBrush((opt->state & State_Selected) ? QColor(255, 255, 255) : QColor(122, 122, 124));
        p->drawPolygon(tri);
        p->restore();
        return;
    }

    case PE_IndicatorHeaderArrow: {
        const auto *h = qstyleoption_cast<const QStyleOptionHeader *>(opt);
        if (h)
            drawArrow(p, opt->rect, h->sortIndicator == QStyleOptionHeader::SortUp ? Qt::UpArrow : Qt::DownArrow, Ink);
        return;
    }

    case PE_PanelItemViewItem: {
        const auto *v = qstyleoption_cast<const QStyleOptionViewItem *>(opt);
        if (v && (v->state & State_Selected) && (v->state & State_Active)) {
            // selected rows get the glossy gel; inactive windows keep the scheme's flat colour
            QRectF r = v->rect;
            paintSelection(p, r, m_appearance);
            return;
        }
        break;
    }

    case PE_IndicatorToolBarHandle:
        return;
    case PE_IndicatorToolBarSeparator: {
        p->save();
        p->setPen(QPen(QColor(110, 110, 110), 1, Qt::DotLine));
        if (opt->state & State_Horizontal)
            p->drawLine(opt->rect.center().x(), opt->rect.top() + 4, opt->rect.center().x(), opt->rect.bottom() - 4);
        else
            p->drawLine(opt->rect.left() + 4, opt->rect.center().y(), opt->rect.right() - 4, opt->rect.center().y());
        p->restore();
        return;
    }

    default:
        break;
    }
    QProxyStyle::drawPrimitive(pe, opt, p, w);
}

// ---------------------------------------------------------------- controls

void Style::drawControl(ControlElement ce, const QStyleOption *opt, QPainter *p, const QWidget *w) const
{
    switch (ce) {
    case CE_PushButtonBevel: {
        const auto *b = qstyleoption_cast<const QStyleOptionButton *>(opt);
        if (!b)
            break;
        const bool sunken = b->state & (State_Sunken | State_On);
        if (b->features & QStyleOptionButton::Flat) {
            if (sunken)
                drawPrimitive(PE_PanelButtonTool, opt, p, w);
            return;
        }
        const bool isDefault = b->features & QStyleOptionButton::DefaultButton;
        const QRect r = b->rect;
        p->save();
        if (!enabled(opt))
            p->setOpacity(0.55);
        if (r.height() > ButtonHeight + ShadowSpace + 8) {
            // tall buttons become bevel buttons, as the HIG recommends (larger text or an icon)
            if (isDefault && windowActive(opt) && !sunken) {
                GelOptions o;
                o.radius = 5.0;
                o.lensInset = 4;
                paintGel(p, QRectF(r).adjusted(0.5, 0.5, -0.5, -2.5), buttonGel(opt, isDefault, sunken), o);
            } else {
                paintBevel(p, QRectF(r), sunken, 4.0);
            }
        } else {
            const qreal h = qMin<qreal>(ButtonHeight, r.height() - ShadowSpace);
            const QRectF capsule(r.left() + 0.5, r.top() + (r.height() - ShadowSpace - h) / 2.0, r.width() - 1, h);
            GelOptions o;
            o.lensInset = ButtonEndCap * 0.55;
            paintGel(p, capsule, buttonGel(opt, isDefault, sunken), o);
        }
        p->restore();
        return;
    }

    case CE_PushButtonLabel: {
        const auto *b = qstyleoption_cast<const QStyleOptionButton *>(opt);
        if (!b)
            break;
        QStyleOptionButton copy(*b);
        copy.palette.setColor(QPalette::ButtonText, enabled(opt) ? Ink : QColor(128, 128, 128));
        copy.rect.translate(0, -1); // centre on the 20px capsule, not the shadow
        QProxyStyle::drawControl(ce, &copy, p, w);
        return;
    }

    case CE_TabBarTabShape: {
        const auto *t = qstyleoption_cast<const QStyleOptionTab *>(opt);
        if (!t)
            break;
        const Side side = tabSide(t->shape);
        const bool selected = t->state & State_Selected;
        // PM_TabBarBaseOverlap is 1 so the selected tab extends over row 0 (#0057ae) of the accent
        // strip and morphs seamlessly into rows 1..5; unselected tabs step back 1px so the #0057ae
        // top rim runs continuously beneath them (HIG Figures 7-23, 8-2).
        QRect tr = t->rect;
        if (!selected) {
            switch (side) {
            case Side::North: tr.adjust(0, 0, 0, -1); break;
            case Side::South: tr.adjust(0, 1, 0, 0); break;
            case Side::West: tr.adjust(0, 0, -1, 0); break;
            case Side::East: tr.adjust(1, 0, 0, 0); break;
            }
        }
        QRectF r(tr);
        switch (side) {
        case Side::North: r.adjust(0.5, 0.5, -0.5, 0.0); break;
        case Side::South: r.adjust(0.5, 0.0, -0.5, -0.5); break;
        case Side::West: r.adjust(0.5, 0.5, 0.0, -0.5); break;
        case Side::East: r.adjust(0.0, 0.5, -0.5, -0.5); break;
        }
        // rounded corners on the side away from the pane; open on the pane side
        QPainterPath path;
        const qreal rad = 4.5;
        switch (side) {
        case Side::North:
            path.moveTo(r.bottomLeft());
            path.lineTo(r.left(), r.top() + rad);
            path.quadTo(r.left(), r.top(), r.left() + rad, r.top());
            path.lineTo(r.right() - rad, r.top());
            path.quadTo(r.right(), r.top(), r.right(), r.top() + rad);
            path.lineTo(r.bottomRight());
            break;
        case Side::South:
            path.moveTo(r.topLeft());
            path.lineTo(r.left(), r.bottom() - rad);
            path.quadTo(r.left(), r.bottom(), r.left() + rad, r.bottom());
            path.lineTo(r.right() - rad, r.bottom());
            path.quadTo(r.right(), r.bottom(), r.right(), r.bottom() - rad);
            path.lineTo(r.topRight());
            break;
        case Side::West:
            path.moveTo(r.topRight());
            path.lineTo(r.left() + rad, r.top());
            path.quadTo(r.left(), r.top(), r.left(), r.top() + rad);
            path.lineTo(r.left(), r.bottom() - rad);
            path.quadTo(r.left(), r.bottom(), r.left() + rad, r.bottom());
            path.lineTo(r.bottomRight());
            break;
        case Side::East:
            path.moveTo(r.topLeft());
            path.lineTo(r.right() - rad, r.top());
            path.quadTo(r.right(), r.top(), r.right(), r.top() + rad);
            path.lineTo(r.right(), r.bottom() - rad);
            path.quadTo(r.right(), r.bottom(), r.right() - rad, r.bottom());
            path.lineTo(r.bottomLeft());
            break;
        }
        QPainterPath rimPath = path; // open: no rim along the pane side
        path.closeSubpath();
        Gel g = gel(GelKind::TabClear, m_appearance);
        if (selected)
            g = windowActive(opt) ? gel(GelKind::TabSelected, m_appearance) : gel(GelKind::TabSelected, Appearance::Graphite);
        else if (t->state & State_Sunken)
            g = gel(GelKind::Pressed, m_appearance);
        if (side == Side::South || side == Side::East) {
            // keep the lens on the outer edge and the cyan merge at the accent-bar edge
            QGradientStops revBody, revLens;
            for (int i = g.body.size() - 1; i >= 0; --i)
                revBody.append({1.0 - g.body[i].first, g.body[i].second});
            for (int i = g.lens.size() - 1; i >= 0; --i)
                revLens.append({1.0 - g.lens[i].first, g.lens[i].second});
            g.body = revBody;
            g.lens = revLens;
            qSwap(g.rimTop, g.rimBottom);
            p->save();
            p->setRenderHint(QPainter::Antialiasing, true);
            p->setPen(Qt::NoPen);
            const bool vert = vertical(side);
            QLinearGradient body(r.topLeft(), vert ? r.topRight() : r.bottomLeft());
            body.setStops(g.body);
            p->setBrush(body);
            p->drawPath(path);
            p->setClipPath(path, Qt::IntersectClip);
            const qreal th = vert ? r.width() : r.height();
            const qreal lensTh = qMin<qreal>(th * 0.32, 7.5);
            const QRectF lens = vert ? QRectF(r.right() - 1 - lensTh, r.top() + 2.5, lensTh, r.height() - 5)
                                     : QRectF(r.left() + 2.5, r.bottom() - 1 - lensTh, r.width() - 5, lensTh);
            QLinearGradient lg(lens.topLeft(), vert ? lens.topRight() : lens.bottomLeft());
            lg.setStops(g.lens);
            p->setBrush(lg);
            p->drawRoundedRect(lens, lensTh * 0.45, lensTh * 0.45);
            p->setClipping(false);
            QLinearGradient rim(r.topLeft(), vert ? r.topRight() : r.bottomLeft());
            rim.setColorAt(0, g.rimTop);
            rim.setColorAt(1, g.rimBottom);
            p->setBrush(Qt::NoBrush);
            p->setPen(QPen(QBrush(rim), 1.0));
            p->drawPath(rimPath);
            p->restore();
            return;
        }
        paintGelPath(p, path, r, g, vertical(side) ? Qt::Vertical : Qt::Horizontal, false, &rimPath);
        return;
    }
    case CE_TabBarTabLabel: {
        const auto *t = qstyleoption_cast<const QStyleOptionTab *>(opt);
        if (!t)
            break;
        QStyleOptionTab copy(*t);
        copy.palette.setColor(QPalette::WindowText, enabled(opt) ? Ink : QColor(128, 128, 128));
        QProxyStyle::drawControl(ce, &copy, p, w);
        return;
    }

    case CE_ProgressBarGroove: {
        const QRect r = opt->rect;
        const QRectF bar(r.left() + 0.5, r.center().y() - ProgressHeight / 2.0 + 0.5, r.width() - 1, ProgressHeight - 1);
        GelOptions o;
        o.radius = 2.0;
        o.lensInset = 2;
        o.shadow = false;
        paintGel(p, bar, trackGel(), o);
        return;
    }
    case CE_ProgressBarContents: {
        const auto *pb = qstyleoption_cast<const QStyleOptionProgressBar *>(opt);
        if (!pb)
            break;
        const QRect r = opt->rect;
        const QRectF bar(r.left() + 0.5, r.center().y() - ProgressHeight / 2.0 + 0.5, r.width() - 1, ProgressHeight - 1);
        const bool busy = pb->minimum == 0 && pb->maximum == 0;
        // inactive windows show the bar in grey (HIG Figure 7-28, second row)
        const Gel fillGel = windowActive(opt) ? gel(GelKind::Progress, m_appearance) : mix(gel(GelKind::Progress, Appearance::Graphite), gel(GelKind::Clear, m_appearance), 0.35);
        GelOptions o;
        o.radius = 2.0;
        o.lensInset = 2;
        o.shadow = false;
        p->save();
        p->setRenderHint(QPainter::Antialiasing, true);
        QPainterPath clip;
        clip.addRoundedRect(bar, 2, 2);
        p->setClipPath(clip);
        if (busy) {
            // indeterminate: the barber pole
            paintGel(p, bar, fillGel, o);
            const qreal period = 16.0;
            const qreal offset = std::fmod(m_phase * 24.0, period);
            p->setPen(Qt::NoPen);
            p->setBrush(QColor(255, 255, 255, 170));
            for (qreal x = bar.left() - bar.height() - period + offset; x < bar.right() + period; x += period) {
                QPolygonF stripe;
                stripe << QPointF(x, bar.bottom()) << QPointF(x + period / 2, bar.bottom()) << QPointF(x + period / 2 + bar.height(), bar.top()) << QPointF(x + bar.height(), bar.top());
                p->drawPolygon(stripe);
            }
            p->setClipping(false);
            p->setBrush(Qt::NoBrush);
            p->setPen(QPen(coloredGel().rimTop, 1.0));
            p->drawRoundedRect(bar, 2, 2);
        } else {
            const qreal frac = pb->maximum > pb->minimum ? qreal(pb->progress - pb->minimum) / (pb->maximum - pb->minimum) : 0;
            if (frac > 0) {
                QRectF fill = bar;
                fill.setWidth(qMax(bar.height(), bar.width() * frac));
                if (pb->invertedAppearance)
                    fill.moveRight(bar.right());
                paintGel(p, fill, fillGel, o);
                // the moving light bands of the determinate bar
                p->setClipRect(fill.adjusted(1, 1, -1, -1), Qt::IntersectClip);
                const qreal period = 12.0;
                const qreal offset = std::fmod(m_phase * 16.0, period);
                for (qreal x = fill.left() - period + offset; x < fill.right(); x += period) {
                    QLinearGradient band(QPointF(x, 0), QPointF(x + period, 0));
                    band.setColorAt(0.0, QColor(255, 255, 255, 0));
                    band.setColorAt(0.5, QColor(255, 255, 255, 64));
                    band.setColorAt(1.0, QColor(255, 255, 255, 0));
                    p->fillRect(QRectF(x, fill.top(), period, fill.height()), band);
                }
            }
        }
        p->restore();
        return;
    }

    case CE_ProgressBarLabel: {
        const auto *pb = qstyleoption_cast<const QStyleOptionProgressBar *>(opt);
        if (!pb || !pb->textVisible || !(pb->state & State_Horizontal))
            break;
        p->save();
        p->setPen(enabled(opt) ? Ink : QColor(128, 128, 128));
        p->drawText(opt->rect, Qt::AlignVCenter | Qt::AlignRight, pb->text);
        p->restore();
        return;
    }

    case CE_MenuItem: {
        const auto *mi = qstyleoption_cast<const QStyleOptionMenuItem *>(opt);
        if (!mi)
            break;
        p->save();
        const QRect r = mi->rect;
        if (mi->menuItemType == QStyleOptionMenuItem::Separator) {
            // Aqua menus separate groups with blank space, not lines
            if (!mi->text.isEmpty()) {
                QFont f = mi->font;
                f.setBold(true);
                p->setFont(f);
                p->setPen(QColor(110, 110, 110));
                p->drawText(r.adjusted(20, 0, -8, 0), Qt::AlignVCenter | Qt::AlignLeft, mi->text);
            }
            p->restore();
            return;
        }
        const bool selected = (mi->state & State_Selected) && enabled(opt);
        QColor text = enabled(opt) ? Ink : QColor(150, 150, 150);
        if (selected) {
            paintSelection(p, r, m_appearance);
            text = Qt::white;
        }
        p->setPen(text);
        const int checkCol = 23; // 10.2 menus start their text ~23px in
        int x = r.left() + checkCol;
        if (mi->checkType != QStyleOptionMenuItem::NotCheckable && mi->checked) {
            QFont f = mi->font;
            p->setFont(f);
            p->drawText(QRect(r.left() + 4, r.top(), checkCol - 4, r.height()), Qt::AlignCenter, QStringLiteral("✓"));
        }
        if (mi->maxIconWidth > 0 && !mi->icon.isNull()) {
            const int is = qMin(16, r.height() - 2);
            const QIcon::Mode mode = !enabled(opt) ? QIcon::Disabled : selected ? QIcon::Selected : QIcon::Normal;
            mi->icon.paint(p, QRect(x, r.top() + (r.height() - is) / 2, is, is), Qt::AlignCenter, mode);
        }
        if (mi->maxIconWidth > 0)
            x += qMin(16, mi->maxIconWidth) + 6;
        QString label = mi->text;
        QString shortcut;
        const int tab = label.indexOf(QLatin1Char('\t'));
        if (tab >= 0) {
            shortcut = label.mid(tab + 1);
            label = label.left(tab);
        }
        p->setFont(mi->font);
        const int rightPad = mi->menuItemType == QStyleOptionMenuItem::SubMenu ? 22 : 14;
        p->drawText(QRect(x, r.top(), r.right() - x - rightPad, r.height()), Qt::AlignVCenter | Qt::AlignLeft | Qt::TextShowMnemonic, label);
        if (!shortcut.isEmpty()) {
            // 10.2 shortcut column: modifier symbols right-aligned against the key, keys in a
            // left-aligned column (Ctrl is shown as the Control symbol, which is what it is)
            QString mods, key = shortcut;
            const QStringList parts = shortcut.split(QLatin1Char('+'));
            if (parts.size() > 1 && !parts.last().isEmpty()) {
                key = parts.last();
                const QString order[4][2] = {{QStringLiteral("Ctrl"), QStringLiteral("⌃")}, {QStringLiteral("Alt"), QStringLiteral("⌥")},
                                             {QStringLiteral("Shift"), QStringLiteral("⇧")}, {QStringLiteral("Meta"), QStringLiteral("⌘")}};
                for (const auto &o : order)
                    if (parts.contains(o[0]))
                        mods += o[1];
            }
            const int keyW = qMax(mi->fontMetrics.horizontalAdvance(QStringLiteral("W")) + 4, mi->fontMetrics.horizontalAdvance(key) + 2);
            const int keyX = r.right() - rightPad - keyW;
            p->drawText(QRect(keyX, r.top(), keyW, r.height()), Qt::AlignVCenter | Qt::AlignLeft, key);
            if (!mods.isEmpty())
                p->drawText(QRect(x, r.top(), keyX - x - 1, r.height()), Qt::AlignVCenter | Qt::AlignRight, mods);
        }
        if (mi->menuItemType == QStyleOptionMenuItem::SubMenu)
            drawArrow(p, QRectF(r.right() - 16, r.top(), 10, r.height()), Qt::RightArrow, text);
        p->restore();
        return;
    }

    case CE_MenuBarEmptyArea: {
        p->save();
        p->fillRect(opt->rect, QBrush(menuStripes()));
        p->setPen(QColor(150, 150, 150));
        p->drawLine(opt->rect.bottomLeft(), opt->rect.bottomRight());
        p->restore();
        return;
    }
    case CE_MenuBarItem: {
        const auto *mi = qstyleoption_cast<const QStyleOptionMenuItem *>(opt);
        if (!mi)
            break;
        p->save();
        const bool selected = (mi->state & State_Selected) && (mi->state & State_Sunken);
        if (selected)
            paintSelection(p, QRectF(mi->rect.adjusted(0, 0, 0, -1)), m_appearance);
        p->setPen(selected ? Qt::white : (enabled(opt) ? Ink : QColor(150, 150, 150)));
        p->setFont(mi->font);
        p->drawText(mi->rect, Qt::AlignCenter | Qt::TextShowMnemonic, mi->text);
        p->restore();
        return;
    }

    case CE_HeaderSection: {
        const auto *h = qstyleoption_cast<const QStyleOptionHeader *>(opt);
        if (!h)
            break;
        p->save();
        const QRect r = h->rect;
        if (h->sortIndicator != QStyleOptionHeader::None && windowActive(opt)) {
            GelOptions o;
            o.radius = 0;
            o.shadow = false;
            o.lensInset = 0;
            paintGel(p, QRectF(r).adjusted(-1, -1, 1, 0), gel(GelKind::TabSelected, m_appearance), o); // lighter blue, HIG Figure 7-34
        } else {
            QLinearGradient g(r.topLeft(), r.bottomLeft());
            g.setColorAt(0, QColor(255, 255, 255));
            g.setColorAt(0.5, QColor(242, 242, 242));
            g.setColorAt(0.51, QColor(234, 234, 236));
            g.setColorAt(1, QColor(246, 246, 248));
            p->fillRect(r, g);
        }
        p->setPen(QColor(150, 150, 154));
        p->drawLine(r.bottomLeft(), r.bottomRight());
        if (h->position != QStyleOptionHeader::End && h->position != QStyleOptionHeader::OnlyOneSection)
            p->drawLine(r.topRight() + QPoint(0, 2), r.bottomRight() - QPoint(0, 2));
        p->restore();
        return;
    }

    case CE_ToolButtonLabel: {
        // bevel button labels use the label font, toolbar labels the small system font
        const auto *t = qstyleoption_cast<const QStyleOptionToolButton *>(opt);
        if (t && !t->text.isEmpty() && t->toolButtonStyle != Qt::ToolButtonIconOnly && t->toolButtonStyle != Qt::ToolButtonTextOnly) {
            QStyleOptionToolButton copy(*t);
            copy.font = (t->state & State_AutoRaise) ? smallFont(t->font) : labelFont(t->font);
            p->save();
            p->setFont(copy.font);
            QProxyStyle::drawControl(ce, &copy, p, w);
            p->restore();
            return;
        }
        break;
    }

    case CE_HeaderLabel: {
        // list headings use the small system font (HIG chapter 10)
        p->save();
        p->setFont(smallFont(p->font()));
        QProxyStyle::drawControl(ce, opt, p, w);
        p->restore();
        return;
    }

    case CE_ShapedFrame: {
        const auto *f = qstyleoption_cast<const QStyleOptionFrame *>(opt);
        if (f && (f->frameShape == QFrame::HLine || f->frameShape == QFrame::VLine)) {
            // separator: etched line, grey with white below / to the right
            p->save();
            const QRect r = f->rect;
            if (f->frameShape == QFrame::HLine) {
                const int y = r.center().y();
                p->setPen(QColor(0, 0, 0, 62));
                p->drawLine(r.left(), y, r.right(), y);
                p->setPen(QColor(255, 255, 255, 200));
                p->drawLine(r.left(), y + 1, r.right(), y + 1);
            } else {
                const int x = r.center().x();
                p->setPen(QColor(0, 0, 0, 62));
                p->drawLine(x, r.top(), x, r.bottom());
                p->setPen(QColor(255, 255, 255, 200));
                p->drawLine(x + 1, r.top(), x + 1, r.bottom());
            }
            p->restore();
            return;
        }
        break;
    }

    case CE_ToolBar: {
        // Finder/Mail top toolbars sit on the window pinstripes with a 1px #a3a3a3 divider below
        // (sampled from HIG Figures 7-16 and 11-19)
        const auto *tb = qstyleoption_cast<const QStyleOptionToolBar *>(opt);
        if (tb && (tb->state & State_Horizontal) && tb->toolBarArea == Qt::TopToolBarArea) {
            p->save();
            p->setPen(windowActive(opt) ? QColor(163, 163, 163) : QColor(190, 190, 190));
            p->drawLine(tb->rect.bottomLeft(), tb->rect.bottomRight());
            p->restore();
        }
        return;
    }

    case CE_DockWidgetTitle: {
        // like a 10.2 utility window: a short pinstriped title bar, small centred title
        const auto *d = qstyleoption_cast<const QStyleOptionDockWidget *>(opt);
        if (!d)
            break;
        paintTitleBar(p, d->rect, windowActive(opt));
        if (!d->title.isEmpty()) {
            p->save();
            p->setFont(smallFont(p->font()));
            p->setPen(windowActive(opt) ? Ink : QColor(139, 139, 139));
            p->drawText(d->rect, Qt::AlignCenter, p->fontMetrics().elidedText(d->title, Qt::ElideRight, d->rect.width() - 50));
            p->restore();
        }
        return;
    }

    case CE_Splitter: {
        // a small dimple in the middle of the splitter
        p->save();
        p->setRenderHint(QPainter::Antialiasing, true);
        const QPointF c = QRectF(opt->rect).center();
        QRadialGradient g(c - QPointF(0.8, 0.8), 3.5);
        g.setColorAt(0, QColor(250, 250, 250));
        g.setColorAt(1, QColor(150, 150, 150));
        p->setBrush(g);
        p->setPen(QColor(120, 120, 120));
        p->drawEllipse(c, 3, 3);
        p->restore();
        return;
    }

    default:
        break;
    }
    QProxyStyle::drawControl(ce, opt, p, w);
}

// ---------------------------------------------------------------- complex controls

void Style::drawScrollBar(const QStyleOptionSlider *opt, QPainter *p, const QWidget *w) const
{
    // Measured from the 10.2 artwork: the whole bar is an opaque white cylinder shaded at its
    // edges (181 -> 255 over ~7px on the leading side); the track ends in rounded caps; the
    // thumb sits 1px inside with a crisp dark navy rim; arrows are small dark triangles.
    const bool horizontal = opt->orientation == Qt::Horizontal;
    const QRect r = opt->rect;
    const QRect groove = subControlRect(CC_ScrollBar, opt, SC_ScrollBarGroove, w);
    const QRect slider = subControlRect(CC_ScrollBar, opt, SC_ScrollBarSlider, w);
    const QRect add = subControlRect(CC_ScrollBar, opt, SC_ScrollBarAddLine, w);
    const QRect sub = subControlRect(CC_ScrollBar, opt, SC_ScrollBarSubLine, w);
    const int thick = horizontal ? r.height() : r.width();
    p->save();

    auto across = [&](const QRect &rr, std::initializer_list<std::pair<qreal, int>> stops) {
        QLinearGradient g(rr.topLeft(), horizontal ? rr.bottomLeft() : rr.topRight());
        for (const auto &[pos, v] : stops)
            g.setColorAt(pos, QColor(v, v, v));
        return g;
    };
    // arrow area / end background: a lighter cylinder
    p->fillRect(r, across(r, {{0.0, 204}, {0.25, 236}, {0.5, 255}, {0.85, 250}, {1.0, 232}}));

    // track: capsule with the inner shadow along the leading edge
    p->setRenderHint(QPainter::Antialiasing, true);
    {
        const qreal rad = thick / 2.0;
        const QRectF t = QRectF(groove).adjusted(0, 0, horizontal ? 0 : 0, 0);
        QPainterPath cap;
        cap.addRoundedRect(t, rad, rad);
        p->setPen(Qt::NoPen);
        p->setBrush(across(groove, {{0.00, 176}, {0.10, 192}, {0.22, 212}, {0.40, 240}, {0.55, 255}, {0.85, 250}, {1.00, 228}}));
        p->drawPath(cap);
        // the rounded caps catch a grey arc, as on 10.2
        p->setBrush(Qt::NoBrush);
        p->setPen(QPen(QColor(0, 0, 0, 46), 1.0));
        p->drawRoundedRect(t.adjusted(0.5, 0.5, -0.5, -0.5), rad - 0.5, rad - 0.5);
    }

    // arrows: together at the end, separated by a fine line
    p->setRenderHint(QPainter::Antialiasing, false);
    for (const QRect &ar : {sub, add}) {
        const bool isAdd = ar == add;
        const bool pressed = (opt->activeSubControls & (isAdd ? SC_ScrollBarAddLine : SC_ScrollBarSubLine)) && (opt->state & State_Sunken);
        if (pressed)
            p->fillRect(ar, across(ar, {{0.0, 150}, {0.5, 196}, {1.0, 170}}));
        const Qt::ArrowType t = horizontal ? (isAdd ? Qt::RightArrow : Qt::LeftArrow) : (isAdd ? Qt::DownArrow : Qt::UpArrow);
        const QRectF ir = QRectF(ar).adjusted(3, 3, -3, -3);
        drawArrow(p, ir.adjusted(0.5, 0.5, -0.5, -0.5), t, enabled(opt) ? QColor(34, 34, 38) : QColor(160, 160, 160));
    }
    p->setPen(QColor(190, 190, 194));
    if (horizontal)
        p->drawLine(add.topLeft(), add.bottomLeft());
    else
        p->drawLine(add.topLeft(), add.topRight());
    // leading edge line against the content
    p->setPen(QColor(150, 150, 154));
    if (horizontal)
        p->drawLine(r.topLeft(), r.topRight());
    else
        p->drawLine(r.topLeft(), r.bottomLeft());

    // thumb
    if (opt->maximum > opt->minimum && slider.isValid() && enabled(opt)) {
        Gel g = windowActive(opt) ? gel(GelKind::Thumb, m_appearance) : gel(GelKind::Clear, m_appearance);
        if ((opt->activeSubControls & SC_ScrollBarSlider) && (opt->state & State_Sunken))
            g = gel(GelKind::Pressed, m_appearance);
        const QRect tr = horizontal ? slider.adjusted(0, 1, 0, -1 + 1) : slider.adjusted(1, 0, -1 + 1, 0);
        const qreal rad = (horizontal ? tr.height() : tr.width()) / 2.0;
        p->setRenderHint(QPainter::Antialiasing, true);
        QPainterPath shape;
        shape.addRoundedRect(QRectF(tr), rad, rad);
        // body across the thumb (lens side first)
        QLinearGradient body(tr.topLeft(), horizontal ? tr.bottomLeft() : tr.topRight());
        body.setStops(g.body);
        p->setPen(Qt::NoPen);
        p->setBrush(body);
        p->drawPath(shape);
        // narrow lens streak, inset from the rounded ends
        p->save();
        p->setClipPath(shape);
        const qreal tk = horizontal ? tr.height() : tr.width();
        const QRectF lens = horizontal ? QRectF(tr.left() + rad * 0.6, tr.top() + 1.5, tr.width() - rad * 1.2, tk * 0.34)
                                       : QRectF(tr.left() + 1.5, tr.top() + rad * 0.6, tk * 0.34, tr.height() - rad * 1.2);
        QLinearGradient lg(lens.topLeft(), horizontal ? lens.bottomLeft() : lens.topRight());
        lg.setStops(g.lens);
        p->setBrush(lg);
        p->drawRoundedRect(lens, tk * 0.17, tk * 0.17);
        // the rounded ends fall into shadow, which gives the pill its depth
        if (windowActive(opt)) {
            QLinearGradient ends(tr.topLeft(), horizontal ? tr.topRight() : tr.bottomLeft());
            const qreal len = horizontal ? tr.width() : tr.height();
            const qreal e = qMin(0.45, (rad * 1.3) / qMax(1.0, len));
            ends.setColorAt(0.0, QColor(10, 40, 120, 90));
            ends.setColorAt(e, QColor(10, 40, 120, 0));
            ends.setColorAt(1.0 - e, QColor(10, 40, 120, 0));
            ends.setColorAt(1.0, QColor(10, 40, 120, 90));
            p->setBrush(ends);
            p->drawRect(QRectF(tr));
        }
        p->restore();
        // crisp dark rim
        p->setBrush(Qt::NoBrush);
        p->setPen(QPen(g.rimTop, 1.0));
        p->drawRoundedRect(QRectF(tr).adjusted(0.5, 0.5, -0.5, -0.5), rad - 0.5, rad - 0.5);
    }
    p->restore();
}

void Style::drawSlider(const QStyleOptionSlider *opt, QPainter *p, const QWidget *w) const
{
    const bool horizontal = opt->orientation == Qt::Horizontal;
    const QRect groove = subControlRect(CC_Slider, opt, SC_SliderGroove, w);
    const QRect handle = subControlRect(CC_Slider, opt, SC_SliderHandle, w);
    p->save();
    p->setRenderHint(QPainter::Antialiasing, true);

    // track: 5px dark capsule with an inner shadow
    {
        const qreal th = 6.0;
        QRectF t = horizontal ? QRectF(groove.left() + 2, groove.center().y() - th / 2 + 0.5, groove.width() - 4, th)
                              : QRectF(groove.center().x() - th / 2 + 0.5, groove.top() + 2, th, groove.height() - 4);
        if (horizontal)
            t.moveCenter(QPointF(t.center().x(), handle.center().y() + 0.5));
        else
            t.moveCenter(QPointF(handle.center().x() + 0.5, t.center().y()));
        QLinearGradient g(t.topLeft(), horizontal ? t.bottomLeft() : t.topRight());
        g.setColorAt(0, QColor(96, 96, 100));
        g.setColorAt(0.45, QColor(140, 140, 144));
        g.setColorAt(1, QColor(200, 200, 204));
        p->setPen(QPen(QColor(84, 84, 88), 1.0));
        p->setBrush(g);
        p->drawRoundedRect(t, th / 2, th / 2);
    }

    // tick marks
    if (opt->tickPosition != QSlider::NoTicks && opt->maximum > opt->minimum) {
        p->setRenderHint(QPainter::Antialiasing, false);
        p->setPen(QColor(110, 110, 114));
        const int interval = opt->tickInterval > 0 ? opt->tickInterval : qMax(1, opt->pageStep);
        const int len = horizontal ? groove.width() - SliderThumb : groove.height() - SliderThumb;
        for (int v = opt->minimum; v <= opt->maximum; v += interval) {
            const int pos = sliderPositionFromValue(opt->minimum, opt->maximum, v, len, opt->upsideDown) + SliderThumb / 2;
            // ticks sit just past the thumb's point
            if (horizontal) {
                const int x = groove.left() + pos;
                if (opt->tickPosition & QSlider::TicksBelow)
                    p->drawLine(x, handle.bottom() + 3, x, handle.bottom() + 6);
                if (opt->tickPosition & QSlider::TicksAbove)
                    p->drawLine(x, handle.top() - 6, x, handle.top() - 3);
            } else {
                const int y = groove.top() + pos;
                if (opt->tickPosition & QSlider::TicksRight)
                    p->drawLine(handle.right() + 3, y, handle.right() + 6, y);
                if (opt->tickPosition & QSlider::TicksLeft)
                    p->drawLine(handle.left() - 6, y, handle.left() - 3, y);
            }
        }
        p->setRenderHint(QPainter::Antialiasing, true);
    }

    // thumb
    Gel g = windowActive(opt) ? coloredGel() : gel(GelKind::Clear, m_appearance);
    if ((opt->activeSubControls & SC_SliderHandle) && (opt->state & State_Sunken))
        g = gel(GelKind::Pressed, m_appearance);
    if (!enabled(opt))
        p->setOpacity(0.5);
    const bool pointed = opt->tickPosition == QSlider::TicksBelow || opt->tickPosition == QSlider::TicksAbove || opt->tickPosition == QSlider::TicksLeft
        || opt->tickPosition == QSlider::TicksRight;
    const QRectF hr = QRectF(handle).adjusted(0.5, 0.5, -0.5, -0.5);
    if (!pointed) {
        GelOptions o;
        o.lensInset = 2.5;
        o.lensHeight = 0.45;
        const qreal d = SliderThumb - 1;
        paintGel(p, QRectF(hr.center().x() - d / 2, hr.center().y() - d / 2, d, d), g, o);
    } else {
        // directional thumb: rounded body with a point towards the ticks (15x18)
        QPainterPath path;
        const QRectF b = hr;
        const qreal rad = 4.0;
        const bool down = horizontal ? (opt->tickPosition == QSlider::TicksBelow) : (opt->tickPosition == QSlider::TicksRight);
        if (horizontal) {
            const qreal tip = down ? b.bottom() : b.top();
            const qreal body = down ? b.bottom() - 6 : b.top() + 6;
            if (down) {
                path.moveTo(b.left(), b.top() + rad);
                path.quadTo(b.left(), b.top(), b.left() + rad, b.top());
                path.lineTo(b.right() - rad, b.top());
                path.quadTo(b.right(), b.top(), b.right(), b.top() + rad);
                path.lineTo(b.right(), body);
                path.lineTo(b.center().x(), tip);
                path.lineTo(b.left(), body);
            } else {
                path.moveTo(b.left(), b.bottom() - rad);
                path.quadTo(b.left(), b.bottom(), b.left() + rad, b.bottom());
                path.lineTo(b.right() - rad, b.bottom());
                path.quadTo(b.right(), b.bottom(), b.right(), b.bottom() - rad);
                path.lineTo(b.right(), body);
                path.lineTo(b.center().x(), tip);
                path.lineTo(b.left(), body);
            }
        } else {
            const qreal tip = down ? b.right() : b.left();
            const qreal body = down ? b.right() - 6 : b.left() + 6;
            if (down) {
                path.moveTo(b.left() + rad, b.top());
                path.quadTo(b.left(), b.top(), b.left(), b.top() + rad);
                path.lineTo(b.left(), b.bottom() - rad);
                path.quadTo(b.left(), b.bottom(), b.left() + rad, b.bottom());
                path.lineTo(body, b.bottom());
                path.lineTo(tip, b.center().y());
                path.lineTo(body, b.top());
            } else {
                path.moveTo(b.right() - rad, b.top());
                path.quadTo(b.right(), b.top(), b.right(), b.top() + rad);
                path.lineTo(b.right(), b.bottom() - rad);
                path.quadTo(b.right(), b.bottom(), b.right() - rad, b.bottom());
                path.lineTo(body, b.bottom());
                path.lineTo(tip, b.center().y());
                path.lineTo(body, b.top());
            }
        }
        path.closeSubpath();
        paintGelPath(p, path, b, g, Qt::Horizontal, true);
    }
    p->restore();
}

void Style::drawComboBox(const QStyleOptionComboBox *opt, QPainter *p, const QWidget *w) const
{
    const QRect r = opt->rect;
    const bool active = windowActive(opt);
    const bool sunken = opt->state & State_Sunken;
    p->save();
    if (!enabled(opt))
        p->setOpacity(0.55);

    if (opt->editable) {
        // combination box: a square text field joined to a rounded arrow button
        const QRect arrow = subControlRect(CC_ComboBox, opt, SC_ComboBoxArrow, w);
        QRect field = r;
        field.setRight(arrow.left() + 2);
        drawTextField(field, opt, p, opt->state & State_HasFocus);
        const QRectF capR(arrow.left() + 0.5, field.top() + 2.5, arrow.width() - 2.5, field.height() - 5);
        p->setRenderHint(QPainter::Antialiasing, true);
        p->save();
        p->setClipRect(capR.adjusted(0, -2, 2, 4));
        GelOptions o;
        o.radius = 4.5;
        o.lensInset = 2;
        o.shadow = false;
        const QRectF wide(capR.left() - 8, capR.top(), capR.width() + 8, capR.height());
        paintGel(p, wide, sunken ? gel(GelKind::Pressed, m_appearance) : (active ? coloredGel() : gel(GelKind::Clear, m_appearance)), o);
        p->restore();
        drawArrow(p, capR.adjusted(3, 4, -3, -4), Qt::DownArrow, GlyphInk);
        p->restore();
        return;
    }

    // pop-up menu: white rounded rect (4.5px corners) with a coloured double-arrow end cap
    const qreal h = qMin<qreal>(ButtonHeight, r.height() - ShadowSpace);
    const QRectF body(r.left() + 0.5, r.top() + (r.height() - ShadowSpace - h) / 2.0, r.width() - 1, h);
    GelOptions o;
    o.radius = 4.5;
    o.lensInset = 3;
    paintGel(p, body, sunken ? gel(GelKind::Pressed, m_appearance) : popupBodyGel(), o);

    const QRectF cap(body.right() - PopupCapWidth, body.top(), PopupCapWidth, body.height());
    p->save();
    p->setClipRect(cap.adjusted(0, -1, 1, 1));
    GelOptions co;
    co.radius = 4.5;
    co.lensInset = 0;
    co.shadow = false;
    paintGel(p, QRectF(body.left(), body.top(), body.width(), body.height()), active && !sunken ? coloredGel() : (sunken ? gel(GelKind::Pressed, m_appearance) : gel(GelKind::Clear, m_appearance)), co);
    p->restore();
    p->setRenderHint(QPainter::Antialiasing, false);
    p->setPen(active ? coloredGel().rimTop : QColor(130, 130, 134));
    p->drawLine(QPointF(cap.left(), cap.top() + 1), QPointF(cap.left(), cap.bottom() - 1));
    // double triangle
    const QPointF c = cap.center() + QPointF(0.5, 0);
    drawArrow(p, QRectF(c.x() - 4, c.y() - 6.5, 8, 6), Qt::UpArrow, GlyphInk);
    drawArrow(p, QRectF(c.x() - 4, c.y() + 0.5, 8, 6), Qt::DownArrow, GlyphInk);
    p->restore();
}

void Style::drawSpinBox(const QStyleOptionSpinBox *opt, QPainter *p, const QWidget *w) const
{
    const QRect frame = subControlRect(CC_SpinBox, opt, SC_SpinBoxFrame, w);
    const QRect up = subControlRect(CC_SpinBox, opt, SC_SpinBoxUp, w);
    const QRect down = subControlRect(CC_SpinBox, opt, SC_SpinBoxDown, w);
    if (opt->frame)
        drawTextField(frame, opt, p, opt->state & State_HasFocus);
    const bool sunken = opt->state & State_Sunken;
    if (opt->buttonSymbols != QAbstractSpinBox::NoButtons) {
        drawLittleArrows(up.united(down), opt, p, sunken && (opt->activeSubControls & SC_SpinBoxUp), sunken && (opt->activeSubControls & SC_SpinBoxDown),
                         opt->stepEnabled & QAbstractSpinBox::StepUpEnabled, opt->stepEnabled & QAbstractSpinBox::StepDownEnabled);
    }
}

void Style::drawComplexControl(ComplexControl cc, const QStyleOptionComplex *opt, QPainter *p, const QWidget *w) const
{
    switch (cc) {
    case CC_ScrollBar:
        if (const auto *s = qstyleoption_cast<const QStyleOptionSlider *>(opt)) {
            drawScrollBar(s, p, w);
            return;
        }
        break;
    case CC_Slider:
        if (const auto *s = qstyleoption_cast<const QStyleOptionSlider *>(opt)) {
            drawSlider(s, p, w);
            return;
        }
        break;
    case CC_ComboBox:
        if (const auto *c = qstyleoption_cast<const QStyleOptionComboBox *>(opt)) {
            drawComboBox(c, p, w);
            return;
        }
        break;
    case CC_SpinBox:
        if (const auto *s = qstyleoption_cast<const QStyleOptionSpinBox *>(opt)) {
            drawSpinBox(s, p, w);
            return;
        }
        break;
    case CC_GroupBox:
        if (const auto *g = qstyleoption_cast<const QStyleOptionGroupBox *>(opt)) {
            const QRect frame = subControlRect(cc, g, SC_GroupBoxFrame, w);
            const QRect label = subControlRect(cc, g, SC_GroupBoxLabel, w);
            const QRect check = subControlRect(cc, g, SC_GroupBoxCheckBox, w);
            if (!(g->features & QStyleOptionFrame::Flat)) {
                p->save();
                QRegion clip(g->rect);
                if (!g->text.isEmpty() || (g->subControls & SC_GroupBoxCheckBox))
                    clip -= QRect(label.united(check.isValid() ? check : label).adjusted(-3, 0, 3, 0));
                p->setClipRegion(clip);
                QStyleOptionFrame f;
                f.QStyleOption::operator=(*g);
                f.rect = frame;
                drawPrimitive(PE_FrameGroupBox, &f, p, w);
                p->restore();
            } else {
                // flat: a separator line 2px right of the title (HIG Figure 8-3)
                p->save();
                const int y = label.center().y();
                p->setPen(QColor(0, 0, 0, 62));
                p->drawLine(label.right() + 3, y, g->rect.right(), y);
                p->setPen(QColor(255, 255, 255, 200));
                p->drawLine(label.right() + 3, y + 1, g->rect.right(), y + 1);
                p->restore();
            }
            if (g->subControls & SC_GroupBoxCheckBox) {
                QStyleOptionButton box;
                box.QStyleOption::operator=(*g);
                box.rect = check;
                drawPrimitive(PE_IndicatorCheckBox, &box, p, w);
            }
            if (!g->text.isEmpty()) {
                p->save();
                p->setFont(smallFont(widgetFont(w)));
                p->setPen(enabled(opt) ? Ink : QColor(128, 128, 128));
                p->drawText(label, Qt::AlignLeft | Qt::AlignVCenter | Qt::TextShowMnemonic, g->text);
                p->restore();
            }
            return;
        }
        break;
    case CC_TitleBar:
        if (const auto *t = qstyleoption_cast<const QStyleOptionTitleBar *>(opt)) {
            // MDI sub-windows: 10.2 title bar with traffic lights on the left
            const bool active = (t->titleBarState & Qt::WindowActive) || (t->state & State_Active);
            paintTitleBar(p, t->rect, active);
            const bool lightsHover = (t->state & State_MouseOver) && (t->activeSubControls & (SC_TitleBarCloseButton | SC_TitleBarMinButton | SC_TitleBarMaxButton | SC_TitleBarNormalButton));
            const SubControl subs[3] = {SC_TitleBarCloseButton, SC_TitleBarMinButton, (t->titleBarState & (Qt::WindowMaximized | Qt::WindowMinimized)) ? SC_TitleBarNormalButton : SC_TitleBarMaxButton};
            for (int i = 0; i < 3; ++i) {
                const QRect r = subControlRect(cc, t, subs[i], w);
                if (!r.isValid())
                    continue;
                const bool pressed = (t->activeSubControls & subs[i]) && (t->state & State_Sunken);
                paintLight(p, r, i, active, lightsHover, pressed);
            }
            const QRect label = subControlRect(cc, t, SC_TitleBarLabel, w);
            p->save();
            p->setPen(active ? Ink : QColor(139, 139, 139));
            p->drawText(label, Qt::AlignCenter, p->fontMetrics().elidedText(t->text, Qt::ElideRight, label.width()));
            p->restore();
            return;
        }
        break;
    default:
        break;
    }
    QProxyStyle::drawComplexControl(cc, opt, p, w);
}

// ---------------------------------------------------------------- geometry

QRect Style::subControlRect(ComplexControl cc, const QStyleOptionComplex *opt, SubControl sc, const QWidget *w) const
{
    switch (cc) {
    case CC_ScrollBar: {
        const auto *s = qstyleoption_cast<const QStyleOptionSlider *>(opt);
        if (!s)
            break;
        const QRect r = s->rect;
        const bool horizontal = s->orientation == Qt::Horizontal;
        const int len = horizontal ? r.width() : r.height();
        const int arrows = qMin(2 * ScrollArrowLength, len / 2);
        const int one = arrows / 2;
        // the track keeps 1px from the content edge line; its end overlaps the arrow area slightly
        QRect groove = horizontal ? QRect(r.left() + 1, r.top() + 1, len - arrows - 1 + 3, r.height() - 1) : QRect(r.left() + 1, r.top() + 1, r.width() - 1, len - arrows - 1 + 3);
        switch (sc) {
        case SC_ScrollBarSubLine:
            return horizontal ? QRect(r.right() - arrows + 1, r.top(), one, r.height()) : QRect(r.left(), r.bottom() - arrows + 1, r.width(), one);
        case SC_ScrollBarAddLine:
            return horizontal ? QRect(r.right() - one + 1, r.top(), one, r.height()) : QRect(r.left(), r.bottom() - one + 1, r.width(), one);
        case SC_ScrollBarGroove:
            return groove;
        case SC_ScrollBarSlider:
        case SC_ScrollBarSubPage:
        case SC_ScrollBarAddPage: {
            const int glen = horizontal ? groove.width() : groove.height();
            const int range = s->maximum - s->minimum;
            int slen = range > 0 ? int(qint64(glen) * s->pageStep / (range + s->pageStep)) : glen;
            slen = qBound(qMin(glen, pixelMetric(PM_ScrollBarSliderMin, opt, w)), slen, glen);
            const int pos = sliderPositionFromValue(s->minimum, s->maximum, s->sliderPosition, glen - slen, s->upsideDown);
            const QRect slider = horizontal ? QRect(groove.left() + pos, groove.top(), slen, groove.height()) : QRect(groove.left(), groove.top() + pos, groove.width(), slen);
            if (sc == SC_ScrollBarSlider)
                return slider;
            if (sc == SC_ScrollBarSubPage)
                return horizontal ? QRect(groove.left(), groove.top(), slider.left() - groove.left(), groove.height())
                                  : QRect(groove.left(), groove.top(), groove.width(), slider.top() - groove.top());
            return horizontal ? QRect(slider.right() + 1, groove.top(), groove.right() - slider.right(), groove.height())
                              : QRect(groove.left(), slider.bottom() + 1, groove.width(), groove.bottom() - slider.bottom());
        }
        default:
            return {};
        }
    }

    case CC_Slider: {
        const auto *s = qstyleoption_cast<const QStyleOptionSlider *>(opt);
        if (!s)
            break;
        const QRect r = s->rect;
        const bool horizontal = s->orientation == Qt::Horizontal;
        const bool pointed = s->tickPosition != QSlider::NoTicks && s->tickPosition != QSlider::TicksBothSides;
        const int thick = pointed ? SliderThumbPointed : SliderThumb;
        if (sc == SC_SliderGroove)
            return r;
        if (sc == SC_SliderHandle) {
            const int len = (horizontal ? r.width() : r.height()) - SliderThumb;
            const int pos = sliderPositionFromValue(s->minimum, s->maximum, s->sliderPosition, len, s->upsideDown);
            if (horizontal) {
                int y = r.center().y() - thick / 2;
                if (s->tickPosition == QSlider::TicksBelow)
                    y = r.center().y() - (thick + 7) / 2;
                else if (s->tickPosition == QSlider::TicksAbove)
                    y = r.center().y() - (thick + 7) / 2 + 7;
                return QRect(r.left() + pos, y, SliderThumb, thick);
            }
            int x = r.center().x() - thick / 2;
            if (s->tickPosition == QSlider::TicksRight)
                x = r.center().x() - (thick + 7) / 2;
            else if (s->tickPosition == QSlider::TicksLeft)
                x = r.center().x() - (thick + 7) / 2 + 7;
            return QRect(x, r.top() + pos, thick, SliderThumb);
        }
        break;
    }

    case CC_ComboBox: {
        const auto *c = qstyleoption_cast<const QStyleOptionComboBox *>(opt);
        if (!c)
            break;
        const QRect r = c->rect;
        if (c->editable) {
            switch (sc) {
            case SC_ComboBoxFrame:
                return r;
            case SC_ComboBoxArrow:
                return QRect(r.right() - 20, r.top(), 21, r.height());
            case SC_ComboBoxEditField:
                return QRect(r.left() + 6, r.top() + 4, r.width() - 6 - 24, r.height() - 8);
            case SC_ComboBoxListBoxPopup:
                return r;
            default:
                break;
            }
        } else {
            const int bodyTop = r.top() + (r.height() - ShadowSpace - ButtonHeight) / 2;
            switch (sc) {
            case SC_ComboBoxFrame:
                return r;
            case SC_ComboBoxArrow:
                return QRect(r.right() - PopupCapWidth, bodyTop, PopupCapWidth, ButtonHeight);
            case SC_ComboBoxEditField:
                return QRect(r.left() + PopupTextInset, bodyTop + 1, r.width() - PopupTextInset - PopupCapWidth - PopupTextInset, ButtonHeight - 2);
            case SC_ComboBoxListBoxPopup:
                return r;
            default:
                break;
            }
        }
        break;
    }

    case CC_GroupBox: {
        const auto *g = qstyleoption_cast<const QStyleOptionGroupBox *>(opt);
        if (!g)
            break;
        const QFontMetrics fm(smallFont(widgetFont(w)));
        const bool hasCheck = g->subControls & SC_GroupBoxCheckBox;
        const int labelH = qMax(fm.height(), hasCheck ? IndicatorSize : 0);
        const int checkW = hasCheck ? IndicatorSize + 3 : 0;
        const int textW = g->text.isEmpty() ? 0 : fm.horizontalAdvance(g->text) + 2;
        const QRect r = g->rect;
        const int top = (g->text.isEmpty() && !hasCheck) ? 0 : labelH / 2;
        switch (sc) {
        case SC_GroupBoxFrame:
            return QRect(r.left(), r.top() + top, r.width(), r.height() - top);
        case SC_GroupBoxCheckBox:
            return hasCheck ? QRect(r.left() + 8, r.top(), IndicatorSize, labelH) : QRect();
        case SC_GroupBoxLabel:
            return QRect(r.left() + 8 + checkW, r.top(), textW, labelH);
        case SC_GroupBoxContents: {
            // HIG: nothing within 16px of the border; layout margins add the other 8
            const QRect f(r.left(), r.top() + top, r.width(), r.height() - top);
            return f.adjusted(8, qMax(8, labelH - top + 4), -8, -8);
        }
        default:
            break;
        }
        break;
    }

    case CC_TitleBar: {
        const auto *t = qstyleoption_cast<const QStyleOptionTitleBar *>(opt);
        if (!t)
            break;
        const QRect r = t->rect;
        const int d = 13, cy = r.top() + (r.height() - d) / 2;
        const bool hasMax = t->titleBarFlags & Qt::WindowMaximizeButtonHint;
        const bool hasMin = t->titleBarFlags & Qt::WindowMinimizeButtonHint;
        switch (sc) {
        case SC_TitleBarCloseButton:
            return QRect(r.left() + 8, cy, d, d);
        case SC_TitleBarMinButton:
            return hasMin && !(t->titleBarState & Qt::WindowMinimized) ? QRect(r.left() + 29, cy, d, d) : QRect();
        case SC_TitleBarMaxButton:
            return hasMax && !(t->titleBarState & (Qt::WindowMaximized | Qt::WindowMinimized)) ? QRect(r.left() + 50, cy, d, d) : QRect();
        case SC_TitleBarNormalButton:
            return (t->titleBarState & (Qt::WindowMaximized | Qt::WindowMinimized)) ? QRect(r.left() + (t->titleBarState & Qt::WindowMinimized ? 29 : 50), cy, d, d) : QRect();
        case SC_TitleBarLabel:
            return r.adjusted(72, 0, -72, 0);
        case SC_TitleBarSysMenu:
        case SC_TitleBarShadeButton:
        case SC_TitleBarUnshadeButton:
        case SC_TitleBarContextHelpButton:
            return QRect();
        default:
            break;
        }
        break;
    }

    case CC_SpinBox: {
        const auto *s = qstyleoption_cast<const QStyleOptionSpinBox *>(opt);
        if (!s)
            break;
        const QRect r = s->rect;
        const bool buttons = s->buttonSymbols != QAbstractSpinBox::NoButtons;
        const int bw = buttons ? LittleArrowsWidth + 3 : 0;
        const QRect frame(r.left(), r.top(), r.width() - bw, r.height());
        const QRect arrows(r.right() - LittleArrowsWidth + 1, r.top() + (r.height() - LittleArrowsHeight) / 2, LittleArrowsWidth, LittleArrowsHeight);
        switch (sc) {
        case SC_SpinBoxFrame:
            return frame;
        case SC_SpinBoxEditField:
            return frame.adjusted(5, 4, -4, -4);
        case SC_SpinBoxUp:
            return buttons ? QRect(arrows.left(), arrows.top(), arrows.width(), arrows.height() / 2) : QRect();
        case SC_SpinBoxDown:
            return buttons ? QRect(arrows.left(), arrows.top() + arrows.height() / 2, arrows.width(), arrows.height() - arrows.height() / 2) : QRect();
        default:
            break;
        }
        break;
    }
    default:
        break;
    }
    return QProxyStyle::subControlRect(cc, opt, sc, w);
}

QRect Style::subElementRect(SubElement se, const QStyleOption *opt, const QWidget *w) const
{
    switch (se) {
    case SE_TabWidgetTabContents: {
        const auto *tw = qstyleoption_cast<const QStyleOptionTabWidgetFrame *>(opt);
        if (tw) {
            const QRect pane = subElementRect(SE_TabWidgetTabPane, opt, w);
            switch (tabSide(tw->shape)) {
            case Side::North:
                return pane.adjusted(2, TabAccentBar + 4, -2, -2);
            case Side::South:
                return pane.adjusted(2, 2, -2, -TabAccentBar - 4);
            case Side::West:
                return pane.adjusted(TabAccentBar + 4, 2, -2, -2);
            case Side::East:
                return pane.adjusted(2, 2, -TabAccentBar - 4, -2);
            }
        }
        break;
    }
    case SE_PushButtonContents:
        return opt->rect.adjusted(ButtonEndCap / 2, 0, -ButtonEndCap / 2, -ShadowSpace);
    case SE_ProgressBarGroove:
    case SE_ProgressBarContents:
    case SE_ProgressBarLabel: {
        const auto *pb = qstyleoption_cast<const QStyleOptionProgressBar *>(opt);
        if (!pb || !(pb->state & State_Horizontal))
            break;
        if (!pb->textVisible)
            return se == SE_ProgressBarLabel ? QRect() : opt->rect;
        const int labelW = opt->fontMetrics.horizontalAdvance(QStringLiteral("100%")) + 8;
        if (se == SE_ProgressBarLabel)
            return QRect(opt->rect.right() - labelW + 1, opt->rect.top(), labelW, opt->rect.height());
        return opt->rect.adjusted(0, 0, -labelW, 0);
    }
    case SE_LineEditContents:
        return opt->rect.adjusted(5, 3, -5, -3);
    default:
        break;
    }
    return QProxyStyle::subElementRect(se, opt, w);
}

int Style::pixelMetric(PixelMetric pm, const QStyleOption *opt, const QWidget *w) const
{
    switch (pm) {
    case PM_ButtonMargin:
        return ButtonEndCap;
    case PM_ButtonDefaultIndicator:
    case PM_ButtonShiftHorizontal:
    case PM_ButtonShiftVertical:
    case PM_TabBarTabShiftHorizontal:
    case PM_TabBarTabShiftVertical:
        return 0;
    case PM_IndicatorWidth:
    case PM_IndicatorHeight:
    case PM_ExclusiveIndicatorWidth:
    case PM_ExclusiveIndicatorHeight:
        return IndicatorSize;
    case PM_CheckBoxLabelSpacing:
    case PM_RadioButtonLabelSpacing:
        return 5;
    case PM_ScrollBarExtent:
        return ScrollBarWidth;
    case PM_ScrollBarSliderMin:
        return 24;
    case PM_SliderThickness:
        return 22;
    case PM_SliderLength:
        return SliderThumb;
    case PM_SliderControlThickness:
        return SliderThumbPointed;
    case PM_SliderTickmarkOffset:
        return 5;
    case PM_TabBarTabHSpace:
        return 2 * TabTextInset;
    case PM_TabBarTabVSpace:
        return 6;
    case PM_TabBarBaseOverlap:
        return 1;
    case PM_TabBarBaseHeight:
        return 6;
    case PM_TabBarTabOverlap:
        return 1;
    case PM_ToolTipLabelFrameWidth:
        return 1;
    case PM_ToolBarIconSize:
        return 32; // HIG chapter 11: 32x32 recommended for toolbar icons
    case PM_ToolBarItemSpacing:
        return 6;
    case PM_ToolBarItemMargin:
        return 2;
    case PM_DefaultFrameWidth:
        if (qobject_cast<const QLineEdit *>(w) || qobject_cast<const QAbstractSpinBox *>(w))
            return 3;
        return 1;
    case PM_MenuPanelWidth:
    case PM_MenuHMargin:
        return 0;
    case PM_MenuVMargin:
        return 4;
    case PM_MenuBarPanelWidth:
    case PM_MenuBarVMargin:
        return 0;
    case PM_MenuBarHMargin:
        return 8;
    case PM_MenuBarItemSpacing:
        return 0;
    case PM_ToolBarHandleExtent:
        return 0;
    case PM_TitleBarHeight:
        return 22;
    case PM_MessageBoxIconSize:
        return 64; // HIG Figure 6-2: the application icon in alerts
    case PM_DockWidgetTitleMargin:
        return 3;
    case PM_ToolBarFrameWidth:
        return 0;
    case PM_SplitterWidth:
        return 9;
    case PM_ScrollView_ScrollBarOverlap:
    case PM_ScrollView_ScrollBarSpacing:
        return 0;
    case PM_LayoutHorizontalSpacing:
        return 12; // HIG: 12px between controls
    case PM_LayoutVerticalSpacing:
        return 8;
    case PM_LayoutLeftMargin:
    case PM_LayoutRightMargin:
    case PM_LayoutTopMargin:
    case PM_LayoutBottomMargin:
        return (w && w->isWindow()) ? 20 : 8; // HIG: 20px from the window edge
    default:
        break;
    }
    return QProxyStyle::pixelMetric(pm, opt, w);
}

QSize Style::sizeFromContents(ContentsType ct, const QStyleOption *opt, const QSize &size, const QWidget *w) const
{
    switch (ct) {
    case CT_PushButton: {
        const auto *b = qstyleoption_cast<const QStyleOptionButton *>(opt);
        int width = size.width() + 2 * ButtonEndCap;
        if (b && !b->text.isEmpty())
            width = qMax(width, ButtonMinWidth);
        int height = qMax(size.height() + 4, ButtonHeight) + ShadowSpace;
        if (b && !b->icon.isNull() && b->text.isEmpty())
            width = qMax(width, height + 8);
        return {width, height};
    }
    case CT_CheckBox:
    case CT_RadioButton: {
        QSize s = QProxyStyle::sizeFromContents(ct, opt, size, w);
        return {s.width(), qMax(s.height(), IndicatorSize)};
    }
    case CT_ComboBox: {
        const auto *c = qstyleoption_cast<const QStyleOptionComboBox *>(opt);
        if (c && c->editable)
            return {size.width() + 6 + 24 + 4, qMax(size.height() + 8, TextFieldHeight + 4)};
        return {size.width() + PopupTextInset + PopupCapWidth + PopupTextInset, qMax(size.height() + 2, ButtonHeight) + ShadowSpace};
    }
    case CT_LineEdit:
        return {size.width() + 10, qMax(size.height() + 6, TextFieldHeight + 4)};
    case CT_SpinBox:
        return {size.width() + 9 + LittleArrowsWidth + 3, qMax(size.height() + 8, TextFieldHeight + 4)};
    case CT_TabBarTab: {
        const auto *t = qstyleoption_cast<const QStyleOptionTab *>(opt);
        QSize s = QProxyStyle::sizeFromContents(ct, opt, size, w);
        if (t) {
            if (vertical(tabSide(t->shape)))
                s.setWidth(TabHeight);
            else
                s.setHeight(TabHeight);
        }
        return s;
    }
    case CT_MenuItem: {
        const auto *mi = qstyleoption_cast<const QStyleOptionMenuItem *>(opt);
        if (mi && mi->menuItemType == QStyleOptionMenuItem::Separator)
            return {size.width(), mi->text.isEmpty() ? MenuSeparatorHeight : MenuItemHeight + 2};
        QSize s = size;
        int width = s.width() + 20 + 22;
        if (mi && mi->maxIconWidth > 0)
            width += qMin(16, mi->maxIconWidth) + 6;
        if (mi && mi->text.contains(QLatin1Char('\t')))
            width += 24;
        return {width, qMax(s.height() + 2, MenuItemHeight)};
    }
    case CT_MenuBarItem:
        return {size.width() + 18, qMax(size.height() + 4, 22)};
    case CT_ProgressBar: {
        QSize s = QProxyStyle::sizeFromContents(ct, opt, size, w);
        return {s.width(), qMax(s.height(), ProgressHeight + 4)};
    }
    case CT_ItemViewItem: {
        // lists: 19pt baseline to baseline (HIG Figure 7-32)
        QSize sz = QProxyStyle::sizeFromContents(ct, opt, size, w);
        return {sz.width(), qMax(sz.height(), 19)};
    }
    case CT_HeaderSection: {
        QSize s = QProxyStyle::sizeFromContents(ct, opt, size, w);
        return {s.width() + 4, qMax(s.height(), 17)};
    }
    case CT_ToolButton: {
        const auto *t = qstyleoption_cast<const QStyleOptionToolButton *>(opt);
        if (t && !t->text.isEmpty() && t->toolButtonStyle == Qt::ToolButtonTextUnderIcon) {
            const bool autoRaise = t->state & State_AutoRaise;
            const QFontMetrics fm(autoRaise ? smallFont(t->font) : labelFont(t->font));
            const int iw = t->icon.isNull() ? 0 : t->iconSize.width();
            const int ih = t->icon.isNull() ? 0 : t->iconSize.height();
            const int padH = autoRaise ? 10 : 12;
            const int padV = autoRaise ? 8 : 12; // HIG: >= 5px around bevel button icon
            return {qMax(iw, fm.horizontalAdvance(t->text)) + padH, ih + 2 + fm.height() + padV};
        }
        QSize s = QProxyStyle::sizeFromContents(ct, opt, size, w);
        if (t && !(t->state & State_AutoRaise) && !t->icon.isNull())
            s = s.expandedTo(t->iconSize + QSize(10, 12));
        return s;
    }
    default:
        break;
    }
    return QProxyStyle::sizeFromContents(ct, opt, size, w);
}

QIcon Style::standardIcon(StandardPixmap sp, const QStyleOption *opt, const QWidget *w) const
{
    int kind = -1;
    switch (sp) {
    case SP_TitleBarCloseButton:
    case SP_DockWidgetCloseButton:
        kind = 0;
        break;
    case SP_TitleBarMinButton:
        kind = 1;
        break;
    case SP_TitleBarMaxButton:
    case SP_TitleBarNormalButton:
        kind = 2;
        break;
    default:
        break;
    }
    if (kind < 0)
        return QProxyStyle::standardIcon(sp, opt, w);
    QIcon icon;
    for (int scale : {1, 2}) {
        QPixmap pm(13 * scale, 13 * scale);
        pm.fill(Qt::transparent);
        pm.setDevicePixelRatio(scale);
        QPainter p(&pm);
        paintLight(&p, QRectF(0, 0, 12, 12), kind, true, false, false);
        p.end();
        icon.addPixmap(pm);
    }
    return icon;
}

int Style::styleHint(StyleHint sh, const QStyleOption *opt, const QWidget *w, QStyleHintReturn *ret) const
{
    switch (sh) {
    case SH_TabBar_Alignment:
        return Qt::AlignCenter; // Aqua tabs are centred above the pane
    case SH_ComboBox_Popup:
        return true; // pop-up menus open as a menu over the button
    case SH_ScrollBar_Transient:
        return false;
    case SH_ScrollView_FrameOnlyAroundContents:
        return true;
    case SH_DialogButtonLayout:
        return QDialogButtonBox::MacLayout;
    case SH_Menu_FlashTriggeredItem:
        return true; // the chosen item blinks before the menu closes
    case SH_MenuBar_AltKeyNavigation:
        return false;
    case SH_ScrollBar_MiddleClickAbsolutePosition:
        return true;
    case SH_Slider_AbsoluteSetButtons:
        return Qt::LeftButton;
    case SH_ItemView_ShowDecorationSelected:
        return true;
    case SH_ToolTipLabel_Opacity:
        return 245;
    case SH_UnderlineShortcut:
        return false;
    case SH_TabBar_PreferNoArrows:
        return true;
    default:
        break;
    }
    return QProxyStyle::styleHint(sh, opt, w, ret);
}
}
