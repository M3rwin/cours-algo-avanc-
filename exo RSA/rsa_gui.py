import tkinter as tk
from tkinter import messagebox


def euclide_etendu(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    old_r, r = a, b
    old_u, u = 1, 0
    old_v, v = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_u, u = u, old_u - q * u
        old_v, v = v, old_v - q * v
    return old_r, old_u, old_v


def euclide_etendu_trace(a: int, b: int):
    """
    Renvoie (pgcd, u, v, rows) pour euclide_etendu(a, b).
    Rows d'init  : ("init", r, v)             ← v coefficient de b
    Rows de step : (n, old_r, q, r, new_r, old_v, v_curr, new_v)
    Appelé avec (phi, e) → colonne E démarre [0, 1] et d = v_final % a.
    """
    rows = []
    old_r, r = a, b
    old_u, u = 1, 0
    old_v, v = 0, 1
    rows.append(("init", old_r, old_v))   # v₀ = 0
    rows.append(("init", r,     v))       # v₁ = 1
    step = 1
    while r != 0:
        q     = old_r // r
        new_r = old_r - q * r
        new_u = old_u - q * u
        new_v = old_v - q * v
        rows.append((step, old_r, q, r, new_r, old_v, v, new_v))
        old_r, r = r, new_r
        old_u, u = u, new_u
        old_v, v = v, new_v
        step += 1
    return old_r, old_u, old_v, rows

# ─────────────────────────────────────────────────────────────
#  Palette dark
# ─────────────────────────────────────────────────────────────
C = {
    "bg":        "#0f1117",   # fond global
    "surface":   "#1a1d2e",   # carte
    "border":    "#2a2d3e",   # bordure carte
    "header_bg": "#1e2235",   # bandeau titre carte
    "text":      "#c9d1d9",   # texte courant
    "muted":     "#6e7681",   # texte secondaire
    "blue":      "#58a6ff",   # accent bleu
    "green":     "#3fb950",   # accent vert
    "purple":    "#bc8cff",   # accent violet
    "orange":    "#ffa657",   # accent orange
    "pink":      "#f778ba",   # accent rose
    "teal":      "#39d353",   # accent teal
    "btn":       "#238636",   # bouton
    "btn_hover": "#2ea043",
    "entry_bg":  "#161b22",
    "entry_bd":  "#30363d",
}

STEP_COLORS = ["#58a6ff", "#bc8cff", "#ffa657", "#f778ba", "#39d353"]

# ─────────────────────────────────────────────────────────────
#  Helpers RSA
# ─────────────────────────────────────────────────────────────

def is_prime(n: int) -> bool:
    if n < 2:   return False
    if n == 2:  return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def choose_e(phi: int) -> int:
    for e in range(2, phi):
        if euclide_etendu(e, phi)[0] == 1:
            return e
    raise ValueError("Impossible de trouver e")


def compute_setup(p: int, q: int) -> tuple[int, int, list[dict]]:
    """Étapes 1-3 : retourne (n, phi, blocks)."""
    blocks = []
    blocks.append({
        "title": "Étape 1 — Vérification des nombres premiers",
        "lines": [
            ("p", str(p), C["blue"]),
            ("q", str(q), C["blue"]),
            ("p est premier ?", "✓ Oui" if is_prime(p) else "✗ Non", C["green"] if is_prime(p) else C["pink"]),
            ("q est premier ?", "✓ Oui" if is_prime(q) else "✗ Non", C["green"] if is_prime(q) else C["pink"]),
        ],
    })
    n = p * q
    blocks.append({
        "title": "Étape 2 — Calcul du module n",
        "formula": f"n  =  p × q  =  {p} × {q}",
        "result":  f"n  =  {n}",
        "lines": [],
    })
    phi = (p - 1) * (q - 1)
    blocks.append({
        "title": "Étape 3 — Indicatrice d'Euler φ(n)",
        "formula": f"φ(n)  =  (p−1)(q−1)  =  {p-1} × {q-1}",
        "result":  f"φ(n)  =  {phi}",
        "lines": [],
    })
    return n, phi, blocks


def compute_keys(n: int, phi: int, e: int, source: str) -> list[dict]:
    """Étapes 4-5 + résultat : retourne blocks."""
    blocks = []
    blocks.append({
        "title": "Étape 4 — Exposant public e",
        "lines": [
            ("Condition",    "1 < e < φ(n)  et  pgcd(e, φ(n)) = 1", C["muted"]),
            ("Origine",      source,                                   C["muted"]),
            ("e",            str(e),                                   C["orange"]),
            ("Vérification", f"pgcd({e}, {phi})  =  {euclide_etendu(e, phi)[0]}  ✓", C["green"]),
        ],
    })
    pgcd, u_phi, v_e, trace = euclide_etendu_trace(phi, e)
    d = v_e % phi
    blocks.append({
        "title": "Étape 5 — Clé privée d  (Euclide étendu)",
        "lines": [
            ("Équation à résoudre", f"e · d  ≡  1  (mod φ(n))", C["muted"]),
            ("Entrées", f"Q(−2) = φ(n) = {phi},   Q(−1) = e = {e}", C["text"]),
        ],
        "trace": trace,
        "bezout": (phi, e, u_phi, v_e, pgcd, d),
    })
    blocks.append({
        "title": "Résultat — Clés RSA",
        "keys": {
            "Clé publique":  f"(e = {e},  n = {n})",
            "Clé privée":    f"(d = {d},  n = {n})",
            "Vérification":  f"e · d  mod  φ(n)  =  {e} · {d}  mod  {phi}  =  {(e*d) % phi}",
        },
    })
    return blocks


# ─────────────────────────────────────────────────────────────
#  Widget carte
# ─────────────────────────────────────────────────────────────

def make_card(parent, block: dict, accent: str) -> tk.Frame:
    card = tk.Frame(parent, bg=C["surface"], bd=0, highlightthickness=1,
                    highlightbackground=accent)
    card.pack(fill="x", padx=0, pady=(0, 14))

    # Bandeau titre
    header = tk.Frame(card, bg=C["header_bg"])
    header.pack(fill="x")
    tk.Label(header, text=block["title"],
             font=("Segoe UI", 11, "bold"),
             bg=C["header_bg"], fg=accent,
             anchor="w", padx=16, pady=8).pack(fill="x")

    body = tk.Frame(card, bg=C["surface"])
    body.pack(fill="x", padx=16, pady=(8, 12))

    # Formule + résultat (blocs 2 et 3)
    if "formula" in block:
        tk.Label(body, text=block["formula"],
                 font=("Consolas", 11), bg=C["surface"], fg=C["muted"],
                 anchor="w").pack(fill="x", pady=(0, 2))
        tk.Label(body, text=block["result"],
                 font=("Consolas", 13, "bold"), bg=C["surface"], fg=accent,
                 anchor="w").pack(fill="x", pady=(0, 4))

    # Lignes label / valeur
    for label, value, color in block.get("lines", []):
        row = tk.Frame(body, bg=C["surface"])
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label,
                 font=("Segoe UI", 10), bg=C["surface"], fg=C["muted"],
                 width=26, anchor="w").pack(side="left")
        tk.Label(row, text=value,
                 font=("Consolas", 10, "bold"), bg=C["surface"], fg=color,
                 anchor="w").pack(side="left")

    # Tableau Euclide étendu
    if "trace" in block:
        trace = block["trace"]
        # bezout = (phi, e, u_phi, v_e, pgcd, d)  ← algo tourné sur (phi, e)
        a_val, b_val, u_val, v_val, pgcd_val, d_val = block["bezout"]

        inits = [r for r in trace if r[0] == "init"]
        steps = [r for r in trace if r[0] != "init"]

        # ─────────────────────────────────────────────
        # En-tête du tableau : 3 colonnes
        # ─────────────────────────────────────────────
        COL_TITLES = [
            ("Reste",    "Q(−2) / Q(−1)",   C["orange"]),
            ("Quotient", "Q(−2) − Q(−1)×R", C["green"]),
            ("E",        "E(−2) − E(−1)×R", C["purple"]),
        ]
        tbl = tk.Frame(body, bg=C["surface"])
        tbl.pack(fill="x", pady=(8, 0))
        tbl.columnconfigure((0, 1, 2), weight=1, uniform="col")

        # ligne de titres
        for ci, (title, subtitle, col) in enumerate(COL_TITLES):
            hf = tk.Frame(tbl, bg=C["header_bg"])
            hf.grid(row=0, column=ci, sticky="ew", padx=1, pady=(0, 1))
            tk.Label(hf, text=title, font=("Segoe UI", 10, "bold"),
                     bg=C["header_bg"], fg=col, pady=4).pack()
            tk.Label(hf, text=subtitle, font=("Consolas", 8),
                     bg=C["header_bg"], fg=C["muted"], pady=0).pack()

        ROW_BG = [C["surface"], "#1f2233"]

        def cell(parent, formula, result, res_fg, bg, is_init=False):
            f = tk.Frame(parent, bg=bg)
            f.pack(fill="both", expand=True, padx=6, pady=5)
            if not is_init:
                tk.Label(f, text=formula, font=("Consolas", 9),
                         bg=bg, fg=C["muted"], anchor="w").pack(anchor="w")
            tk.Label(f, text=result, font=("Consolas", 11, "bold"),
                     bg=bg, fg=res_fg, anchor="w").pack(anchor="w")

        # ─────────────────────────────────────────────
        # Lignes d'initialisation (Reste vide, Quotient = r, E = 0 ou 1)
        # ─────────────────────────────────────────────
        for row_i, row_init in enumerate(inits):
            r_init = row_init[1]
            bg = ROW_BG[row_i % 2]
            q_label = "Q(−2)" if row_i == 0 else "Q(−1)"
            e_label = "E₀ = 0" if row_i == 0 else "E₁ = 1"

            # Reste : vide (pas de division pour les lignes d'init)
            c0 = tk.Frame(tbl, bg=bg)
            c0.grid(row=row_i + 1, column=0, sticky="nsew", padx=1, pady=1)
            tk.Label(c0, text="—", font=("Consolas", 11),
                     bg=bg, fg=C["muted"]).pack(expand=True, pady=5)

            # Quotient : la valeur initiale (phi ou e)
            c1 = tk.Frame(tbl, bg=bg)
            c1.grid(row=row_i + 1, column=1, sticky="nsew", padx=1, pady=1)
            cell(c1, "", f"{q_label} = {r_init}", C["green"], bg, is_init=True)

            # E : 0 ou 1
            c2 = tk.Frame(tbl, bg=bg)
            c2.grid(row=row_i + 1, column=2, sticky="nsew", padx=1, pady=1)
            cell(c2, "", e_label, C["purple"], bg, is_init=True)

        # ─────────────────────────────────────────────
        # Lignes de calcul
        # ─────────────────────────────────────────────
        for idx, (_, old_r, q, r, new_r, old_v, v_curr, new_v) in enumerate(steps):
            bg = ROW_BG[(idx + len(inits)) % 2]
            row_idx = idx + len(inits) + 1

            # Col Reste : la division euclidienne → produit R (le quotient entier)
            c0 = tk.Frame(tbl, bg=bg)
            c0.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            cell(c0, f"{old_r} / {r}", f"R = {q}", C["orange"], bg)

            # Col Quotient : nouveau reste = Q(-2) − Q(-1)×R
            new_r_fg = C["pink"]  if new_r == 0       else \
                       C["teal"]  if new_r == pgcd_val else C["green"]
            c1 = tk.Frame(tbl, bg=bg)
            c1.grid(row=row_idx, column=1, sticky="nsew", padx=1, pady=1)
            cell(c1, f"{old_r} − {r}×{q}", f"= {new_r}", new_r_fg, bg)

            # Col E : nouveau coefficient = E(-2) − E(-1)×R
            e_fg = C["teal"] if new_v == v_val else C["purple"]
            c2 = tk.Frame(tbl, bg=bg)
            c2.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
            cell(c2, f"{old_v} − {v_curr}×{q}", f"= {new_v}", e_fg, bg)

        # ─────────────────────────────────────────────
        # Synthèse
        # ─────────────────────────────────────────────
        tk.Frame(body, bg=C["border"], height=1).pack(fill="x", pady=(10, 4))

        bezout_txt = f"{a_val} × ({u_val})  +  {b_val} × ({v_val})  =  {pgcd_val}"
        tk.Label(body, text="Relation de Bézout :",
                 font=("Segoe UI", 9, "italic"), bg=C["surface"], fg=C["muted"],
                 anchor="w").pack(fill="x")
        tk.Label(body, text=bezout_txt,
                 font=("Consolas", 11, "bold"), bg=C["surface"], fg=C["purple"],
                 anchor="w").pack(fill="x", pady=(0, 4))
        tk.Label(body,
                 text=f"d  =  E_final mod φ(n)  =  {v_val} mod {a_val}  =  {d_val}",
                 font=("Consolas", 11, "bold"), bg=C["surface"], fg=C["teal"],
                 anchor="w").pack(fill="x", pady=(0, 2))

    # Bloc résultat spécial
    if "keys" in block:
        for label, value in block["keys"].items():
            color = C["teal"] if label.startswith("Clé publique") else \
                    C["pink"]  if label.startswith("Clé privée")   else C["orange"]
            bg_row = "#1a2b1a" if label.startswith("Clé") else C["surface"]

            row = tk.Frame(body, bg=bg_row, bd=0)
            row.pack(fill="x", pady=3, ipady=4)
            tk.Label(row, text=label,
                     font=("Segoe UI", 10, "bold"), bg=bg_row, fg=C["muted"],
                     width=16, anchor="w", padx=8).pack(side="left")
            tk.Label(row, text=value,
                     font=("Consolas", 11, "bold"), bg=bg_row, fg=color,
                     anchor="w").pack(side="left")

    return card


