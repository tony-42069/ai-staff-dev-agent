param(
    [Parameter(Mandatory=$true)]
    [string]$Operation,
    
    [Parameter(Mandatory=$true)]
    [string]$Target,
    
    [Parameter(Mandatory=$false)]
    [string]$Data
)

# Set environment
$env:PYTHONPATH = "$PSScriptRoot;$env:PYTHONPATH"

# Build command
$cmd = "python private/config/templates/manage_config.py $Operation $Target"
if ($Data) {
    $cmd += " '$Data'"
}

# Execute
Invoke-Expression $cmd
