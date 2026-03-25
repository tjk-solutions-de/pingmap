# 🌍 pingmap

**Visualize your network latency to servers around the world — live, in your browser.**

pingmap measures how long your data packets take to travel from your machine to 40+ servers across every continent. It runs a local web server and displays an interactive world map with real-time results.

![pingmap screenshot](https://raw.githubusercontent.com/yourusername/pingmap/main/screenshot.png)

---

## ✨ Features

- **Real latency measurements** — TCP SYN/ACK timing (identical to ICMP ping, no `sudo` needed)
- **40+ servers** across 8 regions: Europe, North America, Asia, South America, Africa, Middle East, Oceania
- **No Anycast tricks** — all targets are geographically fixed unicast endpoints (AWS S3 regional, Vultr, Hetzner)
- **Live updating** — auto-refreshes every 10 seconds
- **Interactive map** — Leaflet.js with zoom, pan, animated arc lines
- **Sidebar with full server list** — sorted by latency, filterable by continent
- **Zero dependencies** — pure Python stdlib, no `pip install` needed

---

## 🚀 Quick Start

```bash
git clone https://github.com/yourusername/pingmap.git
cd pingmap
python3 ping_map.py
```

Your browser opens automatically. That's it.

---

## ⚙️ Options

```bash
python3 ping_map.py                    # default: port 8765, 10s interval, 3 pings/target
python3 ping_map.py --interval 15      # measure every 15 seconds
python3 ping_map.py --count 5          # 5 pings per target (more accurate median)
python3 ping_map.py --port 9000        # use a different port
```

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | `8765` | Local web server port |
| `--interval` | `10` | Seconds between measurement rounds |
| `--count` | `3` | Pings per target (median is used) |

---

## 🔬 How it works

### Why TCP instead of ICMP ping?

Classic `ping` uses ICMP Echo packets which require raw socket access (`sudo` on Linux/macOS). Instead, pingmap uses **TCP SYN timing**:

1. Open a TCP connection to port 443 on the target server
2. Measure time until SYN-ACK is received
3. Close the connection

The result is **identical to ICMP RTT** — it measures the same network round-trip time, just using TCP instead of ICMP.

### Why not ping `1.1.1.1` or `8.8.8.8`?

Those are **Anycast** addresses — the same IP exists on hundreds of servers worldwide. Your router automatically routes you to the *nearest* one. So from Berlin, Tokyo, and New York, `1.1.1.1` all respond in ~2ms from a local node. **That tells you nothing about global latency.**

pingmap uses **Unicast regional endpoints** instead:

| Provider | Example endpoint | Why it works |
|----------|-----------------|--------------|
| **AWS S3** | `s3.ap-northeast-1.amazonaws.com` | Resolves to a single Tokyo datacenter IP |
| **Vultr** | `hnd-jp-ping.vultr.com` | Dedicated ping host per location |
| **Hetzner** | `nbg1-speed.hetzner.com` | Fixed Nuremberg datacenter |
| **OVH** | `proof.ovh.net` | Strasbourg datacenter |

### Architecture

```
┌─────────────────────────────────────────────────┐
│  ping_map.py (Python)                           │
│                                                 │
│  ┌─────────────┐    ┌──────────────────────┐   │
│  │  Measurement │    │   HTTP Server        │   │
│  │  Engine      │    │   localhost:8765     │   │
│  │              │    │                      │   │
│  │  TCP SYN/ACK │───▶│  GET /          HTML │   │
│  │  parallel    │    │  GET /api/state JSON │   │
│  │  threads     │    │  GET /api/measure    │   │
│  └─────────────┘    └──────────────────────┘   │
└─────────────────────────────────────────────────┘
          ▲                        │
          │ poll every 600ms       │ serve
          │                        ▼
┌─────────────────────────────────────────────────┐
│  Browser (Leaflet.js map)                       │
│                                                 │
│  • CartoDB Dark Matter tiles                    │
│  • Animated SVG arc lines                       │
│  • Live marker updates as results arrive        │
│  • Sidebar sorted by latency                    │
└─────────────────────────────────────────────────┘
```

---

## 🌐 Server coverage

| Continent | Servers | Providers |
|-----------|---------|-----------|
| 🌍 Europe | 9 | AWS, Hetzner, OVH |
| 🌎 North America | 11 | AWS, Vultr |
| 🌏 Asia | 9 | AWS, Vultr |
| 🌎 South America | 3 | AWS, Vultr |
| 🌍 Africa | 2 | AWS, Vultr |
| 🌏 Middle East | 3 | AWS, Vultr |
| 🌏 Oceania | 3 | AWS, Vultr |

---

## 📊 Reading the results

| Color | Range | Meaning |
|-------|-------|---------|
| 🟢 Green | < 20ms | Same country / nearby datacenter |
| 🟡 Lime | 20–60ms | Same continent |
| 🟡 Amber | 60–150ms | Intercontinental |
| 🟠 Orange | 150–300ms | Far away |
| 🔴 Red | > 300ms | Very far / packet loss |

**Typical values from Central Europe:**
- Frankfurt: 5–15ms
- London/Paris: 15–30ms
- US East Coast: 80–110ms
- US West Coast: 130–160ms
- Tokyo: 220–260ms
- Sydney: 280–320ms

---

## 🛠 Requirements

- Python 3.6+
- No external packages needed (uses only stdlib: `socket`, `threading`, `http.server`, `json`)
- Internet connection
- Browser (opens automatically)

---

## 📄 License

MIT License — do whatever you want with it.

---

## 🤝 Contributing

Pull requests welcome! Ideas:

- [ ] Add more server locations
- [ ] Export results as CSV / JSON
- [ ] Historical latency graph per server
- [ ] Config file for custom targets
- [ ] `--lang en` flag for English UI
