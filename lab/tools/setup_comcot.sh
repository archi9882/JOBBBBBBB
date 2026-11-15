#!/usr/bin/env bash
# 下載並編譯 COMCOT（gfortran 版，中央大學 IHOS 海嘯研究群），放在 lab/vendor/comcot-gfortran/comcot
# 用法：bash lab/tools/setup_comcot.sh
set -euo pipefail
cd "$(dirname "$0")/.."
command -v gfortran >/dev/null || { echo "缺 gfortran：sudo apt install gfortran"; exit 1; }
mkdir -p vendor
[ -d vendor/comcot-gfortran ] || git clone --depth 1 https://github.com/HandsomeAndy/comcot-gfortran.git vendor/comcot-gfortran
cd vendor/comcot-gfortran
make clean >/dev/null 2>&1 || true
# 新版 gfortran（10 以上）預設把引數型別不符當成錯誤；原始碼是舊式寫法，需要這個旗標
make FC_FLAGS="-O2 -fallow-argument-mismatch" >/dev/null
echo "OK：$(pwd)/comcot"
