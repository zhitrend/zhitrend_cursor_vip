# 檢查是否是通過權限提升啟動的
param(
    [switch]$Elevated
)

# 設置顏色主題
$Theme = @{
    Primary   = 'Cyan'
    Success   = 'Green'
    Warning   = 'Yellow'
    Error     = 'Red'
    Info      = 'White'
}

# ASCII Logo
$Logo = @"
██████╗ ███████╗███████╗███████╗████████╗    ████████╗ ██████╗  ██████╗ ██╗     
██╔══██╗██╔════╝██╔════╝██╔════╝╚══██╔══╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     
██████╔╝█████╗  ███████╗█████╗     ██║          ██║   ██║   ██║██║   ██║██║     
██╔══██╗██╔══╝  ╚════██║██╔══╝     ██║          ██║   ██║   ██║██║   ██║██║     
██║  ██║███████╗███████║███████╗   ██║          ██║   ╚██████╔╝╚██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝   ╚═╝          ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
"@

# 美化輸出函數
function Write-Styled {
    param (
        [string]$Message,
        [string]$Color = $Theme.Info,
        [string]$Prefix = "",
        [switch]$NoNewline
    )
    $emoji = switch ($Color) {
        $Theme.Success { "✅" }
        $Theme.Error   { "❌" }
        $Theme.Warning { "⚠️" }
        default        { "ℹ️" }
    }
    
    $output = if ($Prefix) { "$emoji $Prefix :: $Message" } else { "$emoji $Message" }
    if ($NoNewline) {
        Write-Host $output -ForegroundColor $Color -NoNewline
    } else {
        Write-Host $output -ForegroundColor $Color
    }
}

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-NOT $isAdmin) {
    Write-Styled "需要管理員權限來運行重置工具" -Color $Theme.Warning -Prefix "權限"
    Write-Styled "正在請求管理員權限..." -Color $Theme.Primary -Prefix "提升"
    
    # 顯示操作選項
    Write-Host "`n選擇操作:" -ForegroundColor $Theme.Primary
    Write-Host "1. 請求管理員權限" -ForegroundColor $Theme.Info
    Write-Host "2. 退出程序" -ForegroundColor $Theme.Info
    
    $choice = Read-Host "`n請輸入選項 (1-2)"
    
    if ($choice -ne "1") {
        Write-Styled "操作已取消" -Color $Theme.Warning -Prefix "取消"
        Write-Host "`n按任意鍵退出..." -ForegroundColor $Theme.Info
        $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
        exit
    }
    
    try {
        Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Elevated"
        exit
    }
    catch {
        Write-Styled "無法獲取管理員權限" -Color $Theme.Error -Prefix "錯誤"
        Write-Styled "請以管理員身份運行 PowerShell 後重試" -Color $Theme.Warning -Prefix "提示"
        Write-Host "`n按任意鍵退出..." -ForegroundColor $Theme.Info
        $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
        exit 1
    }
}

# 如果是提升權限後的窗口，等待一下確保窗口可見
if ($Elevated) {
    Start-Sleep -Seconds 1
}

# 獲取版本號函數
function Get-LatestVersion {
    try {
        $latestRelease = Invoke-RestMethod -Uri "https://api.github.com/repos/yeongpin/cursor-free-vip/releases/latest"
        return @{
            Version = $latestRelease.tag_name.TrimStart('v')
            Assets = $latestRelease.assets
        }
    } catch {
        Write-Styled $_.Exception.Message -Color $Theme.Error -Prefix "錯誤"
        throw "無法獲取最新版本信息"
    }
}

# 顯示 Logo
Write-Host $Logo -ForegroundColor $Theme.Primary
$releaseInfo = Get-LatestVersion
$version = $releaseInfo.Version
Write-Host "Version $version" -ForegroundColor $Theme.Info
Write-Host "Created by YeongPin`n" -ForegroundColor $Theme.Info

# 設置 TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# 創建臨時目錄
$TmpDir = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null

# 清理函數
function Cleanup {
    if (Test-Path $TmpDir) {
        Remove-Item -Recurse -Force $TmpDir -ErrorAction SilentlyContinue
    }
}

# 主要執行函數
function Start-ResetTool {
    Write-Styled "開始下載重置工具" -Color $Theme.Primary -Prefix "下載"
    
    try {
        # 獲取最新版本
        Write-Styled "正在檢查最新版本..." -Color $Theme.Primary -Prefix "更新"
        $releaseInfo = Get-LatestVersion
        $version = $releaseInfo.Version
        Write-Styled "找到最新版本: $version" -Color $Theme.Success -Prefix "版本"
        
        # 查找對應的資源
        $asset = $releaseInfo.Assets | Where-Object { $_.name -eq "reset_machine_manual.exe" }
        if (!$asset) {
            Write-Styled "找不到重置工具執行檔" -Color $Theme.Error -Prefix "錯誤"
            throw "找不到對應的執行檔"
        }
        
        # 下載
        Write-Styled "正在下載重置工具..." -Color $Theme.Primary -Prefix "下載"
        $downloadPath = Join-Path $TmpDir "reset_machine_manual.exe"
        Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $downloadPath
        
        # 執行
        Write-Styled "正在啟動重置工具..." -Color $Theme.Primary -Prefix "執行"
        Start-Process -FilePath $downloadPath -Wait
        
        Write-Styled "重置完成！" -Color $Theme.Success -Prefix "完成"
        
    }
    catch {
        Write-Styled $_.Exception.Message -Color $Theme.Error -Prefix "錯誤"
        throw
    }
}

# 執行重置
try {
    Start-ResetTool
}
catch {
    Write-Styled "重置工具執行失敗" -Color $Theme.Error -Prefix "錯誤"
    Write-Styled $_.Exception.Message -Color $Theme.Error
}
finally {
    Cleanup
    Write-Host "`n按任意鍵退出..." -ForegroundColor $Theme.Info
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
} 