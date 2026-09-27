#!/usr/bin/env bash
# Builds web-ready assets in ./assets from the raw material in ./static.
# ./static is NOT committed (see .gitignore): it holds a 100 MB+ video,
# print-resolution scans, and folders named after participants.
#
# Usage:  ./build_assets.sh            # everything
#         SKIP_VIDEO=1 ./build_assets.sh   # images only
set -euo pipefail
cd "$(dirname "$0")"

# 1. Main video: H.264 720p, ~14 MB instead of 102 MB, plus a poster frame.
if [[ -z "${SKIP_VIDEO:-}" ]]; then
  mkdir -p assets/video
  ffmpeg -y -loglevel error -i static/iros-painting-robot.mp4 \
    -c:v libx264 -preset slow -crf 28 -pix_fmt yuv420p -vf "scale=1280:-2" \
    -movflags +faststart -c:a aac -b:a 96k \
    assets/video/iros-painting-robot.mp4
fi
mkdir -p assets/video
ffmpeg -y -loglevel error -ss 3 -i static/iros-painting-robot.mp4 \
  -frames:v 1 -vf "scale=1280:-2" -q:v 3 assets/video/poster.jpg

# 2. In-person drawings: shrink scans to 1600 px on the long edge.
rm -rf assets/in-person && mkdir -p assets/in-person
for f in static/in-person/*.jpg; do
  sips -Z 1600 -s format jpeg -s formatOptions 85 "$f" \
    --out "assets/in-person/$(basename "$f")" >/dev/null
done

# 3. Online drawings: only the final robot turn (turn_2_robot.png),
#    renumbered so participant names never appear in the public repo.
for cond in adversarial control; do
  rm -rf "assets/online/$cond" && mkdir -p "assets/online/$cond"
  i=0
  while IFS= read -r -d '' f; do
    i=$((i + 1))
    nn=$(printf '%02d' "$i")
    cp "$f" "assets/online/$cond/$nn.png"
    # Progression frames from raw/: participant strokes blue, agent strokes red.
    mkdir -p "assets/online/$cond/$nn"
    for t in 0 1 2; do
      for who in human robot; do
        cp "$(dirname "$f")/raw/turn_${t}_${who}.png" "assets/online/$cond/$nn/turn_${t}_${who}.png"
      done
    done
  done < <(find "static/online" -path "*/${cond}_*" -name turn_2_robot.png \
             -not -path "*/raw/*" -print0 | sort -z)
  echo "$cond: $i drawings"
done

echo "in-person: $(ls assets/in-person | wc -l | tr -d ' ') drawings"

# 4. Prompt-design grid: 3x3 (visual x semantic) final robot turn per
#    participant, renumbered p1..pN in folder order.
rm -rf assets/grid && mkdir -p assets/grid
n=0
for d in $(ls static/grid | grep -E '^[0-9]+$' | sort -n); do
  n=$((n + 1))
  for v in similar neutral different; do
    for s in similar neutral different; do
      cp "static/grid/$d/custom_visual-${v}_semantic-${s}/turn_2_robot.png" \
         "assets/grid/p${n}_visual-${v}_semantic-${s}.png"
    done
  done
done
echo "grid: $n participants, $(ls assets/grid | wc -l | tr -d ' ') tiles"
