# Deadpan Studio

The production pipeline behind **Tube Town / Deadpan Doug**: animated YouTube Shorts made with Blender, Kokoro TTS and ffmpeg, driven by Claude.

- **Studio website (queue, progress, videos, libraries):** https://claude.ai/artifact/LjaCXL7X6qtSUCa2RfoV7L
- **Episode history:** [EPISODES.md](EPISODES.md)
- **Instructions for Claude:** [CLAUDE.md](CLAUDE.md)

## Using it from any of your Claude accounts

1. Invite the account to the studio website as an **Editor**, by email (Share menu; leave the public link off).
2. In that account, start a Claude Code session with this repo attached.
3. Say **"run the queue"**. Claude runs `bash setup.sh` on first use, reads the queued shorts from the studio, makes them and posts the videos back to the site.

Queue new shorts from the studio's **New short** form, from any invited account.
