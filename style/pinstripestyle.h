// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once

#include "gel.h"

#include <QBasicTimer>
#include <QPointer>
#include <QPainterPath>
#include <QProxyStyle>
#include <QStyleOption>
#include <QHash>
#include <QList>

class KWindowShadow;

namespace Pinstripe
{
class Style : public QProxyStyle
{
    Q_OBJECT
public:
    explicit Style(Appearance appearance);

    void polish(QPalette &palette) override;
    void polish(QWidget *widget) override;
    void unpolish(QWidget *widget) override;

    void drawPrimitive(PrimitiveElement pe, const QStyleOption *opt, QPainter *p, const QWidget *w = nullptr) const override;
    void drawControl(ControlElement ce, const QStyleOption *opt, QPainter *p, const QWidget *w = nullptr) const override;
    void drawComplexControl(ComplexControl cc, const QStyleOptionComplex *opt, QPainter *p, const QWidget *w = nullptr) const override;

    QRect subControlRect(ComplexControl cc, const QStyleOptionComplex *opt, SubControl sc, const QWidget *w = nullptr) const override;
    QRect subElementRect(SubElement se, const QStyleOption *opt, const QWidget *w = nullptr) const override;
    int pixelMetric(PixelMetric pm, const QStyleOption *opt = nullptr, const QWidget *w = nullptr) const override;
    int layoutSpacing(QSizePolicy::ControlType c1, QSizePolicy::ControlType c2, Qt::Orientation o,
                      const QStyleOption *opt = nullptr, const QWidget *w = nullptr) const override;
    QSize sizeFromContents(ContentsType ct, const QStyleOption *opt, const QSize &size, const QWidget *w = nullptr) const override;
    QIcon standardIcon(StandardPixmap sp, const QStyleOption *opt = nullptr, const QWidget *w = nullptr) const override;
    int styleHint(StyleHint sh, const QStyleOption *opt = nullptr, const QWidget *w = nullptr, QStyleHintReturn *ret = nullptr) const override;

protected:
    void timerEvent(QTimerEvent *event) override;
    bool eventFilter(QObject *obj, QEvent *event) override;

private:
    Gel coloredGel() const;
    Gel buttonGel(const QStyleOption *opt, bool isDefault, bool sunken) const;
    void drawScrollBar(const QStyleOptionSlider *opt, QPainter *p, const QWidget *w) const;
    void drawSlider(const QStyleOptionSlider *opt, QPainter *p, const QWidget *w) const;
    void drawComboBox(const QStyleOptionComboBox *opt, QPainter *p, const QWidget *w) const;
    void drawSpinBox(const QStyleOptionSpinBox *opt, QPainter *p, const QWidget *w) const;
    void drawTextField(const QRect &r, const QStyleOption *opt, QPainter *p, bool focus) const;
    void drawLittleArrows(const QRect &r, const QStyleOption *opt, QPainter *p, bool upPressed, bool downPressed, bool upEnabled, bool downEnabled) const;
    void drawArrow(QPainter *p, const QRectF &r, Qt::ArrowType type, const QColor &c) const;
    void paintGelPath(QPainter *p, const QPainterPath &path, const QRectF &bounds, const Gel &g, Qt::Orientation o, bool shadow, const QPainterPath *rimPath = nullptr) const;
    void updateAnimationTimer();
    void installShadow(QWidget *w);
    void removeShadow(QWidget *w);

    Appearance m_appearance;
    QBasicTimer m_timer;
    QList<QPointer<QWidget>> m_animated; // default buttons and progress bars
    qreal m_phase = 0; // seconds, drives pulse and stripes
    QHash<const QWidget *, KWindowShadow *> m_shadows; // menus, tooltips, pop-up lists
};
}
