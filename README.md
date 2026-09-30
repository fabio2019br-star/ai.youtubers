# Cross Viral 🎬↔️📱

**TikTok ↔ Reels Cross-Viralization Engine**

An open-source Python script that adapts **a single video** to run natively
on both TikTok **and** Instagram Reels — respecting the invisible
differences between the two algorithms and avoiding the "raw repost"
detection that causes silent shadow bans.

> **The core idea:** most people grab a TikTok video and post it as-is on
> Reels (or vice versa) — and get hit with silent reach reduction for
> cross-content. Cross-Viralization is the technique of adapting 1 video
> for 2 algorithms while respecting the invisible differences between
> them. Result: the same good video pops on BOTH without being flagged as
> a repost, and your reach multiplies without producing anything new.

---

## 📌 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Known Limitations](#-known-limitations)
- [License](#-license)
- [Legal & Responsibility Notes](#️-legal--responsibility-notes)
- [Contributing](#-contributing)

---

## 🔥 The Problem

TikTok and Instagram Reels are **not the same thing with different names**.
They're recommendation systems with distinct logics. Treating one as a copy
of the other triggers **silent penalization** (shadow ban):

- **Perceptual video hash** (visual and audio fingerprint) — even after
  reencoding, the video's DNA remains.
- **Metadata and export signature** — codec, bitrate, and resolution
  typical of each app.
- **Dynamic watermark** — TikTok moves its logo position.
- **Audio pattern** — licensed tracks from one platform that the other
  doesn't recognize in its catalog.
- **Engagement signals** — if the video performs "oddly" against the
  platform's baseline, the system downranks it.

The punishment is rarely an explicit ban. It's **reduced distribution** —
you think the video "didn't take off," but it was actually deprioritized.

---

## 💡 The Solution

**Cross Viral** downloads the source video, generates **two versions with
different fingerprints**, and adapts each one to the native
characteristics of each platform:

| Dimension | TikTok | Reels |
|---|---|---|
| **Retention** | Aggressive curve, first 1-3s decisive | Tolerates a bit more context |
| **Audio** | Native/trending sound is central | Original audio or Instagram trending |
| **Caption/Text** | On-screen text + native caption | Native caption weighs more |
| **Duration** | Flexible, favors short loop | Favors 7-30s with replay |
| **Social signal** | Shares and comments | Saves and DM shares |
| **Aesthetic** | Rawer, "authentic", UGC | More polished, but not corporate |
| **Hashtags** | Relevant for niche | Less relevant, more context |

The result is that, for each algorithm, that video is **native** — not a
repost. It then competes on equal footing with original content.

---

## ⚙️ How It Works

The script runs three main stages:

### 1. Clean download
Downloads the source video with `yt-dlp`, which removes the watermark
automatically. Output: clean MP4 file.

### 2. Fingerprint rewrite
A single FFmpeg encode handles three things:
- **Light zoom + speed adjustment** → changes the visual and audio fingerprint
- **Reencode (libx264 + AAC)** → overwrites the original codec signature
- **Resolution normalization** → adapts to the target platform

### 3. Caption pack
Generates two caption + hashtag styles, one for each platform.

### Comparison: raw repost vs. Cross Viral

| Action | Raw repost | Cross Viral |
|---|---|---|
| Watermark | Goes with watermark | Removed — clean file |
| Codec fingerprint | Original file uploaded as-is | Reencoded — different signature |
| Audio fingerprint | Original audio | Speed adjusted (atempo ±2%) |
| Visual fingerprint | Original frames | setpts + scale + crop |
| Caption | Copy-paste | Style generated per platform |
| Resolution | Mixed | Standardized 1080×1920 with distinct params |

---

## 🚀 Installation

### Prerequisites

- **Python 3.9+**
- **FFmpeg** installed on the system (required)

#### Install FFmpeg

```bash
# macOS (Homebrew)
brew install ffmpeg

# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg

# Windows (Scoop)
scoop install ffmpeg
