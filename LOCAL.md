# Running Deadpan Studio on your Windows PC (no GitHub)

The studio website, the queue and Claude all run on your PC. You add shorts, upload narration MP3s and request revisions on the site as usual. Everything is saved in the studio folder, and Claude Code (signed in with your Claude account) makes the videos right there.

The pipeline (Blender, the voices, the speech checker, ffmpeg) is Linux software, so it runs inside **WSL**, Microsoft's free built-in Linux. Claude Code must be installed **inside WSL** too. A copy on Windows can't run the pipeline.

## One-time setup (about 30 minutes, mostly waiting)

1. **Install WSL with Ubuntu.** Right-click Start → **Terminal (Admin)**, then run:
   ```
   wsl --install
   ```
   Restart when it asks. Ubuntu opens by itself after the restart (or open **Ubuntu** from the Start menu). Choose a username and password; it asks for this password when installing things.

2. **Get the studio folder into Ubuntu.** In the Ubuntu window:
   ```
   git clone https://github.com/Ianeskiii/deadpan-studio ~/deadpan-studio
   ```
   This is the last time GitHub is needed. It copies everything, including your existing shorts and videos. (If GitHub asks you to sign in, the repo is private: download it as a ZIP from GitHub instead and unzip it to `~/deadpan-studio`.)

3. **Install Claude Code inside Ubuntu and sign in.** In the same window:
   ```
   curl -fsSL https://claude.ai/install.sh | bash
   ```
   Close and reopen Ubuntu, then type `claude`, sign in with your Claude account in the browser, and type `/exit`.

4. **Start the studio:**
   ```
   bash ~/deadpan-studio/local/start.sh
   ```
   The first start installs everything (10–20 minutes, and it asks for your Ubuntu password once). Later starts take seconds.

5. Open **http://localhost:8080** in your browser.

**Desktop shortcut (optional):** in Ubuntu, run this once to put a **Start Deadpan Studio** icon on your Windows desktop:
```
cp ~/deadpan-studio/local/"Start Deadpan Studio.bat" "$(wslpath "$(cmd.exe /c 'echo %USERPROFILE%' 2>/dev/null | tr -d '\r')")/Desktop/"
```

## Day to day

- Double-click **Start Deadpan Studio** (or run `bash ~/deadpan-studio/local/start.sh`). The site opens.
- **Keep that window open** while shorts are being made, and don't let the PC sleep (Windows Settings → System → Power → set sleep to Never while it works). Closing the window stops Claude. The next start picks up where it stopped.
- The bar at the top of the site shows whether Claude is working. **Run the queue now** starts it by hand.
- Claude starts by itself when you add a short, upload an MP3 or request a revision. It also checks every 30 minutes for anything left half-done, for example after your Claude usage limit resets.
- Logs of every Claude run are in `~/deadpan-studio/.local/runs/`.

## Good to know

- **Usage:** each run uses your Claude plan's usage. If you hit a limit, the run stops, the short stays half-done, and the studio tries again 30 minutes later.
- **Turn off the GitHub version** so the two don't both work on things: on GitHub, open **Actions → Run the queue → ⋯ → Disable workflow**. You can still push to GitHub now and then as a backup (`git push` from the studio folder), but nothing depends on it.
- **Other devices:** the site is only on this PC. To open it from your phone on the same Wi-Fi, start with `STUDIO_HOST=0.0.0.0 bash ~/deadpan-studio/local/start.sh` and use the PC's address. Only do this on a home network you trust, because anyone on it could add shorts.
- **Settings:** `STUDIO_PORT` (8080), `STUDIO_MODEL` (claude-opus-5-5), `STUDIO_CHECK_MIN` (30), `STUDIO_AUTORUN=0` to only run when you press the button. Put them before the start command, as in the example above.

## If something goes wrong

- **The site says Claude Code wasn't found:** step 3 wasn't done inside Ubuntu, or Ubuntu wasn't reopened afterwards.
- **localhost:8080 doesn't open:** check that the Ubuntu window still shows "Starting Deadpan Studio". If it does, try `STUDIO_HOST=0.0.0.0` as above.
- **A run fails straight away:** open the newest log in `.local/runs/`. "Not logged in" means run `claude` once in Ubuntu and sign in again.
