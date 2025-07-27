import os
import subprocess
import random
import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class VideoThumbnailGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Thumbnail Generator")
        self.root.geometry("700x500")
        
        # Variables
        self.selected_path = tk.StringVar()
        self.current_file = tk.StringVar()
        self.progress = tk.DoubleVar()
        
        # Video extensions
        self.video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Path selection
        ttk.Label(main_frame, text="Chọn thư mục chứa video:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(path_frame, textvariable=self.selected_path, width=60).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(path_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1, padx=(5, 0))
        
        path_frame.columnconfigure(0, weight=1)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Tùy chọn", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Scale option
        ttk.Label(options_frame, text="Kích thước thumbnail:").grid(row=0, column=0, sticky=tk.W)
        self.scale_var = tk.StringVar(value="480:-1")
        scale_combo = ttk.Combobox(options_frame, textvariable=self.scale_var, width=15)
        scale_combo['values'] = ("480:-1", "720:-1", "1080:-1", "640:-1", "320:-1")
        scale_combo.grid(row=0, column=1, padx=(5, 0), sticky=tk.W)
        
        # Random time range
        ttk.Label(options_frame, text="Khoảng thời gian random (giây):").grid(row=1, column=0, sticky=tk.W, pady=5)
        time_frame = ttk.Frame(options_frame)
        time_frame.grid(row=1, column=1, padx=(5, 0), sticky=tk.W)
        
        ttk.Label(time_frame, text="Từ:").pack(side=tk.LEFT)
        self.min_time = tk.IntVar(value=2)
        ttk.Entry(time_frame, textvariable=self.min_time, width=5).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(time_frame, text="đến:").pack(side=tk.LEFT, padx=(5, 0))
        self.max_offset = tk.IntVar(value=2)
        ttk.Entry(time_frame, textvariable=self.max_offset, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(time_frame, text="giây cuối").pack(side=tk.LEFT, padx=(2, 0))
        
        # Skip existing
        self.skip_existing = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Bỏ qua file thumbnail đã tồn tại", 
                       variable=self.skip_existing).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Thumbnail mode
        ttk.Label(options_frame, text="Vị trí thumbnail:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.thumbnail_mode = tk.StringVar(value="folder")
        mode_frame = ttk.Frame(options_frame)
        mode_frame.grid(row=3, column=1, padx=(5, 0), sticky=tk.W)
        
        ttk.Radiobutton(mode_frame, text="Trong folder .thumbnail", 
                       variable=self.thumbnail_mode, value="folder").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Cùng cấp với video", 
                       variable=self.thumbnail_mode, value="same").pack(side=tk.LEFT, padx=(10, 0))
        
        # Log area
        ttk.Label(main_frame, text="Log:").grid(row=3, column=0, sticky=tk.W, pady=(20, 5))
        
        self.log_text = tk.Text(main_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        scrollbar.grid(row=4, column=1, sticky=(tk.N, tk.S), pady=5)
        
        # Progress bar
        ttk.Label(main_frame, text="Tiến trình:").grid(row=5, column=0, sticky=tk.W, pady=(10, 0))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, textvariable=self.current_file)
        self.status_label.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Scan Video", command=self.scan_videos).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Thumbnails", command=self.start_generation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
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
    
    def find_video_files(self, directory):
        """Tìm tất cả file video trong thư mục và thư mục con"""
        video_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in self.video_extensions:
                    video_files.append(os.path.join(root, file))
        
        return video_files
    
    def get_thumbnail_path(self, video_file):
        """Lấy đường dẫn thumbnail dựa trên mode đã chọn"""
        video_dir = os.path.dirname(video_file)
        video_name = Path(video_file).stem
        
        if self.thumbnail_mode.get() == "folder":
            # Mode: Trong folder .thumbnail
            thumbnail_dir = os.path.join(video_dir, ".thumbnail")
            thumbnail_path = os.path.join(thumbnail_dir, f"{video_name}.jpg")
            return thumbnail_path, thumbnail_dir
        else:
            # Mode: Cùng cấp với video
            thumbnail_path = os.path.join(video_dir, f"{video_name}.jpg")
            return thumbnail_path, video_dir
    
    def scan_videos(self):
        """Scan và hiển thị danh sách video"""
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        self.clear_log()
        self.log_message("🔍 Đang scan video files...")
        
        video_files = self.find_video_files(self.selected_path.get())
        
        if not video_files:
            self.log_message("❌ Không tìm thấy file video nào!")
            return
        
        self.log_message(f"✅ Tìm thấy {len(video_files)} file video:")
        
        for i, video_file in enumerate(video_files[:20]):  # Hiển thị 20 file đầu
            # Kiểm tra thumbnail theo mode đã chọn
            thumb_path, _ = self.get_thumbnail_path(video_file)
            
            status = "✅ Có thumbnail" if os.path.exists(thumb_path) else "❌ Chưa có thumbnail"
            relative_path = os.path.relpath(video_file, self.selected_path.get())
            self.log_message(f"  {i+1}. {relative_path} - {status}")
        
        if len(video_files) > 20:
            self.log_message(f"  ... và {len(video_files) - 20} file khác")
    
    def get_video_duration(self, video_path):
        """Lấy độ dài video bằng ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'error', 
                '-show_entries', 'format=duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', 
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='utf-8', errors='ignore', timeout=30)
            
            if result.returncode == 0:
                duration_str = result.stdout.strip()
                if re.match(r'^[\d\.]+$', duration_str):
                    return int(float(duration_str))
            
            return None
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            self.log_message(f"⚠️  Lỗi khi lấy duration: {e}")
            return None
    
    def generate_thumbnail(self, video_path, timestamp):
        """Tạo thumbnail bằng ffmpeg theo mode đã chọn"""
        try:
            # Lấy đường dẫn thumbnail theo mode
            thumbnail_path, thumbnail_dir = self.get_thumbnail_path(video_path)
            
            # Tạo thư mục nếu cần (chỉ với mode folder)
            if self.thumbnail_mode.get() == "folder" and not os.path.exists(thumbnail_dir):
                os.makedirs(thumbnail_dir)
            
            # Kiểm tra thumbnail đã tồn tại
            if os.path.exists(thumbnail_path) and self.skip_existing.get():
                return True, thumbnail_path
            
            cmd = [
                'ffmpeg', '-y', '-ss', str(timestamp),
                '-i', video_path,
                '-vframes', '1',
                '-vf', f'scale={self.scale_var.get()}',
                thumbnail_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='utf-8', errors='ignore', timeout=60)
            
            return result.returncode == 0, thumbnail_path
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            self.log_message(f"⚠️  Lỗi khi tạo thumbnail: {e}")
            return False, None
    
    def check_ffmpeg_available(self):
        """Kiểm tra ffmpeg và ffprobe có available không"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, 
                         encoding='utf-8', errors='ignore', timeout=10)
            subprocess.run(['ffprobe', '-version'], capture_output=True, 
                         encoding='utf-8', errors='ignore', timeout=10)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def generate_thumbnails(self):
        """Tạo thumbnail cho tất cả video"""
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        # Kiểm tra ffmpeg
        if not self.check_ffmpeg_available():
            messagebox.showerror("Lỗi", 
                               "Không tìm thấy ffmpeg/ffprobe!\n"
                               "Vui lòng cài đặt ffmpeg và thêm vào PATH.")
            return
        
        self.clear_log()
        self.log_message("🚀 Bắt đầu tạo thumbnail...")
        
        video_files = self.find_video_files(self.selected_path.get())
        
        if not video_files:
            self.log_message("❌ Không tìm thấy file video nào!")
            return
        
        total_files = len(video_files)
        processed = 0
        generated = 0
        skipped = 0
        errors = 0
        
        min_time = self.min_time.get()
        max_offset = self.max_offset.get()
        
        for video_file in video_files:
            try:
                # Cập nhật status
                relative_path = os.path.relpath(video_file, self.selected_path.get())
                self.current_file.set(f"Đang xử lý: {relative_path}")
                self.log_message(f"\n📹 Xử lý: {relative_path}")
                
                # Kiểm tra thumbnail theo mode đã chọn
                thumbnail_path, _ = self.get_thumbnail_path(video_file)
                
                # Kiểm tra thumbnail đã tồn tại
                if os.path.exists(thumbnail_path) and self.skip_existing.get():
                    self.log_message("✅ Bỏ qua (đã tồn tại)")
                    skipped += 1
                else:
                    # Lấy duration
                    duration = self.get_video_duration(video_file)
                    
                    if duration is None:
                        self.log_message("⚠️  Không thể lấy độ dài video")
                        errors += 1
                    elif duration <= (min_time + max_offset):
                        # Video quá ngắn, dùng giây thứ 1
                        timestamp = 1
                        self.log_message(f"📏 Video ngắn ({duration}s), dùng timestamp: {timestamp}s")
                    else:
                        # Random timestamp
                        max_time = duration - max_offset
                        timestamp = random.randint(min_time, max_time)
                        self.log_message(f"📏 Duration: {duration}s, Random timestamp: {timestamp}s")
                    
                    if duration is not None:
                        # Tạo thumbnail
                        success, thumb_path = self.generate_thumbnail(video_file, timestamp)
                        
                        if success and thumb_path and os.path.exists(thumb_path):
                            mode_text = "folder .thumbnail" if self.thumbnail_mode.get() == "folder" else "cùng cấp"
                            self.log_message(f"✅ Tạo thumbnail thành công ({mode_text}): {os.path.basename(thumb_path)}")
                            generated += 1
                        else:
                            self.log_message("❌ Lỗi khi tạo thumbnail")
                            errors += 1
                
                processed += 1
                
                # Cập nhật progress
                progress_percent = (processed / total_files) * 100
                self.progress.set(progress_percent)
                self.root.update_idletasks()
                
            except Exception as e:
                self.log_message(f"❌ Lỗi: {e}")
                errors += 1
                processed += 1
        
        # Hoàn thành
        self.progress.set(100)
        self.current_file.set("Hoàn thành!")
        
        self.log_message(f"\n🎉 HOÀN THÀNH!")
        self.log_message(f"📊 Tổng kết:")
        self.log_message(f"   - Tổng file: {total_files}")
        self.log_message(f"   - Đã tạo: {generated}")
        self.log_message(f"   - Bỏ qua: {skipped}")
        self.log_message(f"   - Lỗi: {errors}")
        
        messagebox.showinfo("Hoàn thành", 
                          f"Đã xử lý {total_files} file video!\n"
                          f"Tạo mới: {generated}\n"
                          f"Bỏ qua: {skipped}\n"
                          f"Lỗi: {errors}")
        
        # Reset progress
        self.progress.set(0)
        self.current_file.set("")
    
    def start_generation(self):
        """Bắt đầu tạo thumbnail trong thread riêng"""
        thread = threading.Thread(target=self.generate_thumbnails)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = VideoThumbnailGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
