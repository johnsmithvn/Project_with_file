import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

# Import thư viện xử lý metadata nhạc
try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
    from mutagen.oggvorbis import OggVorbis
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

class AudioThumbnailGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Thumbnail Generator")
        self.root.geometry("700x500")
        
        # Variables
        self.selected_path = tk.StringVar()
        self.current_file = tk.StringVar()
        self.progress = tk.DoubleVar()
        
        # Audio extensions
        self.audio_extensions = {'.mp3', '.flac', '.wav', '.aac', '.m4a', '.ogg', '.opus', '.wma', '.alac', '.aiff'}
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Check mutagen availability
        if not MUTAGEN_AVAILABLE:
            error_frame = ttk.Frame(main_frame)
            error_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
            ttk.Label(error_frame, text="⚠️ Cần cài đặt thư viện mutagen:", 
                     foreground="red", font=("Arial", 10, "bold")).pack()
            ttk.Label(error_frame, text="pip install mutagen", 
                     font=("Consolas", 9)).pack()
            return
        
        # Path selection
        ttk.Label(main_frame, text="Chọn thư mục chứa nhạc:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(path_frame, textvariable=self.selected_path, width=60).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(path_frame, text="Browse", command=self.browse_folder).grid(row=0, column=1, padx=(5, 0))
        
        path_frame.columnconfigure(0, weight=1)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Tùy chọn", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Skip existing
        self.skip_existing = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Bỏ qua file thumbnail đã tồn tại", 
                       variable=self.skip_existing).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Create folder thumbnails
        self.create_folder_thumbs = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Tạo thumbnail đại diện cho folder", 
                       variable=self.create_folder_thumbs).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Thumbnail mode
        ttk.Label(options_frame, text="Vị trí thumbnail:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.thumbnail_mode = tk.StringVar(value="folder")
        mode_frame = ttk.Frame(options_frame)
        mode_frame.grid(row=2, column=1, padx=(5, 0), sticky=tk.W)
        
        ttk.Radiobutton(mode_frame, text="Trong folder .thumbnail", 
                       variable=self.thumbnail_mode, value="folder").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Cùng cấp với nhạc", 
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
        
        ttk.Button(button_frame, text="Scan Audio", command=self.scan_audio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Extract Thumbnails", command=self.start_extraction).pack(side=tk.LEFT, padx=5)
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
    
    def find_audio_files(self, directory):
        """Tìm tất cả file nhạc trong thư mục và thư mục con"""
        audio_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in self.audio_extensions:
                    audio_files.append(os.path.join(root, file))
        
        return audio_files
    
    def get_thumbnail_path(self, audio_file, extension=".jpg"):
        """Lấy đường dẫn thumbnail dựa trên mode đã chọn"""
        audio_dir = os.path.dirname(audio_file)
        audio_name = Path(audio_file).stem
        
        if self.thumbnail_mode.get() == "folder":
            # Mode: Trong folder .thumbnail
            thumbnail_dir = os.path.join(audio_dir, ".thumbnail")
            thumbnail_path = os.path.join(thumbnail_dir, f"{audio_name}{extension}")
            return thumbnail_path, thumbnail_dir
        else:
            # Mode: Cùng cấp với nhạc
            thumbnail_path = os.path.join(audio_dir, f"{audio_name}{extension}")
            return thumbnail_path, audio_dir
    
    def scan_audio(self):
        """Scan và hiển thị danh sách nhạc"""
        if not MUTAGEN_AVAILABLE:
            messagebox.showerror("Lỗi", "Vui lòng cài đặt thư viện mutagen!")
            return
            
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        self.clear_log()
        self.log_message("🎵 Đang scan audio files...")
        
        audio_files = self.find_audio_files(self.selected_path.get())
        
        if not audio_files:
            self.log_message("❌ Không tìm thấy file nhạc nào!")
            return
        
        self.log_message(f"✅ Tìm thấy {len(audio_files)} file nhạc:")
        
        for i, audio_file in enumerate(audio_files[:20]):  # Hiển thị 20 file đầu
            # Kiểm tra thumbnail theo mode đã chọn
            thumb_path_jpg, _ = self.get_thumbnail_path(audio_file, ".jpg")
            thumb_path_png, _ = self.get_thumbnail_path(audio_file, ".png")
            
            has_thumb = os.path.exists(thumb_path_jpg) or os.path.exists(thumb_path_png)
            status = "✅ Có thumbnail" if has_thumb else "❌ Chưa có thumbnail"
            relative_path = os.path.relpath(audio_file, self.selected_path.get())
            self.log_message(f"  {i+1}. {relative_path} - {status}")
        
        if len(audio_files) > 20:
            self.log_message(f"  ... và {len(audio_files) - 20} file khác")
    
    def extract_embedded_artwork(self, audio_file):
        """Extract artwork từ metadata của file nhạc"""
        try:
            audio = MutagenFile(audio_file)
            if audio is None:
                return None, None
            
            artwork_data = None
            extension = ".jpg"
            
            # Xử lý MP3
            if isinstance(audio, MP3):
                for tag in audio.tags.values():
                    if hasattr(tag, 'type') and tag.type == 3:  # Cover (front)
                        artwork_data = tag.data
                        if tag.mime == 'image/png':
                            extension = ".png"
                        break
            
            # Xử lý FLAC
            elif isinstance(audio, FLAC):
                if audio.pictures:
                    pic = audio.pictures[0]
                    artwork_data = pic.data
                    if pic.mime == 'image/png':
                        extension = ".png"
            
            # Xử lý MP4/M4A
            elif isinstance(audio, MP4):
                if 'covr' in audio.tags:
                    cover = audio.tags['covr'][0]
                    artwork_data = cover
                    # MP4 cover format detection
                    if cover[0:4] == b'\x89PNG':
                        extension = ".png"
            
            # Xử lý OGG
            elif isinstance(audio, OggVorbis):
                # OGG thường không có embedded artwork, cần xử lý khác
                pass
            
            return artwork_data, extension
            
        except Exception as e:
            self.log_message(f"⚠️  Lỗi đọc metadata: {e}")
            return None, None
    
    def extract_thumbnail(self, audio_file):
        """Extract và lưu thumbnail từ file nhạc"""
        try:
            # Extract artwork
            artwork_data, extension = self.extract_embedded_artwork(audio_file)
            
            if artwork_data is None:
                return False, "Không có artwork embedded"
            
            # Lấy đường dẫn thumbnail
            thumbnail_path, thumbnail_dir = self.get_thumbnail_path(audio_file, extension)
            
            # Tạo thư mục nếu cần
            if self.thumbnail_mode.get() == "folder" and not os.path.exists(thumbnail_dir):
                os.makedirs(thumbnail_dir)
            
            # Kiểm tra file đã tồn tại
            if os.path.exists(thumbnail_path) and self.skip_existing.get():
                return True, "Đã tồn tại"
            
            # Lưu artwork
            with open(thumbnail_path, 'wb') as f:
                f.write(artwork_data)
            
            return True, thumbnail_path
            
        except Exception as e:
            return False, str(e)
    
    def create_folder_thumbnail(self, folder_path):
        """Tạo thumbnail đại diện cho folder từ file nhạc đầu tiên"""
        try:
            # Tìm file nhạc đầu tiên có thumbnail
            audio_files = []
            for file in os.listdir(folder_path):
                if Path(file).suffix.lower() in self.audio_extensions:
                    audio_files.append(os.path.join(folder_path, file))
            
            if not audio_files:
                return False
            
            # Sắp xếp và lấy file đầu tiên
            audio_files.sort()
            first_audio = audio_files[0]
            
            # Tìm thumbnail của file đầu tiên
            thumb_jpg, _ = self.get_thumbnail_path(first_audio, ".jpg")
            thumb_png, _ = self.get_thumbnail_path(first_audio, ".png")
            
            source_thumb = None
            if os.path.exists(thumb_jpg):
                source_thumb = thumb_jpg
            elif os.path.exists(thumb_png):
                source_thumb = thumb_png
            
            if source_thumb is None:
                return False
            
            # Tạo thumbnail cho folder
            folder_name = os.path.basename(folder_path)
            thumbnail_dir = os.path.join(folder_path, ".thumbnail")
            folder_thumb = os.path.join(thumbnail_dir, f"{folder_name}.jpg")
            
            if not os.path.exists(folder_thumb):
                if not os.path.exists(thumbnail_dir):
                    os.makedirs(thumbnail_dir)
                shutil.copy2(source_thumb, folder_thumb)
                return True
            
            return False
            
        except Exception as e:
            self.log_message(f"⚠️  Lỗi tạo folder thumbnail: {e}")
            return False
    
    def extract_thumbnails(self):
        """Extract thumbnail cho tất cả file nhạc"""
        if not MUTAGEN_AVAILABLE:
            messagebox.showerror("Lỗi", "Vui lòng cài đặt thư viện mutagen!")
            return
            
        if not self.selected_path.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục!")
            return
        
        self.clear_log()
        self.log_message("🚀 Bắt đầu extract thumbnail...")
        
        audio_files = self.find_audio_files(self.selected_path.get())
        
        if not audio_files:
            self.log_message("❌ Không tìm thấy file nhạc nào!")
            return
        
        total_files = len(audio_files)
        processed = 0
        extracted = 0
        skipped = 0
        errors = 0
        
        # Theo dõi folder đã xử lý
        processed_folders = set()
        
        for audio_file in audio_files:
            try:
                # Cập nhật status
                relative_path = os.path.relpath(audio_file, self.selected_path.get())
                self.current_file.set(f"Đang xử lý: {relative_path}")
                self.log_message(f"\n🎵 Xử lý: {relative_path}")
                
                # Extract thumbnail
                success, result = self.extract_thumbnail(audio_file)
                
                if success:
                    if result == "Đã tồn tại":
                        self.log_message("✅ Bỏ qua (đã tồn tại)")
                        skipped += 1
                    else:
                        mode_text = "folder .thumbnail" if self.thumbnail_mode.get() == "folder" else "cùng cấp"
                        self.log_message(f"✅ Extract thành công ({mode_text}): {os.path.basename(result)}")
                        extracted += 1
                else:
                    self.log_message(f"❌ Không thể extract: {result}")
                    errors += 1
                
                # Tạo folder thumbnail nếu cần
                if self.create_folder_thumbs.get():
                    folder_path = os.path.dirname(audio_file)
                    if folder_path not in processed_folders:
                        processed_folders.add(folder_path)
                        if self.create_folder_thumbnail(folder_path):
                            folder_name = os.path.basename(folder_path)
                            self.log_message(f"📁 Tạo folder thumbnail: {folder_name}.jpg")
                
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
        self.log_message(f"   - Đã extract: {extracted}")
        self.log_message(f"   - Bỏ qua: {skipped}")
        self.log_message(f"   - Lỗi: {errors}")
        
        messagebox.showinfo("Hoàn thành", 
                          f"Đã xử lý {total_files} file nhạc!\n"
                          f"Extract: {extracted}\n"
                          f"Bỏ qua: {skipped}\n"
                          f"Lỗi: {errors}")
        
        # Reset progress
        self.progress.set(0)
        self.current_file.set("")
    
    def start_extraction(self):
        """Bắt đầu extract thumbnail trong thread riêng"""
        thread = threading.Thread(target=self.extract_thumbnails)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = AudioThumbnailGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
