import os
import fitz
import tkinter as tk
import shutil
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class PDFReviewer:

    def __init__(self, root):
        self.root = root
        self.root.title("Smart PDF Reviewing System")
        self.root.geometry("1200x800")

        # Professional Theme
        self.bg_color = "#F4F6F9"
        self.primary = "#2563EB"
        self.success = "#16A34A"
        self.danger = "#DC2626"
        self.warning = "#F59E0B"
        self.dark = "#1F2937"

        self.root.configure(bg=self.bg_color)

        self.pdf_files = []
        self.index = 0
        self.images = []
        self.zoom = 1.2
        self.page_positions = []
        self.last_deleted = None
        self.last_deleted_original = None
        self.last_deleted_index = None
        
        # ---------- Title ----------
        title_frame = tk.Frame(root, bg=self.bg_color)
        title_frame.pack(fill="x", pady=(10,5))

        tk.Label(
            title_frame,
            text="SMART PDF REVIEWING SYSTEM",
            font=("Segoe UI", 22, "bold"),
            fg=self.primary,
            bg=self.bg_color
        ).pack()

        tk.Label(
            title_frame,
            text="Review • Search • Manage PDF Files",
            font=("Segoe UI", 10),
            fg="gray",
            bg=self.bg_color
        ).pack()

        # ---------- Top Toolbar Button ----------
        # Scrollable Toolbar
        toolbar_canvas = tk.Canvas(
            root,
            height=60,
            bg="#E5E7EB",
            highlightthickness=0
        )
        toolbar_canvas.pack(fill="x")

        toolbar_scroll = tk.Scrollbar(
            root,
            orient="horizontal",
            command=toolbar_canvas.xview
        )
        toolbar_scroll.pack(fill="x")

        toolbar_canvas.configure(
            xscrollcommand=toolbar_scroll.set
        )

        button_frame = tk.Frame(
            toolbar_canvas,
            bg="#E5E7EB"
        )

        toolbar_canvas.create_window(
            (0, 0),
            window=button_frame,
            anchor="nw"
        )

        button_frame.bind(
            "<Configure>",
            lambda e: toolbar_canvas.configure(
                scrollregion=toolbar_canvas.bbox("all")
            )
        )

        btn_style = {
            "font": ("Segoe UI", 10, "bold"),
            "bd": 0,
            "padx": 15,
            "pady": 10,
            "cursor": "hand2",
            "relief": "flat"
        }

        self.select_btn = tk.Button(
            button_frame,
            text="📂 SELECT FOLDER",
            command=self.select_folder,
            font=("Segoe UI", 10, "bold"),
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.select_btn.pack(side="left", padx=5)   


        self.prev_btn = tk.Button(
            button_frame,
            text="⬅ PREVIOUS",
            command=self.previous_pdf,
            font=("Segoe UI", 10, "bold"),
            bg="#6B7280",
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.prev_btn.pack(side="left", padx=5)
        

        self.keep_btn = tk.Button(
            button_frame,
            text="✔ KEEP",
            command=self.keep_pdf,
            font=("Segoe UI", 10, "bold"),
            bg="#16A34A",
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.keep_btn.pack(side="left", padx=5)

        self.delete_btn = tk.Button(
            button_frame,
            text="🗑 DELETE",
            command=self.delete_pdf,
            font=("Segoe UI", 10, "bold"),
            bg="#DC2626",
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.delete_btn.pack(side="left", padx=5)

        self.undo_btn = tk.Button(
            button_frame,
            text="↩ UNDO",
            command=self.undo_delete,
            font=("Segoe UI", 10, "bold"),
            bg="#F59E0B",
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.undo_btn.pack(side="left", padx=5)
        
        self.next_btn = tk.Button(
            button_frame,
            text="NEXT ➡",
            command=self.next_pdf,
            font=("Segoe UI", 10, "bold"),
            bg="#6B7280",
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.next_btn.pack(side="left", padx=5)

        self.zoomin_btn = tk.Button(
            button_frame,
            text="🔍 ZOOM +",
            command=self.zoom_in,
            font=("Segoe UI", 10, "bold"),
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.zoomin_btn.pack(side="left", padx=5)

        self.zoomout_btn = tk.Button(
            button_frame,
            text="🔎 ZOOM -",
            command=self.zoom_out,
            font=("Segoe UI", 10, "bold"),
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.zoomout_btn.pack(side="left", padx=5)

        # Search PDF
        self.search_entry = tk.Entry(button_frame, width=20)
        self.search_entry.pack(side="left", padx=5)

        self.search_entry.bind(
            "<Return>",
            lambda e: self.search_pdf()
            )
         
        self.search_btn = tk.Button(
            button_frame,
            text="🔍 SEARCH",
            command=self.search_pdf,
            font=("Segoe UI", 10, "bold"),
            bg="#0891B2",
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.search_btn.pack(side="left", padx=5)

        # Go To PDF Number
        self.goto_entry = tk.Entry(button_frame, width=6)
        self.goto_entry.pack(side="left", padx=5)

        self.goto_entry.bind(
            "<Return>",
            lambda e: self.goto_pdf()
            )
        
        self.goto_btn = tk.Button(
            button_frame,
            text="📄 Jump TO PDF",
            command=self.goto_pdf,
            font=("Segoe UI", 10, "bold"),
            bg="#7C3AED",
            fg="white",
            relief="flat",
            bd=0,
            padx=15,
            pady=10,
            cursor="hand2"
        )
        self.goto_btn.pack(side="left", padx=5)

        # Hover Effects
        self.add_hover(self.select_btn, "#2563EB", "#1D4ED8")
        self.add_hover(self.prev_btn, "#6B7280", "#4B5563")
        self.add_hover(self.keep_btn, "#16A34A", "#15803D")
        self.add_hover(self.delete_btn, "#DC2626", "#B91C1C")
        self.add_hover(self.undo_btn, "#F59E0B", "#D97706")
        self.add_hover(self.next_btn, "#6B7280", "#4B5563")
        self.add_hover(self.zoomin_btn, "#2563EB", "#1D4ED8")
        self.add_hover(self.zoomout_btn, "#2563EB", "#1D4ED8")
        self.add_hover(self.search_btn, "#0891B2", "#0E7490")
        self.add_hover(self.goto_btn, "#7C3AED", "#6D28D9")

        # ---------- Status ----------
        self.dark = "#1F2937"

        self.status_label = tk.Label(
            root,
            text="No PDF Loaded",
            font=("Segoe UI", 10, "bold"),
            bg=self.dark,
            fg="white",
            padx=10,
            pady=8,
            anchor="w"
        )
        self.status_label.pack(fill="x")

        # ---------- Canvas Area ----------
        canvas_frame = tk.Frame(root)
        canvas_frame.pack(fill="both", expand=True)

        self.v_scrollbar = tk.Scrollbar(
            canvas_frame,
            orient="vertical"
        )

        self.h_scrollbar = tk.Scrollbar(
            canvas_frame,
            orient="horizontal"
        )

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="#E5E7EB",
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )

        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)

        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.root.bind(
            "<Button-1>",
            self.remove_focus
            )

        # ---------- Mouse Scroll ----------
        def on_mousewheel(event):

            self.canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

            self.update_current_page()

        self.canvas.bind_all(
            "<MouseWheel>",
            on_mousewheel
        )

        self.canvas.bind_all(
            "<Shift-MouseWheel>",
            lambda e: self.canvas.xview_scroll(
                int(-1 * (e.delta / 120)),
                "units"
            )
        )
        self.canvas.bind_all(
            "<Control-MouseWheel>",
            self.ctrl_zoom
        )

        toolbar_canvas.bind_all(
            "<Shift-MouseWheel>",
            lambda e: toolbar_canvas.xview_scroll(
                int(-1 * (e.delta / 120)),
                "units"
            )
        )

        # ---------- Keyboard Shortcuts ----------
        root.bind("<Control-k>", lambda e: self.keep_pdf())
        root.bind("<Control-d>", lambda e: self.delete_pdf())
        root.bind(
            "<Control-s>",
            lambda e: self.search_entry.focus_set()
        )
        root.bind("<Right>", lambda e: self.next_pdf())
        root.bind("<Left>", lambda e: self.previous_pdf())
        root.bind(
            "<Control-j>",
            lambda e: self.goto_entry.focus_set()
        )
        root.bind(
            "<Control-z>",
            lambda e: self.undo_delete()
        )

        root.bind(
            "<Control-plus>",
            lambda e: self.zoom_in()
        )

        root.bind(
            "<Control-equal>",
            lambda e: self.zoom_in()
        )

        root.bind(
            "<Control-minus>",
            lambda e: self.zoom_out()
        )
        root.bind(
            "<F11>",
            lambda e: root.attributes(
                "-fullscreen",
                not root.attributes("-fullscreen")
            )
        )

        self.canvas.bind(
            "<Configure>",
            self.auto_fit_pdf
        )


    def select_folder(self):

        folder = filedialog.askdirectory()

        if not folder:
            return

        self.pdf_files = sorted([
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(".pdf")
        ])

        if not self.pdf_files:
            messagebox.showinfo(
                "Info",
                "No PDF files found."
            )
            return

        self.index = 0
        self.show_pdf()

    def update_status(self):

        if not self.pdf_files:
            self.status_label.config(
                text="No PDF Loaded"
            )
            return

        filename = os.path.basename(
            self.pdf_files[self.index]
        )

        self.status_label.config(
            text=f"{self.index + 1}/{len(self.pdf_files)}  |  {filename}  |  Zoom: {self.zoom:.1f}x"
        )

    def show_pdf(self):

        if not self.pdf_files:
            return

        pdf_path = self.pdf_files[self.index]

        self.canvas.delete("all")
        self.images = []
        self.page_positions = []

        try:

            pdf = fitz.open(pdf_path)

            y_position = 10
            max_width = 0

            for page_num in range(len(pdf)):

                page = pdf.load_page(page_num)

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(
                        self.zoom,
                        self.zoom
                    )
                )

                mode = "RGB"

                image = Image.frombytes(
                    mode,
                    [pix.width, pix.height],
                    pix.samples
                )

                photo = ImageTk.PhotoImage(image)

                self.images.append(photo)

                self.page_positions.append(y_position)

                self.canvas.create_image(
                    10,
                    y_position,
                    anchor="nw",
                    image=photo
                )

                y_position += pix.height + 20

                max_width = max(
                    max_width,
                    pix.width
                )

            self.canvas.config(
                scrollregion=(
                    0,
                    0,
                    max_width + 50,
                    y_position + 50
                )
            )

            self.canvas.yview_moveto(0)

            pdf.close()

            self.update_current_page()

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    def zoom_in(self):

        self.zoom += 0.2
        self.show_pdf()

    def zoom_out(self):

        if self.zoom > 0.4:
            self.zoom -= 0.2
            self.show_pdf()

    def keep_pdf(self):

        if not self.pdf_files:
            return

        self.next_pdf()

    def ctrl_zoom(self, event):

        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def delete_pdf(self):

        if not self.pdf_files:
            return

        pdf_path = self.pdf_files[self.index]
        deleted_folder = os.path.join(
            os.path.dirname(pdf_path),
            "Deleted_PDFs"
        )

        os.makedirs(
            deleted_folder,
            exist_ok=True
        )

        deleted_path = os.path.join(
            deleted_folder,
            os.path.basename(pdf_path)
        )

        self.last_deleted = deleted_path
        self.last_deleted_original = pdf_path
        self.last_deleted_index = self.index
        
        answer = messagebox.askyesno(
            "Delete",
             f"Delete?\n\n{os.path.basename(pdf_path)}"
        )

        if not answer:
            return

        try:

            shutil.move(
                pdf_path,
                deleted_path
            )

            del self.pdf_files[self.index]

            if not self.pdf_files:

                self.canvas.delete("all")

                self.canvas.create_text(
                    600,
                    300,
                    text="All PDFs Reviewed",
                    font=("Arial", 24)
                )

                self.status_label.config(
                    text="Review Completed"
                )

                return

            if self.index >= len(self.pdf_files):
                self.index = len(self.pdf_files) - 1

            self.show_pdf()

        except Exception as e:
            messagebox.showerror(
                "Delete Error",
                str(e)
            )
    
    def undo_delete(self):

        if not self.last_deleted:
            messagebox.showinfo(
                "Undo",
                "Nothing to restore"
            )
            return

        try:

            shutil.move(
                self.last_deleted,
                self.last_deleted_original
            )

            self.pdf_files.insert(
                self.last_deleted_index,
                self.last_deleted_original
            )

            self.index = self.last_deleted_index

            self.show_pdf()

            self.last_deleted = None
            self.last_deleted_original = None
            self.last_deleted_index = None

            messagebox.showinfo(
                "Undo",
                "PDF restored successfully"
            )

        except Exception as e:

            messagebox.showerror(
                "Undo Error",
                str(e)
            )

    def next_pdf(self):

        if not self.pdf_files:
            return

        if self.index < len(self.pdf_files) - 1:

            self.index += 1
            self.show_pdf()

    def previous_pdf(self):

        if not self.pdf_files:
            return

        if self.index > 0:

            self.index -= 1
            self.show_pdf()
    
    def search_pdf(self):

        keyword = self.search_entry.get().lower()

        for i, pdf in enumerate(self.pdf_files):

            if keyword in os.path.basename(pdf).lower():

                self.index = i
                self.show_pdf()
                return

        messagebox.showinfo(
            "Search",
            "PDF not found"
        )
        

    def goto_pdf(self):

        try:

            pdf_no = int(
                self.goto_entry.get()
            )

            if 1 <= pdf_no <= len(self.pdf_files):

                self.index = pdf_no - 1
                self.show_pdf()

            else:

                messagebox.showwarning(
                    "Invalid",
                    "PDF number out of range"
                )

        except:

            messagebox.showwarning(
                "Invalid",
                "Enter valid number"
            )


    def auto_fit_pdf(self, event=None):

        if not self.pdf_files:
            return

        try:

            pdf = fitz.open(
                self.pdf_files[self.index]
            )

            page = pdf.load_page(0)

            canvas_width = max(
                self.canvas.winfo_width(),
                800
            )

            new_zoom = (
                canvas_width - 40
            ) / page.rect.width

            pdf.close()

            if abs(new_zoom - self.zoom) > 0.05:

                self.zoom = new_zoom

                self.root.after(
                    100,
                    self.show_pdf
                )

        except:
            pass
    
    def update_current_page(self):

            if not self.page_positions:
                return

            top_y = self.canvas.canvasy(0)

            current_page = 1

            for i, pos in enumerate(self.page_positions):

                if top_y >= pos:
                    current_page = i + 1
                else:
                    break

            total_pages = len(self.page_positions)

            filename = os.path.basename(
                self.pdf_files[self.index]
            )

            self.status_label.config(
                text=f"PDF {self.index+1}/{len(self.pdf_files)} | Page {current_page}/{total_pages} | {filename} | Zoom: {self.zoom:.1f}x"
            )
    
    def add_hover(self, button, normal_color, hover_color):

            button.bind(
                "<Enter>",
                lambda e: button.config(bg=hover_color)
            )

            button.bind(
                "<Leave>",
                lambda e: button.config(bg=normal_color)
            )

    def remove_focus(self, event):

        if event.widget not in (
            self.search_entry,
            self.goto_entry
        ):
            self.canvas.focus_set()

if __name__ == "__main__":

    root = tk.Tk()

    app = PDFReviewer(root)

    root.mainloop()
