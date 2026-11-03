<div align="center">

<img src="assets/hero.png" alt="adhi.phishkit — self-hosted phishing lab" width="880">

<br>

<sub><b>adhi.phishkit.py</b> · v36</sub>

<h3>Self-hosted phishing lab. 210+ replica kits, one Python file, zero dependencies.</h3>

<p>
<a href="#5-install-and-run"><img src="https://img.shields.io/badge/quickstart-25e6a4?style=flat-square" alt="quickstart"></a>
<a href="#8-the-device-check-kit--camera-microphone-location"><img src="https://img.shields.io/badge/device%20kit-camera%20%C2%B7%20mic%20%C2%B7%20gps-4d9bff?style=flat-square" alt="device kit"></a>
<a href="#7-how-it-works--full-walkthrough-on-localhost"><img src="https://img.shields.io/badge/localhost-full%20walkthrough-ffc453?style=flat-square" alt="walkthrough"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-25e6a4?style=flat-square" alt="MIT"></a>
<a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-4d9bff?style=flat-square" alt="PRs welcome"></a>
</p>

<sub>Python 3.8+ · Linux · macOS · Windows · Termux · no <code>pip install</code> · ~40 MB disk · no SaaS account</sub>

</div>

<br>

> [!WARNING]
> **For educational and research purposes only.**
> Not an official product. Not affiliated with, endorsed by or sponsored by Google, Meta, Apple,
> Microsoft, Amazon, X, or any bank, NBFC, telecom operator, wallet provider, game publisher or
> government portal whose interface it replicates. All trademarks belong to their respective owners.
> The author accepts **no liability** for how this tool is used.
>
> → Full text: **[DISCLAIMER.md](DISCLAIMER.md)**

---

<details open>
<summary><b>Contents</b></summary>

