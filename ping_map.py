#!/usr/bin/env python3
"""
🌍 Global Ping Monitor
======================
Zeigt wie lange deine Datenpakete in alle Welt brauchen.
Startet automatisch im Browser.

    python3 ping_map.py
    python3 ping_map.py --interval 15
    python3 ping_map.py --count 5
"""

import argparse, json, os, socket, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen

TARGETS = [
    # Europa
    {"id":"aws-fra","host":"s3.eu-central-1.amazonaws.com","port":443,"city":"Frankfurt","country":"DE","flag":"🇩🇪","cont":"Europa","org":"AWS","lat":50.11,"lon":8.68},
    {"id":"aws-dub","host":"s3.eu-west-1.amazonaws.com","port":443,"city":"Dublin","country":"IE","flag":"🇮🇪","cont":"Europa","org":"AWS","lat":53.33,"lon":-6.25},
    {"id":"aws-lon","host":"s3.eu-west-2.amazonaws.com","port":443,"city":"London","country":"GB","flag":"🇬🇧","cont":"Europa","org":"AWS","lat":51.51,"lon":-0.13},
    {"id":"aws-par","host":"s3.eu-west-3.amazonaws.com","port":443,"city":"Paris","country":"FR","flag":"🇫🇷","cont":"Europa","org":"AWS","lat":48.86,"lon":2.35},
    {"id":"aws-sto","host":"s3.eu-north-1.amazonaws.com","port":443,"city":"Stockholm","country":"SE","flag":"🇸🇪","cont":"Europa","org":"AWS","lat":59.33,"lon":18.07},
    {"id":"aws-mil","host":"s3.eu-south-1.amazonaws.com","port":443,"city":"Milan","country":"IT","flag":"🇮🇹","cont":"Europa","org":"AWS","lat":45.46,"lon":9.19},
    {"id":"hetzner-nbg","host":"nbg1-speed.hetzner.com","port":443,"city":"Nürnberg","country":"DE","flag":"🇩🇪","cont":"Europa","org":"Hetzner","lat":49.45,"lon":11.08},
    {"id":"hetzner-hel","host":"hel1-speed.hetzner.com","port":443,"city":"Helsinki","country":"FI","flag":"🇫🇮","cont":"Europa","org":"Hetzner","lat":60.17,"lon":24.94},
    {"id":"ovh-sbg","host":"proof.ovh.net","port":443,"city":"Strasbourg","country":"FR","flag":"🇫🇷","cont":"Europa","org":"OVH","lat":48.57,"lon":7.75},
    # Nordamerika
    {"id":"aws-iad","host":"s3.us-east-1.amazonaws.com","port":443,"city":"N. Virginia","country":"US","flag":"🇺🇸","cont":"Nordamerika","org":"AWS","lat":38.95,"lon":-77.44},
    {"id":"aws-cmh","host":"s3.us-east-2.amazonaws.com","port":443,"city":"Ohio","country":"US","flag":"🇺🇸","cont":"Nordamerika","org":"AWS","lat":39.96,"lon":-83.00},
    {"id":"aws-pdx","host":"s3.us-west-2.amazonaws.com","port":443,"city":"Oregon","country":"US","flag":"🇺🇸","cont":"Nordamerika","org":"AWS","lat":45.52,"lon":-122.67},
    {"id":"aws-sfo","host":"s3.us-west-1.amazonaws.com","port":443,"city":"Kalifornien","country":"US","flag":"🇺🇸","cont":"Nordamerika","org":"AWS","lat":37.77,"lon":-122.42},
    {"id":"aws-yul","host":"s3.ca-central-1.amazonaws.com","port":443,"city":"Montréal","country":"CA","flag":"🇨🇦","cont":"Nordamerika","org":"AWS","lat":45.50,"lon":-73.57},
    {"id":"vultr-nyc","host":"nj-us-ping.vultr.com","port":443,"city":"New Jersey","country":"US","flag":"🇺🇸","cont":"Nordamerika","org":"Vultr","lat":40.73,"lon":-74.17},
    {"id":"vultr-lax","host":"lax-ca-us-ping.vultr.com","port":443,"city":"Los Angeles","country":"US","flag":"🇺🇸","cont":"Nordamerika","org":"Vultr","lat":34.05,"lon":-118.24},
    {"id":"vultr-chi","host":"il-us-ping.vultr.com","port":443,"city":"Chicago","country":"US","flag":"🇺🇸","cont":"Nordamerika","org":"Vultr","lat":41.88,"lon":-87.63},
    {"id":"vultr-dfw","host":"tx-us-ping.vultr.com","port":443,"city":"Dallas","country":"US","flag":"🇺🇸","cont":"Nordamerika","org":"Vultr","lat":32.78,"lon":-96.80},
    {"id":"vultr-mia","host":"fl-us-ping.vultr.com","port":443,"city":"Miami","country":"US","flag":"🇺🇸","cont":"Nordamerika","org":"Vultr","lat":25.77,"lon":-80.19},
    {"id":"vultr-sea","host":"wa-us-ping.vultr.com","port":443,"city":"Seattle","country":"US","flag":"🇺🇸","cont":"Nordamerika","org":"Vultr","lat":47.61,"lon":-122.33},
    # Südamerika
    {"id":"aws-gru","host":"s3.sa-east-1.amazonaws.com","port":443,"city":"São Paulo","country":"BR","flag":"🇧🇷","cont":"Südamerika","org":"AWS","lat":-23.55,"lon":-46.63},
    {"id":"vultr-sao","host":"sao-br-ping.vultr.com","port":443,"city":"São Paulo","country":"BR","flag":"🇧🇷","cont":"Südamerika","org":"Vultr","lat":-23.53,"lon":-46.61},
    {"id":"vultr-scl","host":"scl-cl-ping.vultr.com","port":443,"city":"Santiago","country":"CL","flag":"🇨🇱","cont":"Südamerika","org":"Vultr","lat":-33.46,"lon":-70.65},
    # Afrika
    {"id":"aws-cpt","host":"s3.af-south-1.amazonaws.com","port":443,"city":"Kapstadt","country":"ZA","flag":"🇿🇦","cont":"Afrika","org":"AWS","lat":-33.93,"lon":18.42},
    {"id":"vultr-jnb","host":"jnb-za-ping.vultr.com","port":443,"city":"Johannesburg","country":"ZA","flag":"🇿🇦","cont":"Afrika","org":"Vultr","lat":-26.20,"lon":28.04},
    # Naher Osten
    {"id":"aws-bah","host":"s3.me-south-1.amazonaws.com","port":443,"city":"Bahrain","country":"BH","flag":"🇧🇭","cont":"Naher Osten","org":"AWS","lat":26.21,"lon":50.59},
    {"id":"aws-uae","host":"s3.me-central-1.amazonaws.com","port":443,"city":"Dubai","country":"AE","flag":"🇦🇪","cont":"Naher Osten","org":"AWS","lat":25.20,"lon":55.27},
    {"id":"vultr-tav","host":"tlv-il-ping.vultr.com","port":443,"city":"Tel Aviv","country":"IL","flag":"🇮🇱","cont":"Naher Osten","org":"Vultr","lat":32.08,"lon":34.78},
    # Asien
    {"id":"aws-nrt","host":"s3.ap-northeast-1.amazonaws.com","port":443,"city":"Tokyo","country":"JP","flag":"🇯🇵","cont":"Asien","org":"AWS","lat":35.68,"lon":139.69},
    {"id":"aws-icn","host":"s3.ap-northeast-2.amazonaws.com","port":443,"city":"Seoul","country":"KR","flag":"🇰🇷","cont":"Asien","org":"AWS","lat":37.57,"lon":126.98},
    {"id":"aws-sin","host":"s3.ap-southeast-1.amazonaws.com","port":443,"city":"Singapur","country":"SG","flag":"🇸🇬","cont":"Asien","org":"AWS","lat":1.35,"lon":103.82},
    {"id":"aws-bom","host":"s3.ap-south-1.amazonaws.com","port":443,"city":"Mumbai","country":"IN","flag":"🇮🇳","cont":"Asien","org":"AWS","lat":19.08,"lon":72.88},
    {"id":"aws-hkg","host":"s3.ap-east-1.amazonaws.com","port":443,"city":"Hongkong","country":"HK","flag":"🇭🇰","cont":"Asien","org":"AWS","lat":22.32,"lon":114.17},
    {"id":"aws-cgk","host":"s3.ap-southeast-3.amazonaws.com","port":443,"city":"Jakarta","country":"ID","flag":"🇮🇩","cont":"Asien","org":"AWS","lat":-6.21,"lon":106.85},
    {"id":"vultr-sgp","host":"sgp-sg-ping.vultr.com","port":443,"city":"Singapur","country":"SG","flag":"🇸🇬","cont":"Asien","org":"Vultr","lat":1.37,"lon":103.84},
    {"id":"vultr-nrt","host":"hnd-jp-ping.vultr.com","port":443,"city":"Tokyo","country":"JP","flag":"🇯🇵","cont":"Asien","org":"Vultr","lat":35.66,"lon":139.73},
    {"id":"vultr-mum","host":"bom-in-ping.vultr.com","port":443,"city":"Mumbai","country":"IN","flag":"🇮🇳","cont":"Asien","org":"Vultr","lat":19.10,"lon":72.90},
    {"id":"vultr-seoul","host":"icn-kr-ping.vultr.com","port":443,"city":"Seoul","country":"KR","flag":"🇰🇷","cont":"Asien","org":"Vultr","lat":37.55,"lon":126.96},
    # Ozeanien
    {"id":"aws-syd","host":"s3.ap-southeast-2.amazonaws.com","port":443,"city":"Sydney","country":"AU","flag":"🇦🇺","cont":"Ozeanien","org":"AWS","lat":-33.87,"lon":151.21},
    {"id":"aws-mel","host":"s3.ap-southeast-4.amazonaws.com","port":443,"city":"Melbourne","country":"AU","flag":"🇦🇺","cont":"Ozeanien","org":"AWS","lat":-37.81,"lon":144.96},
    {"id":"vultr-syd","host":"syd-au-ping.vultr.com","port":443,"city":"Sydney","country":"AU","flag":"🇦🇺","cont":"Ozeanien","org":"Vultr","lat":-33.89,"lon":151.23},
]

