# Wax — Spotify Session Dashboard

A single-file dashboard that controls Spotify in the browser via the **Web Playback SDK**
and the **Web API** (Authorization Code + PKCE, no server/secret required).

> Requires a **Spotify Premium** account (playback control and in-browser streaming are Premium-only).

## Setup

### 1. Create a Spotify app
1. Go to <https://developer.spotify.com/dashboard> → **Create app**.
2. Name it anything (e.g. "Wax"). For **APIs used**, tick **Web API** and **Web Playback SDK**.
3. Under **Redirect URIs**, add exactly:
   ```
   http://127.0.0.1:5173/index.html
   ```
   (This must match the value shown on the app's connect screen. If you serve at the
   directory root instead, register `http://127.0.0.1:5173/`.)
4. Save, then copy the **Client ID**.

### 2. Add your Client ID
Open [`index.html`](index.html), find the `CONFIG` block near the top of the `<script>`, and set:
```js
clientId: 'your-client-id-here',
```

### 3. Run it
Spotify rejects `file://` redirect URIs, so serve over `http://127.0.0.1`:

```bash
# Python (bundled with most systems)
python -m http.server 5173 --bind 127.0.0.1

# …or Node
npx http-server -a 127.0.0.1 -p 5173
```

Open <http://127.0.0.1:5173/index.html>, click **Connect Spotify**, approve, and the
"Wax" device will appear in Spotify Connect. Press play or pick a playlist.

## What's wired to Spotify

| Widget | Backed by |
|---|---|
| Now Playing (art, title, seek, ⏯ / ⏭ / ⏮) | Web Playback SDK + Web API |
| Shuffle / Loop / Like | `PUT /me/player/shuffle`·`/repeat`, `PUT·DELETE /me/tracks` |
| Volume (in **Volume & EQ**) | `player.setVolume` |
| Up Next · Queue | `GET /me/player/queue` (click a row to play it) |
| Playlists | `GET /me/playlists` → play `context_uri` |
| Output | `GET /me/player/devices` → transfer playback |
| Suggestions | `GET /me/top/tracks` → `+ QUEUE` |
| Session · Top Artist | `GET /me/top/artists` |
| Recently Played | `GET /me/player/recently-played` |
| Theme "Adapt to art" | dominant colour sampled from album art |

## Known Spotify limits (handled gracefully)

- **EQ bands** — no equalizer in the Web API, so they're cosmetic. The volume slider above them is live.
- **Visualizer** — Spotify's audio is DRM-protected with no PCM/FFT access, so this is a
  procedural animation that reacts to real play/pause and the accent colour (not true spectrum data).
- **Lyrics** — Spotify has no public lyrics API; the widget shows the track and a note. Wire in a
  provider like Musixmatch to populate it.
- **Suggestions** use your Top Tracks because the `/recommendations` endpoint was disabled for
  newly-created apps (late 2024).
- **Queue reorder / jump-to-index** isn't supported by the API; clicking a queue row plays that
  track directly.

## Files
- [`index.html`](index.html) — the app.
- [`demo-mock.html`](demo-mock.html) — the original offline mock (no Spotify), for reference.
- [`.claude/launch.json`](.claude/launch.json) — dev-server config for the port above.
