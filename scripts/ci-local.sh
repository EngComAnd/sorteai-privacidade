#!/usr/bin/env bash
# CI local: mesmas verificações do fluxo "Verificar página". Falhou -> não faça push/PR.
# Uso: scripts/ci-local.sh
set -euo pipefail
root="$(git rev-parse --show-toplevel)"; cd "$root"
# Carimbo consultado pelo guard-git antes de `gh pr create`: "<sha> <pass|fail> <epoch>".
stamp="$(git rev-parse --git-dir)/ci-local-last"
sha="$(git rev-parse HEAD)"
trap 'rc=$?; printf "%s %s %s\n" "$sha" "$([ $rc -eq 0 ] && echo pass || echo fail)" "$(date +%s)" > "$stamp"' EXIT
step() { printf '\n==> %s\n' "$*"; }
step "verificar a página"; python3 scripts/verificar-pagina.py
step "páginas em dia com a fonte"
python3 scripts/gerar-pagina.py >/dev/null
git diff --exit-code -- index.html 404.html privacidade
step "CI local verde"
