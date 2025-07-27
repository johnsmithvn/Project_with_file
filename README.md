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

**Tính năng:**
- Tự động scan tất cả video trong thư mục và thư mục con
- Tạo thumbnail từ timestamp ngẫu nhiên
- Hỗ trợ nhiều định dạng video: mp4, mkv, avi, mov, wmv, flv, webm, m4v
- Tùy chỉnh kích thước thumbnail
- Bỏ qua file đã có thumbnail
- Giao diện GUI với log chi tiết

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
3. Click "Scan Video" để xem danh sách video
4. Click "Generate Thumbnails" để tạo thumbnail

## 📁 Cấu trúc thư mục

```
Project_file/
├── venv/                          # Virtual environment (sau khi tạo)
├── manga_renamer.py              # Công cụ đổi tên manga
├── video_thumbnail_generator.py  # Công cụ tạo thumbnail video
├── requirements.txt              # Danh sách thư viện Python
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
