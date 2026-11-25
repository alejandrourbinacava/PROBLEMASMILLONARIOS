#!/bin/bash
# sube.sh <tema> <n> "<mensaje>"
cd "C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS/repo" || exit 1
T=$1
F="vox/$T.py vox/$T.spec.json vox/$T.audio.mp3 vox/$T.locucion.txt vox/$T.voz.json vox/$T.media.json config/guion_$T.md vox/media/$T $4"
git add $F || exit 1
git diff --cached -U0 | grep -aEi '(sk-[A-Za-z0-9]{16}|AIza[0-9A-Za-z_-]{30}|ghp_[A-Za-z0-9]{30}|xox[bp]-|-----BEGIN|api[_-]?key["'"'"' ]*[:=] *["'"'"'][A-Za-z0-9]{16})' && { echo POSIBLE CREDENCIAL; git reset -q; exit 2; }
git diff --cached --stat | tail -3
git commit -q -m "$3

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q origin HEAD && git tag "mod-$T-$2" && git push -q origin "mod-$T-$2" && echo SUBIDO "mod-$T-$2"
