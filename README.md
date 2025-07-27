# Project File Collection

Bộ sưu tập các công cụ Python hữu ích cho việc xử lý file media và quản lý dữ liệu.

## 📋 Danh sách công cụ

### 1. 🎭 Manga Renamer (`manga_renamer.py`)
Công cụ đổi tên file ảnh manga với GUI thân thiện.

**Tính năng:**
- Đổi tên file ảnh theo thứ tự tự nhiên
- Hỗ trợ nhiều định dạng: jpg, png, jpeg, bmp, gif, webp
- Sắp xếp chapter theo thứ tự đúng (1, 2, 3... không phải 1, 10, 2...)
- Reset đánh số cho mỗi manga riêng biệt
- Move/Copy tất cả file vào folder tổng hợp
- Giao diện đồ họa với progress bar và preview

### 2. 🎬 Video Thumbnail Generator (`video_thumbnail_generator.py`)
Tạo thumbnail tự động cho video bằng ffmpeg.

### 3. 🎵 Audio Thumbnail Generator (`audio_thumbnail_generator.py`)
Extract thumbnail từ metadata của file nhạc (album art).

**Tính năng:**
- Extract album art từ file nhạc (MP3, FLAC, M4A, OGG, v.v.)
- Hỗ trợ format ảnh: JPG, PNG tự động nhận diện
- Tạo thumbnail đại diện cho folder từ bài hát đầu tiên
- Lựa chọn vị trí lưu: folder .thumbnail hoặc cùng cấp với nhạc
- Bỏ qua file đã có thumbnail
- Giao diện GUI với progress tracking

### 4. 🔧 Advanced Rename Tool (`advanced_rename_tool.py`)
Công cụ đổi tên file nâng cao với nhiều chế độ và preview.

**Tính năng:**
- Đổi tên theo 4 chế độ: số thứ tự, prefix, suffix, tìm & thay thế
- Hỗ trợ nhiều loại file: ảnh, video, audio, documents
- Preview trước khi đổi tên thực sự
- Windows natural sorting (1, 2, 3, 10, 11...)
- Backup tự động trước khi đổi tên
- Undo để hoàn tác lần đổi tên cuối
- Format số linh hoạt: 001, 01, 1
- Reset counter theo folder hoặc global

### 5. 📊 Folder Analyzer (`folder_analyzer.py`)
Phân tích cấu trúc thư mục chi tiết và xuất báo cáo.

**Tính năng:**
- Phân tích cấu trúc thư mục đến 15 cấp
- Thống kê chi tiết: số file, kích thước, ngày tạo/sửa
- Hiển thị dạng cây phân cấp
- Xuất báo cáo: CSV, JSON, TXT
- Tìm thư mục rỗng và thống kê
- Copy path và mở folder trực tiếp
- Progress tracking cho folder lớn

## 🔧 Cài đặt

### Bước 1: Tạo Virtual Environment

```bash
# Tạo virtual environment trong thư mục project
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Bước 2: Cài đặt Python Dependencies

```bash
# Cài đặt các thư viện Python cần thiết
pip install -r requirements.txt

# Hoặc cài đặt thủ công (nếu requirements.txt không hoạt động)
# Lưu ý: tkinter thường đã có sẵn với Python
```

### Bước 3: Cài đặt FFmpeg (cho Video Thumbnail Generator)

#### Windows:
1. **Tự động bằng Chocolatey:**
   ```bash
   choco install ffmpeg
   ```

2. **Thủ công:**
   - Tải ffmpeg từ: https://ffmpeg.org/download.html
   - Giải nén và thêm vào PATH

#### macOS:
```bash
# Sử dụng Homebrew
brew install ffmpeg
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install ffmpeg
```

### Bước 4: Kiểm tra cài đặt

```bash
# Kiểm tra Python
python --version

