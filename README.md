# Deadpan Studio

The production pipeline behind **Tube Town / Deadpan Doug**: animated YouTube Shorts made with Blender, Kokoro TTS and ffmpeg, driven by Claude.

- **Studio website (queue, progress, videos, libraries):** https://ianeskiii.github.io/deadpan-studio/
- **Episode history:** [EPISODES.md](EPISODES.md)
- **Instructions for Claude:** [CLAUDE.md](CLAUDE.md)

## Using it from any of your Claude accounts

1. **Queue a short** on the website. GitHub opens with the request filled in; click **Commit changes**. You can also tell any Claude session with this repo attached: "queue this short: …".
2. **Make it:** in any Claude account with GitHub connected, start a session with `Ianeskiii/deadpan-studio` attached and say **"run the queue"**. On first use Claude runs `bash setup.sh` (about a minute).
3. **Watch** progress and play or download the videos on the website. Ask for changes with **Request a revision**.

Everything (briefs, status, videos and libraries) lives in this repo, so no account depends on another.