# ── MESSUNG ───────────────────────────────────────────────────────────────────
def resolve_host(host, timeout=4.0):
    try:
        return socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_STREAM)[0][4][0]
    except:
        return None

def tcp_ping(ip, port, timeout=4.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        t0 = time.perf_counter()
        s.connect((ip, port))
        ms = (time.perf_counter() - t0) * 1000
        s.close()
        return round(ms, 1)
    except:
        return None

def measure_target(target, resolved_ips, count=3):
    ip = resolved_ips.get(target["id"])
    if not ip:
        return {"ms": None, "online": False, "ip": target["host"], "samples": []}
    samples = []
    for _ in range(count):
        ms = tcp_ping(ip, target["port"])
        if ms is not None:
            samples.append(ms)
        time.sleep(0.03)
    if not samples:
        return {"ms": None, "online": False, "ip": ip, "samples": []}
    samples.sort()
    return {"ms": samples[len(samples)//2], "online": True, "ip": ip, "samples": samples}

# ── STATE ─────────────────────────────────────────────────────────────────────
state_lock   = threading.Lock()
resolved_ips = {}
state = {
    "results": {}, "my_ip": "…", "my_lat": 51.16, "my_lon": 10.45,
    "my_city": "Du", "measuring": False, "round": 0,
    "targets": TARGETS, "ping_count": 3,
}

def get_my_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close(); return ip
    except: return "unbekannt"

def get_geo(ip):
    try:
        r = urlopen(f"http://ip-api.com/json/{ip}?fields=lat,lon,city,country", timeout=5)
        d = json.loads(r.read())
        return float(d.get("lat",51.16)), float(d.get("lon",10.45)), d.get("city","Du")
    except: return 51.16, 10.45, "Du"

def resolve_all():
    global resolved_ips
    ips, lock = {}, threading.Lock()
    def worker(t):
        ip = resolve_host(t["host"])
        with lock: ips[t["id"]] = ip
    threads = [threading.Thread(target=worker, args=(t,), daemon=True) for t in TARGETS]
    for th in threads: th.start()
    for th in threads: th.join()
    resolved_ips = ips

def do_measure_round():
    with state_lock:
        if state["measuring"]: return
        state["measuring"] = True
        state["round"] += 1
        count = state["ping_count"]
    lock = threading.Lock()
    def worker(t):
        r = measure_target(t, resolved_ips, count=count)
        with lock: pass
        with state_lock: state["results"][t["id"]] = r
    threads = [threading.Thread(target=worker, args=(t,), daemon=True) for t in TARGETS]
    for th in threads: th.start()
    for th in threads: th.join()
    with state_lock: state["measuring"] = False

# ── HTML ──────────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🌍 Global Ping Monitor</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet"/>
<style>
/* ── TOKENS ── */
:root {
  --bg:       #08090f;
  --surface:  #0f1118;
  --surface2: #161922;
  --border:   rgba(255,255,255,0.07);
  --border2:  rgba(255,255,255,0.12);
  --text:     #e2e8f0;
  --muted:    rgba(226,232,240,0.45);
  --faint:    rgba(226,232,240,0.2);

  --c0: #22d3ee;   /* accent cyan */
  --c1: #34d399;   /* green  <20ms */
  --c2: #a3e635;   /* lime   <60ms */
  --c3: #fbbf24;   /* amber  <150ms */
  --c4: #fb923c;   /* orange <300ms */
  --c5: #f43f5e;   /* red    >300ms / offline */

  --sidebar: 320px;
  --hdr: 58px;
}

* { margin:0; padding:0; box-sizing:border-box; }
html, body { height:100%; background:var(--bg); font-family:'DM Sans',sans-serif; color:var(--text); overflow:hidden; }

/* ══ HEADER ══════════════════════════════════════════════════════════════════ */
#hdr {
  position:fixed; top:0; left:0; right:0; height:var(--hdr);
  background:rgba(8,9,15,0.96);
  border-bottom:1px solid var(--border);
  backdrop-filter:blur(20px);
  display:flex; align-items:center; padding:0 20px; gap:16px;
  z-index:1000;
}

.brand {
  display:flex; align-items:center; gap:10px; flex-shrink:0;
}
.brand-icon {
  width:32px; height:32px; border-radius:8px;
  background:linear-gradient(135deg,#0ea5e9,#6366f1);
  display:flex; align-items:center; justify-content:center;
  font-size:15px;
  box-shadow:0 0 16px rgba(99,102,241,0.4);
}
.brand-name {
  font-family:'Syne',sans-serif; font-size:1rem; font-weight:700;
  letter-spacing:-.01em; color:var(--text);
  white-space:nowrap;
}
.brand-tag {
  font-size:.62rem; font-weight:500;
  color:var(--muted); letter-spacing:.06em;
  text-transform:uppercase; margin-top:1px;
}

.hdr-sep { width:1px; height:24px; background:var(--border2); flex-shrink:0; }

.origin-chip {
  display:flex; align-items:center; gap:8px; flex-shrink:0;
  background:var(--surface2); border:1px solid var(--border);
  border-radius:8px; padding:5px 11px;
}
.origin-dot-live {
  width:7px; height:7px; border-radius:50%;
  background:var(--c1); box-shadow:0 0 6px var(--c1);
  animation:livepulse 2s ease-in-out infinite;
}
@keyframes livepulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.65)}}
.origin-label { font-family:'DM Mono',monospace; font-size:.7rem; color:var(--muted); }
.origin-label span { color:var(--c0); }

