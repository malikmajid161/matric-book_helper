# Automatic app updates

The next APK must be installed once to add `expo-updates` to the Android app.
Compatible JavaScript and asset updates can then download automatically when the
phone is online. They apply on the next full app launch; studying is never
interrupted by a forced reload. Launch checks do not delay offline startup.

`AutoUpdates` also checks when the app returns to the foreground or connectivity
returns. These extra checks are limited to once every 30 minutes per running app.
Network errors leave the installed app and downloaded books available.

## Publish a compatible update

From this `mobile` directory, sign into the existing Expo account and publish:

```powershell
$env:EXPO_PUBLIC_API_URL = 'http://192.168.1.7:8000'
npx eas-cli update --channel preview --environment preview --message "Describe the student-visible changes"
```

Keep the same environment values when building and publishing. The preview APK
uses the `preview` channel; production builds use `production`. Do not publish
server API keys as `EXPO_PUBLIC_` variables.

The runtime uses Expo's native fingerprint policy. Changes requiring a different
native runtime, such as adding native libraries, changing Android permissions,
or upgrading Expo, need a new APK. Publishing source changes to GitHub alone does
not publish an Expo update. Expo account quotas and connectivity still apply.

Downloaded textbooks, SQLite vectors, and practice progress live in app storage;
an OTA update does not delete them. Textbook study data is updated separately and
can reuse the existing PDF when its checksum is unchanged.
