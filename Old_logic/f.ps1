Add-Type -AssemblyName System.Windows.Forms

$folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
$folderBrowser.Description = "Select a folder"

if ($folderBrowser.ShowDialog() -eq "OK") {
    $selectedFolder = $folderBrowser.SelectedPath

    if (-not [string]::IsNullOrEmpty($selectedFolder)) {
        try {
            $foldersWithWebp = @{}

            Get-ChildItem -Path "$($selectedFolder)" -Filter "*.css" -File -Recurse | ForEach-Object {
                $folderPath = Split-Path $_.FullName
                $foldersWithWebp[$folderPath] = $true
            }

            $count = $foldersWithWebp.Count

            if ($count -gt 0) {
                # In danh sách thư mục trước
                $foldersWithWebp.Keys | Sort-Object | ForEach-Object { Write-Host $_ }

                # In số đếm xuống cuối cùng
                Write-Host "Found $count folders containing .txt files in '$selectedFolder' and its subfolders."
            } else {
                Write-Host "No .txt files found in '$selectedFolder' and its subfolders."
            }

        } catch {
            Write-Error "An error occurred: $($_.Exception.Message)"
        }
    } else {
        Write-Host "Please select a folder."
    }
} else {
    Write-Host "You cancelled the folder selection."
}