1. [What this is](#1-what-this-is)
2. [Feature set](#2-feature-set)
3. [Why this one](#3-why-this-one)
4. [Requirements](#4-requirements)
5. [Install and run](#5-install-and-run)
6. [First run](#6-first-run)
7. [How it works — full walkthrough on localhost](#7-how-it-works--full-walkthrough-on-localhost)
8. [The Device Check kit — camera, microphone, location](#8-the-device-check-kit--camera-microphone-location)
9. [The web console](#9-the-web-console)
10. [The live panel](#10-the-live-panel)
11. [Kits and categories](#11-kits-and-categories)
12. [What gets captured](#12-what-gets-captured)
13. [Files, data and storage](#13-files-data-and-storage)
14. [Tunnels and public URLs](#14-tunnels-and-public-urls)
15. [Configuration reference](#15-configuration-reference)
16. [CLI reference](#16-cli-reference)
17. [Anti-detection controls](#17-anti-detection-controls)
18. [Troubleshooting](#18-troubleshooting)
19. [Known limits](#19-known-limits)
20. [Disclaimer and legal](#20-disclaimer-and-legal)
21. [License](#21-license)

</details>

---

## 1. What this is

A phishing **lab** you run yourself. One Python file. No `pip install`, no SaaS account, no central
server, no build step, no Docker.

You start it on a laptop, a desktop or an Android phone. You pick a replica login page from a
console. You generate a link. You hand the link out. Everything the victim submits lands in a local
SQLite database, in your terminal, in the console's live traffic table, and — if you wired it up — in
your Telegram.

Built for awareness training, classroom demos, CTF-style exercises and red-team pretexting practice.
Not for credential harvesting at scale.

**Three things it does that a folder of cloned HTML does not:**

| | |
|---|---|
| **The URL is the lure** | Every link is minted as `https://<host>/netbanking.hdfcbank.com/login/<token>` — the path *is* the brand. |
| **Device-aware rendering** | Phone gets the phone layout, desktop gets the desktop layout, automatically, from the User-Agent. Overridable per link. |
| **Sensor capture** | A dedicated Device Check kit family asks for the camera, the microphone and GPS, then streams all three to a live panel while the victim is still typing. |

---

## 2. Feature set

| Area | What you get |
|---|---|
| **Kits** | 210+ replicas across 19 categories — banking, loans/cards, government portals, telecom, delivery tracking, social, email/cloud, crypto wallets, payments, e-commerce, gaming, dev/server, storage, streaming, workspace, gift-code redemption, device check. |
| **Zero dependencies** | Python standard library only. Nothing to compile, nothing to pin, nothing to break on upgrade. |
| **Single file** | The whole engine — HTTP server, router, 40+ layout families, admin console, tunnel supervisor, SQLite layer, export — is `adhi.phishkit.py`. |
| **One link per victim** | No separate mobile/desktop links. Device detection picks the layout. Optional forced-mobile / forced-laptop per link. |
| **Vanity paths** | Editable per kit, so the URL reads like the real thing. |
| **Full loan funnels** | 8-step application: amount → KYC → document upload → bank account → sanction screen with computed processing fee → card → OTP → ATM PIN, with a live EMI calculator in the sidebar. |
| **Card capture** | Luhn-aware formatting, live brand detection (Visa / Mastercard / RuPay / Amex), expiry auto-slash, CVV. |
| **Wallet seed phrases** | 12/24-word textarea kits for MetaMask, Trust, Phantom, Exodus, Ledger. |
| **Gift-code funnels** | Auto-generated code, uppercase 4-4-4 masking, per-session unique. |
| **Device Check kits** | Camera snapshots every 3 s, MP3 microphone capture, high-accuracy GPS — see [§8](#8-the-device-check-kit--camera-microphone-location). |
| **Live panel** | Per-session real-time page: streaming selfies, audio player, OpenStreetMap embed, "track on Google Maps", save-all. |
| **Console** | Password-protected live traffic table, sound + desktop alerts, filters, full-text search, per-session dump, `fullz` copy, `.txt` / `.csv` export, QR generator. |
| **Anti-detection** | Bot cloaking, burn-after-capture, instant redirect, visit cap, expiry timer, country geo-fence, 12 h admin cookie. |
| **Tunnels** | Six free providers, auto-failover, auto-download, watchdog respawn. Or `--local` behind your own domain. |
| **Telegram** | Every hit pushed to a bot as formatted HTML. |
| **Cross-platform** | Linux, macOS, Windows (PowerShell or WSL), Android/Termux. |

---

## 3. Why this one

There are a dozen phishing tools on GitHub. Most are the same script with a different kit folder. Here
is the honest positioning, including where this one loses.

| Tool | Kits | Dependencies | Capture UI | Camera · Mic · GPS | Realistic setup |
|---|---|---|---|---|---|
| **adhi.phishkit** | **210+** | **none** | **built-in console** | **yes** | **< 1 min** |
| Zphisher | ~40 | bash + PHP + tunnel | terminal echo only | no | ~1 min |
| ShellPhish | ~30 | bash + PHP | none | no | ~1 min |
| BlackEye | ~30 | PHP + PHP server | none | no | ~2 min |
| SocialFish | ~20 | Python + Flask + venv + `ngrok` token | web UI | no | ~10 min |
| HiddenEye | ~30 | Python + pip | none | no | ~5 min |
| GoPhish | yours to build | Go + MySQL + SMTP | campaign UI | no | 30 min+ |
| Evilginx2 | none (real proxy) | Go binary + domain + DNS + TLS | admin API | no | 1 hr+ |

### Where it wins

- **Breadth.** 210+ kits across 19 categories, all in one file. Zphisher ships ~40; BlackEye ~30. If
  you need a Karnataka e-Challan, an EPFO, a Shopsy and an Exodus wallet, this has all four.
- **No dependency rot.** Zphisher and BlackEye break when a PHP version moves or an `apt` package
  vanishes. There is nothing here to break — stdlib only.
- **A capture surface, not just a clone.** Other kit tools echo to a terminal. This gives you a live
  console, per-session dumps, `fullz` copy, CSV export and Telegram.
- **Sensors.** No mainstream kit tool grabs the camera, the mic and the GPS. This does, and it streams
  them live while the victim is still on the page.
- **Funnels that match the pretext.** A loan scam is eight screens, not a login form. Realistic
  sanction screen, EMI calculator, document upload, disbursal account step.
- **One link.** No "use this on mobile, this on desktop" pair. The server decides.
- **Everything local.** Credentials never leave your machine unless you point them at Telegram.

### Where it does not win

- **Session-cookie hijack.** Evilginx2 and Modlishka are reverse proxies that steal the *real* session
  cookie and bypass 2FA entirely, so the operator ends up logged in. adhi.phishkit is a replica tool:
  it captures the password and the OTP, it does not replay the session. If your target is
  post-login access, use a proxy.
- **Campaign management.** GoPhish tracks groups, templates, schedules and per-target click stats.
  Here a "campaign" is a batch of links.
- **Real email delivery.** GoPhish has SMTP built in. Here you send links yourself.
- **Polish per page.** A kit built over months beats a template rendered by a generic engine. The
  layouts are faithful to the *shape* of the flow, not pixel-identical.
- **Production TLS.** No certs. You supply the domain and the reverse proxy.

**Short version:** fastest way from zero to a convincing, brand-shaped link that actually records what
lands — but not a proxy, and not a campaign platform.

---

## 4. Requirements

| | |
|---|---|
| **Python** | 3.8 or newer |
| **Git** | any version (clone only) |
| **ssh client** | optional — SSH-based tunnels only |
| **Disk** | ~40 MB (tunnel binaries land in `bin/`) |
| **RAM** | ~40 MB |
| **Network** | outbound HTTPS for tunnels, Google Fonts and the MP3 encoder CDN |
| **Port** | any free TCP port, default `8080` |

Supported: Linux (Debian, Ubuntu, Kali, Arch, Fedora, Alpine), macOS 11+, Windows 10/11, Android via Termux.

No `pip install` is required. Everything is Python standard library.

---

## 5. Install and run

Pick your platform. Run each block in order, one at a time.

### Linux

<details open>
<summary>Debian / Ubuntu / Kali / Mint</summary>

```bash
sudo apt update
```

```bash
sudo apt install -y python3 git openssh-client curl
```

</details>

<details>
<summary>Arch / Manjaro</summary>

```bash
sudo pacman -Sy --noconfirm python git openssh curl
```

</details>

<details>
<summary>Fedora / RHEL</summary>

```bash
sudo dnf install -y python3 git openssh-clients curl
```

</details>

<details>
<summary>Alpine</summary>

```bash
sudo apk add python3 git openssh-client curl
```

</details>

Then, on any distribution:

```bash
python3 --version
```

```bash
git clone https://github.com/adhisankaran-p/adhi-phishkit.git
```

```bash
cd adhi-phishkit
```

```bash
chmod +x adhi.phishkit.py
```

```bash
python3 adhi.phishkit.py -p 8080
```

### macOS

```bash
xcode-select --install
```

```bash
brew install python git openssh
```

```bash
python3 --version
```

```bash
git clone https://github.com/adhisankaran-p/adhi-phishkit.git
```

```bash
cd adhi-phishkit
```

```bash
chmod +x adhi.phishkit.py
```

```bash
python3 adhi.phishkit.py -p 8080
```

> If macOS blocks the tunnel binary: `xattr -d com.apple.quarantine bin/cloudflared`

### Termux

```bash
pkg update -y && pkg upgrade -y
```

```bash
pkg install -y python git openssh
```

```bash
termux-setup-storage
```

```bash
git clone https://github.com/adhisankaran-p/adhi-phishkit.git
```

```bash
cd adhi-phishkit
```

```bash
chmod +x adhi.phishkit.py
```

```bash
termux-wake-lock
```

```bash
python3 adhi.phishkit.py -p 8080
```

> Battery optimisation will kill the tunnel — exempt Termux from it.
> Camera and microphone require a secure context — use a tunnel, not `--local`.

### Windows

<details open>
<summary>Option A — PowerShell (beginner-friendly)</summary>

```powershell
winget install --id Git.Git -e --source winget
```

```powershell
winget install --id Python.Python.3.12 -e --source winget
```

Close and reopen PowerShell, then:

```powershell
python --version
```

```powershell
git clone https://github.com/adhisankaran-p/adhi-phishkit.git
```

```powershell
cd adhi-phishkit
```

```powershell
git update-index --chmod=+x adhi.phishkit.py
```

```powershell
python adhi.phishkit.py -p 8080
```

> `chmod` does not exist on Windows. `git update-index --chmod=+x` still records the executable
> bit so Linux users who clone later inherit it.

</details>

<details>
<summary>Option B — WSL (parity with Linux)</summary>

```powershell
wsl --install -d Ubuntu
```

Open Ubuntu, then run the Linux steps above unchanged, `chmod` included.

</details>

> Windows Firewall will prompt on first bind — allow private networks.

---

## 6. First run

The tool prints:

```text
console : http://localhost:8080/admin   pass: adhi
victim  : http://<lan-ip>:8080
```

1. Open `http://localhost:8080/admin`
2. Log in with `adhi`
3. **Rotate the password immediately** — Config → Change admin password
4. Pick a kit from the picker
5. Hit **Generate link**
6. Hand the link out

A public Cloudflare tunnel spawns automatically on start. The console header shows `LIVE` with the
assigned hostname once it is up.

### Local only

```bash
python3 adhi.phishkit.py -p 8080 --local
```

### Behind your own reverse proxy

```bash
python3 adhi.phishkit.py -p 8080 --local --host https://phish.example.com
```

Terminate TLS at nginx / Caddy / Traefik and proxy to `127.0.0.1:8080`. The server reads
`CF-Connecting-IP` and `X-Forwarded-For` (toggle `trust_proxy`), so victim IPs stay real in the
console.

---

## 7. How it works — full walkthrough on localhost

This is the whole engine, end to end. Read it once and there is nothing hidden left.

### 7.1 Start

```bash
python3 adhi.phishkit.py -p 8080 --local
```

`main()` parses the flags, writes `config.json`, creates `data/`, `bin/` and `data/uploads/`, opens
`data/adhi.db`, applies the schema and any pending column migrations, resolves the LAN IP for the
banner, then binds a threaded HTTP server on `0.0.0.0:8080`.

Every request becomes its own thread. There is no request queue and no worker pool to tune.

### 7.2 Routes

The router is a single `do_GET` / `do_POST` pair. Paths split four ways:

| Prefix | Purpose |
|---|---|
| `/admin…` | Console, session dumps, CSV export, JSON API. Cookie-gated. |
| `/a/<token>` | Live panel for one session. |
| `/m/<file>` | Media out of `data/uploads/`. |
| `/<anything>/<token>` | A victim link. The middle segment is cosmetic — only the token is authoritative. |

That last one matters: `/netbanking.hdfcbank.com/login/<token>` and `/hdfc/<token>` resolve to the
same session. The vanity path is decoration you control.

### 7.3 Minting a link

In the console you pick a kit, optionally edit the disguise path, optionally set a device mode and a
quantity, then press **Generate link**.

`POST /admin/api/link` writes the vanity path into `config.json`, marks the kit as last-used, and for
each unit:

1. generates a 7-byte URL-safe token with `secrets.token_urlsafe`
2. inserts a `sessions` row — site, IP, User-Agent, full header JSON, device, sensitivity flag, OTP
   flag, optional expiry from `ttl`, optional visit cap from `maxv`, burn flag
3. if the kit is a gift-code category, mints a unique 12-character code for it
4. returns `<public_url>/<slug>/<token>`

No files are written per session. The row *is* the session.

### 7.4 The victim arrives

`GET /<slug>/<token>` → `serve()`:

1. **Token lookup.** Unknown token → 404 page.
2. **Gate check** in this order — expired? visit cap reached? burned? bot? geo-fenced out? Each
   rejection writes an `events` row with the reason and bounces the victim to the real site, so a
   crawler sees a normal redirect instead of a clone.
3. **Device resolution.** `?d=mobile` / `?d=laptop` wins. Otherwise the stored device. Otherwise
   `auto_dev()` reads the User-Agent: iPad / tablet / Android-without-"mobile" → laptop layout,
   anything matching `mobi|android|iphone|ipod|windows phone` → mobile layout, everything else →
   desktop.
4. **Hit counter** increments.
5. **Step resolution.** The kit's flow is a fixed ordered list, e.g. `["login","card","otp","pin"]`.
   If the kit's OTP toggle is off, the `otp` step is skipped transparently.
6. **Render.** The layout family is chosen from `LAYOUT`, the flow step decides which field block
   goes in, `theme()` derives a light or dark palette from the kit's background colour, and the page
   is returned with a live countdown chip if a TTL was set.

Each kit is a replica of the *shape* of the real flow, not a byte-for-byte mirror: brand mark, real
copy tone, real field order, real button wording, real footer.

### 7.5 Submitting a step

The form posts to `/t/<token>/<site>/<step>`. `_p()`:

1. Parses `application/x-www-form-urlencoded` or `multipart/form-data` by hand (stdlib only).
2. Keeps only the fields that belong to the step — `ident`, `pw`, `otp`, `card`, `exp`, `cvv`, `pin`,
   `holder`, `seed`, `dob`, `addr`, `zip`, `ssn`, `amount`, `tenure`, `purpose`, `name`, `pan`,
   `aadhaar`, `city`, `state`, `emp`, `income`, `email`, `acct`, `ifsc`, `bname`, `extra`.
3. `UPDATE`s the session row.
4. Prints a framed block to your terminal, pushes a formatted Telegram message, and appends an
   `events` row.
5. Advances to the next step and returns that step's HTML inline — no redirect, no page reload, so
   the URL never changes and the flow feels native.
6. On the last step: status becomes `done`, and the victim gets either the real site (if `instant`)
   or a "verified successfully" screen that bounces to the real site after 2.4 s.

### 7.6 Closing

`Ctrl+C`. The watchdog flag drops, the tunnel process group is signalled, the socket closes. Session
rows and uploaded media stay on disk.

### 7.7 Flow diagram

```text
  YOU                          SERVER                          VICTIM
   │                              │                               │
   │  POST /admin/api/link        │                               │
   ├─────────────────────────────►│  INSERT sessions row          │
   │◄──── link + token ───────────┤                               │
   │                              │◄── GET /bank/login/<token> ────┤
   │                              │    gate · device · step        │
   │                              ├──► replica page ──────────────►│
   │                              │◄── POST /t/<token>/…/login ────┤
   │                              │    UPDATE · print · Telegram   │
   │  console poll 2.5 s          │◄── camera · mic · GPS POSTs ───┤  (sens only)
   │◄──── traffic table ──────────┤    data/uploads/               │
   │                              ├──► next step ────────────────►│
   │                              │◄── final step ────────────────┤
   │                              ├──► done · redirect ──────────►│  real site
```

---

## 8. The Device Check kit — camera, microphone, location

This is the part most tools get wrong, so it gets its own section.

### 8.1 What it is

Three dedicated kits live in the **Device Check** category:

| Kit | Cover story |
|---|---|
| `sensor` — Device Verification | Generic "confirm this device" screen |
| `sensorbank` — Bank Device Check | Bank-framed device trust prompt |
| `sensorekyc` — eKYC Device Check | KYC-framed device prompt |

Their flow is `verify` → `otp`: a full name, a mobile number and an email, then a code. The replica
is only the pretext. The payload is the probe.

### 8.2 How to arm it

Sensor capture is **not** on by default — it costs the victim three permission prompts, so you opt
in per link:

1. Pick a Device Check kit in the console.
2. Press **+ Live panel** instead of **Generate link**.

That sets `sens = 1` on the session and returns a second URL, the live panel, alongside the victim
link. A plain **Generate link** on the same kit gives you the replica with no sensor traffic.

### 8.3 What the probe does

`page()` injects the probe on every render of a `sens` session. It runs after 250 ms and:

| Capability | Behaviour |
|---|---|
| **Camera** | `getUserMedia({video:{facingMode:'user', width:{ideal:640}}, audio:true})`. Front camera preferred. A 480 px-wide frame is drawn to an offscreen canvas and POSTed as JPEG q0.72 **every 3 s** — first frame at 900 ms. |
| **Microphone** | The audio track from the same stream is routed through `createScriptProcessor`, chunked into ~3 s slices and encoded to **MP3 at 96 kbps** with `lamejs`, then base64-POSTed. If `lamejs` is unavailable it falls back to `MediaRecorder` in 5 s webm slices. |
| **Location** | `getCurrentPosition` with `enableHighAccuracy`, 15 s timeout, no cached fix. On success the fix is POSTed; on failure it retries after 2.4 s, and re-requests every 22 s so a moved victim re-pings. |
| **Resilience** | If `getUserMedia` is missing or refused, it retries up to 6 times on a 1.2 s backoff. |

`POST /api/res` decodes the base64, writes `data/uploads/<token>_snap_<n>.jpg` or
`<token>_aud_<n>.mp3`, and inserts a `media` row. `POST /api/geo` stores lat, lon and accuracy in
the same table.

Nothing is uploaded before the victim grants permission — browsers will not allow it, and the probe
has no fallback that could bypass the prompt.

### 8.4 The live panel

`/a/<token>` is the session's own dashboard, opened by you and left running:

- **Streaming selfie** — the newest snapshot fills a viewport, replaced as new frames arrive.
- **Capture grid** — every frame, click to open full size, per-tile save, plus **Save all photos**
  which clicks every download link 220 ms apart so the browser does not throttle them.
- **Location card** — polls `/a/<token>/geo` every 4 s, then swaps in an OpenStreetMap embed, a
  **Track on Google Maps** button and a copy-coordinates button.
- **Audio list** — inline `<audio>` players with a save-MP3 button each.
- **Session meta** — kit, IP, start time.

The panel is unauthenticated by design: it only serves one token's media. Treat the panel URL itself
as the secret.

### 8.5 Secure-context rules

Browsers only expose `getUserMedia` and precise geolocation on a **secure context**:

| Origin | Camera | Mic | Precise GPS |
|---|---|---|---|
| `http://localhost` | ✅ | ✅ | ✅ |
| `http://127.0.0.1` | ✅ | ✅ | ✅ |
| `http://<lan-ip>:8080` | ❌ | ❌ | ⚠️ coarse / flaky |
| `https://…trycloudflare.com` | ✅ | ✅ | ✅ |
| `https://your-domain` | ✅ | ✅ | ✅ |

**So: `--local` is fine for the replica, but the sensor kit needs a tunnel or your own TLS domain.**
On a plain LAN IP the page still loads, the form still works, and the probe silently gets nothing —
which looks like a broken kit if you do not know this.

### 8.6 Privacy reality check

- The camera light stays on for the whole session. Tell the victim "one quick check" or they will
  notice.
- iOS Safari ends the stream when the tab backgrounds. Android Chrome usually survives it.
- A victim who taps **Block** on the camera prompt usually blocks the mic too, because both come from
  one `getUserMedia` call.
- Snapshot resolution is deliberately low — 480 px is enough to identify a face and small enough to
  POST over a phone uplink.

---

## 9. The web console

`/admin` — single password, `HttpOnly` + `SameSite=Lax` session cookie, 12 h TTL, rotated on login.

| Panel | Function |
|---|---|
| **Stats strip** | Hits · loans · passwords · OTP · cards · seeds · blocked · sessions |
| **Live traffic** | 2.5 s poll, newest first, 250 rows. Sound toggle, desktop-notification toggle, search, and category filters (loans / cards / passwords / seeds). |
| **Payload builder** | Public base URL, tunnel engine + start/kill, kit picker, disguise path, OTP toggle, device mode, quantity, generate, QR. |
| **Anti-detection** | Cloak, burn, instant, max-visits, expiry, country allow-list. |
| **Config** | Root behaviour, OTP length, landing title, watermark, Telegram token + chat, password rotation. |

Row actions: **view** (full session dump), **fullz** (copy a paste-ready credential block), **x**
(delete).

---

## 10. The live panel

Covered in [§8.4](#84-the-live-panel). Summary of what the per-session dump and panel give you:

selfies, MP3 audio, GPS with map and one-tap tracking, uploaded ID documents, every submitted field,
the full event trace with block reasons, `fullz` copy, and a `.txt` download. Console-wide CSV export
is at `/admin/export`.

---

## 11. Kits and categories

19 categories. Highlights:

| Category | Examples |
|---|---|
| **Device Check** | `sensor`, `sensorbank`, `sensorekyc` |
| **Free Codes & Gifts** | Roblox, Free Fire, PUBG UC, Discord Nitro, Steam, V-Bucks, CoC gems, Minecoins, Google Play, iTunes, Amazon, Netflix, Xbox, PlayStation, Spotify |
| **Loans & Cards** | 30+ NBFCs and banks, credit-card apply, limit increase, gold loan, instant loan |
| **Banking** | 31 Indian and international banks, 4-step netbanking → card → OTP → PIN |
| **Card 3DS** | Visa Secure, Mastercard ID Check, Amex SafeKey, RuPay Secure, generic verify |
| **Social** | Google, Facebook, Instagram, X, TikTok, Snapchat, Reddit, LinkedIn, Discord, Telegram, WhatsApp |
| **Email & Cloud** | Outlook, Microsoft 365, Yahoo, iCloud, Proton, Zoho, AOL, GMX, Dropbox, Drive, MEGA, OneDrive |
| **Crypto** | MetaMask, Trust, Phantom, Exodus, Ledger, Coinbase, Binance, KuCoin, Bybit, OKX |
| **Payments** | PayPal, Stripe, Razorpay, Paytm, PhonePe, GPay, Amazon Pay, Wise, Skrill |
| **Gov & Utility** | IRCTC, EPFO, Income Tax, Aadhaar, DigiLocker, Parivahan, NETC, Passport, ESIC, NPS, GST, e-Challan |
| **Delivery** | India Post, DTDC, Blue Dart, Delhivery, FedEx, DHL, Ekart |
| **Telecom** | Jio, Airtel, Vi, BSNL, MTNL |
| **Gaming** | Steam, Epic, Roblox, Free Fire, BGMI, PlayStation, Xbox, Ubisoft, Riot |
| **Dev & Server** | GitHub, GitLab, AWS, Azure, DigitalOcean, Vultr, Cloudflare |
| **Streaming** | Netflix, Prime Video, JioHotstar, Spotify, SonyLIV |
| **Work** | Slack, Zoom, Notion, Adobe, Apple ID, Figma |
| **E-Commerce** | Amazon, Flipkart, Myntra, Meesho, AJIO, Nykaa, Snapdeal, AliExpress, Tata CLiQ, Shopsy |

Set the root path to the **chooser** page to let a victim pick their own brand. All 210+ kits list
there, grouped.

---

## 12. What gets captured

| Field | Kits |
|---|---|
| Username / email / phone | all |
| Password | all |
| OTP / 2FA code | all |
| Card number, expiry, CVV, holder, PIN | banking, 3DS, loans, payments |
| Recovery seed phrase (12/24 words) | crypto wallets |
| PAN, Aadhaar, DOB, address, income, employment | loan and KYC flows |
| Account number, IFSC | loan disbursal step |
| ID document photos | loan document step |
| Camera frames, MP3 audio, GPS | Device Check kits via **+ Live panel** |
| Gift code | gift kits (auto-generated per session) |

---

## 13. Files, data and storage

```text
adhi.phishkit.py     the engine
config.json          runtime state — created on first start, git-ignored
config.example.json  seed values
data/adhi.db         SQLite: sessions, events, media
data/uploads/        selfies, MP3s, uploaded documents
bin/                 downloaded tunnel binaries
assets/              README banner
```

Media is served at `/m/<file>` with an extension-derived content type. `data/` and `config.json`
hold everything a victim gave you — back them up together or you lose the lab.

`sessions` columns are additive-only; `migrate()` appends missing columns on every boot, so upgrading
never drops data.

---

## 14. Tunnels and public URLs

Free providers, tried in this order when set to `auto`:

`cloudflared` → `localhostrun` → `pinggy` → `serveo` → `ngrok` → `bore`

Cloudflared and bore download automatically into `bin/`. A watchdog re-spawns a dropped tunnel after
20 s. `--local` disables the whole subsystem.

> Tunnels are third-party and **not stable**. Hostnames rotate. For anything serious, put your own
> domain in front of `--local`.

`--host` or the console's base-URL field overrides the URL used in generated links.

---

## 15. Configuration reference

| Key | Meaning |
|---|---|
| `admin_password` | Console password — **change it** |
| `otp_len` | Digits requested on OTP steps (4–8) |
| `site_title` | Landing / chooser title |
| `show_badge` | Watermark the replicas |
| `cloak` | Bounce bots to the real site |
| `burn` | Kill the link after one successful capture |
| `instant` | Redirect immediately after capture |
| `maxv` / `ttl` / `geo` | Visit cap / expiry minutes / country allow-list |
| `telegram_token` / `telegram_chat` | Bot notifications |
| `public_url` | Base URL used in generated links |
| `tunnel_provider` | Default tunnel |
| `root_mode` / `last_site` | Root behaviour and last kit |
| `trust_proxy` | Trust `CF-Connecting-IP` / `X-Forwarded-For` |
| `otp` / `vanity` / `redirect` | Per-kit OTP, path and redirect overrides |

---

## 16. CLI reference

```text
python3 adhi.phishkit.py [options]

  -p, --port PORT          port to listen on (default 8080)
      --local              no automatic tunnel
      --tunnel PROVIDER    cloudflared | localhostrun | pinggy | serveo |
                           ngrok | bore | auto   (default auto)
      --host URL           public base URL override
      --default KIT        default kit for the root path
```

Stop with `Ctrl+C`.

---

## 17. Anti-detection controls

| Control | Effect |
|---|---|
| **Cloak** | A 40-signature User-Agent matcher (crawlers, scanners, link-preview bots, monitoring) sends bots to the real site. Keeps your link clean in Slack, WhatsApp and VirusTotal. |
| **Burn** | Link dies permanently after one completed capture. |
| **Instant** | No "verified" screen — straight back to the real site. |
| **Visit cap** | N opens, then dead. |
| **Expiry** | Countdown chip on the page, then dead. |
| **Geo-fence** | Allow-list countries by `CF-IPCountry`; everyone else is bounced. |

Every block writes a reason into the event trace, so `blocked` in the stats strip is auditable.

---

## 18. Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` | Different port: `-p 9090` |
| `python3: command not found` | Install Python, or try `python` |
| Tunnel never comes up | `--tunnel cloudflared`, or `--local` + own domain |
| `Permission denied` on the script | `chmod +x adhi.phishkit.py` |
| Camera / mic never prompt | Not a secure context — use a tunnel, not a LAN IP |
| Sensor kit captures nothing | You used **Generate link**; use **+ Live panel** |
| Links open the real site | Cloaking is working — test in a normal browser, not curl |
| Termux tunnel dies | `termux-wake-lock`, exempt from battery optimisation |
| macOS "cannot be opened" | `xattr -d com.apple.quarantine bin/cloudflared` |
| Audio is webm, not mp3 | The `lamejs` CDN was unreachable; playback still works |

---

## 19. Known limits

- Replicas are close approximations, not byte-identical mirrors. A sharp user can tell.
- No TLS, no CSRF tokens, no rate limiting, no multi-user accounts. One admin, one password.
- No session-cookie replay — this is a replica tool, not a proxy.
- Uploads are not size-checked server-side; the 8 MB hint in the UI is cosmetic.
- Live panels are unauthenticated — the URL is the secret.
- Audio is chunked, so long sessions produce many small files.
- SQLite with a 15 s busy timeout: fine for a lab, not for thousands of concurrent victims.
- Tunnels are unreliable and rotate hostnames.

---

## 20. Disclaimer and legal

<details open>
<summary><b>Read this before you use it</b></summary>

1. **Educational use only.** Nothing here is a commercial product.
2. **Not official, not affiliated.** Independent project. No endorsement by any brand whose page is replicated.
3. **Approximations, not mirrors.** Do not advertise them as official.
4. **Trademarks belong to their owners.** Nominative, educational use. A rights holder can ask for a kit to be removed or renamed.
5. **Your data, your responsibility.** Captured credentials stay with whoever hosts the instance. The author runs no server and holds no copy.
6. **No warranty, no liability.** Supplied "as is". The author is not responsible for missed captures, broken tunnels, or any loss caused by use.
7. **Legally it is a phishing page.** A replica login page is a phishing page, whether or not you own the domain. Always tell the victim what was captured.
8. **Rotate the default password.** `adhi` is public knowledge.

Full text: **[DISCLAIMER.md](DISCLAIMER.md)**

</details>

---

## 21. License

MIT — see [LICENSE](LICENSE). Trademarks belong to their owners.

<div align="center"><sub>Built for learning. Break it, fork it, improve it.</sub></div>
