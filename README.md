# Mormir Basic Thermal Printer

A Raspberry Pi-powered thermal printer that randomly prints Magic: The Gathering creature cards based on mana cost (CMC). Built for the Mormir Basic format — press a button to pick your CMC, press another to print a random creature at that cost.

---

## How It Works

Card images are pre-downloaded and sorted into folders by CMC. When you press the print button, the Pi picks a random image from the chosen CMC folder and sends it to a thermal printer. An LCD display shows the current CMC, and three buttons let you navigate up, down, and print.

---

## Files

| File | Description |
|------|-------------|
| `driver2.py` | Main driver. Runs the button loop, LCD display, and printer. Uses a second thread for printing so the buttons stay responsive while the printer works. |
| `get_image_urls.py` | Parses MTGJSON to extract card data and filters out sets you don't want (Un-sets, Universes Beyond, etc.). Calls the Scryfall API to get image URLs for each card. |
| `get_images.py` | Takes the URLs from the previous step and downloads the actual card images, sorting them into one folder per CMC. |
| `bw.py` | Converts images to black and white and resizes them for your printer width. |

---

## Setup

### 1. Data Collection
Run these on your main computer — not the Pi. The Pi will take forever.

```
get_image_urls.py → get_images.py → bw.py
```

Then copy the resulting CMC folders to the Pi.

### 2. Hardware
Wire up your components and install dependencies on the Pi, then copy `driver2.py` over.

### 3. Run on Boot
The driver should start automatically on boot. The easiest way is a systemd service:

```bash
sudo nano /etc/systemd/system/mormir.service
```

```ini
[Unit]
Description=Mormir Card Printer
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/lazarus/mormir_proj/driver2.py
WorkingDirectory=/home/lazarus/mormir_proj
User=lazarus
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable mormir
sudo systemctl start mormir
```

You can also use `cron` with `@reboot`, but systemd is preferred since it handles crashes and boot timing better.

---

## Supplies

- Raspberry Pi (3B+ used here)
- LCD display with I2C backpack
- Breadboard
- 3x push buttons
- DuPont wires (lots)
- Thermal printer — most Chinese vendors will do
- 58mm thermal receipt paper
- A box to put it all in

---

## Tips

- **Do all data collection on your main computer.** Downloading hundreds of card images on a Pi 3B+ is painfully slow.
- **Printer width matters.** This build uses a 58mm printer (384px). If you use an 80mm printer, update the resize width to 576px in `bw.py` and `driver2.py`.
- **Magic famously has no creatures worth 14 mana.** The 14 CMC folder is filled with photos of my friends instead. There are no guardrails stopping a player from selecting CMC 14 — that's a feature, not a bug.
- **Paper orientation matters.** Thermal paper is only heat-sensitive on one side. If nothing prints, flip the roll.
- **usblp conflicts with escpos.** If the printer stops responding, blacklist the `usblp` kernel module: `echo "blacklist usblp" | sudo tee /etc/modprobe.d/blacklist-usblp.conf`


## Inspired by Rhystic Studies' Video: Mormir Vig | Magic's Luckiest Minigame
## Design help from @oboyone https://github.com/oboyone/mb_thermal_printer