# Installateur de l'enregistreur Myfxbook. Lance par installer_enregistreur_windows.bat (double-clic).
# Fichier enregistre en UTF-8 avec BOM pour que PowerShell 5.1 lise les accents.
#
# Ce que fait ce script, dans l'ordre :
#   1. trouve Python 3 ;
#   2. copie l'enregistreur dans %USERPROFILE%\RocBOTT_enregistreur ;
#   3. demande email + mot de passe Myfxbook, puis les chemins de copie (NAS, OneDrive), UNE fois,
#      et ecrit %USERPROFILE%\.rocbott\myfxbook.ini (hors depot, lisible par toi seul) ;
#   4. teste l'ecriture dans chaque destination ;
#   5. fait une premiere interrogation de test et l'affiche en clair ;
#   6. cree la tache planifiee « RocBOTT Enregistreur Myfxbook » (une interrogation toutes les 15 min).

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$env:PYTHONIOENCODING = 'utf-8'

$NomTache   = 'RocBOTT Enregistreur Myfxbook'
$DossierApp = Join-Path $env:USERPROFILE 'RocBOTT_enregistreur'
$DossierCfg = Join-Path $env:USERPROFILE '.rocbott'
$Ini        = Join-Path $DossierCfg 'myfxbook.ini'
$Donnees    = Join-Path $env:USERPROFILE 'RocBOTT_donnees\myfxbook'
$Source     = Join-Path $PSScriptRoot 'enregistreur_myfxbook.py'
$Script     = Join-Path $DossierApp 'enregistreur_myfxbook.py'

function Dire($t, $c = 'White') { Write-Host $t -ForegroundColor $c }

function Trouver-Python {
    $candidats = @(@('py', '-3'), @('python'), @('python3'))
    foreach ($c in $candidats) {
        try {
            $exe = $c[0]
            $args2 = @()
            if ($c.Count -gt 1) { $args2 = $c[1..($c.Count - 1)] }
            $sortie = & $exe @args2 -c "import sys; print(sys.executable); print(sys.version_info[0]*100+sys.version_info[1])" 2>$null
            if ($LASTEXITCODE -eq 0 -and $sortie.Count -ge 2 -and [int]$sortie[1] -ge 308 -and (Test-Path $sortie[0])) {
                return $sortie[0]
            }
        } catch {}
    }
    return $null
}

function Lire-Ini($chemin) {
    $h = @{}
    if (Test-Path $chemin) {
        foreach ($l in Get-Content $chemin -Encoding UTF8) {
            if ($l -match '^\s*([A-Za-z_]+)\s*=\s*(.*)$') { $h[$matches[1].ToLower()] = $matches[2].Trim() }
        }
    }
    return $h
}

function Demander($question, $defaut) {
    if ($defaut) { $r = Read-Host "$question [Entrée = $defaut]" } else { $r = Read-Host "$question [Entrée = aucun]" }
    $r = $r.Trim().Trim('"')
    if ($r -eq '') { return $defaut }
    if ($r -eq '-') { return '' }
    return $r
}

function Ecrire-Ini($email, $mdp, $nas, $onedrive) {
    New-Item -ItemType Directory -Force -Path $DossierCfg | Out-Null
    $txt = "[myfxbook]`r`nemail = $email`r`npassword = $mdp`r`ncopie_nas = $nas`r`ncopie_onedrive = $onedrive`r`n"
    [System.IO.File]::WriteAllText($Ini, $txt, (New-Object System.Text.UTF8Encoding($false)))
    # lisible et modifiable par ton compte seulement
    try { & icacls.exe $Ini /inheritance:r /grant:r "$($env:USERNAME):(R,W)" | Out-Null } catch {}
}

