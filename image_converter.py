#!/usr/bin/env python3
"""
Imageflow - Simple Image Converter Application
Converts between various image formats including png, jpeg, webp, eps, pdf, tiff, bmp, svg, heif/heic, psd, gif
"""

import os
from textwrap import fill
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageGrab
import io
import pystray
from pystray import MenuItem as item
import threading

# Try to import pynput for global hotkeys
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

# Try to import optional libraries
try:
    import pillow_heif
    HEIF_AVAILABLE = True
except ImportError:
    HEIF_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF, renderPM
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False

try:
    from psd_tools import PSDImage
    PSD_AVAILABLE = True
except ImportError:
    PSD_AVAILABLE = False


class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Imageflow - Simple Image Converter")
        self.root.geometry("650x700")
        self.root.resizable(True, True)
        self.root.minsize(600, 650)

        self.input_file = ""
        self.input_file_ext = "ファイル未入力…"
        self.output_file = ""

        # トレイアイコン関連
        self.tray_icon = None
        self.tray_thread = None
        self.is_hidden = False

        # ホットキー関連
        self.hotkey_listener = None
        self.hotkey_thread = None

        # クリップボード関連
        self.is_clipboard_image = False

        # Supported formats
        self.input_formats = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'ico', 'eps']
        if HEIF_AVAILABLE:
            self.input_formats.extend(['heif', 'heic'])
        if PDF_AVAILABLE:
            self.input_formats.append('pdf')
        if SVG_AVAILABLE:
            self.input_formats.append('svg')
        if PSD_AVAILABLE:
            self.input_formats.append('psd')

        self.output_formats = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'ico', 'eps']
        if HEIF_AVAILABLE:
            self.output_formats.extend(['heif', 'heic'])
        if PDF_AVAILABLE:
            self.output_formats.append('pdf')
        self.setup_ui()
        self.setup_tray()
        self.setup_window_events()
        self.setup_hotkey()

    def setup_ui(self):
        """Setup the user interface"""
        # Configure ttk styles
        self.setup_styles()
        
        # Menu bar
        self.create_menu_bar()

        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(
            main_container,
            text="Imageflow - Simple Image Converter",
            style="Title.TLabel")
        title_label.pack(pady=(0, 20))

        # Input file section
        input_frame = ttk.LabelFrame(main_container, text="入力ファイル", padding="15")
        input_frame.pack(fill="x", pady=(0, 10))

        input_content = ttk.Frame(input_frame)
        input_content.pack(fill="x")

        self.input_label = ttk.Label(
            input_content,
            text="ファイルが選択されていません…",
            style="Info.TLabel")
        self.input_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        input_btn = ttk.Button(
            input_content,
            text="ブラウズ…",
            command=self.select_input_file,
            style="Primary.TButton")
        input_btn.pack(side="right")

        # Output file section
        output_frame = ttk.LabelFrame(
            main_container,
            text="出力先(オプション)",
            padding="15")
        output_frame.pack(fill="x", pady=(0, 10))

        output_content = ttk.Frame(output_frame)
        output_content.pack(fill="x")

        self.output_label = ttk.Label(
            output_content,
            text="自動(入力ディレクトリと同じ)",
            style="Info.TLabel")
        self.output_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        output_btn = ttk.Button(
            output_content,
            text="ブラウズ…",
            command=self.select_output_file,
            style="Secondary.TButton")
        output_btn.pack(side="right")

        # Output format section
        format_frame = ttk.LabelFrame(main_container, text="出力形式", padding="15")
        format_frame.pack(fill="x", pady=(0, 10))

        format_content = ttk.Frame(format_frame)
        format_content.pack(fill="x")

        self.format_var = tk.StringVar(value="png")
        self.input_format = ttk.Label(format_content, text=self.input_file_ext.upper(), style="Format.TLabel")
        self.input_format.pack(side="left", padx=(0, 10))

        self.format_arrow = ttk.Label(format_content, text="→", style="Arrow.TLabel")
        self.format_arrow.pack(side="left", padx=10)

        self.format_combo = ttk.Combobox(
            format_content,
            textvariable=self.format_var,
            values=self.output_formats,
            state="readonly",
            width=15,
            style="Format.TCombobox"
        )
        self.format_combo.pack(side="left", padx=(10, 0))
        self.format_combo.bind("<<ComboboxSelected>>", self.on_format_change)

        # Parameters section
        self.params_frame = ttk.LabelFrame(
            main_container,
            text="パラメータ",
            padding="15"
        )
        self.params_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Quality parameter (for JPEG, WebP)
        quality_frame = ttk.Frame(self.params_frame)
        quality_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(quality_frame, text="品質 (1-100):", style="Param.TLabel").pack(side="left")
        self.quality_var = tk.IntVar(value=95)
        self.quality_scale = ttk.Scale(
            quality_frame, from_=1, to=100,
            orient="horizontal", variable=self.quality_var,
            length=300
        )
        self.quality_scale.pack(side="left", padx=(10, 5))
        self.quality_label = ttk.Label(quality_frame, text="95", style="Value.TLabel")
        self.quality_label.pack(side="left")
        self.quality_var.trace_add("write", self.update_quality_label)

        # Compression level (for PNG)
        compress_frame = ttk.Frame(self.params_frame)
        compress_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(compress_frame, text="圧縮度 (0-9):", style="Param.TLabel").pack(side="left")
        self.compress_var = tk.IntVar(value=6)
        self.compress_scale = ttk.Scale(
            compress_frame, from_=0, to=9,
            orient="horizontal", variable=self.compress_var,
            length=300)
        self.compress_scale.pack(side="left", padx=(10, 5))
        self.compress_label = ttk.Label(compress_frame, text="6", style="Value.TLabel")
        self.compress_label.pack(side="left")
        self.compress_var.trace_add("write", self.update_compress_label)

        # Resize options
        resize_frame = ttk.Frame(self.params_frame)
        resize_frame.pack(fill="x", pady=(0, 15))

        self.resize_var = tk.BooleanVar(value=False)
        self.resize_check = ttk.Checkbutton(
            resize_frame, text="画像のリサイズ",
            variable=self.resize_var,
            command=self.toggle_resize,
            style="Param.TCheckbutton")
        self.resize_check.pack(side="left")

        ttk.Label(resize_frame, text="幅:", style="Param.TLabel").pack(side="left", padx=(20, 5))
        self.width_var = tk.StringVar(value="800")
        self.width_entry = ttk.Entry(
            resize_frame,
            textvariable=self.width_var,
            width=6, state="disabled",
            style="Param.TEntry")
        self.width_entry.pack(side="left", padx=3)
        self.width_var.trace_add("write", self.on_width_change)

        ttk.Label(resize_frame, text="高さ:", style="Param.TLabel").pack(side="left", padx=5)
        self.height_var = tk.StringVar(value="600")
        self.height_entry = ttk.Entry(
            resize_frame,
            textvariable=self.height_var,
            width=6, state="disabled",
            style="Param.TEntry")
        self.height_entry.pack(side="left", padx=5)
        self.height_var.trace_add("write", self.on_height_change)

        self.maintain_aspect = tk.BooleanVar(value=True)
        self.aspect_check = ttk.Checkbutton(
            resize_frame, text="アスペクト比を維持",
            variable=self.maintain_aspect, state="disabled",
            style="Param.TCheckbutton")
        self.aspect_check.pack(side="left", padx=10)

        # アスペクト比を保存する変数
        self.original_aspect_ratio = None
        self.is_updating_dimensions = False  # 無限ループを防ぐフラグ

        # Format-specific info
        self.info_label = ttk.Label(
            self.params_frame, text="",
            style="Info.TLabel",
            wraplength=600)
        self.info_label.pack(pady=(10, 0))

        # Convert button
        convert_btn = ttk.Button(
            main_container, text="変換", command=self.convert_image,
            style="Convert.TButton",
            width=20)
        convert_btn.pack(pady=(10, 0))

        # Status bar
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(
            main_container, textvariable=self.status_var,
            style="Status.TLabel",
            anchor="center")
        status_bar.pack(side="bottom", fill="x", pady=(10, 0))

        # Initial parameter visibility update
        self.on_format_change()

    def setup_styles(self):
        """Setup ttk styles for modern appearance"""
        style = ttk.Style()
        
        # Configure theme
        style.theme_use('clam')
        
        # Title style
        style.configure("Title.TLabel",
                       font=("M PLUS 2", 18, "bold"),
                       foreground="#2c3e50")
        
        # Info label style
        style.configure("Info.TLabel",
                       font=("M PLUS 2", 10),
                       foreground="#7f8c8d",
                       wraplength=500)
        
        # Format label style
        style.configure("Format.TLabel",
                       font=("M PLUS 2", 12, "bold"),
                       foreground="#34495e")
        
        # Arrow label style
        style.configure("Arrow.TLabel",
                       font=("M PLUS 2", 14),
                       foreground="#95a5a6")
        
        # Format combobox style
        style.configure("Format.TCombobox",
                       font=("M PLUS 2", 10))
        
        # Parameter label style
        style.configure("Param.TLabel",
                       font=("M PLUS 2", 10),
                       foreground="#2c3e50")
        
        # Value label style
        style.configure("Value.TLabel",
                       font=("M PLUS 2", 10, "bold"),
                       foreground="#e74c3c")
        
        
        # Parameter entry style
        style.configure("Param.TEntry",
                       font=("M PLUS 2", 10))
        
        # Parameter checkbutton style
        style.configure("Param.TCheckbutton",
                       font=("M PLUS 2", 10))
        
        # Primary button style
        style.configure("Primary.TButton",
                       font=("M PLUS 2", 10, "bold"),
                       foreground="white",
                       background="#3498db",
                       padding=(10, 5))
        style.map("Primary.TButton",
                 background=[('active', '#2980b9')])
        
        # Secondary button style
        style.configure("Secondary.TButton",
                       font=("M PLUS 2", 10),
                       foreground="#2c3e50",
                       background="#ecf0f1",
                       padding=(10, 5))
        style.map("Secondary.TButton",
                 background=[('active', '#bdc3c7')])
        
        # Convert button style
        style.configure("Convert.TButton",
                       font=("M PLUS 2", 12, "bold"),
                       foreground="white",
                       background="#27ae60",
                       padding=(20, 10))
        style.map("Convert.TButton",
                 background=[('active', '#229954')])
        
        # Status label style
        style.configure("Status.TLabel",
                       font=("M PLUS 2", 9),
                       foreground="#7f8c8d",
                       background="#ecf0f1",
                       padding=(5, 3))

    def create_menu_bar(self):
        """メニューバーを作成"""
        menubar = tk.Menu(self.root, font=("M PLUS 2", 9))
        self.root.config(menu=menubar)

        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0, font=("M PLUS 2", 9))
        menubar.add_cascade(label="設定", menu=file_menu)

        # 終了オプション
        file_menu.add_command(label="終了", command=self.force_quit, accelerator="Ctrl+Q")

        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0, font=("M PLUS 2", 9))
        menubar.add_cascade(label="ヘルプ", menu=help_menu)

        # ショートカットキー情報
        if PYNPUT_AVAILABLE:
            help_menu.add_command(label="ショートカットキー", command=self.show_shortcuts)

        # キーボードショートカットをバインド
        self.root.bind('<Control-q>', lambda event: self.force_quit())

    def update_quality_label(self, *args):
        """Update quality label"""
        self.quality_label.config(text=str(self.quality_var.get()))

    def update_compress_label(self, *args):
        """Update compression label"""
        self.compress_label.config(text=str(self.compress_var.get()))

    def calculate_aspect_ratio(self):
        """画像のアスペクト比を計算して保存"""
        ##print(f"calculate_aspect_ratio called: input_file={self.input_file}")

        # クリップボード画像の場合は、既に読み込まれた画像オブジェクトを使用
        if self.is_clipboard_image and hasattr(self.input_file, 'size'):
            try:
                width, height = self.input_file.size
                self.original_aspect_ratio = width / height
                # リサイズの幅と高さの値を画像の実際のサイズに設定
                self.width_var.set(str(width))
                self.height_var.set(str(height))
                #print(f"アスペクト比を計算（クリップボード）: {self.original_aspect_ratio:.3f} (width={width}, height={height})")
                return
            except Exception as e:
                #print(f"クリップボード画像のアスペクト比計算に失敗: {e}")
                self.original_aspect_ratio = None
                return

        # ファイルパスの場合
        if not self.input_file or not os.path.exists(self.input_file):
            print("No input file or file doesn't exist")
            self.original_aspect_ratio = None
            return

        try:
            # 画像を開いてサイズを取得
            img = self.load_image(self.input_file)
            width, height = img.size
            self.original_aspect_ratio = width / height
            # リサイズの幅と高さの値を画像の実際のサイズに設定
            self.width_var.set(str(width))
            self.height_var.set(str(height))
            #print(f"アスペクト比を計算: {self.original_aspect_ratio:.3f} (width={width}, height={height})")
        except Exception as e:
            #print(f"アスペクト比の計算に失敗: {e}")
            self.original_aspect_ratio = None

    def on_width_change(self, *args):
        """幅が変更された時の処理"""
        #print(f"on_width_change called: width={self.width_var.get()}, maintain_aspect={self.maintain_aspect.get()}, is_updating={self.is_updating_dimensions}")
        if not self.maintain_aspect.get() or self.is_updating_dimensions:
            return

        try:
            new_width = int(self.width_var.get())
            if self.original_aspect_ratio and new_width > 0:
                self.is_updating_dimensions = True
                new_height = int(new_width / self.original_aspect_ratio)
                #print(f"Calculating new height: {new_height}")
                self.height_var.set(str(new_height))
                self.is_updating_dimensions = False
        except ValueError:
            pass  # 無効な値の場合は何もしない

    def on_height_change(self, *args):
        """高さが変更された時の処理"""
        #print(f"on_height_change called: height={self.height_var.get()}, maintain_aspect={self.maintain_aspect.get()}, is_updating={self.is_updating_dimensions}")
        if not self.maintain_aspect.get() or self.is_updating_dimensions:
            return

        try:
            new_height = int(self.height_var.get())
            if self.original_aspect_ratio and new_height > 0:
                self.is_updating_dimensions = True
                new_width = int(new_height * self.original_aspect_ratio)
                #print(f"Calculating new width: {new_width}")
                self.width_var.set(str(new_width))
                self.is_updating_dimensions = False
        except ValueError:
            pass  # 無効な値の場合は何もしない

    def toggle_resize(self):
        """Toggle resize options"""
        if self.resize_var.get():
            self.width_entry.config(state="normal")
            self.height_entry.config(state="normal")
            self.aspect_check.config(state="normal")
        else:
            self.width_entry.config(state="disabled")
            self.height_entry.config(state="disabled")
            self.aspect_check.config(state="disabled")

    def on_format_change(self, event=None):
        """Update parameter visibility based on selected format"""
        format_type = self.format_var.get().lower()

        # Show/hide quality control
        if format_type in ['jpg', 'jpeg', 'webp']:
            self.quality_scale.config(state="normal")
            self.info_label.config(text=f"品質… 0(低品質)から100(高品質)")
        else:
            self.quality_scale.config(state="disabled")

        # Show/hide compression control
        if format_type == 'png':
            self.compress_scale.config(state="normal")
            self.info_label.config(text="圧縮レベル… 0(無圧縮)から9(最大圧縮)")
        else:
            self.compress_scale.config(state="disabled")

        if format_type not in ['jpg', 'jpeg', 'webp', 'png']:
            self.info_label.config(text="")

        # Special format info
        if format_type in ['heif', 'heic']:
            if HEIF_AVAILABLE:
                self.info_label.config(text="HEIF/HEIC support enabled")
            else:
                self.info_label.config(text="HEIF/HEIC support not available (install pillow-heif)")
        elif format_type == 'pdf':
            if PDF_AVAILABLE:
                self.info_label.config(text="PDF conversion enabled")
            else:
                self.info_label.config(text="PDF support not available (install reportlab)")
        elif format_type == 'eps':
            self.info_label.config(text="EPS format selected")

    def select_input_file(self):
        """Open file dialog to select input file"""
        filetypes = [
            ("All Image Files", " ".join([f"*.{fmt}" for fmt in self.input_formats])),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("GIF files", "*.gif"),
            ("BMP files", "*.bmp"),
            ("TIFF files", "*.tiff *.tif"),
            ("WebP files", "*.webp"),
            ("ICO files", "*.ico"),
            ("EPS files", "*.eps"),
            ("All files", "*.*")
        ]

        if HEIF_AVAILABLE:
            filetypes.insert(-1, ("HEIF/HEIC files", "*.heif *.heic"))
        if PSD_AVAILABLE:
            filetypes.insert(-1, ("PSD files", "*.psd"))
        if SVG_AVAILABLE:
            filetypes.insert(-1, ("SVG files", "*.svg"))

        filename = filedialog.askopenfilename(
            title="Select Input Image",
            filetypes=filetypes
        )

        if filename:
            self.input_file = filename
            self.input_file_ext = os.path.splitext(filename)[1].lower()[1:]
            self.input_format.config(text=self.input_file_ext)
            self.input_label.config(text=filename)
            self.status_var.set(f"Selected: {os.path.basename(filename)}")

            # アスペクト比を計算して保存
            self.calculate_aspect_ratio()

    def select_output_file(self):
        """Open file dialog to select output file"""
        if not self.input_file:
            messagebox.showwarning("Warning", "Please select an input file first")
            return

        # Get default filename with new extension
        input_dir = os.path.dirname(self.input_file)
        input_basename = os.path.splitext(os.path.basename(self.input_file))[0]
        default_name = f"{input_basename}.{self.format_var.get()}"

        filename = filedialog.asksaveasfilename(
            title="Save As",
            initialdir=input_dir,
            initialfile=default_name,
            defaultextension=f".{self.format_var.get()}",
            filetypes=[
                (f"{self.format_var.get().upper()} files", f"*.{self.format_var.get()}"),
                ("All files", "*.*")
            ]
        )

        if filename:
            self.output_file = filename
            self.output_label.config(text=filename)
            self.status_var.set(f"Output: {os.path.basename(filename)}")

    def convert_image(self):
        """Convert the image"""

        if not self.input_file:
            messagebox.showerror("Error", "Please select an input file")
            return

        if not self.is_clipboard_image:
            if not os.path.exists(self.input_file):
                messagebox.showerror("Error", "Input file does not exist")
                return

        # Determine output file
        if not self.output_file:
            if self.is_clipboard_image:
                input_dir = os.path.expanduser('~/Desktop')
                input_basename = "clipboard"
            else:
                input_dir = os.path.dirname(self.input_file)
                input_basename = os.path.splitext(os.path.basename(self.input_file))[0]
            self.output_file = os.path.join(input_dir,
                                            f"{input_basename}.{self.format_var.get()}")
        try:
            self.status_var.set("変換中…")
            self.root.update()

            output_format = self.format_var.get().lower()

            # Load image based on input format
            if self.is_clipboard_image:
                img = self.load_image(filepath="")
            else:
                img = self.load_image(self.input_file)

            # Apply resize if needed
            if self.resize_var.get():
                try:
                    target_width = int(self.width_var.get())
                    target_height = int(self.height_var.get())

                    if self.maintain_aspect.get():
                        img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                    else:
                        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                except ValueError:
                    messagebox.showwarning("Warning", "Invalid width/height values. Skipping resize.")

            # Convert and save
            self.save_image(img, self.output_file, output_format)

            self.status_var.set("変換完了")
            messagebox.showinfo("Success",
                                f"変換完了!\n{self.output_file} に保存されました")

            # Reset output file for next conversion
            self.output_file = ""
            self.output_label.config(text="Auto (same as input location)")

        except Exception as e:
            self.status_var.set("変換に失敗しました")
            messagebox.showerror("Error", f"変換に失敗しました:\n{str(e)}")

    def load_image(self, filepath):
        """Load image from file, handling special formats"""
        # クリップボード画像の場合は特別処理
        if self.is_clipboard_image:
            image = ImageGrab.grabclipboard()
            if image:
                return image
            else:
                print("Clipboard is empty or no image found. Skipped")
                return None

        # ファイルパスが空の場合はNoneを返す
        if not filepath:
            return None

        ext = os.path.splitext(filepath)[1].lower()[1:]

        # Handle HEIF/HEIC
        if ext in ['heif', 'heic']:
            if HEIF_AVAILABLE:
                pillow_heif.register_heif_opener()
                return Image.open(filepath)
            else:
                raise Exception("HEIF/HEIC support not available. Install pillow-heif.")

        # Handle PSD
        elif ext == 'psd':
            if PSD_AVAILABLE:
                psd = PSDImage.open(filepath)
                return psd.topil()
            else:
                raise Exception("PSD support not available. Install psd-tools.")

        # Handle SVG
        elif ext == 'svg':
            if SVG_AVAILABLE:
                drawing = svg2rlg(filepath)
                # Convert SVG to PNG in memory, then load as PIL Image
                img_data = io.BytesIO()
                renderPM.drawToFile(drawing, img_data, fmt='PNG')
                img_data.seek(0)
                return Image.open(img_data)
            else:
                raise Exception("SVG support not available. Install svglib.")

        # Handle PDF (extract first page)
        elif ext == 'pdf':
            raise Exception("PDF as input is not fully supported yet")

        # Standard formats
        else:
            img = Image.open(filepath)
            # Convert to RGB if necessary (for formats that don't support transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Check if we need RGB or can keep RGBA
                if ext in ['jpg', 'jpeg', 'bmp']:
                    # Create a white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    return background
            return img

    def save_image(self, img, filepath, output_format):
        """Save image to file with appropriate parameters"""
        output_format = output_format.lower()

        # Handle JPEG
        if output_format in ['jpg', 'jpeg']:
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            img.save(filepath, 'JPEG', quality=self.quality_var.get(), optimize=True)

        # Handle PNG
        elif output_format == 'png':
            img.save(filepath, 'PNG', compress_level=self.compress_var.get())

        # Handle WebP
        elif output_format == 'webp':
            img.save(filepath, 'WEBP', quality=self.quality_var.get())

        # Handle HEIF/HEIC
        elif output_format in ['heif', 'heic']:
            if HEIF_AVAILABLE:
                pillow_heif.register_heif_opener()
                img.save(filepath, 'HEIF', quality=self.quality_var.get())
            else:
                raise Exception("HEIF/HEIC support not available. Install pillow-heif.")

        # Handle PDF
        elif output_format == 'pdf':
            if PDF_AVAILABLE:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background

                # Save image to PDF
                c = canvas.Canvas(filepath, pagesize=(img.width, img.height))
                # Save image to bytes
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                c.drawImage(ImageReader(img_buffer), 0, 0, width=img.width, height=img.height)
                c.save()
            else:
                raise Exception("PDF support not available. Install reportlab.")

        # Handle EPS
        elif output_format == 'eps':
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            img.save(filepath, 'EPS')

        # Handle TIFF
        elif output_format in ['tiff', 'tif']:
            img.save(filepath, 'TIFF')

        # Handle GIF
        elif output_format == 'gif':
            # Convert to P mode (palette) for GIF
            if img.mode not in ('P', 'L'):
                img = img.convert('P', palette=Image.ADAPTIVE)
            img.save(filepath, 'GIF')

        # Handle BMP
        elif output_format == 'bmp':
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            img.save(filepath, 'BMP')

        # Handle ICO
        elif output_format == 'ico':
            img.save(filepath, 'ICO')

        # Default
        else:
            img.save(filepath)

    def setup_tray(self):
        """トレイアイコンを設定"""
        # icon.pngファイルを読み込み
        try:
            icon_image = Image.open('icon.png')
            # 32x32にリサイズ（トレイアイコンに適したサイズ）
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
        except FileNotFoundError:
            # icon.pngが見つからない場合は、デフォルトの青いアイコンを作成
            print("FileNotFoundError: デフォルトのアイコンファイルが見つかりませんでした")
            icon_image = Image.new('RGB', (32, 32), color='blue')
        except Exception as e:
            # その他のエラーの場合も、デフォルトの青いアイコンを作成
            print(f"アイコンファイルの読み込みに失敗しました: {e}")
            icon_image = Image.new('RGB', (32, 32), color='blue')

        # トレイメニューを作成
        show_label = '表示(Ctrl+Shift+I)' if PYNPUT_AVAILABLE else '表示'
        menu_items = [
            item(show_label, self.show_window, default=True),
            item('終了', self.quit_app),
        ]

        menu = pystray.Menu(*menu_items)

        # トレイアイコンを作成（クリック時の動作も設定）
        self.tray_icon = pystray.Icon("ImageConverter", icon_image, "Imageflow", menu)
        self.tray_icon.default_action = self.show_window  # アイコンクリック時のデフォルト動作

        # トレイアイコンを別スレッドで実行
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()

    def setup_window_events(self):
        """ウィンドウイベントを設定"""
        # ウィンドウの閉じるボタンが押された時の処理
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def hide_to_tray(self):
        """ウィンドウをトレイに隠す"""
        self.root.withdraw()  # ウィンドウを隠す
        self.is_hidden = True

    def show_window(self, icon=None, item=None):
        """ウィンドウを表示"""
        self.root.deiconify()  # ウィンドウを表示
        self.root.lift()  # 最前面に表示
        self.root.focus_force()  # フォーカスを取得
        self.is_hidden = False

    def setup_hotkey(self):
        """グローバルホットキーを設定"""
        if not PYNPUT_AVAILABLE:
            print("pynputライブラリが利用できません。ホットキー機能は無効化されました。")
            return

        try:
            # Ctrl+Shift+I でアプリケーションを表示
            self.hotkey_listener = keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+i': self.show_window_from_hotkey
            })

            # Ctrl+Vで画像を入力に貼り付け
            self.hotkey_listener = keyboard.GlobalHotKeys({
                '<ctrl>+v': self.paste_image_to_input
            })

            # ホットキーリスナーを別スレッドで実行
            self.hotkey_thread = threading.Thread(target=self.hotkey_listener.start, daemon=True)
            self.hotkey_thread.start()
            print("ホットキー設定完了")

        except Exception as e:
            print(f"ホットキー設定に失敗しました: {e}")

    def show_window_from_hotkey(self):
        """ホットキーからウィンドウを表示"""
        # メインスレッドで実行する必要があるため、afterメソッドを使用
        self.root.after(0, self.show_window)

    def paste_image_to_input(self):
        """画像を入力に貼り付け"""
        self.is_clipboard_image = True
        img = self.load_image(filepath="")
        if img:
            self.input_label.config(text="クリップボードから貼り付けられた画像")
            self.input_file = img
            self.input_file_ext = "png"
            self.input_format.config(text=self.input_file_ext.upper())
            self.status_var.set("クリップボードから画像を貼り付けました")
            
            # アスペクト比を計算して保存
            self.calculate_aspect_ratio()

    def show_shortcuts(self):
        """ショートカットキーの情報を表示"""
        shortcuts_info = """ショートカットキー一覧:

・Ctrl+Shift+I: システムトレイからアプリケーションを表示
・Ctrl+Q: アプリケーションを終了
・Ctrl+V: クリップボードから画像を入力に貼り付け

"""
        messagebox.showinfo("ショートカットキー", shortcuts_info)

    def force_quit(self):
        """アプリケーションを強制終了（システムトレイに隠さない）"""
        self.quit_app()

    def quit_app(self, icon=None, item=None):
        """アプリケーションを終了"""
        # ホットキーリスナーを停止
        if self.hotkey_listener:
            self.hotkey_listener.stop()

        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()