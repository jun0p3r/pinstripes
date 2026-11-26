// SPDX-License-Identifier: GPL-2.0-or-later
//
// Offscreen widget gallery for the Pinstripe style. Renders a few windows (active and
// inactive), an open menu and a menu bar into PNGs so the style can be compared with
// the Aqua HIG artwork without touching the running desktop.
//
// usage: QT_PLUGIN_PATH=build/bin pinstripe-gallery <out-dir> [style] [colors-file]

#include <KColorScheme>
#include <KSharedConfig>

#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QDialogButtonBox>
#include <QDockWidget>
#include <QListWidget>
#include <QMainWindow>
#include <QMdiArea>
#include <QMdiSubWindow>
#include <QDir>
#include <QFormLayout>
#include <QGridLayout>
#include <QGroupBox>
#include <QHeaderView>
#include <QLabel>
#include <QLineEdit>
#include <QMenu>
#include <QMenuBar>
#include <QMessageBox>
#include <QIcon>
#include <QPainter>
#include <QProgressBar>
#include <QPushButton>
#include <QRadioButton>
#include <QScrollBar>
#include <QSlider>
#include <QSpinBox>
#include <QStyleFactory>
#include <QTabWidget>
#include <QTextEdit>
#include <QTimer>
#include <QTreeWidget>
#include <QVBoxLayout>

static void spin(int ms)
{
    QEventLoop l;
    QTimer::singleShot(ms, &l, &QEventLoop::quit);
    l.exec();
}

static QWidget *galleryWindow()
{
    auto *win = new QWidget;
    win->setWindowTitle(QStringLiteral("Widget Gallery"));
    auto *outer = new QVBoxLayout(win);
    auto *tabs = new QTabWidget;
    auto *page = new QWidget;
    auto *grid = new QGridLayout(page);
    auto *check = new QCheckBox(QStringLiteral("Checkbox"));
    check->setChecked(true);
    auto *combo = new QComboBox;
    combo->addItems({QStringLiteral("Combo box"), QStringLiteral("Second item")});
    auto *r1 = new QRadioButton(QStringLiteral("Radio button"));
    r1->setChecked(true);
    auto *r2 = new QRadioButton(QStringLiteral("Radio button"));
    auto *button = new QPushButton(QStringLiteral("Button"));
    auto *spinBox = new QSpinBox;
    auto *edit = new QLineEdit;
    edit->setPlaceholderText(QStringLiteral("Text Field"));
    auto *slider = new QSlider(Qt::Horizontal);
    slider->setValue(25);
    auto *progress = new QProgressBar;
    progress->setValue(70);
    auto *vs = new QScrollBar(Qt::Vertical);
    vs->setRange(0, 100);
    vs->setPageStep(40);
    auto *row = new QHBoxLayout;
    row->addWidget(button);
    row->addWidget(spinBox);
    grid->addWidget(check, 0, 0);
    grid->addWidget(combo, 0, 1);
    grid->addWidget(r1, 1, 0);
    grid->addLayout(row, 1, 1);
    grid->addWidget(r2, 2, 0);
    grid->addWidget(edit, 2, 1);
    grid->addWidget(slider, 3, 0);
    grid->addWidget(progress, 3, 1);
    grid->addWidget(vs, 0, 2, 4, 1);
    tabs->addTab(page, QStringLiteral("Tab 1"));
    tabs->addTab(new QWidget, QStringLiteral("Tab 2"));
    outer->addWidget(tabs);
    auto *box = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel);
    box->button(QDialogButtonBox::Ok)->setDefault(true);
    outer->addWidget(box);
    win->resize(470, 270);
    return win;
}

