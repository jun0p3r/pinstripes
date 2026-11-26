#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Papirus -> 10.2 Aqua Interactive Curator GUI.

Review the entire 6,676-icon upstream Papirus set auto-glassified in Mac OS X 10.2 Aqua style:
  - [Space]      Accept the auto-glassified icon (saves SVG + installs PNGs + records in accepted list)
  - [Backspace]  Reject the auto-glassified icon (adds to the hand-craft todo list: artwork/papirus-rejected.txt)
  - [Tab] / [M]  Toggle between Full Aqua Gel ("badge") and Popped-Out Brand Symbol Gel ("symbol")
  - [Left] / [Z] Undo / go back to the previous icon
  - [Right]      Skip for later

Progress is saved atomically after EVERY single keypress to:
  - artwork/papirus-curation.json         (full machine-readable progress state)
  - artwork/papirus-rejected.txt          (rejected icons list for hand-crafted skeuomorphic remakes)
  - artwork/papirus-accepted.txt          (accepted auto-glassified icons list)
  - artwork/papirus-accepted-svgs/<cat>/  (accepted 10.2 Aqua Gel SVGs wired into tools/make_icons.py)
"""
import json
import os
import subprocess
import sys
import threading
from collections import OrderedDict

# Load local Pinstripe Qt style plugin automatically if built
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_BIN = os.path.join(ROOT, "build", "bin")
if os.path.isdir(BUILD_BIN):
    cur_pp = os.environ.get("QT_PLUGIN_PATH", "")
    if BUILD_BIN not in cur_pp:
        os.environ["QT_PLUGIN_PATH"] = f"{BUILD_BIN}:{cur_pp}" if cur_pp else BUILD_BIN

sys.path.insert(0, os.path.join(ROOT, "tools"))
import glassify_papirus as gp  # noqa: E402

from PySide6.QtCore import QEvent, QObject, QRect, QSize, Qt, QTimer, Signal  # noqa: E402
from PySide6.QtGui import (  # noqa: E402
    QColor,
    QFont,
    QImage,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

ARTWORK_DIR = os.path.join(ROOT, "artwork")
STATE_JSON = os.path.join(ARTWORK_DIR, "papirus-curation.json")
REJECTED_TXT = os.path.join(ARTWORK_DIR, "papirus-rejected.txt")
ACCEPTED_TXT = os.path.join(ARTWORK_DIR, "papirus-accepted.txt")
ACCEPTED_SVGS_DIR = os.path.join(ARTWORK_DIR, "papirus-accepted-svgs")
LOCAL_THEME_DIR = os.path.expanduser("~/.local/share/icons/Oxygen-Pinstripe")
KCACHE_PATH = os.path.expanduser("~/.cache/icon-cache.kcache")

SIZES = (16, 22, 32, 48, 64, 128)


def png_bytes_to_pixmap(png_bytes):
    img = QImage.fromData(png_bytes, "PNG")
    return QPixmap.fromImage(img)


class IconStageWidget(QWidget):
    """Paints side-by-side Original vs Auto-Glassified (128, 64, 48, 32, 22, 16 px)
    on both Jaguar Pinstripes (top half) and Dark Dock Slate #282c34 (bottom half)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(680, 410)
        self.orig_128 = None
        self.orig_64 = None
        self.aqua_pixmaps = {}  # size -> QPixmap
        self.alt_64 = None
        self.mode_name = "badge"
        self.alt_mode_name = "symbol"
        self.can_sym = False
        self.status_badge = None  # "accepted" | "rejected" | None

    def set_bundle(self, bundle, mode, status):
        self.mode_name = mode
        self.alt_mode_name = "symbol" if mode == "badge" else "badge"
        self.status_badge = status
        if not bundle:
            self.orig_128 = None
            self.aqua_pixmaps = {}
            self.update()
            return
        self.orig_128 = png_bytes_to_pixmap(bundle["orig_128"])
        self.orig_64 = png_bytes_to_pixmap(bundle["orig_64"])
        self.can_sym = bundle["can_sym"]
        mode_map = bundle[mode]
        self.aqua_pixmaps = {sz: png_bytes_to_pixmap(mode_map[sz]) for sz in SIZES}
        self.alt_64 = png_bytes_to_pixmap(bundle[self.alt_mode_name][64])
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        w, h = self.width(), self.height()
        mid_y = int(h * 0.54)

        # Top half: Authentic Mac OS X 10.2 Jaguar 4-row pinstripe (255, 238, 230, 238)
        for y in range(mid_y):
            v = (255, 238, 230, 238)[y % 4]
            p.fillRect(0, y, w, 1, QColor(v, v, v))

        # Bottom half: Dark panel/dock slate (#282c34) like Franco's screenshot
        p.fillRect(0, mid_y, w, h - mid_y, QColor(40, 44, 52))
        p.setPen(QPen(QColor(150, 156, 166), 1))
        p.drawLine(0, mid_y, w, mid_y)
        p.drawRect(0, 0, w - 1, h - 1)

        if not self.orig_128 or not self.aqua_pixmaps:
            p.setPen(QColor(60, 65, 75))
            p.drawText(self.rect(), Qt.AlignCenter, "Loading Papirus icon…")
            return

        f_lbl = QFont(self.font())
        f_lbl.setPointSize(9)
        f_lbl.setBold(True)
        p.setFont(f_lbl)

        # Left column: Original Papirus SVG
        p.setPen(QColor(55, 62, 74))
        p.drawText(QRect(16, 10, 156, 20), Qt.AlignCenter, "Original Papirus")
        p.drawPixmap(30, 38, self.orig_128)
        p.setPen(QColor(185, 192, 205))
        p.drawText(QRect(16, mid_y + 10, 156, 20), Qt.AlignCenter, "Original (64 px)")
        p.drawPixmap(62, mid_y + 38, self.orig_64)

        # Vertical divider
        p.setPen(QPen(QColor(180, 186, 196, 150), 1))
        p.drawLine(188, 12, 188, h - 12)

        # Center Hero: Auto-Glassified 10.2 Aqua at 128, 64, 48, 32, 22, 16 px
        mode_title = "10.2 Aqua Gel — Full Icon" if self.mode_name == "badge" else "10.2 Aqua Gel — Popped-Out Symbol"
        p.setPen(QColor(18, 56, 128))
        p.drawText(QRect(200, 10, w - 350, 22), Qt.AlignLeft | Qt.AlignVCenter, f"{mode_title}  [Tab to switch]")

        # Status pill if already reviewed
        if self.status_badge in ("accepted", "rejected"):
            pill_col = QColor(30, 156, 72) if self.status_badge == "accepted" else QColor(204, 42, 42)
            p.setBrush(pill_col)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(w - 255, 9, 105, 22, 10, 10)
            p.setPen(QColor(255, 255, 255))
            p.drawText(QRect(w - 255, 9, 105, 22), Qt.AlignCenter, self.status_badge.upper())

        # Draw sizes left-to-right on Light Pinstripe (top) and Dark Slate (bottom)
        x_cursor = 206
        for sz in (128, 64, 48, 32, 22, 16):
            pm = self.aqua_pixmaps[sz]
            # Light pinstripe row (aligned to baseline y = mid_y - 26)
            py_top = max(36, mid_y - 26 - sz)
            p.drawPixmap(x_cursor, py_top, pm)
            p.setPen(QColor(80, 86, 98))
            p.drawText(QRect(x_cursor - 4, mid_y - 21, sz + 8, 16), Qt.AlignCenter, f"{sz}")

            # Dark dock row (aligned to baseline y = h - 28)
            py_bot = max(mid_y + 18, h - 30 - sz)
            p.drawPixmap(x_cursor, py_bot, pm)
            p.setPen(QColor(175, 182, 196))
            p.drawText(QRect(x_cursor - 4, h - 24, sz + 8, 16), Qt.AlignCenter, f"{sz}")

            x_cursor += sz + (18 if sz >= 48 else 14)

        # Right mini preview of alternate [Tab] mode
        alt_x = w - 122
        p.setPen(QPen(QColor(180, 186, 196, 130), 1))
        p.drawLine(alt_x - 14, 12, alt_x - 14, h - 12)
        p.setPen(QColor(70, 76, 88))
        alt_lbl = "Symbol [Tab]" if self.alt_mode_name == "symbol" else "Full [Tab]"
        p.drawText(QRect(alt_x - 8, 10, 118, 20), Qt.AlignCenter, alt_lbl)
        if self.alt_64:
            p.drawPixmap(alt_x + 18, 56, self.alt_64)
            p.drawPixmap(alt_x + 18, mid_y + 38, self.alt_64)


