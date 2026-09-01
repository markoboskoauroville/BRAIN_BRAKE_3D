#!/usr/bin/env bash
# Where has the 3D session got to?
#
#     bash tools/check_3d_session.sh
#
# This repository is written by the Claude Code session working in
# ~/Developer/KEY_3D on the Mac. It reports into EXCHANGE_3D.md here rather than
# into MANTRA_MANIFEST/EXCHANGE.md, because two sessions writing one file
# produce a merge conflict in the thing everybody depends on. Two files, two
# directions, no shared lines.
#
# The script pulls this repository and prints the status. It is for the chat
# session and for Baba. The session that writes EXCHANGE_3D.md does not need it.
set -u
D="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
git -C "$D" pull -q --rebase origin main 2>/dev/null

if [ -f "$D/EXCHANGE_3D.md" ]; then
  sed -n '1,80p' "$D/EXCHANGE_3D.md"
else
  echo "EXCHANGE_3D.md not written yet. Recent commits:"
  git -C "$D" log --oneline -6 --pretty="  %h %ad | %s" --date=format:'%d/%m %H:%M'
fi

echo
echo "--- what is in the repository ---"
for d in mesh scripts stills tools; do
  [ -d "$D/$d" ] && printf '  %-10s %s files\n' "$d" "$(ls -1 "$D/$d" 2>/dev/null | wc -l | tr -d ' ')"
done
printf '  %-10s %s\n' "size" "$(du -sh --exclude=.git "$D" 2>/dev/null | cut -f1)"
