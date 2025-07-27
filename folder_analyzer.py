import os
import csv
import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class FolderAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Structure Analyzer")
        self.root.geometry("900x700")
        
        # Variables
        self.selected_path = tk.StringVar()
        self.current_folder = tk.StringVar()
        self.progress = tk.DoubleVar()
        
        # Analysis settings
        self.max_depth = tk.IntVar(value=9)
        self.include_files = tk.BooleanVar(value=True)
        self.include_size = tk.BooleanVar(value=True)
        self.include_dates = tk.BooleanVar(value=True)
        self.include_permissions = tk.BooleanVar(value=False)
        self.export_format = tk.StringVar(value="csv")
        
        # Statistics
        self.stats = {
            'total_folders': 0,
            'total_files': 0,
            'total_size': 0,
            'max_depth_found': 0,
            'empty_folders': 0
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Path selection
        ttk.Label(main_frame, text="📁 Chọn thư mục gốc để phân tích:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(path_frame, textvariable=self.selected_path, width=70).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(path_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1, padx=(5, 0))
        ttk.Button(path_frame, text="Analyze", command=self.start_analysis).grid(row=0, column=2, padx=(5, 0))
        
        path_frame.columnconfigure(0, weight=1)
        
        # Analysis options
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Tùy chọn phân tích", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Depth setting
        depth_frame = ttk.Frame(options_frame)
        depth_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(depth_frame, text="Độ sâu tối đa:").pack(side=tk.LEFT)
        ttk.Scale(depth_frame, from_=1, to=15, variable=self.max_depth, orient=tk.HORIZONTAL, length=200).pack(side=tk.LEFT, padx=5)
        ttk.Label(depth_frame, textvariable=self.max_depth).pack(side=tk.LEFT, padx=5)
        
        # Include options
        include_frame = ttk.Frame(options_frame)
        include_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(include_frame, text="Đếm file trong folder", variable=self.include_files).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(include_frame, text="Tính kích thước", variable=self.include_size).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(include_frame, text="Ngày tạo/sửa", variable=self.include_dates).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(include_frame, text="Quyền truy cập", variable=self.include_permissions).pack(side=tk.LEFT, padx=10)
        
        # Export format
        export_frame = ttk.Frame(options_frame)
        export_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(export_frame, text="Định dạng xuất:").pack(side=tk.LEFT)
        ttk.Radiobutton(export_frame, text="CSV", variable=self.export_format, value="csv").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(export_frame, text="JSON", variable=self.export_format, value="json").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(export_frame, text="TXT", variable=self.export_format, value="txt").pack(side=tk.LEFT, padx=10)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Thống kê", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=6, width=80)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
        
        # Results tree
        ttk.Label(main_frame, text="🌳 Cấu trúc thư mục:").grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        
        # Tree frame
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Define columns
        columns = ('path', 'level', 'files', 'size', 'created', 'modified')
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=15)
        
        # Configure headings
        self.results_tree.heading('#0', text='Tên thư mục')
        self.results_tree.heading('path', text='Đường dẫn')
        self.results_tree.heading('level', text='Cấp')
        self.results_tree.heading('files', text='Số file')
        self.results_tree.heading('size', text='Kích thước')
        self.results_tree.heading('created', text='Ngày tạo')
        self.results_tree.heading('modified', text='Ngày sửa')
        
        # Configure columns
        self.results_tree.column('#0', width=200)
        self.results_tree.column('path', width=300)
        self.results_tree.column('level', width=50)
        self.results_tree.column('files', width=80)
        self.results_tree.column('size', width=100)
        self.results_tree.column('created', width=120)
        self.results_tree.column('modified', width=120)
        
        tree_scrollbar_v = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        tree_scrollbar_h = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=tree_scrollbar_v.set, xscrollcommand=tree_scrollbar_h.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Progress bar
        ttk.Label(main_frame, text="Tiến trình:").grid(row=6, column=0, sticky=tk.W, pady=(10, 0))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.current_folder)
        self.status_label.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="📈 Analyze", command=self.start_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Export", command=self.export_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📋 Copy Path", command=self.copy_selected_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔍 Open Folder", command=self.open_selected_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Store analysis results
        self.analysis_results = []
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_path.set(folder)
    
    def format_size(self, size_bytes):
        """Format size in bytes to human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size_bytes >= 1024.0 and i < len(size_units) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_units[i]}"
    
    def get_folder_info(self, folder_path):
        """Get detailed information about a folder"""
        info = {
            'path': folder_path,
            'name': os.path.basename(folder_path),
            'level': 0,
            'files_count': 0,
            'folders_count': 0,
            'total_size': 0,
            'created': None,
            'modified': None,
            'accessed': None,
            'permissions': None,
            'is_empty': True
        }
        
        try:
            # Get folder stats
            stat = os.stat(folder_path)
            info['created'] = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            info['modified'] = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            info['accessed'] = datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')
            
            # Count files and calculate size
            if self.include_files.get() or self.include_size.get():
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isfile(item_path):
                        info['files_count'] += 1
                        info['is_empty'] = False
                        if self.include_size.get():
                            try:
                                info['total_size'] += os.path.getsize(item_path)
                            except:
                                pass
                    elif os.path.isdir(item_path):
                        info['folders_count'] += 1
                        info['is_empty'] = False
            
            # Get permissions (Windows)
            if self.include_permissions.get():
                try:
                    import stat
                    mode = os.stat(folder_path).st_mode
                    permissions = []
                    if mode & stat.S_IRUSR: permissions.append('r')
                    if mode & stat.S_IWUSR: permissions.append('w')
                    if mode & stat.S_IXUSR: permissions.append('x')
                    info['permissions'] = ''.join(permissions)
                except:
                    info['permissions'] = 'unknown'
        
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def analyze_folder_structure(self, root_path, max_depth=9):
        """Analyze folder structure up to specified depth"""
        results = []
        total_folders = 0
        
        # First pass: count total folders for progress
        for root, dirs, files in os.walk(root_path):
            level = root.replace(root_path, '').count(os.sep)
            if level < max_depth:
                total_folders += len(dirs)
        
        processed = 0
        
        # Reset stats
        self.stats = {
            'total_folders': 0,
            'total_files': 0,
            'total_size': 0,
            'max_depth_found': 0,
            'empty_folders': 0
        }
        
        # Second pass: collect information
        for root, dirs, files in os.walk(root_path):
            level = root.replace(root_path, '').count(os.sep)
            
            if level >= max_depth:
                dirs.clear()  # Don't go deeper
                continue
            
            # Update current folder status
            relative_path = os.path.relpath(root, root_path)
            self.current_folder.set(f"Analyzing: {relative_path}")
            
            # Get folder info
            folder_info = self.get_folder_info(root)
            folder_info['level'] = level
            
            # Update stats
            self.stats['total_folders'] += 1
            self.stats['total_files'] += folder_info['files_count']
            self.stats['total_size'] += folder_info['total_size']
            self.stats['max_depth_found'] = max(self.stats['max_depth_found'], level)
            if folder_info['is_empty']:
                self.stats['empty_folders'] += 1
            
            results.append(folder_info)
            
            # Update progress
            processed += 1
            if total_folders > 0:
                progress = min(100, (processed / total_folders) * 100)
                self.progress.set(progress)
                self.root.update_idletasks()
        
        return results
    
    def update_statistics(self):
        """Update statistics display"""
        self.stats_text.delete(1.0, tk.END)
        
        stats_text = f"""📊 THỐNG KÊ PHÂN TÍCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Tổng số thư mục: {self.stats['total_folders']:,}