function Lire-MotDePasse {
    $s = Read-Host 'Mot de passe Myfxbook (rien ne s''affiche pendant la frappe, c''est normal)' -AsSecureString
    $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)
    try { return [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) }
    finally { [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
}

try {
    Dire '=== Installation de l''enregistreur Myfxbook ===' Cyan
    Dire ''

    # 1. Python
    $py = Trouver-Python
    if (-not $py) {
        Dire 'Python 3 est introuvable sur ce PC. C''est la seule chose à installer.' Red
        Dire '  1. Va sur https://www.python.org/downloads/ et télécharge Python 3.' Yellow
        Dire '  2. Lance l''installation et COCHE la case « Add python.exe to PATH » en bas de la première fenêtre.' Yellow
        Dire '  3. Quand c''est fini, double-clique de nouveau sur installer_enregistreur_windows.bat.' Yellow
        return
    }
    Dire "Python trouvé : $py" Green
    $pyw = Join-Path (Split-Path $py) 'pythonw.exe'
    if (-not (Test-Path $pyw)) { $pyw = $py }   # pythonw : pas de fenêtre noire toutes les 15 minutes

    # 2. Copie de l'enregistreur hors du dépôt (la tâche ne dépend pas de l'endroit où le dépôt se trouve)
    if (-not (Test-Path $Source)) { throw "Fichier introuvable : $Source" }
    New-Item -ItemType Directory -Force -Path $DossierApp | Out-Null
    Copy-Item $Source $Script -Force
    Dire "Enregistreur copié dans : $DossierApp" Green

    # 3. Identifiants et destinations de copie
    $cfg = Lire-Ini $Ini
    $email = $cfg['email']; $mdp = $cfg['password']
    $nas = $cfg['copie_nas']; $onedrive = $cfg['copie_onedrive']
    $redemander = $true
    if ($email -and $mdp) {
        Dire ''
        $r = Read-Host "Des identifiants Myfxbook sont déjà enregistrés pour $email. Les garder ? [O/n]"
        if ($r -notmatch '^[nN]') { $redemander = $false }
    }

    if (-not $cfg.ContainsKey('copie_onedrive') -or -not $cfg['copie_onedrive']) {
        $racineOD = $env:OneDrive
        if (-not $racineOD) { $racineOD = $env:OneDriveConsumer }
        if (-not $racineOD) { $racineOD = $env:OneDriveCommercial }
        if ($racineOD) { $onedrive = Join-Path $racineOD 'RocBOTT_donnees\myfxbook' }
    }
    Dire ''
    Dire 'Copies de sauvegarde. L''enregistrement se fait toujours sur le disque local ; seuls les jours terminés sont copiés.' Cyan
    $onedrive = Demander 'Dossier OneDrive pour les copies (tape - pour ne pas en utiliser)' $onedrive
    $nas = Demander 'Dossier du NAS pour les copies, par exemple \\NAS\partage\RocBOTT_donnees\myfxbook (tape - pour ne pas en utiliser)' $nas

    $tentative = 0
    while ($true) {
        $tentative++
        if ($redemander) {
            Dire ''
            $email = (Read-Host 'Email du compte Myfxbook').Trim()
            $mdp = Lire-MotDePasse
            $redemander = $false
        }
        Ecrire-Ini $email $mdp $nas $onedrive
        Dire "Identifiants écrits dans $Ini (hors dépôt, jamais envoyés nulle part ailleurs qu'à myfxbook.com)." Green

        # 4. Test des destinations
        Dire ''
        Dire 'Test des dossiers de copie :' Cyan
        & $py $Script --tester-copies

        # 5. Première interrogation, en clair
        Dire ''
        Dire 'Première interrogation de Myfxbook (test) :' Cyan
        & $py $Script --une-fois
        $code = $LASTEXITCODE
        if ($code -eq 0) { break }
        if (($code -eq 4 -or $code -eq 2) -and $tentative -lt 3) {
            Dire ''
            Dire 'Myfxbook a refusé la connexion (email ou mot de passe ?). On réessaie.' Yellow
            $redemander = $true
            continue
        }
        break
    }
    if ($code -eq 4 -or $code -eq 2) {
        Dire ''
        Dire 'La connexion à Myfxbook ne marche toujours pas : la tâche planifiée n''est pas créée. Relance l''installateur quand tu as vérifié le compte.' Red
        return
    }
    if ($code -ne 0) {
        Dire ''
        Dire 'Le test a échoué (voir le message ci-dessus ; internet coupé ?). L''échec est enregistré comme les autres. La tâche va quand même être créée : elle réessaiera toutes les 15 minutes.' Yellow
    }

    # 6. Tâche planifiée : une interrogation puis sortie, toutes les 15 minutes
    Dire ''
    Dire 'Création de la tâche planifiée Windows...' Cyan
    $arguments = '"' + $Script + '" --une-fois --respecter-cadence'
    $cree = $false
    try {
        $action = New-ScheduledTaskAction -Execute $pyw -Argument $arguments -WorkingDirectory $DossierApp
        $t1 = New-ScheduledTaskTrigger -Once -At ((Get-Date).Date) -RepetitionInterval (New-TimeSpan -Minutes 15)
        $t2 = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
        $reglages = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew `
            -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
        $princ = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive
        Register-ScheduledTask -TaskName $NomTache -Action $action -Trigger @($t1, $t2) -Settings $reglages `
            -Principal $princ -Description 'RocBOTT : enregistre le positionnement Myfxbook toutes les 15 minutes' -Force | Out-Null
        $cree = $true
    } catch {
        Dire "Méthode principale refusée ($($_.Exception.Message)). Essai avec schtasks..." Yellow
    }
    if (-not $cree) {
        $tr = '"' + $pyw + '" ' + $arguments
        & schtasks.exe /Create /TN $NomTache /SC MINUTE /MO 15 /TR $tr /F | Out-Null
        if ($LASTEXITCODE -ne 0) { throw 'Impossible de créer la tâche planifiée (schtasks a échoué).' }
        $cree = $true
    }
    $info = Get-ScheduledTaskInfo -TaskName $NomTache -ErrorAction SilentlyContinue
    $tache = Get-ScheduledTask -TaskName $NomTache -ErrorAction SilentlyContinue
    if ($tache) { Dire "Tâche « $NomTache » : état $($tache.State)." Green }

    Dire ''
    Dire '=== C''est installé ===' Green
    Dire "Les données s'accumulent ici : $Donnees" White
    # Raccourci « état » : un double-clic affiche en une ligne si ça tourne
    $contenuEtat = "@echo off`r`n`"$py`" `"$Script`" --etat`r`necho.`r`npause`r`n"
    $fichiersEtat = @((Join-Path $DossierApp 'Etat enregistreur Myfxbook.bat'))
    try { $fichiersEtat += (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Etat enregistreur Myfxbook.bat') } catch {}
    foreach ($f in $fichiersEtat) {
        try { [System.IO.File]::WriteAllText($f, $contenuEtat, (New-Object System.Text.UTF8Encoding($false))) } catch {}
    }
    Dire 'Pour vérifier que ça tourne, à tout moment : double-clique sur « Etat enregistreur Myfxbook » (sur le Bureau).' White
    Dire '  Le PC doit être allumé pour enregistrer. Chaque période éteinte est un trou définitif (il est visible dans les heures).' Yellow
    & $py $Script --etat
} catch {
    Dire ''
    Dire "Une erreur est survenue : $($_.Exception.Message)" Red
    Dire 'Rien n''est cassé. Envoie une capture de cet écran.' Red
}