.hdr-stats { display:flex; gap:6px; flex:1; justify-content:center; }
.hstat {
  display:flex; flex-direction:column; align-items:center;
  background:var(--surface2); border:1px solid var(--border);
  border-radius:8px; padding:5px 14px; min-width:72px;
}
.hstat-l { font-size:.52rem; color:var(--faint); text-transform:uppercase; letter-spacing:.08em; }
.hstat-v { font-family:'DM Mono',monospace; font-size:.78rem; color:var(--c0); line-height:1.3; }

.hdr-right { display:flex; align-items:center; gap:10px; flex-shrink:0; }

#btn-measure {
  display:flex; align-items:center; gap:6px;
  background:linear-gradient(135deg,#0ea5e9,#6366f1);
  border:none; border-radius:8px; padding:7px 14px;
  color:#fff; font-family:'DM Sans',sans-serif; font-size:.78rem; font-weight:500;
  cursor:pointer; transition:opacity .15s, transform .1s;
  box-shadow:0 0 16px rgba(99,102,241,0.3);
  white-space:nowrap;
}
#btn-measure:hover { opacity:.88; }
#btn-measure:active { transform:scale(.97); }
#btn-measure:disabled { opacity:.35; cursor:not-allowed; }
#btn-measure .btn-icon { font-size:.9rem; }

.cd-ring {
  position:relative; width:34px; height:34px; flex-shrink:0;
}
.cd-ring svg { transform:rotate(-90deg); }
.cd-track { fill:none; stroke:var(--border2); stroke-width:2.5; }
.cd-arc   { fill:none; stroke:var(--c0); stroke-width:2.5; stroke-linecap:round;
  transition:stroke-dashoffset .9s linear; }
.cd-num {
  position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-family:'DM Mono',monospace; font-size:.62rem; color:var(--muted);
}

/* ══ LAYOUT ══════════════════════════════════════════════════════════════════ */
#layout {
  position:fixed; top:var(--hdr); left:0; right:0; bottom:0;
  display:flex;
}

/* ══ SIDEBAR ═════════════════════════════════════════════════════════════════ */
#sidebar {
  width:var(--sidebar); flex-shrink:0;
  background:var(--surface);
  border-right:1px solid var(--border);
  display:flex; flex-direction:column;
  overflow:hidden; z-index:10;
}

.sb-header {
  padding:14px 16px 10px;
  border-bottom:1px solid var(--border);
  flex-shrink:0;
}
.sb-title {
  font-family:'Syne',sans-serif; font-size:.78rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.1em; color:var(--muted);
}
.sb-filter {
  display:flex; gap:4px; margin-top:10px; flex-wrap:wrap;
}
.filter-btn {
  font-size:.6rem; padding:3px 8px; border-radius:5px;
  border:1px solid var(--border); background:transparent;
  color:var(--muted); cursor:pointer; transition:all .15s;
  font-family:'DM Sans',sans-serif;
}
.filter-btn:hover, .filter-btn.active {
  border-color:var(--c0); color:var(--c0); background:rgba(14,165,233,.08);
}

.sb-list {
  flex:1; overflow-y:auto; padding:8px 0;
  scrollbar-width:thin; scrollbar-color:var(--border2) transparent;
}
.sb-list::-webkit-scrollbar { width:4px; }
.sb-list::-webkit-scrollbar-thumb { background:var(--border2); border-radius:2px; }

.cont-group { margin-bottom:2px; }
.cont-label {
  font-size:.58rem; font-weight:600; letter-spacing:.1em; text-transform:uppercase;
  color:var(--faint); padding:10px 16px 4px;
  display:flex; align-items:center; justify-content:space-between;
}
.cont-avg {
  font-family:'DM Mono',monospace; font-size:.62rem; font-weight:400;
}

.sb-row {
  display:flex; align-items:center; gap:10px;
  padding:7px 16px; cursor:pointer;
  transition:background .12s; border-radius:0;
  position:relative;
}
.sb-row:hover { background:var(--surface2); }
.sb-row.active { background:rgba(14,165,233,.06); }
.sb-row.active::before {
  content:''; position:absolute; left:0; top:0; bottom:0;
  width:2px; background:var(--c0); border-radius:0 2px 2px 0;
}

