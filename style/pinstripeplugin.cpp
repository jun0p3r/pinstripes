// SPDX-License-Identifier: GPL-2.0-or-later
#include "pinstripestyle.h"

#include <QStylePlugin>

class PinstripeStylePlugin : public QStylePlugin
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QStyleFactoryInterface_iid FILE "pinstripe.json")
public:
    QStyle *create(const QString &key) override
    {
        const QString k = key.toLower();
        if (k == QLatin1String("pinstripe"))
            return new Pinstripe::Style(Pinstripe::Appearance::Blue);
        if (k == QLatin1String("pinstripe graphite"))
            return new Pinstripe::Style(Pinstripe::Appearance::Graphite);
        return nullptr;
    }
};

#include "pinstripeplugin.moc"