# ─────────────────────────────────────────────────────────────
#  Application principale
# ─────────────────────────────────────────────────────────────

class RSAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Générateur de clés RSA")
        self.geometry("780x860")
        self.minsize(680, 600)
        self.configure(bg=C["bg"])
        self._build_header()
        self._build_form()
        self._build_scroll_area()

    # ── En-tête ───────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill="x", padx=30, pady=(24, 4))
        tk.Label(hdr, text="RSA Key Generator",
                 font=("Segoe UI", 22, "bold"),
                 bg=C["bg"], fg=C["blue"]).pack(anchor="w")
        tk.Label(hdr, text="Basé sur l'algorithme d'Euclide étendu · Relation de Bézout",
                 font=("Segoe UI", 10), bg=C["bg"], fg=C["muted"]).pack(anchor="w", pady=(2, 0))
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x", padx=30, pady=(10, 0))

    # ── Formulaire ────────────────────────────

    def _build_form(self):
        form = tk.Frame(self, bg=C["bg"])
        form.pack(fill="x", padx=30, pady=(16, 8))

        def entry_widget(parent, col):
            e = tk.Entry(parent, width=12, font=("Consolas", 14, "bold"),
                         bg=C["entry_bg"], fg=col, insertbackground=col,
                         relief="flat", bd=0, highlightthickness=1,
                         highlightbackground=C["entry_bd"],
                         highlightcolor=col)
            e.pack(ipady=6, padx=2)
            return e

        def field(parent, label, col):
            f = tk.Frame(parent, bg=C["bg"])
            f.pack(side="left", padx=(0, 20))
            tk.Label(f, text=label, font=("Segoe UI", 10),
                     bg=C["bg"], fg=C["muted"]).pack(anchor="w")
            return entry_widget(f, col)

        # ── Ligne 1 : p, q, bouton
        row1 = tk.Frame(form, bg=C["bg"])
        row1.pack(fill="x")
        self.entry_p = field(row1, "Nombre premier  p", C["blue"])
        self.entry_q = field(row1, "Nombre premier  q", C["purple"])

        self.btn = tk.Button(row1, text="  Générer les clés  →",
                             command=self._generate,
                             font=("Segoe UI", 11, "bold"),
                             bg=C["btn"], fg="white",
                             activebackground=C["btn_hover"],
                             activeforeground="white",
                             relief="flat", bd=0, cursor="hand2",
                             padx=14, pady=8)
        self.btn.pack(side="left", anchor="s", pady=(18, 0))
        self.btn.bind("<Enter>", lambda _: self.btn.config(bg=C["btn_hover"]))
        self.btn.bind("<Leave>", lambda _: self.btn.config(bg=C["btn"]))


    # ── Zone scrollable ───────────────────────

    def _build_scroll_area(self):
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x", padx=30)

        container = tk.Frame(self, bg=C["bg"])
        container.pack(fill="both", expand=True, padx=0, pady=0)

        canvas = tk.Canvas(container, bg=C["bg"], bd=0,
                           highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical",
                                 command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.cards_frame = tk.Frame(canvas, bg=C["bg"])
        self._canvas_window = canvas.create_window(
            (0, 0), window=self.cards_frame, anchor="nw")

        def on_resize(evt):
            canvas.itemconfig(self._canvas_window, width=evt.width)
        canvas.bind("<Configure>", on_resize)

        def on_frame_configure(_):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.cards_frame.bind("<Configure>", on_frame_configure)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        self._canvas = canvas

        # Placeholder
        self._placeholder = tk.Label(
            self.cards_frame,
            text="Renseignez p et q, puis cliquez sur « Générer les clés »",
            font=("Segoe UI", 11), bg=C["bg"], fg=C["muted"])
        self._placeholder.pack(pady=60)

    # ── Génération ────────────────────────────

    def _generate(self):
        try:
            p = int(self.entry_p.get())
            q = int(self.entry_q.get())
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des entiers valides.")
            return
        if not is_prime(p):
            messagebox.showerror("Erreur", f"{p} n'est pas un nombre premier.")
            return
        if not is_prime(q):
            messagebox.showerror("Erreur", f"{q} n'est pas un nombre premier.")
            return
        if p == q:
            messagebox.showerror("Erreur", "p et q doivent être distincts.")
            return

        # Réinitialiser la zone de résultats
        for w in self.cards_frame.winfo_children():
            w.destroy()
        tk.Frame(self.cards_frame, bg=C["bg"], height=6).pack()
        inner = tk.Frame(self.cards_frame, bg=C["bg"])
        inner.pack(fill="x", padx=30)

        # Étapes 1-3
        n, phi, blocks_setup = compute_setup(p, q)
        for i, block in enumerate(blocks_setup):
            make_card(inner, block, STEP_COLORS[i])

        # Pause interactive à l'étape 4
        self._show_step4_prompt(inner, n, phi)
        self._canvas.yview_moveto(0)

    # ── Carte interactive étape 4 ─────────────

    def _show_step4_prompt(self, inner, n, phi):
        accent = STEP_COLORS[3]

        card = tk.Frame(inner, bg=C["surface"], highlightthickness=1,
                        highlightbackground=accent)
        card.pack(fill="x", pady=(0, 14))

        # Bandeau
        hdr = tk.Frame(card, bg=C["header_bg"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="Étape 4 — Exposant public  e",
                 font=("Segoe UI", 11, "bold"), bg=C["header_bg"], fg=accent,
                 anchor="w", padx=16, pady=8).pack(fill="x")

        body = tk.Frame(card, bg=C["surface"])
        body.pack(fill="x", padx=16, pady=12)

        # Rappel phi
        tk.Label(body,
                 text=f"φ(n) = {phi}    —    choisir e tel que 1 < e < {phi} et pgcd(e, φ(n)) = 1",
                 font=("Consolas", 10), bg=C["surface"], fg=C["muted"],
                 anchor="w").pack(fill="x", pady=(0, 12))

        tk.Frame(body, bg=C["border"], height=1).pack(fill="x", pady=(0, 12))

        # Zone de choix
        choice_row = tk.Frame(body, bg=C["surface"])
        choice_row.pack(fill="x")

        # ── Option automatique
        auto_f = tk.Frame(choice_row, bg=C["surface"])
        auto_f.pack(side="left", padx=(0, 30))
        tk.Label(auto_f, text="Laisser l'ordinateur choisir",
                 font=("Segoe UI", 10), bg=C["surface"], fg=C["muted"]).pack(anchor="w", pady=(0, 6))

        e_auto = choose_e(phi)
        tk.Label(auto_f, text=f"→  e = {e_auto}  (plus petit valide)",
                 font=("Consolas", 10, "bold"), bg=C["surface"], fg=C["orange"]).pack(anchor="w", pady=(0, 8))

        btn_auto = tk.Button(auto_f, text="  Utiliser  e = {}  →".format(e_auto),
                             font=("Segoe UI", 10, "bold"),
                             bg=C["btn"], fg="white",
                             activebackground=C["btn_hover"], activeforeground="white",
                             relief="flat", bd=0, cursor="hand2", padx=10, pady=6)
        btn_auto.pack(anchor="w")
        btn_auto.bind("<Enter>", lambda _: btn_auto.config(bg=C["btn_hover"]))
        btn_auto.bind("<Leave>", lambda _: btn_auto.config(bg=C["btn"]))

        # ── Séparateur vertical
        tk.Frame(choice_row, bg=C["border"], width=1).pack(side="left", fill="y", padx=(0, 30))

        # ── Option manuelle
        man_f = tk.Frame(choice_row, bg=C["surface"])
        man_f.pack(side="left")
        tk.Label(man_f, text="Saisir e manuellement",
                 font=("Segoe UI", 10), bg=C["surface"], fg=C["muted"]).pack(anchor="w", pady=(0, 6))

        inp_row = tk.Frame(man_f, bg=C["surface"])
        inp_row.pack(anchor="w")
        tk.Label(inp_row, text="e =", font=("Consolas", 12, "bold"),
                 bg=C["surface"], fg=C["orange"]).pack(side="left", padx=(0, 6))
        entry_e = tk.Entry(inp_row, width=10, font=("Consolas", 13, "bold"),
                           bg=C["entry_bg"], fg=C["orange"], insertbackground=C["orange"],
                           relief="flat", bd=0, highlightthickness=1,
                           highlightbackground=C["entry_bd"], highlightcolor=C["orange"])
        entry_e.pack(side="left", ipady=5, padx=2)

        err_lbl = tk.Label(man_f, text="", font=("Segoe UI", 9, "italic"),
                           bg=C["surface"], fg=C["pink"])
        err_lbl.pack(anchor="w", pady=(4, 0))

        btn_man = tk.Button(man_f, text="  Valider e  →",
                            font=("Segoe UI", 10, "bold"),
                            bg="#6e3d8a", fg="white",
                            activebackground="#8a4fad", activeforeground="white",
                            relief="flat", bd=0, cursor="hand2", padx=10, pady=6)
        btn_man.pack(anchor="w", pady=(8, 0))
        btn_man.bind("<Enter>", lambda _: btn_man.config(bg="#8a4fad"))
        btn_man.bind("<Leave>", lambda _: btn_man.config(bg="#6e3d8a"))

        # ── Callbacks
        def on_auto():
            card.destroy()
            self._finalize(inner, n, phi, e_auto, "choisi automatiquement")

        def on_manual():
            try:
                e = int(entry_e.get())
            except ValueError:
                err_lbl.config(text="e doit être un entier.")
                return
            if not (1 < e < phi):
                err_lbl.config(text=f"e doit être compris entre 1 et {phi}.")
                return
            if euclide_etendu(e, phi)[0] != 1:
                err_lbl.config(text=f"pgcd({e}, {phi}) ≠ 1 — choisir un autre e.")
                return
            card.destroy()
            self._finalize(inner, n, phi, e, "saisi manuellement")

        btn_auto.config(command=on_auto)
        btn_man.config(command=on_manual)
        entry_e.bind("<Return>", lambda _: on_manual())

        self._canvas.yview_moveto(1.0)

    # ── Finalisation (étapes 4-5-résultat) ────

    def _finalize(self, inner, n, phi, e, source):
        blocks = compute_keys(n, phi, e, source)
        accents = STEP_COLORS[3:] + [C["teal"]]
        for i, block in enumerate(blocks):
            make_card(inner, block, accents[i % len(accents)])
        d = pow(e, -1, phi)
        self._show_encrypt_prompt(inner, e, d, n)
        self.after(50, lambda: self._canvas.yview_moveto(1.0))

    # ── Chiffrement / Déchiffrement ───────────

    def _show_encrypt_prompt(self, inner, e, d, n):
        accent = "#79c0ff"

        card = tk.Frame(inner, bg=C["surface"], highlightthickness=1,
                        highlightbackground=accent)
        card.pack(fill="x", pady=(0, 14))

        hdr = tk.Frame(card, bg=C["header_bg"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="Chiffrement / Déchiffrement RSA",
                 font=("Segoe UI", 11, "bold"), bg=C["header_bg"], fg=accent,
                 anchor="w", padx=16, pady=8).pack(fill="x")

        body = tk.Frame(card, bg=C["surface"])
        body.pack(fill="x", padx=16, pady=12)

        # Rappel des clés
        keys_row = tk.Frame(body, bg=C["surface"])
        keys_row.pack(fill="x", pady=(0, 10))
        for txt, col in [(f"Clé publique   (e={e}, n={n})", C["teal"]),
                         (f"Clé privée       (d={d}, n={n})", C["pink"])]:
            tk.Label(keys_row, text=txt, font=("Consolas", 9, "bold"),
                     bg=C["surface"], fg=col).pack(side="left", padx=(0, 24))

        tk.Frame(body, bg=C["border"], height=1).pack(fill="x", pady=(0, 10))

        # Saisie du message
        tk.Label(body, text=f"Message  m  —  entier tel que  0 ≤ m < n = {n}",
                 font=("Segoe UI", 10), bg=C["surface"], fg=C["muted"],
                 anchor="w").pack(anchor="w", pady=(0, 6))

        inp_row = tk.Frame(body, bg=C["surface"])
        inp_row.pack(anchor="w")
        tk.Label(inp_row, text="m =", font=("Consolas", 12, "bold"),
                 bg=C["surface"], fg=accent).pack(side="left", padx=(0, 8))
        entry_m = tk.Entry(inp_row, width=14, font=("Consolas", 13, "bold"),
                           bg=C["entry_bg"], fg=accent, insertbackground=accent,
                           relief="flat", bd=0, highlightthickness=1,
                           highlightbackground=C["entry_bd"], highlightcolor=accent)
        entry_m.pack(side="left", ipady=6, padx=2)

        btn = tk.Button(inp_row, text="  Chiffrer  →",
                        font=("Segoe UI", 10, "bold"),
                        bg="#1a4a7a", fg="white",
                        activebackground="#2060a0", activeforeground="white",
                        relief="flat", bd=0, cursor="hand2", padx=10, pady=7)
        btn.pack(side="left", padx=(12, 0))
        btn.bind("<Enter>", lambda _: btn.config(bg="#2060a0"))
        btn.bind("<Leave>", lambda _: btn.config(bg="#1a4a7a"))

        err_lbl = tk.Label(body, text="", font=("Segoe UI", 9, "italic"),
                           bg=C["surface"], fg=C["pink"])
        err_lbl.pack(anchor="w", pady=(4, 0))

        result_frame = tk.Frame(body, bg=C["surface"])
        result_frame.pack(fill="x")

        def block_result(parent, title, formula, result_txt, fg):
            f = tk.Frame(parent, bg=C["header_bg"],
                         highlightthickness=1, highlightbackground=C["border"])
            f.pack(fill="x", pady=(0, 6))
            b = tk.Frame(f, bg=C["header_bg"])
            b.pack(fill="x", padx=14, pady=8)
            tk.Label(b, text=title, font=("Segoe UI", 9, "italic"),
                     bg=C["header_bg"], fg=C["muted"], anchor="w").pack(anchor="w")
            tk.Label(b, text=formula, font=("Consolas", 10),
                     bg=C["header_bg"], fg=C["muted"], anchor="w").pack(anchor="w")
            tk.Label(b, text=result_txt, font=("Consolas", 13, "bold"),
                     bg=C["header_bg"], fg=fg, anchor="w").pack(anchor="w")

        def on_encrypt():
            try:
                m = int(entry_m.get())
            except ValueError:
                err_lbl.config(text="m doit être un entier.")
                return
            if not (0 <= m < n):
                err_lbl.config(text=f"m doit être compris entre 0 et {n - 1}.")
                return
            err_lbl.config(text="")

            for w in result_frame.winfo_children():
                w.destroy()

            c   = pow(m, e, n)
            m2  = pow(c, d, n)
            ok  = (m2 == m)

            tk.Frame(result_frame, bg=C["border"], height=1).pack(
                fill="x", pady=(10, 10))

            block_result(result_frame,
                         "Chiffrement :",
                         f"c  =  m^e mod n  =  {m}^{e} mod {n}",
                         f"c  =  {c}",
                         C["teal"])

            block_result(result_frame,
                         "Déchiffrement :",
                         f"m'  =  c^d mod n  =  {c}^{d} mod {n}",
                         f"m'  =  {m2}",
                         C["blue"])

            verif_bg  = "#1a2b1a" if ok else "#2b1a1a"
            verif_fg  = C["green"] if ok else C["pink"]
            verif_txt = f"✓  m' = m = {m}   —   vérification réussie" \
                        if ok else f"✗  m' = {m2} ≠ m = {m}"
            vf = tk.Frame(result_frame, bg=verif_bg,
                          highlightthickness=1, highlightbackground=verif_fg)
            vf.pack(fill="x")
            tk.Label(vf, text=verif_txt,
                     font=("Consolas", 11, "bold"),
                     bg=verif_bg, fg=verif_fg,
                     anchor="w", padx=14, pady=8).pack(fill="x")

            self.after(50, lambda: self._canvas.yview_moveto(1.0))

        btn.config(command=on_encrypt)
        entry_m.bind("<Return>", lambda _: on_encrypt())


# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = RSAApp()
    app.mainloop()
