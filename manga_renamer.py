import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import shutil

class MangaRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("Manga File Renamer")
        self.root.geometry("600x400")
        
        # Variables
        self.selected_path = tk.StringVar()
        self.current_folder = tk.StringVar()
        self.progress = tk.DoubleVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Path selection
        ttk.Label(main_frame, text="Chọn thư mục chứa manga:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(path_frame, textvariable=self.selected_path, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(path_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1, padx=(5, 0))
        
        path_frame.columnconfigure(0, weight=1)
        
        # Preview area
        ttk.Label(main_frame, text="Preview cấu trúc:").grid(row=2, column=0, sticky=tk.W, pady=(20, 5))
        
        self.preview_text = tk.Text(main_frame, height=15, width=70)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        self.preview_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        scrollbar.grid(row=3, column=1, sticky=(tk.N, tk.S), pady=5)
        
        # Progress bar
        ttk.Label(main_frame, text="Tiến trình:").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.current_folder)
        self.status_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Preview", command=self.preview_renaming).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start Rename", command=self.start_renaming).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Move All", command=self.start_move_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy All", command=self.start_copy_all).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_path.set(folder)
            self.preview_renaming()
    
    def natural_sort_key(self, text):
        """Sắp xếp tự nhiên: 1, 2, 3, 10, 11 thay vì 1, 10, 11, 2, 3"""
        return [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', text)]
    
    def get_image_files(self, folder_path):
        """Lấy danh sách file ảnh và sắp xếp theo thứ tự tự nhiên"""
        extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        files = []
        
        try:
            for file in os.listdir(folder_path):
                if Path(file).suffix.lower() in extensions:
                    files.append(file)
        except OSError:
            return []
        
        return sorted(files, key=self.natural_sort_key)
    
    def get_manga_structure(self, base_path):
        """Phân tích cấu trúc thư mục manga"""
        structure = {}
        
        try:
            # Lấy danh sách thư mục manga
            manga_folders = [d for d in os.listdir(base_path) 
                           if os.path.isdir(os.path.join(base_path, d))]
            manga_folders.sort(key=self.natural_sort_key)
            
            for manga_folder in manga_folders:
                manga_path = os.path.join(base_path, manga_folder)
                chapters = {}
                
                # Lấy danh sách chapter
                chapter_folders = [d for d in os.listdir(manga_path) 
                                 if os.path.isdir(os.path.join(manga_path, d))]
                chapter_folders.sort(key=self.natural_sort_key)
                
                for chapter_folder in chapter_folders:
                    chapter_path = os.path.join(manga_path, chapter_folder)
                    image_files = self.get_image_files(chapter_path)
                    if image_files:  # Chỉ thêm chapter có file ảnh
                        chapters[chapter_folder] = {
                            'path': chapter_path,
                            'files': image_files
                        }
                
                if chapters:  # Chỉ thêm manga có chapter
                    structure[manga_folder] = chapters
        
        except OSError as e:
            messagebox.showerror("Lỗi", f"Không thể đọc thư mục: {e}")
        
        return structure
    
    def preview_renaming(self):
        """Hiển thị preview của quá trình rename"""
        if not self.selected_path.get():
            return
        
        self.preview_text.delete(1.0, tk.END)
        structure = self.get_manga_structure(self.selected_path.get())
        
        if not structure:
            self.preview_text.insert(tk.END, "Không tìm thấy cấu trúc manga hợp lệ!")
            return
        
        global_counter = 1
        preview_content = []
        
        for manga_name, chapters in structure.items():
            preview_content.append(f"📁 MANGA: {manga_name}\n")
            preview_content.append("=" * 50 + "\n")
            
            # Reset counter cho mỗi manga
            manga_counter = 1
            
            for chapter_name, chapter_data in chapters.items():
                preview_content.append(f"  📖 Chapter: {chapter_name}\n")
                
                for i, file_name in enumerate(chapter_data['files'][:5]):  # Hiển thị 5 file đầu
                    old_name = file_name
                    extension = Path(file_name).suffix
                    new_name = f"{manga_counter:03d}_{chapter_name}{extension}"
                    
                    preview_content.append(f"    {old_name} → {new_name}\n")
                    manga_counter += 1
                
                if len(chapter_data['files']) > 5:
                    remaining = len(chapter_data['files']) - 5
                    preview_content.append(f"    ... và {remaining} file khác\n")
                    manga_counter += remaining
                
                preview_content.append("\n")
            
            preview_content.append("\n")
        
        self.preview_text.insert(tk.END, ''.join(preview_content))
    
    def rename_files(self):
        """Thực hiện rename file"""
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        structure = self.get_manga_structure(self.selected_path.get())
        if not structure:
            messagebox.showerror("Lỗi", "Không tìm thấy cấu trúc manga hợp lệ!")
            return
        
        # Tính tổng số file để hiển thị progress
        total_files = sum(len(chapter_data['files']) 
                         for chapters in structure.values() 
                         for chapter_data in chapters.values())
        
        if total_files == 0:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy file ảnh nào!")
            return
        
        # Xác nhận từ người dùng
        result = messagebox.askyesno("Xác nhận", 
                                   f"Bạn có chắc muốn rename {total_files} file?\n"
                                   "Thao tác này không thể hoàn tác!")
        if not result:
            return
        
        processed_files = 0
        global_counter = 1
        errors = []
        
        try:
            for manga_name, chapters in structure.items():
                self.current_folder.set(f"Đang xử lý manga: {manga_name}")
                self.root.update_idletasks()
                
                # Reset counter cho mỗi manga
                manga_counter = 1
                
                for chapter_name, chapter_data in chapters.items():
                    self.current_folder.set(f"Đang xử lý: {manga_name} - {chapter_name}")
                    self.root.update_idletasks()
                    
                    chapter_path = chapter_data['path']
                    
                    for file_name in chapter_data['files']:
                        try:
                            old_path = os.path.join(chapter_path, file_name)
                            extension = Path(file_name).suffix
                            new_name = f"{manga_counter:03d}_{chapter_name}{extension}"
                            new_path = os.path.join(chapter_path, new_name)
                            
                            # Kiểm tra nếu file đích đã tồn tại
                            if os.path.exists(new_path) and old_path != new_path:
                                temp_name = f"temp_{manga_counter}_{chapter_name}{extension}"
                                temp_path = os.path.join(chapter_path, temp_name)
                                os.rename(old_path, temp_path)
                                os.rename(temp_path, new_path)
                            else:
                                os.rename(old_path, new_path)
                            
                            manga_counter += 1
                            processed_files += 1
                            
                            # Cập nhật progress
                            progress_percent = (processed_files / total_files) * 100
                            self.progress.set(progress_percent)
                            self.root.update_idletasks()
                            
                        except OSError as e:
                            error_msg = f"Lỗi rename file {file_name}: {e}"
                            errors.append(error_msg)
                            print(error_msg)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")
            return
        
        # Hoàn thành
        self.progress.set(100)
        self.current_folder.set("Hoàn thành!")
        
        if errors:
            error_text = "\n".join(errors[:10])  # Hiển thị 10 lỗi đầu
            if len(errors) > 10:
                error_text += f"\n... và {len(errors) - 10} lỗi khác"
            messagebox.showwarning("Hoàn thành với lỗi", 
                                 f"Đã rename {processed_files}/{total_files} file.\n\n"
                                 f"Các lỗi:\n{error_text}")
        else:
            messagebox.showinfo("Thành công", 
                              f"Đã rename thành công {processed_files} file!")
        
        # Reset progress
        self.progress.set(0)
        self.current_folder.set("")
        
        # Refresh preview
        self.preview_renaming()
    
    def start_renaming(self):
        """Bắt đầu quá trình rename trong thread riêng"""
        thread = threading.Thread(target=self.rename_files)
        thread.daemon = True
        thread.start()
    
    def move_or_copy_all_files(self, operation="move"):
        """Move hoặc copy toàn bộ file đã rename vào folder 'all'"""
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        structure = self.get_manga_structure(self.selected_path.get())
        if not structure:
            messagebox.showerror("Lỗi", "Không tìm thấy cấu trúc manga hợp lệ!")
            return
        
        # Tính tổng số file
        total_files = sum(len(chapter_data['files']) 
                         for chapters in structure.values() 
                         for chapter_data in chapters.values())
        
        if total_files == 0:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy file ảnh nào!")
            return
        
        operation_text = "di chuyển" if operation == "move" else "sao chép"
        result = messagebox.askyesno("Xác nhận", 
                                   f"Bạn có chắc muốn {operation_text} {total_files} file vào folder 'all'?")
        if not result:
            return
        
        processed_files = 0
        errors = []
        
        try:
            for manga_name, chapters in structure.items():
                # Tạo folder 'all' trong thư mục manga
                manga_path = os.path.join(self.selected_path.get(), manga_name)
                all_folder = os.path.join(manga_path, "all")
                
                if not os.path.exists(all_folder):
                    os.makedirs(all_folder)
                
                self.current_folder.set(f"Đang {operation_text} files từ manga: {manga_name}")
                self.root.update_idletasks()
                
                # Reset counter cho mỗi manga
                manga_file_counter = 1
                
                for chapter_name, chapter_data in chapters.items():
                    self.current_folder.set(f"Đang {operation_text}: {manga_name} - {chapter_name}")
                    self.root.update_idletasks()
                    
                    chapter_path = chapter_data['path']
                    
                    for file_name in chapter_data['files']:
                        try:
                            # Tìm file đã được rename (có format 001_Chapter...)
                            renamed_files = [f for f in os.listdir(chapter_path) 
                                           if f.startswith(f"{manga_file_counter:03d}_")]
                            
                            if not renamed_files:
                                # Nếu không tìm thấy file đã rename, tìm file gốc
                                if os.path.exists(os.path.join(chapter_path, file_name)):
                                    source_file = file_name
                                else:
                                    manga_file_counter += 1
                                    processed_files += 1
                                    continue
                            else:
                                source_file = renamed_files[0]
                            
                            source_path = os.path.join(chapter_path, source_file)
                            dest_path = os.path.join(all_folder, source_file)
                            
                            # Tránh trùng tên file
                            counter = 1
                            original_dest = dest_path
                            while os.path.exists(dest_path):
                                name, ext = os.path.splitext(source_file)
                                dest_path = os.path.join(all_folder, f"{name}_{counter}{ext}")
                                counter += 1
                            
                            if operation == "move":
                                shutil.move(source_path, dest_path)
                            else:  # copy
                                shutil.copy2(source_path, dest_path)
                            
                            manga_file_counter += 1
                            processed_files += 1
                            
                            # Cập nhật progress
                            progress_percent = (processed_files / total_files) * 100
                            self.progress.set(progress_percent)
                            self.root.update_idletasks()
                            
                        except Exception as e:
                            error_msg = f"Lỗi {operation_text} file {file_name}: {e}"
                            errors.append(error_msg)
                            print(error_msg)
                            manga_file_counter += 1
                            processed_files += 1
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")
            return
        
        # Hoàn thành
        self.progress.set(100)
        self.current_folder.set("Hoàn thành!")
        
        if errors:
            error_text = "\n".join(errors[:10])
            if len(errors) > 10:
                error_text += f"\n... và {len(errors) - 10} lỗi khác"
            messagebox.showwarning("Hoàn thành với lỗi", 
                                 f"Đã {operation_text} {processed_files}/{total_files} file.\n\n"
                                 f"Các lỗi:\n{error_text}")
        else:
            messagebox.showinfo("Thành công", 
                              f"Đã {operation_text} thành công {processed_files} file vào folder 'all'!")
        
        # Reset progress
        self.progress.set(0)
        self.current_folder.set("")
    
    def start_move_all(self):
        """Bắt đầu quá trình move all trong thread riêng"""
        thread = threading.Thread(target=lambda: self.move_or_copy_all_files("move"))
        thread.daemon = True
        thread.start()
    
    def start_copy_all(self):
        """Bắt đầu quá trình copy all trong thread riêng"""
        thread = threading.Thread(target=lambda: self.move_or_copy_all_files("copy"))
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = MangaRenamer(root)
    root.mainloop()

if __name__ == "__main__":
    main()