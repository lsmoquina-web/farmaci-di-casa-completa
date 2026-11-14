$ErrorActionPreference = "Stop"
$dest = Join-Path $PSScriptRoot "farmaci-debug.keystore"
$keytool = Get-Command keytool -ErrorAction SilentlyContinue
if (-not $keytool) {
    $bundled = "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe"
    if (Test-Path $bundled) { $keytool = Get-Item $bundled } else { throw "keytool non trovato: installa Java 17 o Android Studio." }
}
$exe = if ($keytool.Source) { $keytool.Source } else { $keytool.FullName }
if (-not (Test-Path $dest)) {
 & $exe -genkeypair -v -keystore $dest -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Farmaci di casa, O=Uso personale, C=IT"
 if ($LASTEXITCODE -ne 0) { throw "Creazione chiave non riuscita" }
}
[Convert]::ToBase64String([IO.File]::ReadAllBytes($dest)) | Set-Clipboard
Write-Host "Chiave codificata copiata negli appunti. Incollala nel secret GitHub ANDROID_KEYSTORE_BASE64."
Write-Host "Conserva il file keystore in luogo sicuro. Non caricarlo nel repository."
