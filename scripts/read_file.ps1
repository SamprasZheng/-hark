param(
  [Parameter(Mandatory = $true)]
  [string]$Path
)

$resolved = Resolve-Path -LiteralPath $Path
Get-Content -LiteralPath $resolved -Raw