class PrefetchSignals(QObject):
    ready = Signal(str)


class PapirusCuratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oxygen Pinstripe — Papirus 10.2 Aqua Curator (Space = Accept, Backspace = Reject)")
        self.resize(1120, 680)

        os.makedirs(ARTWORK_DIR, exist_ok=True)
        os.makedirs(ACCEPTED_SVGS_DIR, exist_ok=True)

        # Load full Papirus catalog (all 6,676 unique masters + 6,138 aliases)
        self.all_items = gp.scan_entire_papirus()
        self.item_by_id = {it["id"]: it for it in self.all_items}

        # Load persistent progress state
        self.decisions = {}  # id -> {"status": "accepted"|"rejected", "mode": "badge"|"symbol"}
        self.history_stack = []
        self._load_progress()

        # Thread-safe LRU cache of rendered bundles: id -> dict
        self._cache = OrderedDict()
        self._cache_lock = threading.Lock()
        self._prefetch_sig = PrefetchSignals()
        self._prefetch_sig.ready.connect(self._on_prefetch_ready)

        self.filtered_items = []
        self.current_idx = 0
        self.current_mode = "badge"

        self._build_ui()
        self._setup_shortcuts()
        self._rebuild_lists()
        self._apply_filter(jump_to_unreviewed=True)

    # ------------------------------------------------------------------
    # Persistence (atomic save on every keypress!)
    # ------------------------------------------------------------------
    def _load_progress(self):
        if os.path.isfile(STATE_JSON):
            try:
                with open(STATE_JSON, encoding="utf-8") as f:
                    data = json.load(f)
                self.decisions = data.get("decisions", {})
            except Exception as e:
                print(f"Warning: could not read {STATE_JSON}: {e}", file=sys.stderr)

    def _save_progress(self):
        accepted_lines = []
        rejected_lines = []
        for item_id, rec in sorted(self.decisions.items()):
            it = self.item_by_id.get(item_id)
            al_str = f"  # aliases: {', '.join(it['aliases'][:8])}" if (it and it["aliases"]) else ""
            if rec["status"] == "accepted":
                accepted_lines.append(f"{item_id}\tmode={rec.get('mode', 'badge')}{al_str}")
            elif rec["status"] == "rejected":
                rejected_lines.append(f"{item_id}{al_str}")

        payload = {
            "total_papirus_masters": len(self.all_items),
            "accepted_count": len(accepted_lines),
            "rejected_count": len(rejected_lines),
            "decisions": self.decisions,
        }
        tmp_json = STATE_JSON + ".tmp"
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
        os.replace(tmp_json, STATE_JSON)

        tmp_rej = REJECTED_TXT + ".tmp"
        with open(tmp_rej, "w", encoding="utf-8") as f:
            f.write("# Rejected Auto-Glassified Papirus Icons (Needs Hand-Crafted 10.2 Skeuomorphic Icon)\n")
            for ln in rejected_lines:
                f.write(ln + "\n")
        os.replace(tmp_rej, REJECTED_TXT)

        tmp_acc = ACCEPTED_TXT + ".tmp"
        with open(tmp_acc, "w", encoding="utf-8") as f:
            f.write("# Accepted Auto-Glassified Papirus Icons\n")
            for ln in accepted_lines:
                f.write(ln + "\n")
        os.replace(tmp_acc, ACCEPTED_TXT)

    def _persist_accepted_icon_files(self, item, mode, bundle):
        """Write accepted 10.2 Aqua SVG to artwork/papirus-accepted-svgs/<cat>/<name>.svg
        and optionally install PNGs + symlinks into ~/.local/share/icons/Oxygen-Pinstripe."""
        cat = item["category"]
        name = item["name"]
        cat_dir = os.path.join(ACCEPTED_SVGS_DIR, cat)
        os.makedirs(cat_dir, exist_ok=True)
        svg_out = os.path.join(cat_dir, f"{name}.svg")
        with open(svg_out, "wb") as f:
            f.write(bundle[f"{mode}_svg"])

        if self.chk_live_install.isChecked() and os.path.isdir(LOCAL_THEME_DIR):
            # Do not overwrite our 66 hand-crafted ARTWORK_ICONS!
            handcrafted = os.path.join(ARTWORK_DIR, "aqua-icons", f"{name}.svg")
            if not os.path.isfile(handcrafted):
                for sz in SIZES:
                    d = os.path.join(LOCAL_THEME_DIR, f"{sz}x{sz}", cat)
                    os.makedirs(d, exist_ok=True)
                    png_p = os.path.join(d, f"{name}.png")
                    with open(png_p, "wb") as f:
                        f.write(bundle[mode][sz])
                    for al in item["aliases"]:
                        al_p = os.path.join(d, f"{al}.png")
                        if not os.path.lexists(al_p):
                            os.symlink(f"{name}.png", al_p)

    def _remove_accepted_icon_files(self, item):
        svg_out = os.path.join(ACCEPTED_SVGS_DIR, item["category"], f"{item['name']}.svg")
        if os.path.isfile(svg_out):
            os.remove(svg_out)

    # ------------------------------------------------------------------
    # Rendering & Background Prefetching
    # ------------------------------------------------------------------
    def _compute_bundle(self, item):
        with self._cache_lock:
            if item["id"] in self._cache:
                self._cache.move_to_end(item["id"])
                return self._cache[item["id"]]

        svg_p = item["svg_path"]
        with open(svg_p, "rb") as f:
            raw_bytes = f.read()
        orig_128 = gp.render_svg_bytes_to_png_bytes(raw_bytes, 128)
        orig_64 = gp.render_svg_bytes_to_png_bytes(raw_bytes, 64)
        can_sym = gp.can_extract_symbol(svg_p, item["category"])

        badge_svg = gp.glassify_svg_to_bytes(svg_p, mode="badge")
        sym_svg = gp.glassify_svg_to_bytes(svg_p, mode="symbol")
        badge_map = {sz: gp.render_svg_bytes_to_png_bytes(badge_svg, sz) for sz in SIZES}
        sym_map = {sz: gp.render_svg_bytes_to_png_bytes(sym_svg, sz) for sz in SIZES}

        bundle = {
            "orig_128": orig_128,
            "orig_64": orig_64,
            "can_sym": can_sym,
            "badge_svg": badge_svg,
            "symbol_svg": sym_svg,
            "badge": badge_map,
            "symbol": sym_map,
        }
        with self._cache_lock:
            self._cache[item["id"]] = bundle
            while len(self._cache) > 48:
                self._cache.popitem(last=False)
        return bundle

    def _trigger_prefetch(self):
        # Pre-render next 14 items in background thread so Space/Backspace feels instantaneous
        upcoming = self.filtered_items[self.current_idx:self.current_idx + 14]

        def worker():
            for it in upcoming:
                with self._cache_lock:
                    already = it["id"] in self._cache
                if not already:
                    try:
                        self._compute_bundle(it)
                        self._prefetch_sig.ready.emit(it["id"])
                    except Exception:
                        pass

        threading.Thread(target=worker, daemon=True).start()

    def _on_prefetch_ready(self, item_id):
        if self.filtered_items and 0 <= self.current_idx < len(self.filtered_items):
            if self.filtered_items[self.current_idx]["id"] == item_id:
                self._refresh_stage()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_lay = QVBoxLayout(central)
        root_lay.setContentsMargins(16, 14, 16, 14)
        root_lay.setSpacing(10)

        # Top Filter & Progress Bar
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Queue:"))
        self.cmb_filter = QComboBox()
        self.cmb_filter.addItems([
            f"All Papirus Icons ({len(self.all_items)})",
            "Unreviewed Only",
            "Installed on this PC First",
            "Category: apps",
            "Category: mimetypes",
            "Category: places",
            "Category: devices",
            "Category: status",
            "Category: emblems / emotes / actions",
            "Accepted Only",
            "Rejected (Hand-Craft List) Only",
        ])
        self.cmb_filter.currentIndexChanged.connect(lambda _: self._apply_filter(jump_to_unreviewed=True))
        top_row.addWidget(self.cmb_filter)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search icon or alias (press Esc to clear focus so Space/Backspace work)…")
        self.txt_search.textChanged.connect(lambda _: self._apply_filter(jump_to_unreviewed=False))
        top_row.addWidget(self.txt_search, 1)

        self.chk_live_install = QCheckBox("Live-install accepted to ~/.local")
        self.chk_live_install.setChecked(True)
        self.chk_live_install.setFocusPolicy(Qt.NoFocus)
        top_row.addWidget(self.chk_live_install)

        root_lay.addLayout(top_row)

        # Progress bar + counters
        prog_row = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setRange(0, len(self.all_items))
        prog_row.addWidget(self.progress, 1)
        self.lbl_counts = QLabel()
        prog_row.addWidget(self.lbl_counts)
        root_lay.addLayout(prog_row)

        # Main Splitter: Left/Center Stage + Right Rejected/Accepted Lists
        splitter = QSplitter(Qt.Horizontal)

        left_pane = QWidget()
        left_lay = QVBoxLayout(left_pane)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(8)

        self.lbl_title = QLabel()
        f_title = QFont(self.font())
        f_title.setPointSize(13)
        f_title.setBold(True)
        self.lbl_title.setFont(f_title)
        left_lay.addWidget(self.lbl_title)

        self.lbl_meta = QLabel()
        self.lbl_meta.setWordWrap(True)
        left_lay.addWidget(self.lbl_meta)

        self.stage = IconStageWidget()
        left_lay.addWidget(self.stage, 1)

        # Action Controls Row
        btn_row = QHBoxLayout()
        self.btn_undo = QPushButton("← Undo (Z)")
        self.btn_undo.setFocusPolicy(Qt.NoFocus)
        self.btn_undo.clicked.connect(self.action_undo)

        self.btn_reject = QPushButton("⌫ Reject → Add to Hand-Craft List (Backspace)")
        self.btn_reject.setFocusPolicy(Qt.NoFocus)
        self.btn_reject.clicked.connect(self.action_reject)

        self.btn_mode = QPushButton("⇄ Switch Full / Symbol Gel (Tab)")
        self.btn_mode.setFocusPolicy(Qt.NoFocus)
        self.btn_mode.clicked.connect(self.action_toggle_mode)

        self.btn_skip = QPushButton("Skip (→)")
        self.btn_skip.setFocusPolicy(Qt.NoFocus)
        self.btn_skip.clicked.connect(self.action_skip)

        self.btn_accept = QPushButton("✓ Accept Auto-Glassified (Space)")
        self.btn_accept.setDefault(True)
        self.btn_accept.setFocusPolicy(Qt.NoFocus)
        self.btn_accept.clicked.connect(self.action_accept)

        for b in (self.btn_undo, self.btn_reject, self.btn_mode, self.btn_skip, self.btn_accept):
            btn_row.addWidget(b)
        left_lay.addLayout(btn_row)

        splitter.addWidget(left_pane)

        # Right Pane: Live Rejected List ("put it in a list") & Accepted List
        right_pane = QWidget()
        right_lay = QVBoxLayout(right_pane)
        right_lay.setContentsMargins(6, 0, 0, 0)
        self.tabs = QTabWidget()
        self.tabs.setFocusPolicy(Qt.NoFocus)

        self.lst_rejected = QListWidget()
        self.lst_rejected.setFocusPolicy(Qt.NoFocus)
        self.lst_rejected.itemClicked.connect(self._on_list_item_clicked)
        self.tabs.addTab(self.lst_rejected, "Rejected List (0)")

        self.lst_accepted = QListWidget()
        self.lst_accepted.setFocusPolicy(Qt.NoFocus)
        self.lst_accepted.itemClicked.connect(self._on_list_item_clicked)
        self.tabs.addTab(self.lst_accepted, "Accepted List (0)")

        right_lay.addWidget(self.tabs, 1)

        flush_btn = QPushButton("Flush KDE Icon Cache Now")
        flush_btn.setFocusPolicy(Qt.NoFocus)
        flush_btn.clicked.connect(self._flush_kde_cache)
        right_lay.addWidget(flush_btn)

        lbl_paths = QLabel(f"Auto-saved on every keypress:\n• {os.path.relpath(REJECTED_TXT, ROOT)}\n• {os.path.relpath(STATE_JSON, ROOT)}")
        f_small = QFont(self.font())
        f_small.setPointSize(9)
        lbl_paths.setFont(f_small)
        right_lay.addWidget(lbl_paths)

        splitter.addWidget(right_pane)
        splitter.setSizes([790, 300])
        root_lay.addWidget(splitter, 1)

    def _setup_shortcuts(self):
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Escape:
                self.txt_search.clearFocus()
                self.cmb_filter.clearFocus()
                self.stage.setFocus()
                return True
            if not self.txt_search.hasFocus():
                if key == Qt.Key_Space and not event.isAutoRepeat():
                    self.action_accept()
                    return True
                if key in (Qt.Key_Backspace, Qt.Key_Delete) and not event.isAutoRepeat():
                    self.action_reject()
                    return True
                if key in (Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_M):
                    self.action_toggle_mode()
                    return True
                if key == Qt.Key_Z:
                    self.action_undo()
                    return True
                if key == Qt.Key_Left:
                    self.action_prev()
                    return True
                if key in (Qt.Key_Right, Qt.Key_S):
                    self.action_skip()
                    return True
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    # Filtering & Navigation
    # ------------------------------------------------------------------
    def _apply_filter(self, jump_to_unreviewed=False):
        mode_idx = self.cmb_filter.currentIndex()
        q = self.txt_search.text().strip().lower()

        out = []
        for it in self.all_items:
            st = self.decisions.get(it["id"], {}).get("status")
            if mode_idx == 1 and st is not None:
                continue
            elif mode_idx == 2 and not it["installed"]:
                continue
            elif mode_idx == 3 and it["category"] != "apps":
                continue
            elif mode_idx == 4 and it["category"] != "mimetypes":
                continue
            elif mode_idx == 5 and it["category"] != "places":
                continue
            elif mode_idx == 6 and it["category"] != "devices":
                continue
            elif mode_idx == 7 and it["category"] != "status":
                continue
            elif mode_idx == 8 and it["category"] not in ("emblems", "emotes", "actions", "animations"):
                continue
            elif mode_idx == 9 and st != "accepted":
                continue
            elif mode_idx == 10 and st != "rejected":
                continue

            if q:
                hay = f"{it['id']} {' '.join(it['aliases'])}".lower()
                if q not in hay:
                    continue
            out.append(it)

        self.filtered_items = out
        self.current_idx = 0
        if jump_to_unreviewed:
            for i, it in enumerate(self.filtered_items):
                if it["id"] not in self.decisions:
                    self.current_idx = i
                    break
        self._select_current_item()

    def _select_current_item(self):
        self._update_counters()
        if not self.filtered_items:
            self.lbl_title.setText("No icons match current filter!")
            self.lbl_meta.setText("")
            self.stage.set_bundle(None, "badge", None)
            return
        self.current_idx = max(0, min(len(self.filtered_items) - 1, self.current_idx))
        it = self.filtered_items[self.current_idx]
        bundle = self._compute_bundle(it)

        # Pick saved mode if already decided, else auto-pick symbol mode when strictly clean 2-part app badge
        saved = self.decisions.get(it["id"])
        if saved:
            self.current_mode = saved.get("mode", "badge")
        else:
            self.current_mode = "symbol" if bundle["can_sym"] else "badge"

        self._refresh_stage()
        self._trigger_prefetch()

    def _refresh_stage(self):
        if not self.filtered_items:
            return
        it = self.filtered_items[self.current_idx]
        bundle = self._compute_bundle(it)
        st = self.decisions.get(it["id"], {}).get("status")
        inst_tag = "  ★ Installed on this PC" if it["installed"] else ""
        self.lbl_title.setText(
            f"[{self.current_idx + 1:,} / {len(self.filtered_items):,}]   {it['category']} / {it['name']}{inst_tag}"
        )
        aliases_preview = ", ".join(it["aliases"][:12])
        if len(it["aliases"]) > 12:
            aliases_preview += f" (+{len(it['aliases']) - 12} more)"
        self.lbl_meta.setText(
            f"Source: Papirus/{it['size_dir']}/{it['category']}/{it['name']}.svg"
            + (f"   |   Aliases: {aliases_preview}" if aliases_preview else "   |   Aliases: none")
        )
        self.stage.set_bundle(bundle, self.current_mode, st)

    def _update_counters(self):
        n_acc = sum(1 for r in self.decisions.values() if r["status"] == "accepted")
        n_rej = sum(1 for r in self.decisions.values() if r["status"] == "rejected")
        n_tot = n_acc + n_rej
        self.progress.setValue(n_tot)
        self.lbl_counts.setText(
            f"Reviewed: {n_tot:,} / {len(self.all_items):,}   |   ✓ Accepted: {n_acc:,}   |   ⌫ Rejected: {n_rej:,}"
        )
        self.tabs.setTabText(0, f"Rejected List ({n_rej:,})")
        self.tabs.setTabText(1, f"Accepted List ({n_acc:,})")

    def _rebuild_lists(self):
        self.lst_rejected.clear()
        self.lst_accepted.clear()
        for item_id, rec in self.decisions.items():
            lw = self.lst_rejected if rec["status"] == "rejected" else self.lst_accepted
            qli = QListWidgetItem(item_id)
            qli.setData(Qt.UserRole, item_id)
            lw.addItem(qli)
        self._update_counters()

    def _upsert_side_list(self, item_id, status):
        # Remove existing entry from both lists, then append to target list
        for lw in (self.lst_rejected, self.lst_accepted):
            for i in range(lw.count() - 1, -1, -1):
                if lw.item(i).data(Qt.UserRole) == item_id:
                    lw.takeItem(i)
        if status in ("rejected", "accepted"):
            target = self.lst_rejected if status == "rejected" else self.lst_accepted
            qli = QListWidgetItem(item_id)
            qli.setData(Qt.UserRole, item_id)
            target.insertItem(0, qli)

    def _on_list_item_clicked(self, qli):
        item_id = qli.data(Qt.UserRole)
        for i, it in enumerate(self.filtered_items):
            if it["id"] == item_id:
                self.current_idx = i
                self._select_current_item()
                return
        # Switch filter to All if not in current filter
        self.cmb_filter.setCurrentIndex(0)
        for i, it in enumerate(self.filtered_items):
            if it["id"] == item_id:
                self.current_idx = i
                self._select_current_item()
                return

    # ------------------------------------------------------------------
    # Key Actions: Space (Accept), Backspace (Reject), Tab (Mode), Z (Undo)
    # ------------------------------------------------------------------
    def action_accept(self):
        if not self.filtered_items:
            return
        it = self.filtered_items[self.current_idx]
        prev = self.decisions.get(it["id"])
        self.history_stack.append((self.current_idx, it["id"], prev))

        bundle = self._compute_bundle(it)
        self.decisions[it["id"]] = {"status": "accepted", "mode": self.current_mode}
        self._save_progress()
        self._persist_accepted_icon_files(it, self.current_mode, bundle)
        self._upsert_side_list(it["id"], "accepted")
        self._advance_next()

    def action_reject(self):
        if not self.filtered_items:
            return
        it = self.filtered_items[self.current_idx]
        prev = self.decisions.get(it["id"])
        self.history_stack.append((self.current_idx, it["id"], prev))

        self.decisions[it["id"]] = {"status": "rejected", "mode": self.current_mode}
        self._remove_accepted_icon_files(it)
        self._save_progress()
        self._upsert_side_list(it["id"], "rejected")
        self._advance_next()

    def action_toggle_mode(self):
        self.current_mode = "symbol" if self.current_mode == "badge" else "badge"
        self._refresh_stage()

    def action_skip(self):
        if not self.filtered_items:
            return
        if self.current_idx + 1 < len(self.filtered_items):
            self.current_idx += 1
            self._select_current_item()

    def action_prev(self):
        if not self.filtered_items:
            return
        if self.current_idx > 0:
            self.current_idx -= 1
            self._select_current_item()

    def action_undo(self):
        if not self.history_stack:
            self.action_prev()
            return
        prev_idx, item_id, prev_rec = self.history_stack.pop()
        it = self.item_by_id.get(item_id)
        if prev_rec is None:
            self.decisions.pop(item_id, None)
            if it:
                self._remove_accepted_icon_files(it)
            self._upsert_side_list(item_id, None)
        else:
            self.decisions[item_id] = prev_rec
            if it and prev_rec["status"] == "accepted":
                b = self._compute_bundle(it)
                self._persist_accepted_icon_files(it, prev_rec.get("mode", "badge"), b)
            elif it:
                self._remove_accepted_icon_files(it)
            self._upsert_side_list(item_id, prev_rec["status"])

        self._save_progress()
        # Jump back to undone item
        for i, cand in enumerate(self.filtered_items):
            if cand["id"] == item_id:
                self.current_idx = i
                self._select_current_item()
                return
        self._update_counters()

    def _advance_next(self):
        # If viewing "Unreviewed Only", current item drops out when refiltered, else advance index
        if self.cmb_filter.currentIndex() == 1:
            old_idx = self.current_idx
            self.filtered_items = [x for x in self.filtered_items if x["id"] not in self.decisions]
            self.current_idx = min(old_idx, max(0, len(self.filtered_items) - 1))
        elif self.current_idx + 1 < len(self.filtered_items):
            self.current_idx += 1
        self._select_current_item()

    def _flush_kde_cache(self):
        if os.path.exists(KCACHE_PATH):
            try:
                os.remove(KCACHE_PATH)
            except OSError:
                pass
        QMessageBox.information(
            self,
            "KDE Icon Cache Cleared",
            "Removed ~/.cache/icon-cache.kcache.\nToggle the icon theme in System Settings to refresh running apps.",
        )


def main():
    app = QApplication(sys.argv)
    if "Pinstripe" in QApplication.style().objectName() or True:
        try:
            app.setStyle("Pinstripe")
        except Exception:
            pass
    win = PapirusCuratorWindow()
    win.show()
    # Optional offscreen screenshot hook for automated verification
    shot = os.environ.get("CURATOR_SCREENSHOT")
    if shot:
        def snap_and_quit():
            win.grab().save(shot)
            app.quit()
        QTimer.singleShot(350, snap_and_quit)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
