$folder = 'C:\Users\joel\Documents\Obsidian Vault\Stabssystem\Rapporter'
$files = Get-ChildItem $folder -Filter '*.md'
foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw -Encoding UTF8
    if ($content -match 'stund:\s*"([^"]+)"') {
        $stund = $Matches[1].Trim()
        $safe = $stund -replace '[\\/:*?"<>|]', ''
        $newName = "$safe.md"
        $newPath = Join-Path $folder $newName
        if ($newPath -ne $f.FullName) {
            Rename-Item -Path $f.FullName -NewName $newName -Force
            Write-Host "$($f.Name) -> $newName"
        }
    }
}
Write-Host 'Klart.'