📄 Tổng số file: {self.stats['total_files']:,}
💾 Tổng kích thước: {self.format_size(self.stats['total_size'])}
📏 Độ sâu tối đa tìm thấy: {self.stats['max_depth_found']} cấp
📂 Thư mục rỗng: {self.stats['empty_folders']:,}
📈 Tỷ lệ thư mục rỗng: {(self.stats['empty_folders']/max(1, self.stats['total_folders'])*100):.1f}%
⏰ Thời gian phân tích: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.stats_text.insert(tk.END, stats_text)
    
    def populate_tree(self, results):
        """Populate the results tree with analysis data"""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Group by level for hierarchical display
        nodes = {}  # path -> tree_item_id
        
        for folder_info in sorted(results, key=lambda x: (x['level'], x['path'])):
            path = folder_info['path']
            level = folder_info['level']
            name = folder_info['name'] if folder_info['name'] else os.path.basename(path)
            
            # Prepare values
            values = [
                path,
                str(level),
                str(folder_info['files_count']) if self.include_files.get() else '',
                self.format_size(folder_info['total_size']) if self.include_size.get() else '',
                folder_info['created'] if self.include_dates.get() else '',
                folder_info['modified'] if self.include_dates.get() else ''
            ]
            
            # Find parent
            parent = ''
            if level > 0:
                parent_path = os.path.dirname(path)
                parent = nodes.get(parent_path, '')
            
            # Insert into tree
            item_id = self.results_tree.insert(parent, 'end', text=name, values=values)
            nodes[path] = item_id
            
            # Color coding based on properties
            if folder_info['is_empty']:
                self.results_tree.set(item_id, 'files', '(empty)')
    
    def analyze_folders(self):
        """Main analysis function"""
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        if not os.path.exists(self.selected_path.get()):
            messagebox.showerror("Lỗi", "Thư mục không tồn tại!")
            return
        
        self.clear_results()
        self.current_folder.set("Đang bắt đầu phân tích...")
        
        try:
            # Perform analysis
            results = self.analyze_folder_structure(
                self.selected_path.get(), 
                self.max_depth.get()
            )
            
            self.analysis_results = results
            
            # Update displays
            self.populate_tree(results)
            self.update_statistics()
            
            # Complete
            self.progress.set(100)
            self.current_folder.set(f"Hoàn thành! Phân tích {len(results)} thư mục")
            
            messagebox.showinfo("Hoàn thành", f"Đã phân tích {len(results)} thư mục!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi trong quá trình phân tích: {e}")
        
        finally:
            self.progress.set(0)
    
    def export_results(self):
        """Export analysis results to file"""
        if not self.analysis_results:
            messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu để xuất!")
            return
        
        # Choose file to save
        file_extension = self.export_format.get()
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{file_extension}",
            filetypes=[(f"{file_extension.upper()} files", f"*.{file_extension}"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            if file_extension == "csv":
                self.export_csv(filename)
            elif file_extension == "json":
                self.export_json(filename)
            elif file_extension == "txt":
                self.export_txt(filename)
            
            messagebox.showinfo("Thành công", f"Đã xuất dữ liệu ra {filename}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xuất file: {e}")
    
    def export_csv(self, filename):
        """Export to CSV format"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Path', 'Name', 'Level', 'Files_Count', 'Total_Size', 'Size_Formatted', 
                         'Created', 'Modified', 'Is_Empty']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for folder in self.analysis_results:
                writer.writerow({
                    'Path': folder['path'],
                    'Name': folder['name'],
                    'Level': folder['level'],
                    'Files_Count': folder['files_count'],
                    'Total_Size': folder['total_size'],
                    'Size_Formatted': self.format_size(folder['total_size']),
                    'Created': folder['created'],
                    'Modified': folder['modified'],
                    'Is_Empty': folder['is_empty']
                })
    
    def export_json(self, filename):
        """Export to JSON format"""
        export_data = {
            'analysis_info': {
                'root_path': self.selected_path.get(),
                'max_depth': self.max_depth.get(),
                'analysis_time': datetime.now().isoformat(),
                'statistics': self.stats
            },
            'folders': self.analysis_results
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False, default=str)
    
    def export_txt(self, filename):
        """Export to TXT format"""
        with open(filename, 'w', encoding='utf-8') as txtfile:
            txtfile.write("FOLDER STRUCTURE ANALYSIS REPORT\n")
            txtfile.write("=" * 50 + "\n\n")
            
            txtfile.write(f"Root Path: {self.selected_path.get()}\n")
            txtfile.write(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            txtfile.write(f"Max Depth: {self.max_depth.get()}\n\n")
            
            txtfile.write("STATISTICS:\n")
            txtfile.write("-" * 20 + "\n")
            txtfile.write(f"Total Folders: {self.stats['total_folders']:,}\n")
            txtfile.write(f"Total Files: {self.stats['total_files']:,}\n")
            txtfile.write(f"Total Size: {self.format_size(self.stats['total_size'])}\n")
            txtfile.write(f"Max Depth Found: {self.stats['max_depth_found']}\n")
            txtfile.write(f"Empty Folders: {self.stats['empty_folders']:,}\n\n")
            
            txtfile.write("FOLDER DETAILS:\n")
            txtfile.write("-" * 20 + "\n")
            
            for folder in self.analysis_results:
                indent = "  " * folder['level']
                txtfile.write(f"{indent}{folder['name']}\n")
                txtfile.write(f"{indent}  Path: {folder['path']}\n")
                txtfile.write(f"{indent}  Files: {folder['files_count']}\n")
                txtfile.write(f"{indent}  Size: {self.format_size(folder['total_size'])}\n")
                if folder['created']:
                    txtfile.write(f"{indent}  Created: {folder['created']}\n")
                txtfile.write("\n")
    
    def copy_selected_path(self):
        """Copy selected folder path to clipboard"""
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            path = self.results_tree.set(item, 'path')
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            messagebox.showinfo("Copied", f"Đã copy path: {path}")
    
    def open_selected_folder(self):
        """Open selected folder in file explorer"""
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            path = self.results_tree.set(item, 'path')
            try:
                import subprocess
                subprocess.run(['explorer', path], check=True)
            except:
                messagebox.showerror("Lỗi", "Không thể mở folder!")
    
    def clear_results(self):
        """Clear all results and reset"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.stats_text.delete(1.0, tk.END)
        self.analysis_results.clear()
        self.progress.set(0)
        self.current_folder.set("")
    
    def start_analysis(self):
        """Start analysis in separate thread"""
        thread = threading.Thread(target=self.analyze_folders)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = FolderAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