static QWidget *secondWindow()
{
    auto *win = new QWidget;
    win->setWindowTitle(QStringLiteral("More Controls"));
    auto *lay = new QGridLayout(win);
    auto *tree = new QTreeWidget;
    tree->setHeaderLabels({QStringLiteral("Name"), QStringLiteral("Date Modified"), QStringLiteral("Size")});
    const char *names[] = {"Applications", "Documents", "Library", "Movies", "Music", "Pictures", "Public", "Sites"};
    for (auto n : names) {
        auto *it = new QTreeWidgetItem(tree, {QString::fromLatin1(n), QStringLiteral("Today, 7:17 PM"), QStringLiteral("--")});
        new QTreeWidgetItem(it, {QStringLiteral("Item"), QStringLiteral("Yesterday"), QStringLiteral("4 KB")});
    }
    tree->setSortingEnabled(true);
    tree->sortByColumn(0, Qt::AscendingOrder);
    tree->setCurrentItem(tree->topLevelItem(2));
    tree->expandItem(tree->topLevelItem(1));
    tree->header()->resizeSection(0, 130);
    lay->addWidget(tree, 0, 0, 1, 2);

    auto *group = new QGroupBox(QStringLiteral("Icon Arrangement"));
    auto *gl = new QVBoxLayout(group);
    auto *n = new QRadioButton(QStringLiteral("None"));
    auto *a = new QRadioButton(QStringLiteral("Always snap to grid"));
    a->setChecked(true);
    auto *c = new QCheckBox(QStringLiteral("Show hard disks"));
    c->setCheckState(Qt::PartiallyChecked);
    c->setTristate(true);
    gl->addWidget(n);
    gl->addWidget(a);
    gl->addWidget(c);
    lay->addWidget(group, 1, 0);

    auto *form = new QFormLayout;
    auto *ec = new QComboBox;
    ec->setEditable(true);
    ec->addItem(QStringLiteral("Combination box"));
    form->addRow(QStringLiteral("Kind:"), ec);
    auto *ticks = new QSlider(Qt::Horizontal);
    ticks->setTickPosition(QSlider::TicksBelow);
    ticks->setTickInterval(20);
    ticks->setValue(40);
    form->addRow(QStringLiteral("Icon Size:"), ticks);
    auto *busy = new QProgressBar;
    busy->setRange(0, 0);
    busy->setTextVisible(false);
    form->addRow(QStringLiteral("Copying:"), busy);
    auto *disabled = new QPushButton(QStringLiteral("Disabled"));
    disabled->setEnabled(false);
    auto *more = new QPushButton(QStringLiteral("More Info…"));
    auto *br = new QHBoxLayout;
    br->addWidget(disabled);
    br->addWidget(more);
    form->addRow(br);
    lay->addLayout(form, 1, 1);
    auto *hs = new QScrollBar(Qt::Horizontal);
    hs->setRange(0, 100);
    hs->setPageStep(30);
    hs->setValue(20);
    lay->addWidget(hs, 2, 0, 1, 2);
    win->resize(520, 380);
    return win;
}

static QWidget *dockMdiWindow()
{
    auto *mw = new QMainWindow;
    mw->setWindowTitle(QStringLiteral("Docks, MDI and tabs"));
    auto *mdi = new QMdiArea;
    mdi->setBackground(QColor(110, 140, 190));
    auto addSub = [&](const QString &title, QTabWidget::TabPosition pos, QPoint at) {
        auto *tabs = new QTabWidget;
        tabs->setTabPosition(pos);
        auto *page = new QWidget;
        auto *l = new QVBoxLayout(page);
        l->addWidget(new QCheckBox(QStringLiteral("Show preview")));
        l->addWidget(new QRadioButton(QStringLiteral("Icons")));
        l->addStretch();
        tabs->addTab(page, QStringLiteral("General"));
        tabs->addTab(new QWidget, QStringLiteral("Advanced"));
        auto *sub = mdi->addSubWindow(tabs);
        sub->setWindowTitle(title);
        sub->resize(250, 170);
        sub->move(at);
        return sub;
    };
    addSub(QStringLiteral("Bottom tabs"), QTabWidget::South, QPoint(10, 10));
    auto *active = addSub(QStringLiteral("Left tabs"), QTabWidget::West, QPoint(150, 120));
    mw->setCentralWidget(mdi);
    mdi->setActiveSubWindow(active);
    auto *dock = new QDockWidget(QStringLiteral("Places"));
    auto *list = new QListWidget;
    for (auto n : {"Home", "Desktop", "Documents", "Downloads", "Music", "Pictures"})
        list->addItem(QString::fromLatin1(n));
    list->setCurrentRow(2);
    dock->setWidget(list);
    mw->addDockWidget(Qt::LeftDockWidgetArea, dock);
    mw->resize(620, 340);
    return mw;
}

static QWidget *dialogWindow()
{
    // a preferences pane laid out after HIG Figures 8-2 and 8-4: a titled group box, and a
    // flat group (title + separator line) instead of a second box
    auto *win = new QWidget;
    auto *lay = new QVBoxLayout(win);
    auto *box = new QGroupBox(QStringLiteral("Mail Cache"));
    auto *form = new QFormLayout(box);
    auto *once = new QRadioButton(QStringLiteral("Once per session"));
    once->setChecked(true);
    auto *rb = new QVBoxLayout;
    rb->addWidget(once);
    rb->addWidget(new QRadioButton(QStringLiteral("Never")));
    form->addRow(QStringLiteral("Update mailbox:"), rb);
    auto *size = new QHBoxLayout;
    auto *sz = new QSpinBox;
    sz->setValue(5);
    sz->setSuffix(QStringLiteral(" MB"));
    size->addWidget(sz);
    size->addWidget(new QPushButton(QStringLiteral("Empty Cache")));
    form->addRow(QStringLiteral("Size:"), size);
    lay->addWidget(box);
    auto *flat = new QGroupBox(QStringLiteral("Display sleep"));
    flat->setFlat(true);
    auto *fl = new QVBoxLayout(flat);
    auto *sep = new QCheckBox(QStringLiteral("Separate timing for display sleep"));
    sep->setChecked(true);
    fl->addWidget(sep);
    auto *sl = new QSlider(Qt::Horizontal);
    sl->setTickPosition(QSlider::TicksBelow);
    sl->setTickInterval(10);
    sl->setValue(60);
    fl->addWidget(sl);
    lay->addWidget(flat);
    win->resize(430, 300);
    return win;
}

