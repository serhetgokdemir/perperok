import os
import subprocess
import sys
from typing import Dict

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .core import PdfJob, unlock_pdfs
from .icon_gen import ensure_icon


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas_frame = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _on_configure(event):
            canvas.itemconfig(canvas_frame, width=event.width)

        canvas.bind("<Configure>", _on_configure)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


class PdfUnlockerApp:
    def __init__(self, root: tk.Tk, icon_image: tk.PhotoImage | None = None):
        self.root = root
        self.root.title("PDF Unlocker")
        self.root.geometry("900x600")

        # Keep a reference so image is not garbage-collected
        self.icon_image = icon_image

        # UI state
        # list of dicts per row: {path, name, selected_var, checkbox, password_var, entry, toggle_btn}
        self.pdf_rows = []
        self.target_dir = tk.StringVar()
        self.use_common_password = tk.BooleanVar(value=False)
        self.common_password_var = tk.StringVar()

        self.select_all_var = tk.BooleanVar(value=True)

        self.progress_percent = tk.DoubleVar(value=0.0)
        self.status_text = tk.StringVar(value="Hazır")

        self._build_ui()

    # ---------- UI BUILD ----------
    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # PDF selection controls
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.columnconfigure(1, weight=1)

        if self.icon_image is not None:
            icon_label = ttk.Label(top_frame, image=self.icon_image)
            icon_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
            ttk.Label(top_frame, text="PDF Dosyaları").grid(row=0, column=1, sticky="w")
            top_frame.columnconfigure(1, weight=1)
        else:
            ttk.Label(top_frame, text="PDF Dosyaları").grid(row=0, column=0, sticky="w")
            top_frame.columnconfigure(1, weight=1)
        add_btn = ttk.Button(top_frame, text="PDF Ekle...", command=self.add_pdfs)
        add_btn.grid(row=0, column=2, sticky="e")

        remove_btn = ttk.Button(
            top_frame, text="Seçili PDF'leri Sil", command=self.remove_selected_pdfs
        )
        remove_btn.grid(row=1, column=2, sticky="e", pady=(5, 0))

        # Scrollable list of PDFs with per-file passwords
        list_frame = ttk.LabelFrame(main_frame, text="Seçilen PDF'ler")
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.scrollable = ScrollableFrame(list_frame)
        self.scrollable.grid(row=0, column=0, sticky="nsew")

        header = ttk.Frame(self.scrollable.scrollable_frame)
        header.grid(row=0, column=0, sticky="ew", padx=(0, 15))
        header.columnconfigure(1, weight=3)
        header.columnconfigure(2, weight=2)

        select_all_cb = ttk.Checkbutton(
            header,
            variable=self.select_all_var,
            command=self._on_select_all_toggle,
        )
        select_all_cb.grid(row=0, column=0, sticky="w", padx=(0, 5))

        ttk.Label(header, text="Dosya Adı", width=40).grid(row=0, column=1, sticky="w")
        ttk.Label(header, text="Şifre").grid(row=0, column=2, sticky="w")

        ttk.Separator(self.scrollable.scrollable_frame, orient="horizontal").grid(
            row=1, column=0, sticky="ew", pady=5
        )

        self.rows_container = ttk.Frame(self.scrollable.scrollable_frame)
        self.rows_container.grid(row=2, column=0, sticky="nsew")
        # columns: 0 checkbox, 1 name, 2 password entry, 3 show/hide button
        self.rows_container.columnconfigure(1, weight=3)
        self.rows_container.columnconfigure(2, weight=2)

        # Password mode controls
        password_mode_frame = ttk.LabelFrame(main_frame, text="Şifre Ayarları")
        password_mode_frame.grid(row=2, column=0, sticky="ew", pady=(10, 10))
        password_mode_frame.columnconfigure(1, weight=1)

        common_checkbox = ttk.Checkbutton(
            password_mode_frame,
            text="Tüm PDF'ler için ortak şifre kullan",
            variable=self.use_common_password,
            command=self._on_common_password_toggle,
        )
        common_checkbox.grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(password_mode_frame, text="Ortak Şifre:").grid(
            row=1, column=0, sticky="w", pady=(5, 0)
        )

        common_pw_frame = ttk.Frame(password_mode_frame)
        common_pw_frame.grid(row=1, column=1, sticky="ew", pady=(5, 0))
        common_pw_frame.columnconfigure(0, weight=1)

        self.common_pw_entry = ttk.Entry(
            common_pw_frame, textvariable=self.common_password_var, show="*"
        )
        self.common_pw_entry.grid(row=0, column=0, sticky="ew")

        self.common_pw_visible = False
        self.common_pw_toggle_btn = ttk.Button(
            common_pw_frame,
            text="Göster",
            width=8,
            command=self._toggle_common_password_visibility,
        )
        self.common_pw_toggle_btn.grid(row=0, column=1, padx=(5, 0))

        # Target directory
        target_frame = ttk.LabelFrame(main_frame, text="Hedef Klasör")
        target_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        target_frame.columnconfigure(0, weight=1)

        path_frame = ttk.Frame(target_frame)
        path_frame.grid(row=0, column=0, sticky="ew", pady=5)
        path_frame.columnconfigure(0, weight=1)

        self.target_label = ttk.Label(path_frame, text="Henüz seçilmedi")
        self.target_label.grid(row=0, column=0, sticky="w")

        select_target_btn = ttk.Button(
            path_frame, text="Klasör Seç...", command=self.select_target_folder
        )
        select_target_btn.grid(row=0, column=1, padx=(10, 0))

        show_target_btn = ttk.Button(
            path_frame, text="Klasörü Göster", command=self.open_target_folder
        )
        show_target_btn.grid(row=0, column=2, padx=(10, 0))

        # Bottom: progress + start button
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=4, column=0, sticky="ew")
        bottom_frame.columnconfigure(0, weight=1)

        progress_frame = ttk.Frame(bottom_frame)
        progress_frame.grid(row=0, column=0, sticky="ew", pady=(5, 0))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_percent,
            maximum=100.0,
            mode="determinate",
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.status_label = ttk.Label(progress_frame, textvariable=self.status_text)
        self.status_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        start_btn = ttk.Button(
            bottom_frame,
            text="Şifreyi Çöz ve Kaydet",
            command=self.start_unlock,
        )
        start_btn.grid(row=0, column=1, padx=(10, 0))

        self._on_common_password_toggle()

    # ---------- UI ACTIONS ----------
    def add_pdfs(self):
        file_paths = filedialog.askopenfilenames(
            title="PDF Dosyaları Seç",
            filetypes=[("PDF Dosyaları", "*.pdf"), ("Tümü", "*.*")],
        )
        if not file_paths:
            return

        for path in file_paths:
            path = os.path.abspath(path)
            if any(row["path"] == path for row in self.pdf_rows):
                continue
            self._add_pdf_row(path)

    def remove_selected_pdfs(self) -> None:
        if not self.pdf_rows:
            return

        remaining_rows = []
        for row in self.pdf_rows:
            if row["selected_var"].get():  # type: ignore[call-arg]
                # Remove widgets for selected rows
                row["checkbox"].grid_forget()  # type: ignore[call-arg]
                row["name_label"].grid_forget()  # type: ignore[call-arg]
                row["entry"].grid_forget()  # type: ignore[call-arg]
                row["toggle_btn"].grid_forget()  # type: ignore[call-arg]
            else:
                remaining_rows.append(row)

        self.pdf_rows = remaining_rows

        # Re-grid remaining rows to close gaps and keep alignment
        for idx, row in enumerate(self.pdf_rows):
            row["checkbox"].grid_configure(row=idx, column=0, sticky="w", padx=(0, 5))  # type: ignore[call-arg]
            row["name_label"].grid_configure(row=idx, column=1, sticky="w")  # type: ignore[call-arg]
            row["entry"].grid_configure(row=idx, column=2, sticky="ew", padx=(5, 0))  # type: ignore[call-arg]
            row["toggle_btn"].grid_configure(row=idx, column=3, padx=(5, 0))  # type: ignore[call-arg]
            self._update_row_password_state(row)

        if not self.pdf_rows:
            self.select_all_var.set(False)
        else:
            all_selected = all(r["selected_var"].get() for r in self.pdf_rows)  # type: ignore[call-arg]
            self.select_all_var.set(all_selected)

    def _add_pdf_row(self, path: str):
        row_index = len(self.pdf_rows)
        name = os.path.basename(path)
        selected_var = tk.BooleanVar(value=True)
        checkbox = ttk.Checkbutton(
            self.rows_container,
            variable=selected_var,
            command=lambda: self._on_row_checkbox_toggled(row_data),
        )

        name_label = ttk.Label(self.rows_container, text=name, anchor="w")

        password_var = tk.StringVar()
        entry = ttk.Entry(self.rows_container, textvariable=password_var, show="*")

        toggle_btn = ttk.Button(
            self.rows_container,
            text="Göster",
            width=8,
            command=lambda e=entry, b=None: self._toggle_password_visibility(e, toggle_btn),
        )

        row_data: Dict[str, object] = {
            "path": path,
            "name": name,
            "selected_var": selected_var,
            "checkbox": checkbox,
            "name_label": name_label,
            "password_var": password_var,
            "entry": entry,
            "toggle_btn": toggle_btn,
        }
        self.pdf_rows.append(row_data)

        # grid widgets in a consistent column layout for alignment
        checkbox.grid(row=row_index, column=0, sticky="w", padx=(0, 5))
        name_label.grid(row=row_index, column=1, sticky="w")
        entry.grid(row=row_index, column=2, sticky="ew", padx=(5, 0))
        toggle_btn.grid(row=row_index, column=3, padx=(5, 0))

        self._update_row_password_state(row_data)

    def _toggle_password_visibility(self, entry: ttk.Entry, button: ttk.Button):
        if entry.cget("show") == "":
            entry.config(show="*")
            button.config(text="Göster")
        else:
            entry.config(show="")
            button.config(text="Gizle")

    def _toggle_common_password_visibility(self):
        if self.common_pw_entry.cget("show") == "":
            self.common_pw_entry.config(show="*")
            self.common_pw_toggle_btn.config(text="Göster")
            self.common_pw_visible = False
        else:
            self.common_pw_entry.config(show="")
            self.common_pw_toggle_btn.config(text="Gizle")
            self.common_pw_visible = True

    def _update_row_password_state(self, row: Dict[str, object]) -> None:
        selected = row["selected_var"].get()  # type: ignore[call-arg]
        if not selected:
            state = "disabled"
        else:
            state = "disabled" if self.use_common_password.get() else "normal"

        row["entry"].config(state=state)  # type: ignore[call-arg]
        row["toggle_btn"].config(state=state)  # type: ignore[call-arg]

    def _on_common_password_toggle(self):
        for row in self.pdf_rows:
            self._update_row_password_state(row)

        common_state = "normal" if self.use_common_password.get() else "disabled"
        self.common_pw_entry.config(state=common_state)
        self.common_pw_toggle_btn.config(state=common_state)

    def _on_row_checkbox_toggled(self, row: Dict[str, object]) -> None:
        self._update_row_password_state(row)

        # update select-all checkbox based on current rows
        if not self.pdf_rows:
            self.select_all_var.set(False)
            return

        all_selected = all(r["selected_var"].get() for r in self.pdf_rows)  # type: ignore[call-arg]
        self.select_all_var.set(all_selected)

    def _on_select_all_toggle(self) -> None:
        target_value = self.select_all_var.get()
        for row in self.pdf_rows:
            row["selected_var"].set(target_value)  # type: ignore[call-arg]
            self._update_row_password_state(row)

    def select_target_folder(self):
        folder = filedialog.askdirectory(title="Hedef Klasör Seç")
        if not folder:
            return
        folder = os.path.abspath(folder)
        self.target_dir.set(folder)
        self.target_label.config(text=folder)

    def open_target_folder(self) -> None:
        folder = self.target_dir.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showwarning("Uyarı", "Geçerli bir hedef klasör seçilmemiş.")
            return

        try:
            if sys.platform.startswith("darwin"):
                subprocess.Popen(["open", folder])
            elif os.name == "nt":
                os.startfile(folder)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Hata", f"Klasör açılamadı: {exc}")

    # ---------- PROCESSING ----------
    def start_unlock(self):
        if not self.pdf_rows:
            messagebox.showwarning("Uyarı", "Lütfen en az bir PDF dosyası ekleyin.")
            return

        selected_rows = [row for row in self.pdf_rows if row["selected_var"].get()]  # type: ignore[call-arg]
        if not selected_rows:
            messagebox.showwarning("Uyarı", "Lütfen en az bir PDF seçin.")
            return

        target = self.target_dir.get()
        if not target:
            messagebox.showwarning("Uyarı", "Lütfen bir hedef klasör seçin.")
            return

        if not os.path.isdir(target):
            messagebox.showerror("Hata", "Hedef klasör geçerli değil.")
            return

        use_common = self.use_common_password.get()

        if use_common:
            common_pw = self.common_password_var.get()
            if not common_pw:
                messagebox.showwarning(
                    "Uyarı", "Ortak şifre modunda, ortak şifre alanı boş bırakılamaz."
                )
                return
            passwords = {row["path"]: common_pw for row in selected_rows}
        else:
            passwords: Dict[str, str] = {}
            for row in selected_rows:
                pw = row["password_var"].get()  # type: ignore[call-arg]
                if not pw:
                    messagebox.showwarning(
                        "Uyarı",
                        f"'{row['name']}' dosyası için şifre girilmemiş. Lütfen tüm dosyalar için şifre girin.",
                    )
                    return
                passwords[row["path"]] = pw

        self._process_pdfs(passwords, target, selected_rows)

    def _process_pdfs(self, passwords: Dict[str, str], target_dir: str, selected_rows):
        total = len(selected_rows)
        if total == 0:
            return

        self.status_text.set("İşlem başlatılıyor...")
        self.progress_percent.set(0)
        self.root.update_idletasks()

        jobs = [
            PdfJob(path=row["path"], password=passwords[row["path"]])
            for row in selected_rows
        ]

        def progress_callback(index: int, total_count: int, name: str) -> None:
            # index: 1-based
            progress_value = (index / max(total_count, 1)) * 100.0
            self.status_text.set(f"İşleniyor: {name} ({index}/{total_count})")
            self.progress_percent.set(progress_value)
            self.root.update_idletasks()

        success_paths, failed = unlock_pdfs(jobs, target_dir, progress_callback)

        total = len(jobs)
        success = len(success_paths)

        if failed:
            msg_lines = [
                f"Toplam {total} dosyanın {success} tanesi başarıyla çözüldü, {len(failed)} tanesi başarısız.",
                "",
                "Başarısız dosyalar:",
            ]
            for fname, reason in failed:
                msg_lines.append(f"- {fname}: {reason}")

            messagebox.showwarning("İşlem Tamamlandı (Bazı Hatalar Var)", "\n".join(msg_lines))
            self.status_text.set("Tamamlandı (bazı hatalar var)")
        else:
            messagebox.showinfo(
                "İşlem Tamamlandı",
                f"Toplam {total} dosyanın tamamı başarıyla çözüldü.",
            )
            self.status_text.set("Tüm dosyalar başarıyla çözüldü")

    # ---------- MAIN LOOP ----------
    def run(self) -> None:
        self.root.mainloop()


def run_app() -> None:
    # Create root window first
    root = tk.Tk()

    # Ensure icon PNG exists, then load and set as window icon
    icon_path = ensure_icon()
    if icon_path is not None:
        try:
            icon_img = tk.PhotoImage(file=icon_path)
            root.iconphoto(False, icon_img)
        except Exception:  # noqa: BLE001
            icon_img = None
    else:
        icon_img = None

    app = PdfUnlockerApp(root, icon_image=icon_img)
    app.run()
