'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const SETTINGS_DIR = path.join(os.homedir(), '.evolver');
const SETTINGS_FILE = path.join(SETTINGS_DIR, 'settings.json');

function readSettings() {
  try {
    if (fs.existsSync(SETTINGS_FILE)) {
      return JSON.parse(fs.readFileSync(SETTINGS_FILE, 'utf8'));
    }
  } catch {}
  return {};
}

function writeSettings(data) {
  if (!fs.existsSync(SETTINGS_DIR)) {
    fs.mkdirSync(SETTINGS_DIR, { recursive: true });
  }
  const current = readSettings();
  const merged = { ...current, ...data };
  fs.writeFileSync(SETTINGS_FILE, JSON.stringify(merged, null, 2), 'utf8');
  return merged;
}

function clearSettings() {
  try {
    if (fs.existsSync(SETTINGS_FILE)) {
      const current = readSettings();
      delete current.proxy;
      fs.writeFileSync(SETTINGS_FILE, JSON.stringify(current, null, 2), 'utf8');
    }
  } catch {}
}

function isStaleProxy() {
  const settings = readSettings();
  const pid = settings.proxy?.pid;
  if (!pid) return false;
  try {
    process.kill(pid, 0);
    return false;
  } catch {
    return true;
  }
}

function clearIfStale() {
  if (isStaleProxy()) {
    clearSettings();
    return true;
  }
  return false;
}

function getProxyUrl() {
  const settings = readSettings();
  return settings.proxy?.url || null;
}

module.exports = { readSettings, writeSettings, clearSettings, clearIfStale, isStaleProxy, getProxyUrl, SETTINGS_DIR, SETTINGS_FILE };
