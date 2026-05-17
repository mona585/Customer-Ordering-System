# Copy README screenshots from Downloads into docs/screenshots/
$src = "C:\Users\TECHNO\Downloads"
$dst = Join-Path $PSScriptRoot "..\docs\screenshots"
New-Item -ItemType Directory -Force -Path $dst | Out-Null

$files = @(
    "menu.png",
    "product-details.png",
    "cart.png",
    "checkout.png",
    "order-tracking.png",
    "admin-dashboard.png",
    "admin-orders.png",
    "admin-order-detail.png",
    "admin-menu.png",
    "delivery-dashboard.png",
    "profile.png",
    "notifications.png"
)

foreach ($f in $files) {
    $from = Join-Path $src $f
    if (Test-Path -LiteralPath $from) {
        Copy-Item -LiteralPath $from -Destination (Join-Path $dst $f) -Force
        Write-Host "Copied $f"
    } else {
        Write-Warning "Missing: $from"
    }
}

Write-Host "Done. Files in: $dst"
