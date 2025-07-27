import os
import ctypes
import shutil
import re
from ctypes import wintypes
from functools import cmp_to_key
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

# Load Windows API for natural sorting
try:
    shlwapi = ctypes.WinDLL("Shlwapi")
    StrCmpLogicalW = shlwapi.StrCmpLogicalW
    StrCmpLogicalW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    StrCmpLogicalW.restype = wintypes.INT
    WINDOWS_SORT_AVAILABLE = True
except:
    WINDOWS_SORT_AVAILABLE = False

class AdvancedRenameTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced File Rename Tool")
        self.root.geometry("800x700")
        
        # Variables
        self.selected_path = tk.StringVar()
        self.current_file = tk.StringVar()
        self.progress = tk.DoubleVar()
        
        # Rename settings
        self.rename_mode = tk.StringVar(value="sequential")  # sequential, prefix, suffix, replace
        self.number_format = tk.StringVar(value="001")  # 001, 01, 1
        self.keep_original = tk.BooleanVar(value=False)
        self.custom_prefix = tk.StringVar()
        self.custom_suffix = tk.StringVar()
        self.find_text = tk.StringVar()
        self.replace_text = tk.StringVar()
        self.start_number = tk.IntVar(value=1)
        self.reset_counter = tk.BooleanVar(value=True)
        
        # File type filters
        self.file_types = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'All Files': ['*']
        }
        self.selected_file_type = tk.StringVar(value="Images")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Path selection
        ttk.Label(main_frame, text="📁 Chọn thư mục chứa file:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(path_frame, textvariable=self.selected_path, width=70).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(path_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1, padx=(5, 0))
        ttk.Button(path_frame, text="Scan", command=self.scan_files).grid(row=0, column=2, padx=(5, 0))
        
        path_frame.columnconfigure(0, weight=1)
        
        # File type selection
        file_type_frame = ttk.LabelFrame(main_frame, text="🎯 Loại file", padding="10")
        file_type_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        for i, (type_name, extensions) in enumerate(self.file_types.items()):
            ttk.Radiobutton(file_type_frame, text=f"{type_name} ({', '.join(extensions[:3])}...)", 
                           variable=self.selected_file_type, value=type_name).grid(row=i//3, column=i%3, sticky=tk.W, padx=10)
        
        # Rename options
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Tùy chọn đổi tên", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Rename mode
        ttk.Label(options_frame, text="Chế độ đổi tên:").grid(row=0, column=0, sticky=tk.W)
        mode_frame = ttk.Frame(options_frame)
        mode_frame.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=10)
        
        ttk.Radiobutton(mode_frame, text="Đánh số thứ tự", variable=self.rename_mode, value="sequential").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Thêm prefix", variable=self.rename_mode, value="prefix").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Thêm suffix", variable=self.rename_mode, value="suffix").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Tìm & thay thế", variable=self.rename_mode, value="replace").pack(side=tk.LEFT, padx=10)
        
        # Sequential numbering options
        seq_frame = ttk.Frame(options_frame)
        seq_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(seq_frame, text="Format số:").pack(side=tk.LEFT)
        ttk.Radiobutton(seq_frame, text="001", variable=self.number_format, value="001").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(seq_frame, text="01", variable=self.number_format, value="01").pack(side=tk.LEFT)
        ttk.Radiobutton(seq_frame, text="1", variable=self.number_format, value="1").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(seq_frame, text="Bắt đầu từ:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Entry(seq_frame, textvariable=self.start_number, width=5).pack(side=tk.LEFT)
        
        ttk.Checkbutton(seq_frame, text="Giữ tên gốc", variable=self.keep_original).pack(side=tk.LEFT, padx=20)
        ttk.Checkbutton(seq_frame, text="Reset số đếm mỗi folder", variable=self.reset_counter).pack(side=tk.LEFT, padx=10)
        
        # Custom text options
        custom_frame = ttk.Frame(options_frame)
        custom_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(custom_frame, text="Prefix:").pack(side=tk.LEFT)
        ttk.Entry(custom_frame, textvariable=self.custom_prefix, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(custom_frame, text="Suffix:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Entry(custom_frame, textvariable=self.custom_suffix, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(custom_frame, text="Tìm:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Entry(custom_frame, textvariable=self.find_text, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(custom_frame, text="Thay:").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Entry(custom_frame, textvariable=self.replace_text, width=15).pack(side=tk.LEFT, padx=5)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="👁️ Preview", padding="10")
        preview_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Preview listbox
        preview_list_frame = ttk.Frame(preview_frame)
        preview_list_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.preview_tree = ttk.Treeview(preview_list_frame, columns=('old', 'new'), show='headings', height=8)
        self.preview_tree.heading('old', text='Tên cũ')
        self.preview_tree.heading('new', text='Tên mới')
        self.preview_tree.column('old', width=300)
        self.preview_tree.column('new', width=300)
        
        preview_scrollbar = ttk.Scrollbar(preview_list_frame, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        preview_list_frame.columnconfigure(0, weight=1)
        preview_list_frame.rowconfigure(0, weight=1)
        
        # Log area
        ttk.Label(main_frame, text="📝 Log:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        
        self.log_text = tk.Text(main_frame, height=8, width=80)
        log_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_scrollbar.grid(row=6, column=2, sticky=(tk.N, tk.S), pady=5)
        
        # Progress bar
        ttk.Label(main_frame, text="Tiến trình:").grid(row=7, column=0, sticky=tk.W, pady=(10, 0))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.current_file)
        self.status_label.grid(row=9, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="🔍 Preview", command=self.preview_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="▶️ Rename", command=self.start_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Backup & Rename", command=self.backup_and_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="↩️ Undo Last", command=self.undo_last_rename).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Store for undo
        self.last_rename_actions = []
    
    def windows_explorer_compare(self, a, b):
        """Windows natural sort comparison"""
        if WINDOWS_SORT_AVAILABLE:
            return StrCmpLogicalW(a, b)
        else:
            # Fallback natural sort
            def natural_key(text):
                return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]
            
            key_a = natural_key(a)
            key_b = natural_key(b)
            return -1 if key_a < key_b else (1 if key_a > key_b else 0)
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_path.set(folder)
    
    def log_message(self, message):
        """Thêm message vào log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Xóa log"""
        self.log_text.delete(1.0, tk.END)
        # Clear preview
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
    
    def get_file_extensions(self):
        """Lấy danh sách extension theo loại file đã chọn"""
        file_type = self.selected_file_type.get()
        extensions = self.file_types.get(file_type, ['*'])
        return extensions if extensions != ['*'] else None
    
    def find_files(self, directory):
        """Tìm tất cả file theo loại đã chọn"""
        files = []
        extensions = self.get_file_extensions()
        
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if extensions is None or any(filename.lower().endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))
        
        return files
    
    def scan_files(self):
        """Scan và hiển thị danh sách file"""
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        self.clear_log()
        self.log_message("🔍 Đang scan files...")
        
        files = self.find_files(self.selected_path.get())
        
        if not files:
            self.log_message("❌ Không tìm thấy file nào!")
            return
        
        self.log_message(f"✅ Tìm thấy {len(files)} file:")
        
        # Group by folder
        folders = {}
        for file_path in files:
            folder = os.path.dirname(file_path)
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(os.path.basename(file_path))
        
        for folder, filenames in folders.items():
            relative_folder = os.path.relpath(folder, self.selected_path.get())
            self.log_message(f"📁 {relative_folder}: {len(filenames)} files")
    
    def generate_new_name(self, old_name, counter, folder_path):
        """Tạo tên mới theo mode đã chọn"""
        name_without_ext = os.path.splitext(old_name)[0]
        extension = os.path.splitext(old_name)[1]
        
        mode = self.rename_mode.get()
        
        if mode == "sequential":
            # Đánh số thứ tự
            if self.number_format.get() == "001":
                number = f"{counter:03d}"
            elif self.number_format.get() == "01":
                number = f"{counter:02d}"
            else:
                number = str(counter)
            
            if self.keep_original.get():
                new_name = f"{number}_{old_name}"
            else:
                new_name = f"{number}{extension}"
        
        elif mode == "prefix":
            prefix = self.custom_prefix.get()
            new_name = f"{prefix}{old_name}" if prefix else old_name
        
        elif mode == "suffix":
            suffix = self.custom_suffix.get()
            new_name = f"{name_without_ext}{suffix}{extension}" if suffix else old_name
        
        elif mode == "replace":
            find_text = self.find_text.get()
            replace_text = self.replace_text.get()
            if find_text:
                new_name = old_name.replace(find_text, replace_text)
            else:
                new_name = old_name
        
        else:
            new_name = old_name
        
        return new_name
    
    def preview_rename(self):
        """Preview đổi tên không thực sự đổi"""
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        # Clear preview
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        self.log_message("👁️ Generating preview...")
        
        files = self.find_files(self.selected_path.get())
        
        if not files:
            self.log_message("❌ Không tìm thấy file nào!")
            return
        
        # Group by folder và sort
        folders = {}
        for file_path in files:
            folder = os.path.dirname(file_path)
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(os.path.basename(file_path))
        
        counter = self.start_number.get()
        
        for folder_path in sorted(folders.keys()):
            filenames = folders[folder_path]
            # Sort files naturally
            sorted_files = sorted(filenames, key=cmp_to_key(self.windows_explorer_compare))
            
            if self.reset_counter.get():
                counter = self.start_number.get()
            
            for filename in sorted_files:
                old_name = filename
                new_name = self.generate_new_name(old_name, counter, folder_path)
                
                # Add to preview tree
                relative_path = os.path.relpath(folder_path, self.selected_path.get())
                display_old = f"{relative_path}/{old_name}" if relative_path != "." else old_name
                display_new = f"{relative_path}/{new_name}" if relative_path != "." else new_name
                
                self.preview_tree.insert('', 'end', values=(display_old, display_new))
                
                if self.rename_mode.get() == "sequential":
                    counter += 1
        
        self.log_message(f"✅ Preview hoàn thành cho {len(files)} file")
    
    def rename_files(self):
        """Thực hiện đổi tên file"""
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        self.clear_log()
        self.log_message("🚀 Bắt đầu đổi tên files...")
        
        files = self.find_files(self.selected_path.get())
        
        if not files:
            self.log_message("❌ Không tìm thấy file nào!")
            return
        
        # Group by folder và sort
        folders = {}
        for file_path in files:
            folder = os.path.dirname(file_path)
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(os.path.basename(file_path))
        
        total_files = len(files)
        processed = 0
        success_count = 0
        error_count = 0
        counter = self.start_number.get()
        
        # Store for undo
        self.last_rename_actions = []
        
        for folder_path in sorted(folders.keys()):
            filenames = folders[folder_path]
            # Sort files naturally
            sorted_files = sorted(filenames, key=cmp_to_key(self.windows_explorer_compare))
            
            if self.reset_counter.get():
                counter = self.start_number.get()
            
            for filename in sorted_files:
                try:
                    old_path = os.path.join(folder_path, filename)
                    new_name = self.generate_new_name(filename, counter, folder_path)
                    new_path = os.path.join(folder_path, new_name)
                    
                    # Cập nhật status
                    relative_path = os.path.relpath(old_path, self.selected_path.get())
                    self.current_file.set(f"Đang xử lý: {relative_path}")
                    
                    # Kiểm tra file đã tồn tại
                    if os.path.exists(new_path) and old_path != new_path:
                        self.log_message(f"⚠️ File đã tồn tại: {new_name}")
                        error_count += 1
                    elif old_path != new_path:
                        os.rename(old_path, new_path)
                        self.log_message(f"✅ {filename} → {new_name}")
                        
                        # Store for undo
                        self.last_rename_actions.append((new_path, old_path))
                        success_count += 1
                    
                    if self.rename_mode.get() == "sequential":
                        counter += 1
                    
                    processed += 1
                    
                    # Cập nhật progress
                    progress_percent = (processed / total_files) * 100
                    self.progress.set(progress_percent)
                    self.root.update_idletasks()
                    
                except Exception as e:
                    self.log_message(f"❌ Lỗi đổi tên {filename}: {e}")
                    error_count += 1
                    processed += 1
        
        # Hoàn thành
        self.progress.set(100)
        self.current_file.set("Hoàn thành!")
        
        self.log_message(f"\n🎉 HOÀN THÀNH!")
        self.log_message(f"📊 Tổng kết:")
        self.log_message(f"   - Tổng file: {total_files}")
        self.log_message(f"   - Đổi tên thành công: {success_count}")
        self.log_message(f"   - Lỗi: {error_count}")
        
        messagebox.showinfo("Hoàn thành", 
                          f"Đã đổi tên {success_count}/{total_files} file!")
        
        # Reset progress
        self.progress.set(0)
        self.current_file.set("")
    
    def backup_and_rename(self):
        """Backup trước khi đổi tên"""
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        # Tạo backup folder
        backup_folder = os.path.join(self.selected_path.get(), "_BACKUP_" + str(int(time.time())))
        
        try:
            self.log_message(f"💾 Tạo backup tại: {backup_folder}")
            shutil.copytree(self.selected_path.get(), backup_folder, ignore=shutil.ignore_patterns("_BACKUP_*"))
            self.log_message("✅ Backup hoàn thành!")
            
            # Thực hiện rename
            self.rename_files()
            
        except Exception as e:
            self.log_message(f"❌ Lỗi tạo backup: {e}")
            messagebox.showerror("Lỗi", f"Không thể tạo backup: {e}")
    
    def undo_last_rename(self):
        """Hoàn tác lần đổi tên cuối"""
        if not self.last_rename_actions:
            messagebox.showinfo("Thông báo", "Không có thao tác nào để hoàn tác!")
            return
        
        success_count = 0
        error_count = 0
        
        self.log_message("↩️ Đang hoàn tác...")
        
        for new_path, old_path in reversed(self.last_rename_actions):
            try:
                if os.path.exists(new_path):
                    os.rename(new_path, old_path)
                    success_count += 1
                    self.log_message(f"↩️ {os.path.basename(new_path)} → {os.path.basename(old_path)}")
            except Exception as e:
                error_count += 1
                self.log_message(f"❌ Lỗi hoàn tác: {e}")
        
        self.log_message(f"✅ Hoàn tác: {success_count} file, Lỗi: {error_count}")
        self.last_rename_actions.clear()
        messagebox.showinfo("Hoàn tác", f"Đã hoàn tác {success_count} file!")
    
    def start_rename(self):
        """Bắt đầu đổi tên trong thread riêng"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn đổi tên file? Thao tác này không thể hoàn tác hoàn toàn."):
            thread = threading.Thread(target=self.rename_files)
            thread.daemon = True
            thread.start()

def main():
    root = tk.Tk()
    app = AdvancedRenameTool(root)
    root.mainloop()

if __name__ == "__main__":
    import time
    main()
