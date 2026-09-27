# Co-drawing robot project page

Minimal GitHub Pages site: one video, in-person co-drawings, and the final
robot turn from the online sessions (adversarial vs. control).

## Layout

```
index.html          the page (plain HTML + CSS, no build step, no JS)
assets/             web-ready copies, committed
  video/            compressed video (~14 MB, 720p) + poster frame
  poster.pdf        conference poster, flattened to one JPEG page (56 MB -> ~4 MB)
  in-person/        scans resized to 1600 px
  online/{adversarial,control}/NN.png   turn_2_robot.png, renumbered
  online/{adversarial,control}/NN/     six raw/ progression frames shown on hover
  grid/pN_visual-V_semantic-S.png     3x3 prompt-design tiles per participant
static/             raw material, NOT committed (.gitignore)
build_assets.sh     regenerates assets/ from static/
```

`static/` stays out of the repo on purpose: the original video is 102 MB
(GitHub rejects files over 100 MB), the original poster is 56 MB, and the
online folders are named after participants.

## Deploy to GitHub Pages

```sh
cd website
git init -b main
git add .
git commit -m "Project page"
gh repo create <user>/<repo> --public --source=. --push
gh api -X POST repos/<user>/<repo>/pages -f 'source[branch]=main' -f 'source[path]=/'
```

Or without `gh`: create an empty repo on github.com, push `main`, then in
the repo go to Settings → Pages → Source: `main` / `/ (root)`.

Use a repo named `<user>.github.io` to publish at that domain, or any other
name to publish at `https://<user>.github.io/<repo>/`.

## Updating the gallery

Drop new material into `static/` and run:

```sh
./build_assets.sh                 # video + images (video takes ~1 min)
SKIP_VIDEO=1 ./build_assets.sh    # images only
```

Then add the new `<img>` tags to `index.html`.

For the 3x3 prompt-design grid, participant folders under `static/grid/` are
renumbered p1..pN in numeric order; after adding one, bump `data-participants`
on the `#prompt-grid` section in `index.html`.
