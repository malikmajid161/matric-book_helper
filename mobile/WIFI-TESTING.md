# Android Wi-Fi test build

This preview APK uses `http://192.168.1.7:8000` and Expo project
`c7fb7019-d357-45a6-8698-d50abfb188e8`. Its installed name is PTB Scholar.

1. Keep the computer and phone on the same Wi-Fi.
2. Run `backend/start-wifi.ps1` on the computer and keep its terminal open.
3. Open `http://192.168.1.7:8000/health` on the phone to check connectivity.
4. Install the APK, sign in from Settings, select a book, and download it once.
5. Saved PDFs can be opened offline. New AI answers require the backend and internet.

Windows Firewall may require a scoped inbound exception before phone access works.
In an Administrator PowerShell, run `backend/wifi-firewall.ps1` to allow only local
Wi-Fi devices to reach the backend. Run it again with `-Remove` after testing.
If the computer's Wi-Fi IP changes, update the preview URL in `eas.json` and rebuild.
HTTP is enabled for this LAN preview. Use an HTTPS backend for a public release.
Server API keys are excluded from the mobile build.

Physics and Mathematics currently support PDF reading; their scanned text is awaiting
OCR review. Chemistry has indexed text for grounded answers. Device testing remains
necessary before calling this a production release.
