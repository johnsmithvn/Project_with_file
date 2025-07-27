$videoExtensions = @("*.mp4", "*.mkv", "*.avi", "*.mov")

foreach ($ext in $videoExtensions) {
    Get-ChildItem -Recurse -Include $ext -File | ForEach-Object {
        $video = $_.FullName
        $thumb = [System.IO.Path]::ChangeExtension($video, ".jpg")

        if (-not (Test-Path $thumb)) {
            Write-Host "Generating thumbnail for: $video"

            # Lấy độ dài video bằng ffprobe
            $duration = & ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video"

            if ($duration -match '^[\d\.]+$') {
                $duration = [math]::Floor([double]::Parse($duration))

                # Random từ 2s đến (duration - 2)
                if ($duration -gt 4) {
                    $randSec = Get-Random -Minimum 2 -Maximum ($duration - 2)
                } else {
                    $randSec = 1
                }

                Write-Host ("Using random second: {0}s" -f $randSec)

                # Chú ý: -ss phải đặt trước -i nếu muốn input seeking
                & ffmpeg -y -ss $randSec -i "$video" -vframes 1 -vf "scale=480:-1" "$thumb"
            } else {
                Write-Host "⚠️  Skipping: could not get video duration"
            }
        } else {
            Write-Host "✅ Skipped (already exists): $thumb"
        }
    }
}