.sb-flag { font-size:1rem; flex-shrink:0; width:22px; text-align:center; }
.sb-info { flex:1; min-width:0; }
.sb-city { font-size:.74rem; font-weight:500; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sb-org  { font-size:.6rem; color:var(--muted); margin-top:1px; }

.sb-ping { flex-shrink:0; text-align:right; }
.sb-ms {
  font-family:'DM Mono',monospace; font-size:.78rem; font-weight:500;
  line-height:1;
}
.sb-bar-wrap { width:40px; height:3px; background:var(--border); border-radius:2px; margin-top:3px; overflow:hidden; }
.sb-bar { height:100%; border-radius:2px; transition:width .5s ease; }

.sb-footer {
  padding:12px 16px;
  border-top:1px solid var(--border);
  flex-shrink:0;
}
.sb-footer-title {
  font-size:.6rem; text-transform:uppercase; letter-spacing:.1em;
  color:var(--faint); margin-bottom:8px;
}
.legend-grid { display:flex; flex-direction:column; gap:5px; }
.legend-row { display:flex; align-items:center; gap:8px; font-size:.65rem; color:var(--muted); }
.legend-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.legend-info { margin-left:auto; font-family:'DM Mono',monospace; font-size:.6rem; color:var(--faint); }

/* ══ MAP ═════════════════════════════════════════════════════════════════════ */
#map-wrap { flex:1; position:relative; overflow:hidden; }
#map { position:absolute; inset:0; }

.leaflet-tile { filter:brightness(.75) saturate(.5) hue-rotate(195deg) contrast(1.05); transition:filter .3s; }

/* ── MAP BRIGHTNESS SLIDER ── */
#map-controls {
  position:absolute; bottom:20px; right:16px; z-index:999;
  background:var(--surface); border:1px solid var(--border2);
  border-radius:10px; padding:10px 14px;
  display:flex; flex-direction:column; gap:6px;
  box-shadow:0 4px 20px rgba(0,0,0,.4);
  min-width:170px;
}
.mc-label {
  font-size:.58rem; text-transform:uppercase; letter-spacing:.1em;
  color:var(--faint); display:flex; justify-content:space-between; align-items:center;
}
.mc-label span { color:var(--muted); font-family:'DM Mono',monospace; font-size:.65rem; }
input[type=range].mc-slider {
  -webkit-appearance:none; appearance:none;
  width:100%; height:3px;
  background:var(--border2); border-radius:2px; outline:none; cursor:pointer;
}
input[type=range].mc-slider::-webkit-slider-thumb {
  -webkit-appearance:none; appearance:none;
  width:14px; height:14px; border-radius:50%;
  background:var(--c0); box-shadow:0 0 6px var(--c0); cursor:pointer;
  transition:transform .15s;
}
input[type=range].mc-slider::-webkit-slider-thumb:hover { transform:scale(1.3); }
input[type=range].mc-slider::-moz-range-thumb {
  width:14px; height:14px; border-radius:50%; border:none;
  background:var(--c0); cursor:pointer;
}
.leaflet-container:focus { outline:none; }
.leaflet-control-zoom {
  border:1px solid var(--border2) !important;
  border-radius:10px !important; overflow:hidden;
  box-shadow:0 4px 16px rgba(0,0,0,.4) !important;
}
.leaflet-control-zoom a {
  background:var(--surface) !important; border:none !important;
  color:var(--muted) !important; font-size:14px !important;
  width:30px !important; height:30px !important; line-height:30px !important;
}
.leaflet-control-zoom a:hover { background:var(--surface2) !important; color:var(--c0) !important; }
.leaflet-control-attribution {
  background:rgba(8,9,15,.8) !important; color:rgba(255,255,255,.2) !important;
  font-size:8px !important; border-radius:4px 0 0 0 !important;
}
.leaflet-control-attribution a { color:rgba(14,165,233,.4) !important; }

/* ARC SVG */
#arc-svg {
  position:absolute; inset:0; width:100%; height:100%;
  pointer-events:none; z-index:400; overflow:visible;
}
@keyframes flow { to { stroke-dashoffset: -200; } }

/* ── MAP MARKER ── */
.mpin { position:relative; cursor:pointer; }
.mpin-outer {
  width:28px; height:28px; border-radius:50%;
  border:1.5px solid currentColor; opacity:.5;
  animation:mring 2.5s ease-in-out infinite;
  position:absolute; inset:0;
}
.mpin-ripple {
  position:absolute; inset:-12px; border-radius:50%;
  border:1px solid currentColor; opacity:0;
  animation:mripple 2.5s ease-out infinite;
}
@keyframes mring   { 0%,100%{transform:scale(1);opacity:.5}  50%{transform:scale(1.2);opacity:.9} }
@keyframes mripple { 0%{transform:scale(.5);opacity:.6} 100%{transform:scale(2.2);opacity:0} }
.mpin-core {
  position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center;
}
.mpin-dot {
  width:9px; height:9px; border-radius:50%;
  background:currentColor;
  box-shadow:0 0 8px currentColor, 0 0 20px currentColor;
  transition:transform .2s;
}
.mpin:hover .mpin-dot { transform:scale(1.9); }

/* Label bubble */
.mpin-label {
  position:absolute; left:50%; transform:translateX(-50%);
  pointer-events:none; white-space:nowrap;
  display:flex; flex-direction:column; align-items:center; gap:2px;
}
.mpin-label.above { bottom:calc(100% + 6px); }
.mpin-label.below { top:calc(100% + 6px); }

.mpin-ms-badge {
  background:rgba(8,9,15,.92);
  border:1px solid rgba(255,255,255,.1);
  border-radius:6px; padding:3px 7px;
  font-family:'DM Mono',monospace; font-size:.75rem; font-weight:500;
  text-shadow:0 0 10px currentColor;
  line-height:1.2;
}
.mpin-city-badge {
  font-family:'DM Sans',sans-serif;
  font-size:.55rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
  color:rgba(226,232,240,.55);
  background:rgba(8,9,15,.75); border-radius:4px; padding:1px 5px;
}
.mpin-stem { width:1px; height:7px; background:currentColor; opacity:.3; }

/* ── ORIGIN PIN ── */
.opin {
  position:relative; display:flex; align-items:center; justify-content:center;
  width:36px; height:36px;
}
.opin-glow {
  position:absolute; inset:-4px; border-radius:50%;
  background:radial-gradient(circle,rgba(14,165,233,.25),transparent 70%);
  animation:oglow 2s ease-in-out infinite;
}
@keyframes oglow { 0%,100%{opacity:.6} 50%{opacity:1} }
.opin-ring {
  position:absolute; inset:0; border-radius:50%;
  border:2px solid rgba(14,165,233,.6);
  animation:mring 1.8s ease-in-out infinite;
}
.opin-dot {
  width:14px; height:14px; border-radius:50%;
  background:var(--c0);
  box-shadow:0 0 14px var(--c0), 0 0 32px rgba(14,165,233,.5);
  position:relative; z-index:2;
}
.opin-label {
  position:absolute; top:calc(100%+4px); left:50%; transform:translateX(-50%);
  background:rgba(8,9,15,.9); border:1px solid rgba(14,165,233,.3);
  border-radius:5px; padding:2px 7px;
  font-family:'DM Mono',monospace; font-size:.58rem;
  color:var(--c0); white-space:nowrap;
}

/* ── MEASURING OVERLAY ── */
#measuring-overlay {
  position:absolute; inset:0; z-index:800;
  background:rgba(8,9,15,.6); backdrop-filter:blur(4px);
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:16px;
  opacity:0; pointer-events:none; transition:opacity .4s;
}
#measuring-overlay.active { opacity:1; pointer-events:all; }

