<h1 align="center">Wax</h1>

<p align="center">A draggable, themeable <b>Spotify session dashboard</b> that runs entirely in the browser.</p>

<p align="center">
  <img alt="Made with React" src="https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=white">
  <img alt="Spotify Web API" src="https://img.shields.io/badge/Spotify-Web%20API%20%2B%20Playback%20SDK-1db954?logo=spotify&logoColor=white">
  <img alt="Auth" src="https://img.shields.io/badge/auth-PKCE%20(no%20secret)-blue">
  <img alt="Single file" src="https://img.shields.io/badge/build-single%20file-lightgrey">
</p>

---

Wax turns your Spotify account into a live "session dashboard": eleven rearrangeable widgets —
now playing, a visualizer, queue, playlists, output devices, volume/EQ, suggestions, stats, a
clock, recently played, and lyrics. Everything is one self-contained `index.html` (React via CDN,
no build step), authenticating directly against Spotify with **Authorization Code + PKCE** — no
backend and no client secret.

> [!IMPORTANT]
> Playback control and in-browser streaming require a **Spotify Premium** account
> (this is a Spotify Web Playback SDK requirement, not a Wax one).

## Features

- 🎧 **In-tab playback** — the Web Playback SDK registers a **"Wax"** device; audio streams in the page.
- ⏯ **Full transport** — play/pause, next/prev, seek, shuffle, loop, like/save.
- 🔊 **Live volume** + a cosmetic 5-band EQ display.
- 📋 **Queue** — see what's next; click a row to jump to it.
- 💿 **Playlists** — your library, click to play.
- 📡 **Output switching** — transfer playback across your Spotify Connect devices.
- ✨ **Suggestions** — your Top Tracks, one-click `+ QUEUE`.
- 📊 **Session stats** + top artist, **recently played**, and a **clock**.
- 🎨 **Adaptive theming** — the accent color is sampled from the current album art (or pick a fixed hue).
- 🧩 **Drag to rearrange**, resize, fullscreen, or hide any widget — layout persists in `localStorage`.

## Quick start

### 1. Serve it over `127.0.0.1`
Spotify rejects `file://` redirect URIs, so run a static server:

```bash
python -m http.server 5173 --bind 127.0.0.1
# or:  npx http-server -a 127.0.0.1 -p 5173
```

Then open **http://127.0.0.1:5173/index.html**.

### 2. Use your own Spotify app (if cloning)
This repo ships with a Client ID wired for its owner's Spotify app. To run it under your own:

1. Create an app at <https://developer.spotify.com/dashboard> (enable **Web API** + **Web Playback SDK**).
2. Add the redirect URI shown on the connect screen — exactly:
   `http://127.0.0.1:5173/index.html`
3. Set `CONFIG.clientId` near the top of [`index.html`](index.html) to your app's **Client ID**
   (it's not a secret — PKCE means no client secret is ever used).

### 3. Connect
Click **Connect Spotify**, approve the scopes, and the dashboard fills with live data. Press play
or pick a playlist to start audio in the tab.

## How it maps to Spotify

| Widget | Backed by |
|---|---|
| Now Playing (art, seek, ⏮ ⏯ ⏭) | Web Playback SDK + `GET /me/player` |
| Shuffle / Loop / Like | `PUT /me/player/shuffle`·`/repeat`, `PUT`·`DELETE /me/tracks` |
| Volume | `player.setVolume` |
| Up Next · Queue | `GET /me/player/queue` |
| Playlists | `GET /me/playlists` → play `context_uri` |
| Output | `GET /me/player/devices` → transfer |
| Suggestions | `GET /me/top/tracks` → `POST /me/player/queue` |
| Session · Top Artist | `GET /me/top/artists` |
| Recently Played | `GET /me/player/recently-played` |
| "Adapt to art" theme | dominant color sampled from album art on a canvas |

## Known Spotify limits (handled gracefully)

- **EQ** — the Web API has no equalizer, so the bands are cosmetic. The volume slider above them is live.
- **Visualizer** — Spotify audio is DRM-protected with no PCM/FFT access; this is a procedural
  animation that reacts to real play/pause and the accent color, not a true spectrum.
- **Lyrics** — Spotify has no public lyrics API. The widget shows the track and a note; wire in a
  provider (Musixmatch, LRCLIB) to populate it.
- **Suggestions** use Top Tracks because `/recommendations` was disabled for newly-created apps (late 2024).
- **Queue reorder / jump-to-index** isn't exposed by the API; clicking a queue row plays that track directly.

## Tech

Single-file React 18 (loaded from CDN, JSX compiled in-browser by Babel Standalone), the Spotify
Web Playback SDK, and the Web API over `fetch`. Auth is Authorization Code + PKCE with silent token
refresh; tokens live in `localStorage`. No bundler, no backend.

## Project files

- [`index.html`](index.html) — the app.
- [`demo-mock.html`](demo-mock.html) — the original offline mock (no Spotify), for reference/design.
- [`.claude/launch.json`](.claude/launch.json) — dev-server config for port 5173.

## Roadmap

- Real synced lyrics via a third-party provider
- Progress-synced visualizer
- Richer, persisted listening stats
- Friendlier "no active device" and token-expiry handling
