---
name: app-store-compliance
description: Android and iOS app store compliance audit and fix workflow. Use when the user wants to prepare a Capacitor-based app for Google Play Store or Apple App Store submission. Triggers on: "app store compliance", "submit to app store", "fix Android manifest", "add iOS permissions", "Capacitor compliance", "Play Store requirements", "App Store review", "native project fixes", "adaptive icons", "Info.plist keys", "entitlements".
license: Complete terms in LICENSE.txt
---

# App Store Compliance

This skill covers the complete workflow for preparing a Capacitor-based Next.js app for Google Play Store and Apple App Store submission.

## Android Fixes

### 1. Fix AndroidManifest.xml
```xml
<!-- REMOVE deprecated APP_BROWSER category -->
<!-- ADD proper app link intent-filter with autoVerify -->
<!-- SET usesCleartextTraffic="false" -->
<!-- ADD Google Play required features -->
```

### 2. Fix Adaptive Icons
Create proper adaptive icon resources:
- `res/mipmap-anydpi-v26/ic_launcher.xml` — background + foreground
- `res/mipmap-anydpi-v26/ic_launcher_round.xml` — rounded variant
- `res/values/ic_launcher_background.xml` — solid color

### 3. Fix Network Security
- Set `usesCleartextTraffic="false"` in manifest
- Add domain exceptions in `network_security_config.xml`
- Only allow localhost/127.0.0.1 for dev

### 4. Add Runtime Permissions
Update `MainActivity.java` to request POST_NOTIFICATIONS at runtime:
```java
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
            != PackageManager.PERMISSION_GRANTED) {
        ActivityCompat.requestPermissions(this,
            new String[]{Manifest.permission.POST_NOTIFICATIONS},
            REQUEST_CODE_POST_NOTIFICATIONS);
    }
}
```

## iOS Fixes

### 1. Generate Info.plist
Run `npx cap sync ios` to generate the project, then add required keys:

```xml
<key>NSCameraUsageDescription</key>
<string>Allow camera access to upload profile photos</string>

<key>NSMicrophoneUsageDescription</key>
<string>Allow microphone access for VOIP calls</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>Allow location access to find nearby therapists</string>

<key>NSUserTrackingUsageDescription</key>
<string>This allows us to show relevant content and improve your experience</string>

<key>NSPhotoLibraryAddUsageDescription</key>
<string>Allow saving photos to your library</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>Allow access to select profile photos</string>

<key>NSLocalNetworkUsageDescription</key>
<string>Allow local network access for VOIP calling</string>

<key>UIUserInterfaceStyle</key>
<string>Automatic</string>

<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
</dict>
```

### 2. Create Entitlements File
Create `ios/App/App/OnlyHands.entitlements`:
```xml
<key>com.apple.developer.associated-domains</key>
<array>
    <string>applinks:onlyhands.com</string>
</array>
<key>com.apple.developer.push-notifications</key>
<true/>
```

### 3. Update LaunchScreen
Update `Base.lproj/LaunchScreen.storyboard` to show splash properly.

## Cross-Platform

### 1. Install Push Notifications Plugin
```bash
npm install @capacitor/push-notifications
npx cap sync
```

### 2. Generate App Icons
Use the icon generator script:
```bash
node scripts/generate-icons.js
# Creates: public/icon.svg, public/splash.svg
# Updates: Android adaptive icon background
```

### 3. Sync Native Projects
```bash
npx cap sync
```

## Pre-Submission Checklist

### Google Play Store
- [ ] `APP_BROWSER` category removed from manifest
- [ ] Adaptive icons complete (background + foreground)
- [ ] `usesCleartextTraffic="false"`
- [ ] POST_NOTIFICATIONS runtime request implemented
- [ ] Privacy policy URL configured in Play Console
- [ ] App signing key prepared (keystore)
- [ ] 64-bit native libraries (if any)

### Apple App Store
- [ ] Info.plist has all NS*UsageDescription keys
- [ ] Entitlements file with push + associated domains
- [ ] Dark mode support (UIUserInterfaceStyle = Automatic)
- [ ] App Store Connect metadata prepared
- [ ] Screenshots generated (6.5" and 5.5")
- [ ] App icon 1024x1024 PNG ready
- [ ] Privacy policy URL configured
- [ ] TestFlight build uploaded

## Capacitor Configuration
```typescript
// capacitor.config.ts
const config: CapacitorConfig = {
  appId: 'com.onlyhands.app',
  appName: 'OnlyHands',
  webDir: 'out',
  server: {
    androidScheme: 'https',
    cleartext: false, // Change to false for production
  },
  android: {
    buildOptions: {
      releaseType: 'AAB', // Required for Google Play
    },
  },
  ios: {
    buildOptions: {
      signingStyle: 'manual', // or 'automatic' for fastlane
    },
  },
};
```