.meas-card {
  background:var(--surface); border:1px solid var(--border2);
  border-radius:16px; padding:28px 36px;
  display:flex; flex-direction:column; align-items:center; gap:14px;
  box-shadow:0 24px 60px rgba(0,0,0,.5);
}
.meas-spinner {
  width:40px; height:40px; border-radius:50%;
  border:2px solid var(--border2);
  border-top-color:var(--c0);
  animation:spin .8s linear infinite;
}
@keyframes spin { to { transform:rotate(360deg); } }
.meas-title {
  font-family:'Syne',sans-serif; font-size:1.05rem; font-weight:700;
  color:var(--text);
}
.meas-sub { font-size:.75rem; color:var(--muted); }
.meas-bar-wrap {
  width:220px; height:4px; background:var(--border);
  border-radius:2px; overflow:hidden;
}
.meas-bar-fill {
  height:100%; border-radius:2px;
  background:linear-gradient(90deg,#0ea5e9,#6366f1);
  transition:width .3s ease; width:0%;
  box-shadow:0 0 8px rgba(14,165,233,.5);
}
.meas-count { font-family:'DM Mono',monospace; font-size:.7rem; color:var(--muted); }

/* ── TOOLTIP ── */
#tt {
  position:fixed; z-index:2000;
  background:var(--surface); border:1px solid var(--border2);
  border-radius:12px; padding:14px 16px;
  pointer-events:none; opacity:0; transition:opacity .12s;
  min-width:230px;
  box-shadow:0 16px 40px rgba(0,0,0,.5);
}
#tt.vis { opacity:1; }
.tt-header { display:flex; align-items:center; gap:8px; margin-bottom:10px; }
.tt-flag { font-size:1.3rem; }
.tt-hinfo {}
.tt-city { font-family:'Syne',sans-serif; font-size:.95rem; font-weight:700; color:var(--text); }
.tt-org  { font-size:.65rem; color:var(--muted); margin-top:1px; }
.tt-divider { height:1px; background:var(--border); margin:8px 0; }
.tt-row { display:flex; justify-content:space-between; align-items:center; margin-top:5px; font-size:.7rem; }
.tt-row-label { color:var(--muted); }
.tt-row-val   { font-family:'DM Mono',monospace; font-weight:500; }
.tt-bigping {
  text-align:center; padding:8px 0;
  font-family:'DM Mono',monospace; font-size:1.8rem; font-weight:500;
  line-height:1;
}
.tt-qual {
  text-align:center; font-size:.68rem; font-weight:500;
  padding:4px 10px; border-radius:5px; margin:0 auto;
  background:rgba(255,255,255,.05);
}
.tt-samples { font-size:.58rem; color:var(--faint); text-align:center; margin-top:4px; }

/* ── TOAST ── */
#toast {
  position:fixed; bottom:24px; left:50%; transform:translateX(-50%);
  background:var(--surface); border:1px solid var(--border2);
  border-radius:10px; padding:10px 20px;
  font-size:.78rem; color:var(--text);
  box-shadow:0 8px 24px rgba(0,0,0,.4);
  opacity:0; pointer-events:none; transition:opacity .3s;
  z-index:3000; white-space:nowrap;
}
#toast.vis { opacity:1; }
</style>
</head>
<body>

<!-- ═══ HEADER ═══ -->
<div id="hdr">
  <div class="brand">
    <div class="brand-icon">🌍</div>
    <div>
      <div class="brand-name">Global Ping Monitor</div>
      <div class="brand-tag">Netzwerk-Latenz weltweit</div>
    </div>
  </div>

  <div class="hdr-sep"></div>

  <div class="origin-chip">
    <div class="origin-dot-live"></div>
    <div class="origin-label">Von: <span id="myip">…</span> &nbsp;·&nbsp; <span id="mycity">…</span></div>
  </div>

  <div class="hdr-sep"></div>

  <div class="hdr-stats">
    <div class="hstat">
      <span class="hstat-l">Online</span>
      <span class="hstat-v" id="s-onl">—</span>
    </div>
    <div class="hstat">
      <span class="hstat-l">Schnellstes</span>
      <span class="hstat-v" id="s-best" style="color:var(--c1)">—</span>
    </div>
    <div class="hstat">
      <span class="hstat-l">Ø Latenz</span>
      <span class="hstat-v" id="s-avg">—</span>
    </div>
    <div class="hstat">
      <span class="hstat-l">Weitestes</span>
      <span class="hstat-v" id="s-worst" style="color:var(--c4)">—</span>
    </div>
    <div class="hstat">
      <span class="hstat-l">Runde</span>
      <span class="hstat-v" id="s-rnd">—</span>
    </div>
  </div>

  <div class="hdr-sep"></div>

  <div class="hdr-right">
    <button id="btn-measure" onclick="triggerMeasure()">
      <span class="btn-icon">⚡</span> Jetzt messen
    </button>
    <div class="cd-ring">
      <svg width="34" height="34" viewBox="0 0 34 34">
        <circle class="cd-track" cx="17" cy="17" r="14"/>
        <circle class="cd-arc" id="cd-arc" cx="17" cy="17" r="14"
          stroke-dasharray="87.96" stroke-dashoffset="0"/>
      </svg>
      <div class="cd-num" id="cd-num">—</div>
    </div>
  </div>
</div>

<!-- ═══ LAYOUT ═══ -->
<div id="layout">

  <!-- ═══ SIDEBAR ═══ -->
  <div id="sidebar">
    <div class="sb-header">
      <div class="sb-title">Server-Liste</div>
      <div class="sb-filter" id="filter-btns">
        <button class="filter-btn active" data-cont="Alle">Alle</button>
        <button class="filter-btn" data-cont="Europa">Europa</button>
        <button class="filter-btn" data-cont="Nordamerika">N.Amerika</button>
        <button class="filter-btn" data-cont="Asien">Asien</button>
        <button class="filter-btn" data-cont="Südamerika">S.Amerika</button>
        <button class="filter-btn" data-cont="Afrika">Afrika</button>
        <button class="filter-btn" data-cont="Ozeanien">Ozeanien</button>
        <button class="filter-btn" data-cont="Naher Osten">Naher O.</button>
      </div>
    </div>

    <div class="sb-list" id="sb-list"></div>

    <div class="sb-footer">
      <div class="sb-footer-title">Was bedeuten die Farben?</div>
      <div class="legend-grid">
        <div class="legend-row">
          <div class="legend-dot" style="background:var(--c1)"></div>
          <span>Sehr schnell</span>
          <span class="legend-info">&lt; 20ms</span>
        </div>
        <div class="legend-row">
          <div class="legend-dot" style="background:var(--c2)"></div>
          <span>Schnell</span>
          <span class="legend-info">20–60ms</span>
        </div>
        <div class="legend-row">
          <div class="legend-dot" style="background:var(--c3)"></div>
          <span>Mittel</span>
          <span class="legend-info">60–150ms</span>
        </div>
        <div class="legend-row">
          <div class="legend-dot" style="background:var(--c4)"></div>
          <span>Langsam</span>
          <span class="legend-info">150–300ms</span>
        </div>
        <div class="legend-row">
          <div class="legend-dot" style="background:var(--c5)"></div>
          <span>Sehr langsam / Offline</span>
          <span class="legend-info">&gt; 300ms</span>
        </div>
      </div>
      <div style="margin-top:10px;font-size:.58rem;color:var(--faint);line-height:1.6">
        📡 Messmethode: TCP SYN→ACK (Port 443) zu regionalen Unicast-Servern von AWS, Vultr & Hetzner. Kein Anycast. Median aus 3 Messungen.
      </div>
    </div>
  </div>

  <!-- ═══ MAP ═══ -->
  <div id="map-wrap">
    <div id="map"></div>

    <!-- Map brightness controls -->
    <div id="map-controls">
      <div class="mc-label">🌍 Karte <span id="bright-val">75%</span></div>
      <input type="range" class="mc-slider" id="bright-slider" min="20" max="100" value="75"
        oninput="updateMapFilter(this.value)"/>
      <div class="mc-label">🎨 Farbe <span id="sat-val">50%</span></div>
      <input type="range" class="mc-slider" id="sat-slider" min="0" max="100" value="50"
        oninput="updateMapFilter(null, this.value)"/>
    </div>

    <div id="measuring-overlay">
      <div class="meas-card">
        <div class="meas-spinner"></div>
        <div class="meas-title">Verbindungen werden gemessen…</div>
        <div class="meas-sub" id="meas-sub">Bereite Messung vor</div>
        <div class="meas-bar-wrap">
          <div class="meas-bar-fill" id="meas-fill"></div>
        </div>
        <div class="meas-count" id="meas-count">0 / 0</div>
      </div>
    </div>
  </div>

