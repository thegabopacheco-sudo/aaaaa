# build.ps1
param (
    [string]$Config = "Release",
    [string]$TargetProcess = "FiveM.exe"
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "[*] Matando inyector anterior..." -ForegroundColor Cyan
cmd /c "taskkill /F /IM injector.exe /T >nul 2>&1"

Write-Host "[*] Limpiando DLL anterior..." -ForegroundColor Cyan
$DllPath = Join-Path $ProjectRoot "build\$Config\fivem_cheat.dll"
if (Test-Path $DllPath) {
    Remove-Item $DllPath -Force -ErrorAction SilentlyContinue
}

# Verificar si hay que configurar CMake (si la carpeta build no existe o está vacía)
$CMakeCache = Join-Path $ProjectRoot "build\CMakeCache.txt"
if (-not (Test-Path $CMakeCache)) {
    Write-Host "[*] Configurando CMake (primera vez o cache borrada)..." -ForegroundColor Cyan
    cmake -B build -A x64
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Error en la configuración de CMake. Abortando." -ForegroundColor Red
        exit 1
    }
}

Write-Host "[*] Compilando..." -ForegroundColor Cyan
cmake --build build --config $Config

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Error en la compilación. Abortando." -ForegroundColor Red
    exit 1
}

Write-Host "[*] Compilación exitosa." -ForegroundColor Green

$proc = Get-Process -Name $TargetProcess -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "[*] Inyectando en $TargetProcess (PID: $($proc.Id))..." -ForegroundColor Yellow
    $InjectorPath = Join-Path $ProjectRoot "build\$Config\injector.exe"
    if (Test-Path $InjectorPath) {
        & $InjectorPath $DllPath
        Write-Host "[*] Inyección completada. Dale a ENTER en el juego." -ForegroundColor Green
    } else {
        Write-Host "[!] No se encontró injector.exe en build\$Config\" -ForegroundColor Red
    }
} else {
    Write-Host "[!] $TargetProcess no está corriendo. Inicia el juego y ejecuta el inyector manualmente." -ForegroundColor Red
}