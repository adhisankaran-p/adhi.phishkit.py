
# adhi.phishkit

**Ultimate educational phishing toolkit — 210+ replica login kits, one
self-hosted Python file, zero dependencies.**

Self-hosted phishing lab for training, awareness demos and red-team exercises.
Replica login flows for bank, wallet, telecom, government, gaming, gift-card
and social logins — with a live operator console, camera/mic/geo capture, bot
cloaking and one-command Cloudflare tunnels.

> **For educational purposes only.** This is not an official product.
> It is not affiliated with Google, Meta, Apple, Microsoft, Amazon, X, or any
> bank, telecom operator, wallet provider, game publisher or government portal
> whose interface it replicates. All trademarks belong to their owners.
> See [DISCLAIMER.md](DISCLAIMER.md).

---

## Requirements

- Python **3.8+**
- `ssh` client (only for SSH-based tunnels)
- Termux: `pkg install python openssh`

## Install & run

```bash
git clone https://github.com/<your-user>/adhi-phishkit.git
cd adhi-phishkit
python3 adhi.phishkit.py -p 8080
