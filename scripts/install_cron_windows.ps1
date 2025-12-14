# Script PowerShell pour configurer le Task Scheduler Windows
# Exécutez ce script en tant qu'administrateur pour configurer automatiquement le cron job

# Vérifier les privilèges administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ Ce script doit être exécuté en tant qu'administrateur." -ForegroundColor Red
    Write-Host "Faites un clic droit sur PowerShell et sélectionnez 'Exécuter en tant qu'administrateur'" -ForegroundColor Yellow
    exit 1
}

# Obtenir le répertoire du script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$BatchScript = Join-Path $ScriptDir "verifier_rappels.bat"

# Vérifier que le script batch existe
if (-not (Test-Path $BatchScript)) {
    Write-Host "❌ Le script batch verifier_rappels.bat est introuvable." -ForegroundColor Red
    Write-Host "Chemin attendu: $BatchScript" -ForegroundColor Yellow
    exit 1
}

# Nom de la tâche
$TaskName = "KeyPer-VerifierRappels"

# Supprimer la tâche existante si elle existe
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "⚠️  Suppression de la tâche existante..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Créer l'action (exécuter le script batch)
$Action = New-ScheduledTaskAction -Execute $BatchScript -WorkingDirectory $ProjectDir

# Créer le déclencheur (quotidien à 8h00)
$Trigger = New-ScheduledTaskTrigger -Daily -At "08:00"

# Créer les paramètres de la tâche
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Créer le principal (exécuter même si l'utilisateur n'est pas connecté)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Highest

# Enregistrer la tâche
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Vérifie les rappels automatiques des tâches KeyPer quotidiennement à 8h00"
    Write-Host "✅ Tâche planifiée créée avec succès !" -ForegroundColor Green
    Write-Host "   Nom de la tâche: $TaskName" -ForegroundColor Cyan
    Write-Host "   Horaire: Tous les jours à 8h00" -ForegroundColor Cyan
    Write-Host "   Script: $BatchScript" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pour vérifier la tâche, ouvrez le Planificateur de tâches Windows et cherchez '$TaskName'" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Erreur lors de la création de la tâche: $_" -ForegroundColor Red
    exit 1
}

