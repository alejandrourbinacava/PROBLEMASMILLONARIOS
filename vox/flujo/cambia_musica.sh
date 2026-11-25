#!/bin/bash
# cambia_musica.sh <tema> <CARPETA> <base> [sufijo]: rehace la mezcla con la musica actual y la mete en los mp4 sin tocar la imagen
B="C:/Users/aleja/Desktop/PROBLEMAS MILLONARIOS"; cd "$B/repo" || exit 1
python vox/sonido.py "$B/$2/voz.wav" "vox/$1.spec.json" "vox/$1.audio.mp3" | tail -1 || exit 1
for q in 1080p 720p; do
  f="$B/$2/$3_$q.mp4"; t="$B/$2/_tmp_$q.mp4"; d="$B/$2/$3${4}_$q.mp4"; br=192k; [ $q = 720p ] && br=128k
  ffmpeg -y -v error -i "$f" -i "vox/$1.audio.mp3" -map 0:v -map 1:a -c:v copy -c:a aac -b:a $br -movflags +faststart "$t" || { echo "FALLO $f"; rm -f "$t"; exit 2; }
  a=$(ffprobe -v error -select_streams v -show_entries stream=nb_frames,duration -of csv=p=0 "$f"); b=$(ffprobe -v error -select_streams v -show_entries stream=nb_frames,duration -of csv=p=0 "$t")
  [ "$a" = "$b" ] && mv -f "$t" "$d" && echo "ok $d video $b audio $(ffprobe -v error -select_streams a -show_entries stream=duration -of csv=p=0 "$d")" || { echo "DISTINTO $f $a / $b"; exit 3; }
done
