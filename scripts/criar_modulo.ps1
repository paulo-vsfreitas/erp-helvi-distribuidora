param(
    [Parameter(Mandatory = $true)]
    [string]$Modulo
)

Write-Host ""
Write-Host "====================================="
Write-Host " Criando módulo: $Modulo"
Write-Host "====================================="
Write-Host ""

$base = ".\$Modulo"

# Pastas
$pastas = @(
    "$base\services",
    "$base\utils",
    "$base\views",
    "$base\templates\$Modulo"
)

foreach ($pasta in $pastas) {
    New-Item $pasta -ItemType Directory -Force | Out-Null
}

# Arquivos
$arquivos = @(
    "$base\forms.py",
    "$base\urls.py",
    "$base\views\__init__.py",
    "$base\views\$Modulo.py",
    "$base\services\__init__.py",
    "$base\utils\__init__.py",
    "$base\templates\$Modulo\lista_$Modulo.html",
    "$base\templates\$Modulo\form_$Modulo.html"
)

foreach ($arquivo in $arquivos) {
    if (!(Test-Path $arquivo)) {
        New-Item $arquivo -ItemType File | Out-Null
    }
}

Write-Host ""
Write-Host "✅ Estrutura criada com sucesso!"
Write-Host ""