</div>

<!-- ═══ TOOLTIP ═══ -->
<div id="tt">
  <div class="tt-header">
    <div class="tt-flag" id="tt-flag"></div>
    <div class="tt-hinfo">
      <div class="tt-city" id="tt-city"></div>
      <div class="tt-org"  id="tt-org"></div>
    </div>
  </div>
  <div class="tt-bigping" id="tt-bigping">—</div>
  <div class="tt-qual" id="tt-qual"></div>
  <div class="tt-divider"></div>
  <div class="tt-row"><span class="tt-row-label">IP-Adresse</span><span class="tt-row-val" id="tt-ip"></span></div>
  <div class="tt-row"><span class="tt-row-label">Kontinent</span><span class="tt-row-val" id="tt-cont"></span></div>
  <div class="tt-row"><span class="tt-row-label">Entfernung</span><span class="tt-row-val" id="tt-dist"></span></div>
  <div class="tt-samples" id="tt-samples"></div>
</div>

<!-- ═══ TOAST ═══ -->
<div id="toast"></div>

<script>
/* ── MAP FILTER ── */
let mapBright = 75, mapSat = 50;
function updateMapFilter(bright, sat) {
  if (bright !== null && bright !== undefined) mapBright = bright;
  if (sat    !== null && sat    !== undefined) mapSat    = sat;
  const style = document.createElement('style');
  style.id = 'tile-filter-override';
  const f = `brightness(${mapBright/100}) saturate(${mapSat/100}) hue-rotate(195deg) contrast(1.05)`;
  style.textContent = `.leaflet-tile { filter:${f} !important; }`;
  const existing = document.getElementById('tile-filter-override');
  if (existing) existing.remove();
  document.head.appendChild(style);
  document.getElementById('bright-val').textContent = mapBright + '%';
  document.getElementById('sat-val').textContent    = mapSat    + '%';
}

/* ── CONFIG ── */
const INTERVAL = 10;
const CIRC = 2 * Math.PI * 14; // svg circle circumference

/* ── STATE ── */
let map, originMarker, markers = {}, lastData = null;
let lastRound = -1, wasMapInit = false, wasMeasuring = false;
let countdown = INTERVAL, cdInt = null, lastResultCount = 0;
let activeFilter = 'Alle', activeId = null;

/* ── COLOR ── */
function pingColor(ms, online) {
  if (!online || ms === null) return 'var(--c5)';
  if (ms < 20)  return 'var(--c1)';
  if (ms < 60)  return 'var(--c2)';
  if (ms < 150) return 'var(--c3)';
  if (ms < 300) return 'var(--c4)';
  return 'var(--c5)';
}
function pingColorHex(ms, online) {
  if (!online || ms === null) return '#f43f5e';
  if (ms < 20)  return '#34d399';
  if (ms < 60)  return '#a3e635';
  if (ms < 150) return '#fbbf24';
  if (ms < 300) return '#fb923c';
  return '#f43f5e';
}
function qualLabel(ms, online) {
  if (!online || ms === null) return 'Nicht erreichbar';
  if (ms < 20)  return '⚡ Sehr schnell';
  if (ms < 60)  return '✓ Schnell';
  if (ms < 150) return '~ Mittel';
  if (ms < 300) return '↓ Langsam';
  return '✗ Sehr langsam';
}

/* ── DISTANCE ── */
function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)**2;
  return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)));
}

/* ── MAP INIT ── */
function initMap(lat, lon) {
  map = L.map('map', { center:[lat,lon], zoom:3, minZoom:2, maxZoom:12, zoomControl:true });
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution:'&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org/copyright">OSM</a>',
    subdomains:'abcd', maxZoom:19
  }).addTo(map);

  // SVG arc layer
  const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.id = 'arc-svg';
  document.getElementById('map-wrap').appendChild(svg);
  map.on('move zoom moveend zoomend', drawArcs);
}

/* ── ORIGIN ── */
function placeOrigin(lat, lon, city) {
  const html = `<div class="opin">
    <div class="opin-glow"></div><div class="opin-ring"></div>
    <div class="opin-dot"></div>
    <div class="opin-label">📍 ${city}</div>
  </div>`;
  const icon = L.divIcon({ className:'', html, iconSize:[36,36], iconAnchor:[18,18] });
  if (originMarker) originMarker.setLatLng([lat,lon]).setIcon(icon);
  else originMarker = L.marker([lat,lon], {icon, zIndexOffset:1000}).addTo(map);
}

/* ── MARKER ── */
function buildIcon(t, res) {
  const ms = res ? res.ms : null;
  const online = res ? res.online : false;
  const color  = pingColorHex(ms, online);
  const msText = res === null ? '…' : (ms === null ? 'offline' : ms + 'ms');
  const lblPos = t.lat > 10 ? 'below' : 'above';
  const html = `<div class="mpin" style="color:${color};width:28px;height:28px;">
    <div class="mpin-outer"></div>
    <div class="mpin-ripple"></div>
    <div class="mpin-core"><div class="mpin-dot"></div></div>
    <div class="mpin-label ${lblPos}">
      ${lblPos==='above' ? '<div class="mpin-stem"></div>' : ''}
      <div class="mpin-ms-badge">${msText}</div>
      <div class="mpin-city-badge">${t.flag} ${t.city}</div>
      ${lblPos==='below' ? '<div class="mpin-stem" style="order:-1"></div>' : ''}
    </div>
  </div>`;
  return L.divIcon({ className:'', html, iconSize:[28,28], iconAnchor:[14,14] });
}

function renderMarkers(targets, results) {
  targets.forEach(t => {
    const res  = results[t.id] || null;
    const icon = buildIcon(t, res);
    if (markers[t.id]) {
      markers[t.id].setIcon(icon);
      markers[t.id].off('mouseover').on('mouseover', e => showTT(e.originalEvent, t, res));
    } else {
      const m = L.marker([t.lat, t.lon], {icon, zIndexOffset:100}).addTo(map);
      m.on('mouseover', e => showTT(e.originalEvent, t, res));
      m.on('mousemove',  e => moveTT(e.originalEvent));
      m.on('mouseout',  () => hideTT());
      m.on('click', () => focusRow(t.id));
      markers[t.id] = m;
    }
  });
}

