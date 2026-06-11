# =============================================================
#  물리보안 연동성 검증 도구 — 빌드 스크립트
#  사용법: 프로젝트 루트에서  .\build.ps1
#  동작:
#    1) 오늘 날짜(MMdd) 폴더를 dist 아래에 생성  (예: dist\0611)
#    2) console 버전 onefile exe 빌드
#    3) 산출물: dist\<MMdd>\물리보안 연동성 검증 도구.exe
# =============================================================

$ErrorActionPreference = "Stop"

# 스크립트 위치(프로젝트 루트)로 이동 — 어디서 실행하든 동일하게 동작
Set-Location -Path $PSScriptRoot

# 빌드 요청 시점의 날짜로 폴더명 결정 (MMdd)
$date = Get-Date -Format "MMdd"
$dist = Join-Path "dist" $date
$work = Join-Path $dist "build"

Write-Host "[빌드 시작] 날짜 폴더: $dist (console 버전)"

& ".venv\Scripts\pyinstaller.exe" "ValidationTool_onefile_Level1.spec" `
    --distpath $dist --workpath $work --noconfirm

$exe = Join-Path $dist "물리보안 연동성 검증 도구.exe"
if (Test-Path $exe) {
    $mb = [math]::Round((Get-Item $exe).Length / 1MB, 1)
    Write-Host "[빌드 완료] $exe ($mb MB)"
} else {
    Write-Host "[경고] 예상 산출물을 찾지 못했습니다: $exe"
}
