# 🏗️ Moodify Aura App Build Instructions

This directory contains the Tauri wrapper config to package `https://modify-s9hc.onrender.com/` as a lightweight native app.

---

## 📱 1. Android App (.apk) — The Cloud Way (Easiest)

Since your PWA is already working perfectly, the easiest way to generate an Android package without installing the Android SDK, Gradle, and Java locally is to use **PWABuilder** (maintained by Microsoft).

1. Go to [PWABuilder.com](https://www.pwabuilder.com/).
2. Enter your website URL: `https://modify-s9hc.onrender.com/` and click **Start**.
3. It will scan your PWA configuration (manifest, service worker, icons).
4. Click **Package for Store** under **Google Play (Android)**.
5. Download the generated ZIP file containing your ready-to-use `.apk` and `.aab` packages!

---

## 🐧 2. Linux App (.deb / .AppImage)

To compile the Tauri desktop wrapper for Linux on your machine:

1. Install the compilation dependencies:
   ```bash
   sudo apt update
   sudo apt install -y libwebkit2gtk-4.1-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev patchelf build-essential
!   ```
2. Navigate to the `desktop-app` directory and build the app:
   ```bash
   cd desktop-app
   npm run tauri build
   ```
3. Once completed, your binaries will be located in:
   `desktop-app/src-tauri/target/release/bundle/deb/` (for Debian/Ubuntu installer)
   `desktop-app/src-tauri/target/release/bundle/appimage/` (for standalone AppImage)

---

## 🪟 3. Windows App (.exe / .msi)

To compile the Tauri desktop wrapper for Windows:

1. Clone or copy your project folder onto a Windows machine.
2. Ensure you have Rust installed (`rustup default stable`).
3. Open your terminal (PowerShell or Command Prompt) and run:
   ```cmd
   cd desktop-app
   npm install
   npm run tauri build
   ```
4. The compiled installer (`.msi`) will be generated inside:
   `desktop-app/src-tauri/target/release/bundle/msi/`