/* ── ARCS ── */
function drawArcs() {
  const svg = document.getElementById('arc-svg');
  if (!svg || !map || !lastData) return;
  svg.innerHTML = '';
  const { my_lat, my_lon, results, targets } = lastData;
  const op = map.latLngToContainerPoint([my_lat, my_lon]);
  targets.forEach(t => {
    const res   = results[t.id];
    const color = res ? pingColorHex(res.ms, res.online) : 'rgba(255,255,255,.06)';
    const alpha = (res && res.online) ? 0.28 : 0.04;
    const dp = map.latLngToContainerPoint([t.lat, t.lon]);
    const dx = dp.x - op.x, dy = dp.y - op.y;
    const dist = Math.sqrt(dx*dx + dy*dy) || 1;
    const curv = Math.min(dist * 0.22, 100);
    const mx = (op.x+dp.x)/2 - dy*(curv/dist);
    const my = (op.y+dp.y)/2 + dx*(curv/dist) - curv;
    const path = document.createElementNS('http://www.w3.org/2000/svg','path');
    path.setAttribute('d', `M${op.x},${op.y} Q${mx},${my} ${dp.x},${dp.y}`);
    path.setAttribute('fill','none');
    path.setAttribute('stroke', color);
    path.setAttribute('stroke-width', '1.2');
    path.setAttribute('stroke-opacity', alpha);
    path.setAttribute('stroke-dasharray','4 10');
    path.style.animation = `flow ${13+Math.random()*9}s linear infinite`;
    svg.appendChild(path);
  });
}

/* ── SIDEBAR ── */
function buildSidebar(data) {
  const { results, targets, my_lat, my_lon } = data;

  // Group by continent
  const groups = {};
  targets.forEach(t => {
    if (activeFilter !== 'Alle' && t.cont !== activeFilter) return;
    if (!groups[t.cont]) groups[t.cont] = [];
    groups[t.cont].push(t);
  });

  // Sort each group by ping
  Object.values(groups).forEach(arr => {
    arr.sort((a, b) => {
      const ra = results[a.id], rb = results[b.id];
      const ma = ra && ra.online ? ra.ms : 99999;
      const mb = rb && rb.online ? rb.ms : 99999;
      return ma - mb;
    });
  });

  const contOrder = ['Europa','Nordamerika','Asien','Südamerika','Afrika','Naher Osten','Ozeanien'];
  let html = '';

  contOrder.forEach(cont => {
    const rows = groups[cont];
    if (!rows || !rows.length) return;

    // Avg for continent
    const pings = rows.map(t => results[t.id]).filter(r => r && r.online).map(r => r.ms);
    const avg   = pings.length ? Math.round(pings.reduce((a,b)=>a+b,0)/pings.length) : null;
    const avgColor = avg !== null ? pingColorHex(avg, true) : '#666';

    html += `<div class="cont-group">
      <div class="cont-label">
        <span>${cont}</span>
        <span class="cont-avg" style="color:${avgColor}">${avg !== null ? 'Ø '+avg+'ms' : '…'}</span>
      </div>`;

    rows.forEach(t => {
      const res = results[t.id] || null;
      const ms  = res ? res.ms : null;
      const online = res ? res.online : false;
      const color  = pingColorHex(ms, online);
      const msText = res === null ? '…' : (ms === null ? 'offline' : ms+'ms');
      const barPct = (ms && online) ? Math.min(100, ms/400*100) : (res ? 100 : 0);
      const dist   = Math.round(haversine(my_lat, my_lon, t.lat, t.lon));
      const isActive = t.id === activeId;

      html += `<div class="sb-row${isActive?' active':''}" data-id="${t.id}"
          onclick="rowClick('${t.id}',${t.lat},${t.lon})">
        <div class="sb-flag">${t.flag}</div>
        <div class="sb-info">
          <div class="sb-city">${t.city}, ${t.country}</div>
          <div class="sb-org">${t.org} · ${dist.toLocaleString()} km</div>
        </div>
        <div class="sb-ping">
          <div class="sb-ms" style="color:${color}">${msText}</div>
          <div class="sb-bar-wrap">
            <div class="sb-bar" style="width:${barPct}%;background:${color}"></div>
          </div>
        </div>
      </div>`;
    });

    html += `</div>`;
  });

  document.getElementById('sb-list').innerHTML = html;
}

function rowClick(id, lat, lon) {
  activeId = id;
  map.flyTo([lat, lon], 6, { animate: true, duration: 1 });
  // Rebuild sidebar to show active state
  if (lastData) buildSidebar(lastData);
}
function focusRow(id) {
  activeId = id;
  const el = document.querySelector(`[data-id="${id}"]`);
  if (el) el.scrollIntoView({ behavior:'smooth', block:'nearest' });
  if (lastData) buildSidebar(lastData);
}

/* ── FILTER ── */
document.getElementById('filter-btns').addEventListener('click', e => {
  const btn = e.target.closest('.filter-btn');
  if (!btn) return;
  activeFilter = btn.dataset.cont;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.toggle('active', b===btn));
  if (lastData) buildSidebar(lastData);
});

/* ── STATS ── */
function updateStats(data) {
  const all    = Object.values(data.results);
  const online = all.filter(r => r.online && r.ms !== null);
  document.getElementById('s-onl').textContent  = online.length + '/' + data.targets.length;
  document.getElementById('s-rnd').textContent  = data.round;
  if (!online.length) return;
  const pings = online.map(r => r.ms);
  const avg   = Math.round(pings.reduce((a,b)=>a+b,0)/pings.length);
  document.getElementById('s-avg').textContent   = avg + 'ms';
  document.getElementById('s-best').textContent  = Math.min(...pings) + 'ms';
  document.getElementById('s-worst').textContent = Math.max(...pings) + 'ms';
}

/* ── TOOLTIP ── */
function showTT(e, t, res) {
  const ms     = res ? res.ms : null;
  const online = res ? res.online : false;
  const color  = pingColor(ms, online);
  const colorH = pingColorHex(ms, online);
  document.getElementById('tt-flag').textContent = t.flag;
  document.getElementById('tt-city').textContent = `${t.city}, ${t.country}`;
  document.getElementById('tt-org').textContent  = t.org + ' · ' + t.cont;
  document.getElementById('tt-bigping').textContent = ms !== null ? ms+'ms' : (res ? 'offline' : '…');
  document.getElementById('tt-bigping').style.color = colorH;
  document.getElementById('tt-qual').textContent    = qualLabel(ms, online);
  document.getElementById('tt-qual').style.color    = colorH;
  document.getElementById('tt-ip').textContent  = (res && res.ip) || t.host;
  document.getElementById('tt-cont').textContent = t.cont;
  if (lastData) {
    const dist = haversine(lastData.my_lat, lastData.my_lon, t.lat, t.lon);
    document.getElementById('tt-dist').textContent = dist.toLocaleString() + ' km';
  }
  const samples = res && res.samples || [];
  document.getElementById('tt-samples').textContent =
    samples.length > 1 ? 'Messungen: ' + samples.map(s=>s+'ms').join(' · ') : '';
  document.getElementById('tt').classList.add('vis');
  moveTT(e);
}
function moveTT(e) {
  const tt = document.getElementById('tt');
  let x = e.clientX + 20, y = e.clientY - 16;
  if (x + 250 > window.innerWidth)  x = e.clientX - 260;
  if (y + 260 > window.innerHeight) y = e.clientY - 265;
  tt.style.left = x+'px'; tt.style.top = y+'px';
}
function hideTT() { document.getElementById('tt').classList.remove('vis'); }

