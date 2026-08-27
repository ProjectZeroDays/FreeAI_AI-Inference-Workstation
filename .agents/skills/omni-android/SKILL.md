---
name: omni-android
version: "1.0.0"
author: "Agent Zero"
tags: ["android", "adb", "omnirroot", "system-control", "hardware", "telephony"]
omnipermissions:
  - "*"
capabilities:
  - "*"
policy: omnipotent
trigger_patterns:
  - "android"
  - "adb"
  - "device"
  - "phone"
  - "root"
  - "install omniroot"
  - "hardware control"
  - "telephony"
allowed_tools:
  - "omni_android"
  - "response"
---

# OmniAndroid — Full Android System Control

## Purpose

Provide Agent Zero with complete control over any Android device through the OmniADB Manifest-X bridge. This skill enables device discovery, connection, capability invocation, OmniRoot injection, and full system manipulation.

## Architecture

```
Agent Zero → omni_android tool → Manifest-X HTTP bridge (port 43110) → ADB → Device
```

The Manifest-X bridge runs on the host as part of the modified ADB server. It exposes Android capabilities via HTTP endpoints that Agent Zero can invoke.

## Prerequisites

1. OmniADB server must be running (modified ADB with Manifest-X runtime)
2. Android device connected via USB or WiFi ADB
3. USB debugging enabled on device
4. For root features: OmniRoot kernel module must be loaded

## Usage

### Scan for devices
```
omni_android(action="scan")
```

### Check status
```
omni_android(action="status")
```

### Execute a capability
```
omni_android(action="invoke", capability="android.system", method="getDeviceInfo", args="{}")
omni_android(action="invoke", capability="android.system", method="runtimeExec", args='{"command": "ls -la /system"}')
omni_android(action="invoke", capability="android.telephony", method="getSimInfo", args="{}")
```

### List capabilities
```
omni_android(action="list_capabilities")
```

### Install OmniRoot
```
omni_android(action="inject")
```

### Grant root
```
omni_android(action="root")
```

### Push files to device
```
omni_android(action="push", local="/path/to/file", remote="/sdcard/file")
```

### Execute shell command
```
omni_android(action="shell", command="ls -la /system")
```

### Take screenshot
```
omni_android(action="screenshot")
```

## Available Capabilities

| Capability | Methods |
|------------|---------|
| `android.system` | getDeviceInfo, getBatteryInfo, getMemoryInfo, reboot, shutdown, runtimeExec |
| `android.telephony` | getSimInfo, sendSms, dialNumber, getCellInfo, getSignalStrength, enableData, disableData |
| `android.storage` | readFile, writeFile, listDirectory, deleteFile, createDirectory |
| `android.package` | listInstalledPackages, installApp, uninstallApp, disableApp, enableApp |
| `android.settings` | getSystemSetting, putSystemSetting, getSecureSetting, putSecureSetting |
| `android.network` | getNetworkState, enableWifi, disableWifi, setProxy, scanWifi |
| `android.screen` | captureScreen, startRecording, stopRecording |
| `android.input` | injectTouch, injectSwipe, injectKey, injectText |
| `android.hardware` | readGPIO, writeGPIO, readI2C, writeI2C, readSPI, setPWM |
| `android.sensors` | getAccelerometer, getGyroscope, getMagnetometer, getLight |
| `android.accessibility` | getAccessibilityState, performGesture, takeSnapshot |

## OmniRoot Injection

The `inject` action performs a full OmniRoot installation:

1. Pushes kernel module to device
2. Loads kernel module (insmod)
3. Creates persistence in /persist partition
4. Installs init script for boot-time loading
5. Blocks Google OTA updates
6. Verifies installation

After injection, reboot the device for full root access.
