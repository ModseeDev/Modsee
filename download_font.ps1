# PowerShell script to download Roboto Regular font
$fontUrl = "https://github.com/openmaptiles/fonts/raw/master/roboto/Roboto-Regular.ttf"
$outputDir = "resources\fonts"
$outputFile = Join-Path -Path $outputDir -ChildPath "Roboto-Regular.ttf"

# Create directory if it doesn't exist
if (-not (Test-Path -Path $outputDir)) {
    New-Item -Path $outputDir -ItemType Directory -Force
}

Write-Host "Downloading Roboto-Regular.ttf from $fontUrl..."

try {
    # Download the font file
    Invoke-WebRequest -Uri $fontUrl -OutFile $outputFile
    
    if (Test-Path -Path $outputFile) {
        Write-Host "Font downloaded successfully to $outputFile"
    } else {
        Write-Host "Error: Font download failed"
    }
} catch {
    Write-Host "Error downloading font: $_"
} 