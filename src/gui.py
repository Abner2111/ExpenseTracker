#!/usr/bin/env python3
"""
ExpenseTracker GUI — Modern redesign
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
from datetime import datetime
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import ExpenseTracker
except ImportError as e:
    print(f"Error importing modules: {e}")

try:
    from database import ExpenseDatabase
    _db_available = True
except ImportError:
    _db_available = False


# ── Colour palette ────────────────────────────────────────────────────────────
C = {
    "sidebar":              "#1e293b",
    "sidebar_hover":        "#2d3f55",
    "sidebar_active":       "#334155",
    "sidebar_text":         "#94a3b8",
    "sidebar_active_text":  "#f8fafc",
    "bg":                   "#f1f5f9",
    "card":                 "#ffffff",
    "primary":              "#6366f1",
    "primary_dark":         "#4f46e5",
    "success":              "#10b981",
    "error":                "#ef4444",
    "warning":              "#f59e0b",
    "info":                 "#3b82f6",
    "text":                 "#0f172a",
    "text_dim":             "#64748b",
    "text_muted":           "#94a3b8",
    "border":               "#e2e8f0",
    "statusbar":            "#0f172a",
    "statusbar_text":       "#64748b",
    # log terminal palette
    "log_bg":               "#0f172a",
    "log_fg":               "#e2e8f0",
    "log_success":          "#34d399",
    "log_error":            "#f87171",
    "log_info":             "#60a5fa",
    "log_warn":             "#fbbf24",
    "log_dim":              "#64748b",
}


class ExpenseTrackerGUI:
    SIDEBAR_W = 210

    def __init__(self, root):
        self.root = root
        self.root.title("ExpenseTracker")
        self.root.geometry("1120x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=C["bg"])
        self.root.resizable(True, True)

        self.is_running = False
        self.config = self.load_config()

        self._build_layout()
        self._show_page("run")

    # ── Layout scaffold ───────────────────────────────────────────────────────
    def _build_layout(self):
        # Status bar at very bottom
        self.statusbar = tk.Frame(self.root, bg=C["statusbar"], height=28)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.statusbar.pack_propagate(False)

        self.status_var = tk.StringVar(value="Listo")
        tk.Label(self.statusbar, textvariable=self.status_var,
                 bg=C["statusbar"], fg=C["statusbar_text"],
                 font=("Segoe UI", 9), padx=14).pack(side=tk.LEFT, anchor="w")

        self.time_var = tk.StringVar()
        tk.Label(self.statusbar, textvariable=self.time_var,
                 bg=C["statusbar"], fg=C["statusbar_text"],
                 font=("Segoe UI", 9), padx=14).pack(side=tk.RIGHT, anchor="e")
        self._tick_clock()

        # Sidebar | main
        self.sidebar = tk.Frame(self.root, bg=C["sidebar"], width=self.SIDEBAR_W)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.main_area = tk.Frame(self.root, bg=C["bg"])
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_pages()

    def _tick_clock(self):
        self.time_var.set(datetime.now().strftime("%Y-%m-%d   %H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        # Logo / branding
        logo = tk.Frame(self.sidebar, bg=C["sidebar"])
        logo.pack(fill=tk.X, pady=(28, 12))
        tk.Label(logo, text="💰", bg=C["sidebar"], fg="white",
                 font=("Segoe UI", 28)).pack()
        tk.Label(logo, text="ExpenseTracker", bg=C["sidebar"],
                 fg="white", font=("Segoe UI", 13, "bold")).pack(pady=(4, 0))
        tk.Label(logo, text="BAC Credomatic", bg=C["sidebar"],
                 fg=C["sidebar_text"], font=("Segoe UI", 9)).pack(pady=(2, 0))

        # Divider
        tk.Frame(self.sidebar, bg="#334155", height=1).pack(
            fill=tk.X, padx=18, pady=(12, 8))

        # Nav buttons
        self._nav_btns = {}
        for key, icon, label in [
            ("run",    "▶",  "  Ejecutar"),
            ("config", "⚙", "  Configuración"),
            ("db",     "🗃", "  Base de datos"),
            ("status", "📋", "  Estado & Logs"),
        ]:
            f = tk.Frame(self.sidebar, bg=C["sidebar"])
            f.pack(fill=tk.X)
            btn = tk.Button(
                f, text=f" {icon}{label}",
                anchor="w", bg=C["sidebar"], fg=C["sidebar_text"],
                activebackground=C["sidebar_hover"], activeforeground="white",
                relief="flat", bd=0, cursor="hand2",
                font=("Segoe UI", 11), padx=22, pady=13,
                command=lambda k=key: self._show_page(k),
            )
            btn.pack(fill=tk.X)
            # Hover binding
            btn.bind("<Enter>", lambda e, b=btn, k=key: b.config(
                bg=C["sidebar_active"] if self._active == k else C["sidebar_hover"],
                fg="white"))
            btn.bind("<Leave>", lambda e, b=btn, k=key: b.config(
                bg=C["sidebar_active"] if self._active == k else C["sidebar"],
                fg=C["sidebar_active_text"] if self._active == k else C["sidebar_text"]))
            self._nav_btns[key] = btn

        self._active = None

        # Version
        tk.Label(self.sidebar, text="v2.0", bg=C["sidebar"],
                 fg=C["sidebar_text"], font=("Segoe UI", 8)).pack(
            side=tk.BOTTOM, pady=14)

    def _show_page(self, key):
        self._active = key
        for k, btn in self._nav_btns.items():
            if k == key:
                btn.config(bg=C["sidebar_active"], fg=C["sidebar_active_text"])
            else:
                btn.config(bg=C["sidebar"], fg=C["sidebar_text"])
        for k, frame in self._pages.items():
            if k == key:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()

    # ── Pages ─────────────────────────────────────────────────────────────────
    def _build_pages(self):
        self._pages = {}
        for key, builder in [
            ("run",    self._build_run_page),
            ("config", self._build_config_page),
            ("db",     self._build_db_page),
            ("status", self._build_status_page),
        ]:
            f = tk.Frame(self.main_area, bg=C["bg"])
            builder(f)
            self._pages[key] = f

    # ── Widget helpers ────────────────────────────────────────────────────────
    def _page_header(self, parent, title, subtitle=""):
        hdr = tk.Frame(parent, bg=C["bg"])
        hdr.pack(fill=tk.X, padx=28, pady=(26, 0))
        tk.Label(hdr, text=title, bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(hdr, text=subtitle, bg=C["bg"], fg=C["text_dim"],
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 0))
        tk.Frame(parent, bg=C["border"], height=1).pack(
            fill=tk.X, padx=28, pady=(14, 0))

    def _card(self, parent, title=None, pady_inner=18, padx_inner=22):
        outer = tk.Frame(parent, bg=C["card"], bd=0,
                         highlightthickness=1,
                         highlightbackground=C["border"])
        if title:
            th = tk.Frame(outer, bg=C["card"])
            th.pack(fill=tk.X, padx=padx_inner, pady=(15, 0))
            tk.Label(th, text=title, bg=C["card"], fg=C["text"],
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
            tk.Frame(outer, bg=C["border"], height=1).pack(
                fill=tk.X, padx=padx_inner, pady=(10, 0))
        inner = tk.Frame(outer, bg=C["card"])
        inner.pack(fill=tk.BOTH, expand=True,
                   padx=padx_inner, pady=pady_inner)
        return outer, inner

    def _btn(self, parent, text, bg, command,
             font=("Segoe UI", 10, "bold"), padx=18, pady=8, state=tk.NORMAL):
        b = tk.Button(parent, text=text, fg="white", bg=bg,
                      activeforeground="white", activebackground=bg,
                      relief="flat", bd=0, cursor="hand2",
                      font=font, padx=padx, pady=pady,
                      command=command, state=state)
        # Simple hover darken
        darker = self._darken(bg)
        b.bind("<Enter>", lambda e: b.config(bg=darker))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _ghost_btn(self, parent, text, command,
                   font=("Segoe UI", 9)):
        b = tk.Button(parent, text=text, fg=C["text_dim"], bg=C["bg"],
                      activeforeground=C["text"], activebackground=C["border"],
                      relief="flat", bd=0, cursor="hand2",
                      font=font, padx=10, pady=6,
                      highlightthickness=1,
                      highlightbackground=C["border"],
                      command=command)
        return b

    @staticmethod
    def _darken(hex_color, amount=20):
        """Return a slightly darker hex colour."""
        try:
            r = max(0, int(hex_color[1:3], 16) - amount)
            g = max(0, int(hex_color[3:5], 16) - amount)
            b = max(0, int(hex_color[5:7], 16) - amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    def _entry(self, parent, var, mono=False, height=8):
        e = tk.Entry(
            parent, textvariable=var,
            font=("Consolas", 10) if mono else ("Segoe UI", 10),
            bg="#f8fafc", fg=C["text"],
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=C["border"],
            highlightcolor=C["primary"],
            insertbackground=C["primary"],
        )
        e.pack(fill=tk.X, ipady=height)
        return e

    def _field_group(self, parent, label, var, hint="", mono=False):
        tk.Label(parent, text=label, bg=C["card"], fg=C["text_dim"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self._entry(parent, var, mono=mono)
        if hint:
            tk.Label(parent, text=hint, bg=C["card"], fg=C["text_muted"],
                     font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 0))

    # ── Log terminal helpers ──────────────────────────────────────────────────
    def _make_log_widget(self, parent):
        widget = tk.Text(
            parent,
            font=("Consolas", 10),
            bg=C["log_bg"], fg=C["log_fg"],
            relief="flat", bd=0, wrap=tk.WORD,
            padx=14, pady=10, cursor="arrow",
            selectbackground=C["primary"],
            insertbackground="white",
            state=tk.DISABLED,
        )
        vsb = ttk.Scrollbar(parent, orient="vertical",
                             command=widget.yview)
        widget.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        widget.pack(fill=tk.BOTH, expand=True)

        for tag, fg in [
            ("success", C["log_success"]),
            ("error",   C["log_error"]),
            ("info",    C["log_info"]),
            ("warn",    C["log_warn"]),
            ("dim",     C["log_dim"]),
            ("bold",    None),
        ]:
            kw = {"foreground": fg} if fg else {}
            if tag == "bold":
                kw["font"] = ("Consolas", 10, "bold")
            widget.tag_configure(tag, **kw)
        return widget

    def _log_write(self, widget, text, tag=None):
        widget.config(state=tk.NORMAL)
        if tag:
            widget.insert(tk.END, text, tag)
        else:
            widget.insert(tk.END, text)
        widget.see(tk.END)
        widget.config(state=tk.DISABLED)

    def _log(self, text, tag=None):
        self._log_write(self.results_text, text, tag)

    def _log_to_history(self, text, tag=None):
        self._log_write(self.logs_text, text, tag)

    def _clear_log(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)

    # ── Run page ──────────────────────────────────────────────────────────────
    def _build_run_page(self, parent):
        self._page_header(parent, "Ejecutar Tracker",
                          "Procesa correos de notificación de BAC Credomatic")

        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=28, pady=20)

        # ── Left panel ────────────────────────────────────────────────────────
        left = tk.Frame(body, bg=C["bg"])
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16))

        # Controls card
        ctrl_outer, ctrl = self._card(left, "Control")
        ctrl_outer.pack(fill=tk.X, pady=(0, 14))

        self.run_btn = self._btn(
            ctrl, "▶   Ejecutar Tracker", C["primary"],
            self.run_tracker,
            font=("Segoe UI", 13, "bold"), padx=20, pady=12,
        )
        self.run_btn.pack(fill=tk.X)

        self.stop_btn = self._btn(
            ctrl, "⏹   Detener", C["error"],
            self.stop_tracker,
            font=("Segoe UI", 11), pady=9, state=tk.DISABLED,
        )
        self.stop_btn.pack(fill=tk.X, pady=(8, 12))

        # Progress bar
        style = ttk.Style()
        style.configure("Run.Horizontal.TProgressbar",
                        troughcolor=C["border"],
                        background=C["primary"],
                        bordercolor=C["border"],
                        lightcolor=C["primary"],
                        darkcolor=C["primary"])
        self.progress = ttk.Progressbar(
            ctrl, mode="indeterminate",
            style="Run.Horizontal.TProgressbar",
        )
        self.progress.pack(fill=tk.X, pady=(0, 10))

        self.run_status_var = tk.StringVar(value="✅  Listo para ejecutar")
        tk.Label(ctrl, textvariable=self.run_status_var,
                 bg=C["card"], fg=C["text_dim"],
                 font=("Segoe UI", 10),
                 anchor="w", wraplength=190,
                 justify="left").pack(anchor="w")

        # Active config card
        cfg_outer, cfg = self._card(left, "Configuración activa")
        cfg_outer.pack(fill=tk.X)

        for attr in ("cfg_sheet_lbl", "cfg_tab_lbl", "cfg_filter_lbl"):
            lbl = tk.Label(cfg, text="", bg=C["card"], fg=C["text_dim"],
                           font=("Segoe UI", 9), anchor="w",
                           wraplength=175, justify="left")
            lbl.pack(anchor="w", pady=2)
            setattr(self, attr, lbl)
        self._update_run_config_display()

        # ── Right panel: log terminal ─────────────────────────────────────────
        right = tk.Frame(body, bg=C["bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_outer, log_inner = self._card(right, "Resultados")
        log_outer.pack(fill=tk.BOTH, expand=True)
        log_inner.pack_configure(pady=10)

        top_bar = tk.Frame(log_inner, bg=C["card"])
        top_bar.pack(fill=tk.X, pady=(0, 6))
        tk.Label(top_bar, text="● LIVE LOG", bg=C["card"],
                 fg=C["log_success"], font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT)
        self._ghost_btn(top_bar, "Limpiar", self._clear_log,
                        font=("Segoe UI", 8)).pack(side=tk.RIGHT)

        self.results_text = self._make_log_widget(log_inner)

        self._log("  Bienvenido a ExpenseTracker\n\n", "info")
        self._log("  1.  Configura tu Google Sheet en 'Configuración'\n", "dim")
        self._log("  2.  Haz clic en '▶ Ejecutar Tracker'\n", "dim")
        self._log("  3.  Si el token expiró, el navegador pedirá autenticación\n\n", "dim")

    # ── Config page ───────────────────────────────────────────────────────────
    def _build_config_page(self, parent):
        self._page_header(parent, "Configuración",
                          "Conecta tu Google Sheet y ajusta los filtros")

        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=28, pady=20)

        # Google Sheets card
        gs_outer, gs = self._card(body, "Google Sheets")
        gs_outer.pack(fill=tk.X, pady=(0, 14))

        # URL / ID row
        tk.Label(gs, text="URL o ID de Google Sheet", bg=C["card"],
                 fg=C["text_dim"], font=("Segoe UI", 9, "bold")).pack(anchor="w")

        url_row = tk.Frame(gs, bg=C["card"])
        url_row.pack(fill=tk.X, pady=(5, 2))

        self.sheet_id_var = tk.StringVar(value=self.config.get("google_sheet_id", ""))
        self.sheet_id_var.trace("w", self.on_sheet_id_change)

        self.sheet_id_entry = tk.Entry(
            url_row, textvariable=self.sheet_id_var,
            font=("Consolas", 10), bg="#f8fafc", fg=C["text"],
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=C["border"],
            highlightcolor=C["primary"], insertbackground=C["primary"],
        )
        self.sheet_id_entry.pack(side=tk.LEFT, fill=tk.X,
                                 expand=True, ipady=8, padx=(0, 8))

        self._ghost_btn(url_row, "📋 Pegar",
                        self.paste_from_clipboard).pack(side=tk.RIGHT)

        self.sheet_id_status_var = tk.StringVar()
        tk.Label(gs, textvariable=self.sheet_id_status_var,
                 bg=C["card"], fg=C["success"],
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 10))

        # Row 2: tab + month
        row2 = tk.Frame(gs, bg=C["card"])
        row2.pack(fill=tk.X)

        left2 = tk.Frame(row2, bg=C["card"])
        left2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))

        self.sheet_tab_var = tk.StringVar(
            value=self.config.get("google_sheet_tab", "Transactions"))
        self._field_group(left2, "Nombre de la hoja",
                          self.sheet_tab_var, hint="Ej: Transactions, Gastos")

        right2 = tk.Frame(row2, bg=C["card"])
        right2.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.month_filter_var = tk.StringVar(
            value=self.config.get("filter_by_month") or "")
        self._field_group(right2, "Filtrar por mes",
                          self.month_filter_var,
                          hint="Ej: 2026/07 — vacío = todos los meses")

        # Buttons + inline feedback
        btn_row = tk.Frame(gs, bg=C["card"])
        btn_row.pack(fill=tk.X, pady=(20, 6))

        self._btn(btn_row, "💾  Guardar", C["success"],
                  self.save_config).pack(side=tk.LEFT, padx=(0, 10))

        self._ghost_btn(btn_row, "Validar ID",
                        self.test_config).pack(side=tk.LEFT)

        self.save_status_var = tk.StringVar()
        tk.Label(gs, textvariable=self.save_status_var,
                 bg=C["card"], fg=C["success"],
                 font=("Segoe UI", 9)).pack(anchor="w")

        # Help card
        help_outer, help_inner = self._card(body, "Cómo obtener el ID")
        help_outer.pack(fill=tk.X)

        steps = [
            ("1.", "Abre tu Google Sheet en el navegador"),
            ("2.", "Copia la URL completa y pégala en el campo de arriba"),
            ("3.", "El ID se extrae automáticamente"),
            ("",   ""),
            ("ID:", "Es la parte alfanumérica larga entre /d/ y /edit"),
        ]
        for num, text in steps:
            r = tk.Frame(help_inner, bg=C["card"])
            r.pack(fill=tk.X, pady=2)
            if num:
                tk.Label(r, text=num, bg=C["card"], fg=C["primary"],
                         font=("Segoe UI", 9, "bold"), width=3,
                         anchor="w").pack(side=tk.LEFT)
            tk.Label(r, text=text, bg=C["card"], fg=C["text_dim"],
                     font=("Segoe UI", 9), anchor="w").pack(side=tk.LEFT)

    # ── DB editor page ────────────────────────────────────────────────────────
    def _build_db_page(self, parent):
        self._page_header(parent, "Base de Datos",
                          "Edita vendors, reglas de categorías y prueba el clasificador")

        if not _db_available:
            tk.Label(parent, text="No se pudo cargar el módulo de base de datos.",
                     bg=C["bg"], fg=C["error"], font=("Segoe UI", 12)).pack(pady=40)
            return

        # Lazy-init DB connection (once)
        self._db = ExpenseDatabase()

        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Sub-tab strip (manual, styled to match theme)
        tab_bar = tk.Frame(body, bg=C["bg"])
        tab_bar.pack(fill=tk.X, padx=28, pady=(14, 0))

        self._db_tab_frames = {}
        self._db_tab_btns   = {}

        def _switch_db_tab(name):
            for n, f in self._db_tab_frames.items():
                if n == name:
                    f.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 16))
                else:
                    f.pack_forget()
            for n, b in self._db_tab_btns.items():
                b.config(
                    bg=C["primary"] if n == name else C["card"],
                    fg="white"      if n == name else C["text_dim"],
                )
            self._db_active_tab = name

        for tab_key, tab_label in [
            ("vendors", "🏪  Vendors"),
            ("rules",   "📐  Reglas"),
            ("test",    "🔬  Probar"),
        ]:
            btn = tk.Button(
                tab_bar, text=tab_label,
                bg=C["card"], fg=C["text_dim"],
                activebackground=C["primary"], activeforeground="white",
                relief="flat", bd=0, cursor="hand2",
                font=("Segoe UI", 10, "bold"),
                padx=18, pady=8,
                highlightthickness=1, highlightbackground=C["border"],
                command=lambda k=tab_key: _switch_db_tab(k),
            )
            btn.pack(side=tk.LEFT, padx=(0, 6))
            self._db_tab_btns[tab_key] = btn

        # Build the three tab content frames
        for key, builder in [
            ("vendors", self._build_db_vendors_tab),
            ("rules",   self._build_db_rules_tab),
            ("test",    self._build_db_test_tab),
        ]:
            f = tk.Frame(body, bg=C["bg"])
            builder(f)
            self._db_tab_frames[key] = f

        _switch_db_tab("vendors")

    # ── Vendors tab ───────────────────────────────────────────────────────────
    def _build_db_vendors_tab(self, parent):
        # Search bar + action buttons
        top = tk.Frame(parent, bg=C["bg"])
        top.pack(fill=tk.X, pady=(14, 8))

        self._vendor_search_var = tk.StringVar()
        self._vendor_search_var.trace("w", lambda *_: self._refresh_vendors())
        sk = tk.Entry(
            top, textvariable=self._vendor_search_var,
            font=("Segoe UI", 10), bg="white", fg=C["text"],
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=C["border"],
            highlightcolor=C["primary"],
        )
        sk.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7, padx=(0, 10))
        tk.Label(top, text="🔍", bg=C["bg"], font=("Segoe UI", 12)).place(in_=sk, relx=0, rely=0.5, anchor="w", x=6)

        self._btn(top, "+ Agregar",   C["success"], self._vendor_add_dialog).pack(side=tk.LEFT, padx=(0, 6))
        self._btn(top, "✏ Editar",    C["info"],    self._vendor_edit_dialog).pack(side=tk.LEFT, padx=(0, 6))
        self._btn(top, "✕ Eliminar",  C["error"],   self._vendor_delete,      font=("Segoe UI", 9, "bold"), pady=7).pack(side=tk.LEFT)

        # Treeview
        tree_frame = tk.Frame(parent, bg=C["card"],
                              highlightthickness=1, highlightbackground=C["border"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("DB.Treeview",
                        background=C["card"], fieldbackground=C["card"],
                        foreground=C["text"], rowheight=28,
                        font=("Segoe UI", 10))
        style.configure("DB.Treeview.Heading",
                        background=C["bg"], foreground=C["text_dim"],
                        font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("DB.Treeview", background=[("selected", C["primary"])],
                  foreground=[("selected", "white")])

        cols = ("keyword", "vendor_name", "category")
        self._vendor_tree = ttk.Treeview(tree_frame, columns=cols,
                                          show="headings", style="DB.Treeview")
        for col, heading, w in [
            ("keyword",     "Keyword",      240),
            ("vendor_name", "Nombre del vendor", 260),
            ("category",    "Categoría",    180),
        ]:
            self._vendor_tree.heading(col, text=heading,
                                       command=lambda c=col: self._sort_tree(self._vendor_tree, c))
            self._vendor_tree.column(col, width=w, minwidth=80)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self._vendor_tree.yview)
        self._vendor_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._vendor_tree.pack(fill=tk.BOTH, expand=True)
        self._vendor_tree.bind("<Double-1>", lambda _: self._vendor_edit_dialog())

        # Store row id mapping
        self._vendor_id_map = {}
        self._refresh_vendors()

    def _refresh_vendors(self):
        q = self._vendor_search_var.get().lower()
        self._vendor_tree.delete(*self._vendor_tree.get_children())
        self._vendor_id_map = {}
        for row_id, kw, vendor, cat in self._db.get_all_vendors_full():
            if q and q not in kw.lower() and q not in vendor.lower() and q not in (cat or "").lower():
                continue
            iid = self._vendor_tree.insert("", tk.END, values=(kw, vendor, cat))
            self._vendor_id_map[iid] = row_id

    def _vendor_add_dialog(self):
        self._vendor_form_dialog("Agregar Vendor", None, None, None, None)

    def _vendor_edit_dialog(self):
        sel = self._vendor_tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona un vendor", "Haz clic en un vendor para editarlo.")
            return
        iid = sel[0]
        kw, vendor, cat = self._vendor_tree.item(iid, "values")
        self._vendor_form_dialog("Editar Vendor", iid, kw, vendor, cat)

    def _vendor_form_dialog(self, title, iid, kw, vendor, cat):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("440x280")
        win.configure(bg=C["bg"])
        win.resizable(False, False)
        win.grab_set()
        self._center_window(win, 440, 280)

        tk.Label(win, text=title, bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=24, pady=(20, 14))

        form = tk.Frame(win, bg=C["bg"])
        form.pack(fill=tk.X, padx=24)

        kw_var     = tk.StringVar(value=kw or "")
        vendor_var = tk.StringVar(value=vendor or "")
        cat_var    = tk.StringVar(value=cat or "")

        for label, var, hint, editable in [
            ("Keyword (texto a buscar)",  kw_var,     "ej: uber eats",         iid is None),
            ("Nombre del vendor",         vendor_var, "ej: Uber Eats",         True),
            ("Categoría",                 cat_var,    "ej: Dining Out",        True),
        ]:
            row = tk.Frame(form, bg=C["bg"])
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=label, bg=C["bg"], fg=C["text_dim"],
                     font=("Segoe UI", 9, "bold"), width=28, anchor="w").pack(side=tk.LEFT)
            e = tk.Entry(row, textvariable=var,
                         font=("Segoe UI", 10), bg="white", fg=C["text"],
                         relief="flat", highlightthickness=1,
                         highlightbackground=C["border"],
                         highlightcolor=C["primary"],
                         state=tk.NORMAL if editable else "readonly")
            e.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        def _save():
            k = kw_var.get().strip().lower()
            v = vendor_var.get().strip()
            c = cat_var.get().strip() or None
            if not k or not v:
                messagebox.showerror("Campos requeridos", "Keyword y Nombre son obligatorios.", parent=win)
                return
            if iid is None:
                ok = self._db.add_vendor_keyword(k, v, c)
            else:
                ok = self._db.update_vendor_keyword(k, v, c)
            if ok:
                self._refresh_vendors()
                win.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar.", parent=win)

        btn_row = tk.Frame(win, bg=C["bg"])
        btn_row.pack(fill=tk.X, padx=24, pady=(16, 0))
        self._btn(btn_row, "Guardar", C["success"], _save).pack(side=tk.LEFT, padx=(0, 10))
        self._ghost_btn(btn_row, "Cancelar", win.destroy).pack(side=tk.LEFT)

    def _vendor_delete(self):
        sel = self._vendor_tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona un vendor", "Haz clic en un vendor para eliminarlo.")
            return
        kw = self._vendor_tree.item(sel[0], "values")[0]
        if not messagebox.askyesno("Confirmar",
                                   f"¿Eliminar el keyword '{kw}'?",
                                   icon="warning"):
            return
        if self._db.delete_vendor_keyword(kw):
            self._refresh_vendors()
        else:
            messagebox.showerror("Error", "No se pudo eliminar.")

    # ── Rules tab ─────────────────────────────────────────────────────────────
    def _build_db_rules_tab(self, parent):
        top = tk.Frame(parent, bg=C["bg"])
        top.pack(fill=tk.X, pady=(14, 8))

        self._rules_search_var = tk.StringVar()
        self._rules_search_var.trace("w", lambda *_: self._refresh_rules())
        sk = tk.Entry(
            top, textvariable=self._rules_search_var,
            font=("Segoe UI", 10), bg="white", fg=C["text"],
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=C["border"],
            highlightcolor=C["primary"],
        )
        sk.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=7, padx=(0, 10))

        self._btn(top, "+ Agregar",  C["success"], self._rule_add_dialog).pack(side=tk.LEFT, padx=(0, 6))
        self._btn(top, "✏ Editar",   C["info"],    self._rule_edit_dialog).pack(side=tk.LEFT, padx=(0, 6))
        self._btn(top, "✕ Eliminar", C["error"],   self._rule_delete,     font=("Segoe UI", 9, "bold"), pady=7).pack(side=tk.LEFT)

        tree_frame = tk.Frame(parent, bg=C["card"],
                              highlightthickness=1, highlightbackground=C["border"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("rule_type", "pattern", "category", "priority")
        self._rules_tree = ttk.Treeview(tree_frame, columns=cols,
                                         show="headings", style="DB.Treeview")
        for col, heading, w in [
            ("rule_type", "Tipo de regla",  170),
            ("pattern",   "Patrón",         240),
            ("category",  "Categoría",      180),
            ("priority",  "Prioridad",       80),
        ]:
            self._rules_tree.heading(col, text=heading,
                                      command=lambda c=col: self._sort_tree(self._rules_tree, c))
            self._rules_tree.column(col, width=w, minwidth=60)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self._rules_tree.yview)
        self._rules_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._rules_tree.pack(fill=tk.BOTH, expand=True)
        self._rules_tree.bind("<Double-1>", lambda _: self._rule_edit_dialog())

        self._rule_id_map = {}
        self._refresh_rules()

    def _refresh_rules(self):
        q = self._rules_search_var.get().lower()
        self._rules_tree.delete(*self._rules_tree.get_children())
        self._rule_id_map = {}
        for row_id, rt, pat, cat, pri in self._db.get_all_category_rules_with_id():
            if q and q not in rt.lower() and q not in pat.lower() and q not in cat.lower():
                continue
            iid = self._rules_tree.insert("", tk.END, values=(rt, pat, cat, pri))
            self._rule_id_map[iid] = row_id

    def _rule_add_dialog(self):
        self._rule_form_dialog("Agregar Regla", None, None, None, None, None)

    def _rule_edit_dialog(self):
        sel = self._rules_tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona una regla", "Haz clic en una regla para editarla.")
            return
        iid = sel[0]
        rt, pat, cat, pri = self._rules_tree.item(iid, "values")
        db_id = self._rule_id_map.get(iid)
        self._rule_form_dialog("Editar Regla", iid, db_id, rt, pat, cat, int(pri))

    def _rule_form_dialog(self, title, iid, db_id, rt, pat, cat, pri=50):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("480x340")
        win.configure(bg=C["bg"])
        win.resizable(False, False)
        win.grab_set()
        self._center_window(win, 480, 340)

        tk.Label(win, text=title, bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=24, pady=(20, 14))

        form = tk.Frame(win, bg=C["bg"])
        form.pack(fill=tk.X, padx=24)

        RULE_TYPES = ["vendor_exact", "vendor_contains", "keyword_contains"]

        rt_var  = tk.StringVar(value=rt  or RULE_TYPES[1])
        pat_var = tk.StringVar(value=pat or "")
        cat_var = tk.StringVar(value=cat or "")
        pri_var = tk.StringVar(value=str(pri or 50))

        # Rule type dropdown
        row = tk.Frame(form, bg=C["bg"])
        row.pack(fill=tk.X, pady=4)
        tk.Label(row, text="Tipo de regla", bg=C["bg"], fg=C["text_dim"],
                 font=("Segoe UI", 9, "bold"), width=22, anchor="w").pack(side=tk.LEFT)
        rt_menu = ttk.Combobox(row, textvariable=rt_var, values=RULE_TYPES,
                               state="readonly", font=("Segoe UI", 10), width=28)
        rt_menu.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        for label, var, hint in [
            ("Patrón (en minúsculas)", pat_var, "ej: uber eats"),
            ("Categoría",             cat_var, "ej: Dining Out"),
            ("Prioridad",             pri_var, "número — mayor = más prioritario"),
        ]:
            row = tk.Frame(form, bg=C["bg"])
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=label, bg=C["bg"], fg=C["text_dim"],
                     font=("Segoe UI", 9, "bold"), width=22, anchor="w").pack(side=tk.LEFT)
            e = tk.Entry(row, textvariable=var,
                         font=("Segoe UI", 10), bg="white", fg=C["text"],
                         relief="flat", highlightthickness=1,
                         highlightbackground=C["border"],
                         highlightcolor=C["primary"])
            e.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        def _save():
            try:
                pri_int = int(pri_var.get().strip())
            except ValueError:
                messagebox.showerror("Prioridad inválida", "La prioridad debe ser un número.", parent=win)
                return
            rtype = rt_var.get()
            patt  = pat_var.get().strip().lower()
            categ = cat_var.get().strip()
            if not patt or not categ:
                messagebox.showerror("Campos requeridos", "Patrón y Categoría son obligatorios.", parent=win)
                return
            if iid is None:
                ok = self._db.add_category_rule(rtype, patt, categ, pri_int)
            else:
                ok = self._db.update_category_rule(db_id, rtype, patt, categ, pri_int)
            if ok:
                self._refresh_rules()
                win.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar.", parent=win)

        btn_row = tk.Frame(win, bg=C["bg"])
        btn_row.pack(fill=tk.X, padx=24, pady=(16, 0))
        self._btn(btn_row, "Guardar", C["success"], _save).pack(side=tk.LEFT, padx=(0, 10))
        self._ghost_btn(btn_row, "Cancelar", win.destroy).pack(side=tk.LEFT)

    def _rule_delete(self):
        sel = self._rules_tree.selection()
        if not sel:
            messagebox.showinfo("Selecciona una regla", "Haz clic en una regla para eliminarla.")
            return
        iid    = sel[0]
        pat    = self._rules_tree.item(iid, "values")[1]
        db_id  = self._rule_id_map.get(iid)
        if not messagebox.askyesno("Confirmar",
                                   f"¿Eliminar la regla '{pat}'?",
                                   icon="warning"):
            return
        if self._db.delete_category_rule(db_id):
            self._refresh_rules()
        else:
            messagebox.showerror("Error", "No se pudo eliminar.")

    # ── Test tab ──────────────────────────────────────────────────────────────
    def _build_db_test_tab(self, parent):
        outer, inner = self._card(parent, "Probar clasificación")
        outer.pack(fill=tk.X, pady=(14, 14))

        tk.Label(inner, text="Ingresa el nombre del comercio o el texto del correo:",
                 bg=C["card"], fg=C["text_dim"], font=("Segoe UI", 10)).pack(anchor="w")

        inp_row = tk.Frame(inner, bg=C["card"])
        inp_row.pack(fill=tk.X, pady=(8, 0))

        self._test_input_var = tk.StringVar()
        e = tk.Entry(inp_row, textvariable=self._test_input_var,
                     font=("Segoe UI", 11), bg="#f8fafc", fg=C["text"],
                     relief="flat", highlightthickness=1,
                     highlightbackground=C["border"], highlightcolor=C["primary"])
        e.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=9, padx=(0, 10))
        e.bind("<Return>", lambda _: self._run_db_test())

        self._btn(inp_row, "Probar", C["primary"], self._run_db_test,
                  pady=9).pack(side=tk.LEFT)

        # Result panel
        res_outer, res_inner = self._card(parent, "Resultado")
        res_outer.pack(fill=tk.X)

        grid = tk.Frame(res_inner, bg=C["card"])
        grid.pack(fill=tk.X)

        self._test_vendor_var   = tk.StringVar(value="—")
        self._test_category_var = tk.StringVar(value="—")

        for row_i, (lbl, var, color) in enumerate([
            ("Vendor identificado:", self._test_vendor_var,   C["info"]),
            ("Categoría asignada:", self._test_category_var, C["success"]),
        ]):
            tk.Label(grid, text=lbl, bg=C["card"], fg=C["text_dim"],
                     font=("Segoe UI", 10, "bold"), anchor="w", width=22
                     ).grid(row=row_i, column=0, sticky="w", pady=5)
            tk.Label(grid, textvariable=var, bg=C["card"], fg=color,
                     font=("Segoe UI", 12, "bold"), anchor="w"
                     ).grid(row=row_i, column=1, sticky="w", padx=(10, 0), pady=5)

    def _run_db_test(self):
        text = self._test_input_var.get().strip()
        if not text:
            return
        vendor, category = self._db.test_text(text)
        self._test_vendor_var.set(vendor)
        self._test_category_var.set(category)

    # ── Treeview sort helper ──────────────────────────────────────────────────
    def _sort_tree(self, tree, col):
        data = [(tree.set(iid, col), iid) for iid in tree.get_children("")]
        try:
            data.sort(key=lambda x: int(x[0]))
        except ValueError:
            data.sort(key=lambda x: x[0].lower())
        for idx, (_, iid) in enumerate(data):
            tree.move(iid, "", idx)

    @staticmethod
    def _center_window(win, w, h):
        win.update_idletasks()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Status page ───────────────────────────────────────────────────────────
    def _build_status_page(self, parent):
        self._page_header(parent, "Estado & Logs",
                          "Estado del sistema y registro de ejecuciones")

        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=28, pady=20)

        # Status cards row
        cards_row = tk.Frame(body, bg=C["bg"])
        cards_row.pack(fill=tk.X, pady=(0, 14))

        self._status_items = {}
        for key, icon, title in [
            ("creds",  "🔐", "Credenciales"),
            ("config", "⚙️", "Google Sheet"),
            ("db",     "🗄️", "Base de datos"),
        ]:
            outer, inner = self._card(cards_row,
                                      pady_inner=14, padx_inner=18)
            outer.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
            tk.Label(inner, text=icon, bg=C["card"], fg=C["text"],
                     font=("Segoe UI", 22)).pack(anchor="w")
            tk.Label(inner, text=title, bg=C["card"], fg=C["text_dim"],
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4, 2))
            lbl = tk.Label(inner, text="—", bg=C["card"],
                           fg=C["text_muted"], font=("Segoe UI", 9),
                           wraplength=160, justify="left")
            lbl.pack(anchor="w")
            self._status_items[key] = lbl

        self._ghost_btn(cards_row, "🔄  Actualizar",
                        self.refresh_status).pack(side=tk.RIGHT, anchor="n")

        self._update_status_labels()

        # Log viewer
        log_outer, log_inner = self._card(body, "Historial de ejecuciones")
        log_outer.pack(fill=tk.BOTH, expand=True)
        log_inner.pack_configure(pady=10)

        hdr = tk.Frame(log_inner, bg=C["card"])
        hdr.pack(fill=tk.X, pady=(0, 6))
        tk.Label(hdr, text="● HISTORY", bg=C["card"],
                 fg=C["log_dim"], font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT)
        self._ghost_btn(
            hdr, "Limpiar",
            lambda: (self.logs_text.config(state=tk.NORMAL),
                     self.logs_text.delete("1.0", tk.END),
                     self.logs_text.config(state=tk.DISABLED)),
            font=("Segoe UI", 8),
        ).pack(side=tk.RIGHT)

        self.logs_text = self._make_log_widget(log_inner)

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_to_history(f"  [{ts}]  Sistema iniciado\n", "info")
        self._log_to_history("  Interfaz gráfica cargada correctamente\n\n", "dim")

    # ── Business logic ────────────────────────────────────────────────────────
    def extract_sheet_id_from_url(self, url_or_id):
        url_or_id = url_or_id.strip()
        for pattern in [
            r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)",
            r"/spreadsheets/d/([a-zA-Z0-9-_]+)",
            r"d/([a-zA-Z0-9-_]+)",
        ]:
            m = re.search(pattern, url_or_id)
            if m:
                return m.group(1)
        if re.match(r"^[a-zA-Z0-9-_]+$", url_or_id) and len(url_or_id) > 20:
            return url_or_id
        return url_or_id

    def on_sheet_id_change(self, *args):
        val = self.sheet_id_var.get()
        if val:
            extracted = self.extract_sheet_id_from_url(val)
            if extracted != val:
                self.sheet_id_var.set(extracted)
                self.sheet_id_status_var.set("✅ ID extraído automáticamente")
                self.root.after(3000, lambda: self.sheet_id_status_var.set(""))
            else:
                self.sheet_id_status_var.set("")

    def paste_from_clipboard(self):
        try:
            content = self.root.clipboard_get()
            if content:
                self.sheet_id_var.set(content.strip())
        except tk.TclError:
            pass

    def load_config(self):
        try:
            import config
            return {
                "google_sheet_id":  getattr(config, "SPREADSHEET_ID", ""),
                "google_sheet_tab": getattr(config, "SPREADSHEET_NAME", "Transactions"),
                "filter_by_month":  getattr(config, "FILTER_BY_MONTH", None),
            }
        except Exception:
            return {
                "google_sheet_id":  "",
                "google_sheet_tab": "Transactions",
                "filter_by_month":  None,
            }

    def save_config(self):
        try:
            raw = self.sheet_id_var.get().strip()
            sheet_id     = self.extract_sheet_id_from_url(raw)
            sheet_tab    = self.sheet_tab_var.get().strip() or "Transactions"
            month_filter = self.month_filter_var.get().strip() or None

            if not sheet_id:
                messagebox.showerror("Error", "El ID de Google Sheet es obligatorio")
                return

            if raw != sheet_id:
                self.sheet_id_var.set(sheet_id)

            content = (
                "# Configuration file for Expense Tracker\n"
                "import os\n\n"
                "BASE_DIR = os.path.dirname(os.path.abspath(__file__))\n\n"
                f'SPREADSHEET_ID = "{sheet_id}"\n'
                f'SPREADSHEET_NAME = "{sheet_tab}"\n'
                f"FILTER_BY_MONTH = {repr(month_filter)}\n\n"
                'GMAIL_CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")\n'
                'TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")\n'
            )

            cfg_path = os.path.join(os.path.dirname(__file__), "config.py")
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.config = {
                "google_sheet_id":  sheet_id,
                "google_sheet_tab": sheet_tab,
                "filter_by_month":  month_filter,
            }
            self._update_run_config_display()
            self._update_status_labels()

            self.save_status_var.set("✅ Guardado correctamente")
            self.root.after(3000, lambda: self.save_status_var.set(""))

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")

    def test_config(self):
        raw = self.sheet_id_var.get().strip()
        if not raw:
            messagebox.showerror("Error", "Ingresa una URL o ID primero")
            return
        sheet_id = self.extract_sheet_id_from_url(raw)
        if len(sheet_id) < 20:
            messagebox.showwarning("ID muy corto",
                                   "El ID parece muy corto. Verifica que sea correcto.")
            return
        if not re.match(r"^[a-zA-Z0-9-_]+$", sheet_id):
            messagebox.showwarning("Caracteres inválidos",
                                   "El ID contiene caracteres no válidos.")
            return
        preview = sheet_id[:24] + ("…" if len(sheet_id) > 24 else "")
        messagebox.showinfo("ID válido",
                            f"Formato correcto ✅\nID: {preview}\n\n"
                            "Guarda y ejecuta el tracker para probar la conexión.")

    # ── Status helpers ────────────────────────────────────────────────────────
    def check_credentials(self):
        p = os.path.join(os.path.dirname(__file__), "credentials.json")
        return "encontrado" if os.path.exists(p) else "no encontrado"

    def check_config_status(self):
        return "Configurado" if self.config.get("google_sheet_id") else "Falta configurar"

    def check_database_status(self):
        p = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "data", "expense_tracker.db")
        return "encontrada" if os.path.exists(p) else "no encontrada"

    def _update_status_labels(self):
        checks = {
            "creds":  (self.check_credentials(),   "encontrado",
                       "credentials.json encontrado",
                       "No encontrado — coloca credentials.json en src/"),
            "config": (self.check_config_status(), "Configurado",
                       "Sheet ID configurado",
                       "Falta configurar"),
            "db":     (self.check_database_status(), "encontrada",
                       "Base de datos activa",
                       "Base de datos no encontrada"),
        }
        for key, (status, kw, ok_txt, err_txt) in checks.items():
            ok = kw in status
            self._status_items[key].config(
                text=("✅  " + ok_txt) if ok else ("❌  " + err_txt),
                fg=C["success"] if ok else C["error"],
            )

    def _update_run_config_display(self):
        sid    = self.config.get("google_sheet_id", "")
        tab    = self.config.get("google_sheet_tab", "Transactions")
        mfilter = self.config.get("filter_by_month") or "Todos los meses"
        disp   = (sid[:22] + "…") if len(sid) > 24 else (sid or "No configurado")
        self.cfg_sheet_lbl.config( text=f"📄  {disp}")
        self.cfg_tab_lbl.config(   text=f"📋  {tab}")
        self.cfg_filter_lbl.config(text=f"📅  {mfilter}")

    def refresh_status(self):
        self.config = self.load_config()
        self._update_status_labels()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_to_history(f"  [{ts}]  Estado del sistema actualizado\n", "info")

    # ── Run tracker ───────────────────────────────────────────────────────────
    def run_tracker(self):
        if self.is_running:
            return
        if not self.config.get("google_sheet_id"):
            messagebox.showerror("Sin configuración",
                                 "Configura el Google Sheet ID en 'Configuración' primero.")
            return
        if not os.path.exists(os.path.join(os.path.dirname(__file__),
                                            "credentials.json")):
            messagebox.showerror("Credenciales no encontradas",
                                 "Coloca credentials.json en src/\n"
                                 "Descárgalo desde Google Cloud Console.")
            return

        self.is_running = True
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()
        self.run_status_var.set("🔄  Ejecutando…")
        self.status_var.set("Ejecutando tracker…")

        self._clear_log()
        ts = datetime.now().strftime("%H:%M:%S")
        self._log(f"  [{ts}]  Iniciando ExpenseTracker\n\n", "info")
        self._log("  🔐  Verificando sesión de Google…\n", "dim")
        self._log("      Si el token expiró, el navegador abrirá una ventana de Google\n\n", "dim")

        t = threading.Thread(target=self._run_tracker_thread)
        t.daemon = True
        t.start()
        self.tracker_thread = t

    def _run_tracker_thread(self):
        try:
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                tracker = ExpenseTracker()
                results = tracker.process_expenses()
            self.root.after(0, self._tracker_completed, buf.getvalue(), results)
        except Exception as e:
            self.root.after(0, self._tracker_error, str(e))

    def _tracker_completed(self, output, results):
        self.is_running = False
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()

        ts       = datetime.now().strftime("%H:%M:%S")
        ok_list  = [r for r in (results or []) if r.success]
        err_list = [r for r in (results or []) if not r.success]

        if ok_list:
            self.run_status_var.set(f"✅  {len(ok_list)} gasto(s) procesado(s)")
            self.status_var.set(f"Completado — {len(ok_list)} gastos")
            self._log(f"  [{ts}]  ✅  COMPLETADO\n", "success")
            self._log(f"  Gastos agregados: {len(ok_list)}\n\n", "success")
            for i, r in enumerate(ok_list[:10], 1):
                self._log(f"  {i:>2}.  {r.message or 'Procesado'}\n", "dim")
            if len(ok_list) > 10:
                self._log(f"\n  … y {len(ok_list) - 10} más\n", "dim")
        elif not results:
            self.run_status_var.set("📭  Sin correos nuevos")
            self.status_var.set("Sin correos nuevos")
            self._log(f"  [{ts}]  📭  No hay correos nuevos para procesar\n", "warn")
        else:
            self.run_status_var.set(f"⚠  {len(err_list)} error(es)")
            self.status_var.set("Completado con errores")
            self._log(f"  [{ts}]  ⚠  Completado con errores\n", "warn")

        if err_list:
            self._log(f"\n  ❌  Errores ({len(err_list)}):\n", "error")
            for r in err_list[:5]:
                self._log(f"     • {r.error or r.message}\n", "error")

        if output.strip():
            self._log("\n  ─── Log detallado ─────────────────────────\n", "dim")
            for line in output.splitlines():
                self._log(f"  {line}\n", "dim")
            self._log("  ───────────────────────────────────────────\n\n", "dim")

        # Mirror summary to history log
        self._log_to_history(
            f"  [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
            f"  OK={len(ok_list)}  ERR={len(err_list)}\n",
            "success" if ok_list else "warn",
        )

        if ok_list:
            msg = f"✅  {len(ok_list)} gasto(s) agregado(s) a Google Sheets."
            if err_list:
                msg += f"\n\n⚠  {len(err_list)} correo(s) con errores — revisa los logs."
            messagebox.showinfo("Completado", msg)
        elif err_list:
            messagebox.showerror("Errores al procesar",
                                 f"{len(err_list)} error(es). Revisa los logs.")

    def _tracker_error(self, error_msg):
        self.is_running = False
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()

        ts = datetime.now().strftime("%H:%M:%S")
        self.run_status_var.set("❌  Error de ejecución")
        self.status_var.set("Error")

        is_auth = any(k in error_msg.lower() for k in
                      ["invalid_grant", "authentication", "credential",
                       "token", "oauth"])

        self._log(f"  [{ts}]  ❌  ERROR\n", "error")
        self._log(f"  {error_msg}\n", "error")

        if is_auth:
            self._log("\n  💡  Token de Google expirado.\n"
                      "      Haz clic en 'Ejecutar' de nuevo — el navegador pedirá autenticación.\n",
                      "warn")
            messagebox.showerror(
                "Sesión expirada",
                "La sesión de Google expiró.\n\n"
                "Haz clic en '▶ Ejecutar' de nuevo — se abrirá el navegador para iniciar sesión.",
            )
        else:
            self._log("\n  💡  Revisa la pestaña 'Estado & Logs' para más detalles.\n", "dim")
            messagebox.showerror("Error de ejecución",
                                 f"Ocurrió un error:\n\n{error_msg}")

        self._log_to_history(
            f"  [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
            f"  ERROR: {error_msg[:80]}\n",
            "error",
        )

    def stop_tracker(self):
        if self.is_running:
            self.is_running = False
            self.run_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.progress.stop()
            ts = datetime.now().strftime("%H:%M:%S")
            self.run_status_var.set("⏹  Detenido")
            self.status_var.set("Detenido")
            self._log(f"\n  [{ts}]  ⏹  Detenido por el usuario\n", "warn")

    def _append_result(self, text, tag=None):
        """Compatibility shim used by older call-sites."""
        self._log(text, tag)


def main():
    root = tk.Tk()
    try:
        root.iconbitmap(default="icon.ico")
    except Exception:
        pass
    app = ExpenseTrackerGUI(root)
    root.update_idletasks()
    w, h = root.winfo_width(), root.winfo_height()
    x = (root.winfo_screenwidth()  // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.mainloop()


if __name__ == "__main__":
    main()