# Kiểm tra ffmpeg (cho video thumbnail)
ffmpeg -version
ffprobe -version
```

## 🚀 Sử dụng

### Manga Renamer
```bash
# Kích hoạt virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Chạy chương trình
python manga_renamer.py
```

**Cách dùng:**
1. Click "Browse" và chọn thư mục chứa các folder manga
2. Click "Preview" để xem trước kết quả rename
3. Click "Start Rename" để thực hiện đổi tên
4. Click "Move All" hoặc "Copy All" để tổng hợp file

### Video Thumbnail Generator
```bash
# Kích hoạt virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Chạy chương trình
python video_thumbnail_generator.py
```

**Cách dùng:**
1. Click "Browse" và chọn thư mục chứa video
2. Điều chỉnh tùy chọn (kích thước, thời gian random...)
3. Chọn vị trí thumbnail: folder .thumbnail hoặc cùng cấp
4. Click "Scan Video" để xem danh sách video
5. Click "Generate Thumbnails" để tạo thumbnail

### Audio Thumbnail Generator

```bash
python audio_thumbnail_generator.py
```

**Cách dùng:**
1. Click "Browse" và chọn thư mục chứa nhạc
2. Điều chỉnh tùy chọn:
   - Bỏ qua file đã có thumbnail
   - Tạo thumbnail đại diện cho folder
   - Chọn vị trí lưu: folder .thumbnail hoặc cùng cấp
3. Click "Scan Audio" để xem danh sách file nhạc
4. Click "Extract Thumbnails" để extract album art

### Advanced Rename Tool

```bash
python advanced_rename_tool.py
```

**Cách dùng:**
1. Click "Browse" và chọn thư mục chứa file cần đổi tên
2. Chọn loại file: Images, Videos, Audio, Documents, All Files
3. Chọn chế độ đổi tên:
   - **Sequential**: Đánh số thứ tự (001, 002...)
   - **Prefix**: Thêm text vào đầu tên
   - **Suffix**: Thêm text vào cuối tên (trước extension)
   - **Replace**: Tìm và thay thế text trong tên
4. Điều chỉnh tùy chọn (format số, giữ tên gốc, reset counter...)
5. Click "Preview" để xem trước kết quả
6. Click "Rename" hoặc "Backup & Rename" để thực hiện

### Folder Analyzer

```bash
python folder_analyzer.py
```

**Cách dùng:**
1. Click "Browse" và chọn thư mục gốc cần phân tích
2. Điều chỉnh tùy chọn:
   - Độ sâu tối đa (1-15 cấp)
   - Thông tin cần thu thập (file count, size, dates, permissions)
   - Định dạng xuất (CSV, JSON, TXT)
3. Click "Analyze" để bắt đầu phân tích
4. Xem kết quả trong cây thư mục và bảng thống kê
5. Click "Export" để xuất báo cáo

## 📁 Cấu trúc thư mục

```
Project_file/
├── venv/                          # Virtual environment (sau khi tạo)
├── manga_renamer.py              # Công cụ đổi tên manga
├── video_thumbnail_generator.py  # Công cụ tạo thumbnail video
├── audio_thumbnail_generator.py  # Công cụ extract thumbnail từ nhạc
├── advanced_rename_tool.py       # Công cụ đổi tên file nâng cao
├── folder_analyzer.py            # Phân tích cấu trúc thư mục
├── requirements.txt              # Danh sách thư viện Python
├── setup.bat                     # Script setup cho Windows
├── setup.sh                      # Script setup cho Unix/macOS
└── README.md                     # File hướng dẫn này
```

## 📋 Yêu cầu hệ thống

- **Python:** 3.7 trở lên
- **OS:** Windows, macOS, Linux
- **GUI:** tkinter (thường có sẵn với Python)
- **FFmpeg:** Cần thiết cho video thumbnail generator

## 🔍 Xử lý lỗi

### Lỗi tkinter không tìm thấy:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter
# hoặc
sudo dnf install python3-tkinter
```

### Lỗi ffmpeg không tìm thấy:
1. Kiểm tra ffmpeg đã cài đặt: `ffmpeg -version`
2. Thêm ffmpeg vào PATH environment
3. Restart terminal/command prompt

### Lỗi permission:
```bash
# Nếu gặp lỗi permission khi tạo virtual environment
python -m venv venv --copies
```

## 🎯 Tính năng nổi bật

### Manga Renamer:
- ✅ Sắp xếp tự nhiên (1, 2, 3, 10, 11...)
- ✅ Reset số đếm cho mỗi manga
- ✅ Format: `001_Chapter-Name.jpg`
- ✅ Move/Copy tất cả vào folder "all"
- ✅ Preview trước khi thực hiện

### Video Thumbnail Generator:
- ✅ Random timestamp thông minh
- ✅ Nhiều kích thước thumbnail
- ✅ Xử lý hàng loạt
- ✅ Bỏ qua file đã tồn tại
- ✅ Log chi tiết quá trình

### Audio Thumbnail Generator:
- ✅ Extract album art từ metadata
- ✅ Hỗ trợ MP3, FLAC, M4A, OGG
- ✅ Tự động nhận diện JPG/PNG
- ✅ Tạo folder thumbnail đại diện
- ✅ Lựa chọn vị trí lưu file

## 🛠️ Troubleshooting

### Virtual Environment không hoạt động:
```bash
# Xóa và tạo lại
rmdir /s venv  # Windows
rm -rf venv    # macOS/Linux

python -m venv venv
```

### Chương trình không chạy:
1. Kiểm tra Python version: `python --version`
2. Kiểm tra virtual environment đã activate
3. Kiểm tra tkinter: `python -c "import tkinter"`

### FFmpeg issues:
1. Tải lại từ official website
2. Kiểm tra PATH environment
3. Restart system sau khi cài đặt

### Lỗi mutagen không tìm thấy:
```bash
# Cài đặt trong virtual environment
pip install mutagen

# Hoặc cài đặt từ requirements.txt
pip install -r requirements.txt
```

## 📝 Ghi chú

- Tất cả dependencies được cài đặt local trong virtual environment
- Không ảnh hưởng đến Python global system
- An toàn và dễ dàng gỡ bỏ
- Có thể copy toàn bộ folder sang máy khác

## 🔄 Cập nhật

Để cập nhật project:
```bash
# Kích hoạt virtual environment
venv\Scripts\activate

# Cập nhật requirements nếu có thay đổi
pip install -r requirements.txt --upgrade
```

## ❓ Hỗ trợ

Nếu gặp vấn đề, hãy kiểm tra:
1. Python version compatibility
2. Virtual environment đã activate
3. FFmpeg đã cài đặt đúng
4. Permissions của thư mục làm việc