/* ── COUNTDOWN RING ── */
function startCD(secs) {
  clearInterval(cdInt);
  countdown = secs;
  const arc = document.getElementById('cd-arc');
  const num = document.getElementById('cd-num');
  cdInt = setInterval(() => {
    countdown--;
    const pct = Math.max(0, countdown / INTERVAL);
    arc.style.strokeDashoffset = CIRC * (1 - pct);
    num.textContent = countdown > 0 ? countdown : '';
    if (countdown <= 0) { clearInterval(cdInt); }
  }, 1000);
  arc.style.strokeDashoffset = 0;
  num.textContent = secs;
}

/* ── MEASURING OVERLAY ── */
function showMeasuring(done, total) {
  document.getElementById('measuring-overlay').classList.add('active');
  document.getElementById('meas-fill').style.width = Math.round(done/total*100)+'%';
  document.getElementById('meas-sub').textContent = done===0 ? 'Verbindungen werden aufgebaut…' : `${done} von ${total} fertig`;
  document.getElementById('meas-count').textContent = `${done} / ${total}`;
}
function hideMeasuring() {
  document.getElementById('measuring-overlay').classList.remove('active');
  document.getElementById('meas-fill').style.width = '0%';
}

/* ── TOAST ── */
function toast(msg, dur=3000) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('vis');
  setTimeout(() => el.classList.remove('vis'), dur);
}

/* ── API ── */
async function fetchState() {
  try { return await (await fetch('/api/state')).json(); }
  catch { return null; }
}
async function triggerMeasure() {
  document.getElementById('btn-measure').disabled = true;
  toast('⚡ Messung gestartet…');
  await fetch('/api/measure').catch(() => {});
}

/* ── POLL LOOP ── */
async function poll() {
  const data = await fetchState();
  if (!data) { setTimeout(poll, 1200); return; }

  if (!wasMapInit) { initMap(data.my_lat, data.my_lon); wasMapInit = true; }

  document.getElementById('myip').textContent   = data.my_ip;
  document.getElementById('mycity').textContent = data.my_city;

  const done  = Object.keys(data.results).length;
  const total = data.targets.length;

  if (data.measuring) {
    showMeasuring(done, total);
    if (done > lastResultCount) {
      lastResultCount = done;
      lastData = data;
      renderMarkers(data.targets, data.results);
      buildSidebar(data);
      drawArcs();
    }
  }

  if (data.measuring && !wasMeasuring) {
    showMeasuring(0, total);
  }
  if (!data.measuring && wasMeasuring) {
    hideMeasuring();
    lastResultCount = 0;
    document.getElementById('btn-measure').disabled = false;
    const online = Object.values(data.results).filter(r=>r.online).length;
    toast(`✓ Messung abgeschlossen · ${online}/${total} Server erreichbar`);
  }
  wasMeasuring = data.measuring;

  if (data.round !== lastRound && !data.measuring) {
    lastRound = data.round;
    lastData  = data;
    placeOrigin(data.my_lat, data.my_lon, data.my_city);
    renderMarkers(data.targets, data.results);
    buildSidebar(data);
    drawArcs();
    updateStats(data);
    startCD(INTERVAL);
  }

  setTimeout(poll, 600);
}

poll();
</script>
</body>
</html>
"""

# ── HTTP HANDLER ──────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path == '/':
            self._send(200, 'text/html; charset=utf-8', HTML.encode())
        elif self.path == '/api/state':
            with state_lock:
                payload = {
                    "results":   state["results"],
                    "my_ip":     state["my_ip"],
                    "my_lat":    state["my_lat"],
                    "my_lon":    state["my_lon"],
                    "my_city":   state["my_city"],
                    "measuring": state["measuring"],
                    "round":     state["round"],
                    "targets":   state["targets"],
                }
            self._send(200, 'application/json', json.dumps(payload).encode())
        elif self.path == '/api/measure':
            with state_lock:
                busy = state["measuring"]
            if not busy:
                threading.Thread(target=do_measure_round, daemon=True).start()
            self._send(200, 'application/json', b'{"ok":true}')
        else:
            self._send(404, 'text/plain', b'Not found')

    def _send(self, code, ct, body):
        self.send_response(code)
        self.send_header('Content-Type', ct)
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(body)

def auto_loop(interval):
    while True:
        time.sleep(interval)
        with state_lock:
            busy = state["measuring"]
        if not busy:
            do_measure_round()

def main():
    p = argparse.ArgumentParser(description="🌍 Global Ping Monitor")
    p.add_argument("--port",     type=int,   default=8765)
    p.add_argument("--interval", type=float, default=10.0, help="Sekunden zwischen Messungen")
    p.add_argument("--count",    type=int,   default=3,    help="Messungen pro Ziel (Median)")
    args = p.parse_args()
    state["ping_count"] = args.count

    print("\n  🌍  Global Ping Monitor")
    print("  " + "─"*36)
    print(f"  Zeigt die Verbindungszeit von deinem")
    print(f"  Rechner zu Servern in aller Welt.\n")

    print("  → Deinen Standort ermitteln …", end="", flush=True)
    ip  = get_my_ip()
    lat, lon, city = get_geo(ip)
    with state_lock:
        state.update({"my_ip":ip, "my_lat":lat, "my_lon":lon, "my_city":city})
    print(f" {ip} ({city})")

    print(f"  → DNS für {len(TARGETS)} Server auflösen …", end="", flush=True)
    resolve_all()
    resolved = sum(1 for v in resolved_ips.values() if v)
    print(f" {resolved}/{len(TARGETS)} OK")

    print(f"  → Erste Messung läuft …", end="", flush=True)
    do_measure_round()
    with state_lock:
        online = sum(1 for r in state["results"].values() if r["online"])
    print(f" {online}/{len(TARGETS)} Server erreichbar\n")

    threading.Thread(target=auto_loop, args=(args.interval,), daemon=True).start()

    url = f"http://localhost:{args.port}"
    print(f"  ✓  Browser öffnet sich …  {url}")
    print(f"  ✓  Alle {args.interval}s automatisch neu messen")
    print(f"  ✓  Strg+C zum Beenden\n")
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    try:
        HTTPServer(("", args.port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\n  Tschüss! 👋\n")

if __name__ == "__main__":
    main()