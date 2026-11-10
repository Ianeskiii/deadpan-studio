# Deadpan Studio

The production pipeline behind **Tube Town / Deadpan Doug**: animated YouTube Shorts made with Blender, Kokoro TTS and ffmpeg, driven by Claude.

- **Studio website (queue, progress, videos, libraries):** https://ianeskiii.github.io/deadpan-studio/
- **Episode history:** [EPISODES.md](EPISODES.md)
- **Instructions for Claude:** [CLAUDE.md](CLAUDE.md)

## Using it from any of your Claude accounts

1. **Queue a short** on the website. GitHub opens with the request filled in; click **Commit changes**. You can also tell any Claude session with this repo attached: "queue this short: …".
2. **It gets made automatically.** Committing the request starts the "Run the queue" GitHub Action, which runs Claude with your Claude subscription tokens (repo secrets `CLAUDE_TOKEN_1` to `CLAUDE_TOKEN_3`, one per account). You can also start it by hand from the Actions tab, or say "run the queue" in any Claude session with the repo attached.
3. **Watch** progress and play or download the videos on the website. Ask for changes with **Request a revision**.

Everything (briefs, status, videos and libraries) lives in this repo, so no account depends on another.
