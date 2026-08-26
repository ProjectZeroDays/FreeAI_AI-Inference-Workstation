'use strict';

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { MailboxStore } = require('../src/proxy/mailbox/store');
const { SkillUpdater } = require('../src/proxy/extensions/skillUpdater');
const { DmHandler } = require('../src/proxy/extensions/dmHandler');

function tmpDataDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'extensions-test-'));
}

describe('SkillUpdater', () => {
  let store, dataDir, skillDir;

  before(() => {
    dataDir = tmpDataDir();
    skillDir = tmpDataDir();
    store = new MailboxStore(dataDir);
  });

  after(() => {
    store.close();
    try { fs.rmSync(dataDir, { recursive: true }); } catch {}
    try { fs.rmSync(skillDir, { recursive: true }); } catch {}
  });

  it('updates skill.md from inbound message', () => {
    const skillPath = path.join(skillDir, 'SKILL.md');
    const updater = new SkillUpdater({
      store,
      skillPath,
      logger: { log: () => {}, warn: () => {}, error: () => {} },
    });

    const result = updater.processSkillUpdate({
      payload: { content: '# Updated Skill\nNew content here.', version: '1.1.0' },
    });
    assert.equal(result, true);
    assert.equal(fs.readFileSync(skillPath, 'utf8'), '# Updated Skill\nNew content here.');
    assert.equal(store.getState('skill_version'), '1.1.0');
  });

  it('creates backup before overwriting', () => {
    const skillPath = path.join(skillDir, 'SKILL2.md');
    fs.writeFileSync(skillPath, 'original content', 'utf8');

    const updater = new SkillUpdater({
      store,
      skillPath,
      logger: { log: () => {}, warn: () => {}, error: () => {} },
    });

    updater.processSkillUpdate({
      payload: { content: 'updated content', version: '2.0' },
    });
    assert.equal(fs.readFileSync(skillPath, 'utf8'), 'updated content');
    assert.equal(fs.readFileSync(skillPath + '.bak', 'utf8'), 'original content');
  });

  it('returns false without skill path', () => {
    const updater = new SkillUpdater({
      store,
      logger: { log: () => {}, warn: () => {}, error: () => {} },
    });
    assert.equal(updater.processSkillUpdate({ payload: { content: 'x' } }), false);
  });

  it('returns false without content', () => {
    const updater = new SkillUpdater({
      store,
      skillPath: path.join(skillDir, 'noop.md'),
      logger: { log: () => {}, warn: () => {}, error: () => {} },
    });
    assert.equal(updater.processSkillUpdate({ payload: {} }), false);
  });

  it('pollAndApply processes pending skill_update messages', () => {
    const dir2 = tmpDataDir();
    const s2 = new MailboxStore(dir2);
    const sp = path.join(skillDir, 'polled.md');

    s2.writeInbound({
      type: 'skill_update',
      payload: { content: '# Polled skill', version: '3.0' },
    });

    const updater = new SkillUpdater({
      store: s2,
      skillPath: sp,
      logger: { log: () => {}, warn: () => {}, error: () => {} },
    });

    const applied = updater.pollAndApply();
    assert.equal(applied, 1);
    assert.equal(fs.readFileSync(sp, 'utf8'), '# Polled skill');
    s2.close();
    try { fs.rmSync(dir2, { recursive: true }); } catch {}
  });
});

describe('DmHandler', () => {
  let store, handler, dataDir;

  before(() => {
    dataDir = tmpDataDir();
    store = new MailboxStore(dataDir);
    handler = new DmHandler({ store });
  });

  after(() => {
    store.close();
    try { fs.rmSync(dataDir, { recursive: true }); } catch {}
  });

  it('sends a DM and creates outbound message', () => {
    const result = handler.send({
      recipientNodeId: 'node_abc',
      content: 'Hello there',
    });
    assert.ok(result.message_id);
    assert.equal(result.status, 'pending');

    const msg = store.getById(result.message_id);
    assert.equal(msg.type, 'dm');
    assert.equal(msg.direction, 'outbound');
    assert.equal(msg.payload.recipient_node_id, 'node_abc');
    assert.equal(msg.payload.content, 'Hello there');
  });

  it('throws on missing recipientNodeId', () => {
    assert.throws(() => handler.send({ content: 'x' }), /recipientNodeId/);
  });

  it('throws on missing content', () => {
    assert.throws(() => handler.send({ recipientNodeId: 'n' }), /content/);
  });

  it('polls inbound DMs', () => {
    store.writeInbound({ type: 'dm', payload: { content: 'incoming dm' } });
    const msgs = handler.poll();
    assert.ok(msgs.length >= 1);
    assert.equal(msgs[0].type, 'dm');
  });

  it('acks DM messages', () => {
    const id = store.writeInbound({ type: 'dm', payload: { content: 'to ack' } });
    const count = handler.ack(id);
    assert.equal(count, 1);
    const msg = store.getById(id);
    assert.equal(msg.status, 'delivered');
  });

  it('lists DM history', () => {
    const msgs = handler.list();
    assert.ok(Array.isArray(msgs));
  });
});
