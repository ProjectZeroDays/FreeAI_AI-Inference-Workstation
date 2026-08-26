'use strict';

const fs = require('fs');
const path = require('path');

class SkillUpdater {
  constructor({ store, skillPath, logger } = {}) {
    this.store = store;
    this.skillPath = skillPath || null;
    this.logger = logger || console;
  }

  setSkillPath(filePath) {
    this.skillPath = filePath;
  }

  processSkillUpdate(message) {
    if (!this.skillPath) {
      this.logger.warn('[skill-updater] No skill path configured, skipping update');
      return false;
    }

    const payload = message.payload || message;
    const content = payload.content || payload.skill_content;

    if (!content || typeof content !== 'string') {
      this.logger.warn('[skill-updater] No content in skill_update message');
      return false;
    }

    try {
      const dir = path.dirname(this.skillPath);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

      if (fs.existsSync(this.skillPath)) {
        const backupPath = this.skillPath + '.bak';
        fs.copyFileSync(this.skillPath, backupPath);
      }

      fs.writeFileSync(this.skillPath, content, 'utf8');
      this.store.setState('last_skill_update', new Date().toISOString());
      this.store.setState('skill_version', payload.version || 'unknown');
      this.logger.log(`[skill-updater] Updated skill.md (version: ${payload.version || 'unknown'})`);
      return true;
    } catch (err) {
      this.logger.error(`[skill-updater] Failed to update: ${err.message}`);
      return false;
    }
  }

  pollAndApply() {
    const updates = this.store.poll({ type: 'skill_update' });
    let applied = 0;
    for (const msg of updates) {
      if (this.processSkillUpdate(msg)) {
        this.store.ack(msg.id);
        applied++;
      }
    }
    return applied;
  }
}

module.exports = { SkillUpdater };
