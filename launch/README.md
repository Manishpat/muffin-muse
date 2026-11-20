# Launch reel

`muffin-muse-launch.mp4` is an 18-second vertical video (1080×1920, 30 fps) with an original synthesised soundtrack, made for Instagram Reels and Stories.

| Time | Scene |
|---|---|
| 0–4 s | Animated brand intro: the cupcake logo draws itself, a sprinkle burst, letters drop in, "cakes by Diksha" writes on |
| 4–11.5 s | Beat-cut cake montage with whip, flash and zoom transitions |
| 11.5–14 s | "Every celebration deserves a little more sweetness." word by word |
| 14–18 s | End card: logo, Now taking orders, Book your cake button, website link, @muffinmuse_i |

To rebuild it, put the portrait photos in `img/`, then run:

```
python music.py music2.wav
python render.py muffin-muse-launch.mp4 "your-website-link"
```

You need Pillow, NumPy and imageio-ffmpeg installed. The second argument changes the link shown on the end card.

The cake photos are Unsplash stock images. Re-render with Diksha's own cakes before using the reel as a portfolio.
