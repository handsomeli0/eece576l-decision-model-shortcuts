#!/usr/bin/env bash
# Is $KEV at the commit this project pins (the third_party/kev submodule)?
set -euo pipefail
source "$(dirname "$0")/env.sh"
want=$(git -C "$PROJ" ls-tree HEAD third_party/kev | awk '{print $3}')
have=$(git -C "$KEV" rev-parse HEAD)
dirty=$(git -C "$KEV" status --porcelain --untracked-files=no | wc -l)
echo "pinned $want"; echo "KEV    $have ($KEV, $dirty modified tracked files)"
[ "$want" = "$have" ] && echo OK || { echo "MISMATCH: check out $want in $KEV or update the submodule" >&2; exit 1; }
