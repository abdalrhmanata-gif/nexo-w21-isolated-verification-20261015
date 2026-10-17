# Run the pinned 13-query Development-only read-only audit.
# The token is requested as a SecureString, never echoed, and removed from this process environment.
$ErrorActionPreference = "Stop"

$runner = Join-Path (Get-Location) "tools/supabase_readonly_migration_effect_audit.py"
$reviewer = Join-Path (Get-Location) "tools/review_hosted_migration_ledger.py"
if (-not (Test-Path $runner) -or -not (Test-Path $reviewer)) {
    throw "Run this script from the root of the isolated ZAVQERA audit repository."
}

Write-Host "Checking the pinned SQL pack locally (no network request)..."
& py -3 $runner --self-test
if ($LASTEXITCODE -ne 0) {
    throw "Audit self-test failed. No token was requested and no hosted query was sent."
}

$env:SUPABASE_PROJECT_REF = "mrwmmbytcymqgwvcoywd"
$env:ZAVQERA_AUDIT_CONFIRMATION = "DEVELOPMENT_ONLY_READ_ONLY"
$secureToken = $null
$tokenPointer = [IntPtr]::Zero
$evidenceZip = $null

try {
    $secureToken = Read-Host "Enter the scoped read-only Supabase Management API token (input hidden)" -AsSecureString
    if ($null -eq $secureToken -or $secureToken.Length -eq 0) {
        throw "No token entered."
    }
    $tokenPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    $env:SUPABASE_ACCESS_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($tokenPointer)

    Write-Host "Running the pinned 13-query read-only Development capture..."
    $captureOutput = & py -3 $runner 2>&1
    $captureExitCode = $LASTEXITCODE

    # The offline reviewer must not inherit the Management API token.
    Remove-Item Env:\SUPABASE_ACCESS_TOKEN -ErrorAction SilentlyContinue
    if ($tokenPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenPointer)
        $tokenPointer = [IntPtr]::Zero
    }
    if ($null -ne $secureToken) {
        $secureToken.Dispose()
        $secureToken = $null
    }

    $captureOutput | ForEach-Object { Write-Output $_ }
    $match = [regex]::Match(($captureOutput -join [Environment]::NewLine), "(?m)^Evidence: (.+)$")
    if ($match.Success) {
        $auditDir = $match.Groups[1].Value.Trim()
    }

    if ($captureExitCode -ne 0) {
        if ($match.Success -and (Test-Path $auditDir)) {
            $evidenceZip = "$($auditDir).zip"
            Compress-Archive -Path (Join-Path $auditDir "*") -DestinationPath $evidenceZip -CompressionLevel Optimal
            Write-Host "Partial evidence ZIP: $evidenceZip"
        }
        throw "Read-only capture stopped with exit code $captureExitCode. Review the BLOCKED stage; do not retry by changing the SQL or role gate."
    }
    if (-not $match.Success) {
        throw "Capture completed but did not report its evidence folder. Inspect the output above."
    }

    Write-Host "Running the offline reviewer against this exact source checkout..."
    & py -3 $reviewer --evidence-dir $auditDir
    $reviewExitCode = $LASTEXITCODE
    if ($reviewExitCode -ne 0) {
        Write-Warning "Offline reviewer returned $reviewExitCode. Preserve the evidence for review; do not apply hosted changes."
    }

    $evidenceZip = "$($auditDir).zip"
    if (Test-Path $evidenceZip) {
        Remove-Item -LiteralPath $evidenceZip -Force
    }
    Compress-Archive -Path (Join-Path $auditDir "*") -DestinationPath $evidenceZip -CompressionLevel Optimal
    Write-Host "Evidence ZIP: $evidenceZip"
    Write-Host "Upload this ZIP for offline review. Never upload or paste the token."
    Write-Host "A successful capture is not a release approval; inherited ACLs or migration mismatches keep the release NO-GO."
}
finally {
    Remove-Item Env:\SUPABASE_ACCESS_TOKEN -ErrorAction SilentlyContinue
    Remove-Item Env:\SUPABASE_PROJECT_REF -ErrorAction SilentlyContinue
    Remove-Item Env:\ZAVQERA_AUDIT_CONFIRMATION -ErrorAction SilentlyContinue
    if ($tokenPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenPointer)
    }
    if ($null -ne $secureToken) {
        $secureToken.Dispose()
    }
}