static QWidget *alertWindow()
{
    auto *m = new QMessageBox;
    m->setIconPixmap(QIcon::fromTheme(QStringLiteral("system-file-manager")).pixmap(64, 64));
    m->setText(QStringLiteral("The document “Report” could not be saved."));
    m->setInformativeText(QStringLiteral("You don’t have permission to write to this folder. Choose another location, or ask the owner for access."));
    m->setStandardButtons(QMessageBox::Cancel | QMessageBox::Save);
    m->button(QMessageBox::Save)->setText(QStringLiteral("Save As…"));
    m->setDefaultButton(QMessageBox::Save);
    m->resize(440, 150);
    return m;
}

static QMenu *demoMenu(QWidget *parent)
{
    auto *m = new QMenu(parent);
    m->addAction(QStringLiteral("New Finder Window"))->setShortcut(QKeySequence(QStringLiteral("Ctrl+N")));
    auto *nf = m->addAction(QStringLiteral("New Folder"));
    nf->setShortcut(QKeySequence(QStringLiteral("Ctrl+Shift+N")));
    m->addAction(QStringLiteral("Open"))->setShortcut(QKeySequence(QStringLiteral("Ctrl+O")));
    m->addAction(QStringLiteral("Close Window"))->setShortcut(QKeySequence(QStringLiteral("Ctrl+W")));
    m->addSeparator();
    auto *si = m->addAction(QStringLiteral("Show Info"));
    si->setShortcut(QKeySequence(QStringLiteral("Ctrl+I")));
    auto *sub = m->addMenu(QStringLiteral("Recent Items"));
    sub->addAction(QStringLiteral("Report.odt"));
    m->addSeparator();
    auto *chk = m->addAction(QStringLiteral("Show Hidden Files"));
    chk->setCheckable(true);
    chk->setChecked(true);
    auto *dis = m->addAction(QStringLiteral("Eject"));
    dis->setEnabled(false);
    m->setActiveAction(nf);
    return m;
}

int main(int argc, char **argv)
{
    qputenv("QT_QPA_PLATFORM", "offscreen");
    QApplication app(argc, argv);
    const QStringList args = app.arguments();
    const QString out = args.value(1, QStringLiteral("."));
    const QString styleName = args.value(2, QStringLiteral("Pinstripe"));
    const QString colors = args.value(3);
    QDir().mkpath(out);

    QStyle *style = QStyleFactory::create(styleName);
    if (!style) {
        fprintf(stderr, "style %s not found; keys: %s\n", qPrintable(styleName), qPrintable(QStyleFactory::keys().join(QLatin1Char(','))));
        return 1;
    }
    QApplication::setStyle(style);
    if (!colors.isEmpty())
    {
        // the KDE platform theme hands its palette to the style for polishing; do the same
        QPalette pal = KColorScheme::createApplicationPalette(KSharedConfig::openConfig(colors, KConfig::SimpleConfig));
        style->polish(pal);
        QApplication::setPalette(pal);
    }
    // the 10.2 system font was Lucida Grande 13pt; use it if installed, else Luxi Sans
    // (same designers, Bigelow & Holmes), else DejaVu Sans
    QFont f;
    f.setFamilies({QStringLiteral("Lucida Grande"), QStringLiteral("Luxi Sans"), QStringLiteral("DejaVu Sans")});
    f.setPixelSize(13);
    QApplication::setFont(f);

    auto *dummy = new QWidget;
    dummy->resize(10, 10);

    auto render = [&](QWidget *w, const QString &name, bool active) {
        w->show();
        if (active)
            w->activateWindow();
        else {
            dummy->show();
            dummy->activateWindow();
        }
        spin(300);
        QPixmap pm = w->grab();
        pm.save(out + QLatin1Char('/') + name);
    };

    QWidget *g = galleryWindow();
    render(g, QStringLiteral("gallery-active.png"), true);
    render(g, QStringLiteral("gallery-inactive.png"), false);
    g->hide();
    QWidget *s = secondWindow();
    render(s, QStringLiteral("more-active.png"), true);
    s->hide();

    QIcon::setThemeSearchPaths({QDir::homePath() + QStringLiteral("/.local/share/icons"), QStringLiteral("/usr/share/icons")});
    QIcon::setThemeName(QStringLiteral("oxygen"));
    QWidget *dlg = dialogWindow();
    render(dlg, QStringLiteral("dialog.png"), true);
    dlg->hide();
    QWidget *al = alertWindow();
    render(al, QStringLiteral("alert.png"), true);
    al->hide();

    QWidget *dm = dockMdiWindow();
    render(dm, QStringLiteral("docks-mdi.png"), true);
    dm->hide();

    auto *host = new QWidget;
    auto *menu = demoMenu(host);
    menu->popup(QPoint(0, 0));
    spin(300);
    menu->grab().save(out + QStringLiteral("/menu.png"));
    menu->hide();

    auto *mbw = new QWidget;
    auto *mb = new QMenuBar(mbw);
    for (auto t : {"Finder", "File", "Edit", "View", "Go", "Window", "Help"})
        mb->addMenu(QString::fromLatin1(t));
    mbw->resize(420, mb->sizeHint().height());
    mb->resize(mbw->size());
    render(mbw, QStringLiteral("menubar.png"), true);
    return 0;
}
