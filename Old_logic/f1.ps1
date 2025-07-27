Add-Type -AssemblyName System.Windows.Forms

$folderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
$folderBrowser.Description = "Select a folder"

if ($folderBrowser.ShowDialog() -eq "OK") {
    $selectedFolder = $folderBrowser.SelectedPath

    if (-not [string]::IsNullOrEmpty($selectedFolder)) {
        try {
            $filesFound = Get-ChildItem -Path $selectedFolder -Filter "*.webp" -File -Recurse -ErrorAction SilentlyContinue
            $fileCount = $filesFound.Count

            $foldersWithFiles = [System.Collections.Generic.HashSet[string]]::new()
            foreach ($file in $filesFound) {
                [void]$foldersWithFiles.Add((Split-Path $file.FullName)) # ĐÃ SỬA LỖI
            }
            $foldersWithFileCount = $foldersWithFiles.Count

            $allFolders = Get-ChildItem -Path $selectedFolder -Directory -Recurse -ErrorAction SilentlyContinue
            $allFolderCount = $allFolders.Count

            if ($fileCount -gt 0) {
                $filesFound | ForEach-Object { Write-Host $_.FullName }
                Write-Host ""
                Write-Host "Found $foldersWithFileCount subfolder(s) containing .webp files."
                Write-Host "Found $allFolderCount total subfolder(s) in '$selectedFolder'."
                Write-Host "Found $fileCount .webp file(s) in '$selectedFolder' and its subfolders:" # ĐÃ CHUYỂN XUỐNG CUỐI
            } else {
                Write-Host "No .webp files were found in '$selectedFolder' and its subfolders."
                Write-Host "Found $allFolderCount total subfolder(s) in '$selectedFolder'."
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