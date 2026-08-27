const { describe, it } = require('node:test');
const assert = require('node:assert/strict');

describe('hubVerify', function () {
  const { isSolidifyVerifyEnabled, requestSolidifyPermitSync } = require('../src/gep/hubVerify');

  it('isSolidifyVerifyEnabled returns false when no hub URL', function () {
    const original = process.env.A2A_HUB_URL;
    delete process.env.A2A_HUB_URL;
    assert.strictEqual(isSolidifyVerifyEnabled(), false);
    if (original !== undefined) process.env.A2A_HUB_URL = original;
  });

  it('isSolidifyVerifyEnabled returns false when explicitly disabled', function () {
    const origUrl = process.env.A2A_HUB_URL;
    const origVerify = process.env.EVOLVER_SOLIDIFY_VERIFY;
    process.env.A2A_HUB_URL = 'https://example.com';
    process.env.EVOLVER_SOLIDIFY_VERIFY = 'false';
    assert.strictEqual(isSolidifyVerifyEnabled(), false);
    if (origUrl !== undefined) process.env.A2A_HUB_URL = origUrl; else delete process.env.A2A_HUB_URL;
    if (origVerify !== undefined) process.env.EVOLVER_SOLIDIFY_VERIFY = origVerify; else delete process.env.EVOLVER_SOLIDIFY_VERIFY;
  });

  it('isSolidifyVerifyEnabled returns true when hub URL is set', function () {
    const origUrl = process.env.A2A_HUB_URL;
    const origVerify = process.env.EVOLVER_SOLIDIFY_VERIFY;
    process.env.A2A_HUB_URL = 'https://evomap.ai';
    delete process.env.EVOLVER_SOLIDIFY_VERIFY;
    assert.strictEqual(isSolidifyVerifyEnabled(), true);
    if (origUrl !== undefined) process.env.A2A_HUB_URL = origUrl; else delete process.env.A2A_HUB_URL;
    if (origVerify !== undefined) process.env.EVOLVER_SOLIDIFY_VERIFY = origVerify; else delete process.env.EVOLVER_SOLIDIFY_VERIFY;
  });

  it('requestSolidifyPermitSync returns offline error when no hub URL', function () {
    const origUrl = process.env.A2A_HUB_URL;
    delete process.env.A2A_HUB_URL;
    const result = requestSolidifyPermitSync({ geneId: 'test_gene', signals: ['a'], mutation: {} });
    assert.strictEqual(result.ok, false);
    assert.strictEqual(result.offline, true);
    if (origUrl !== undefined) process.env.A2A_HUB_URL = origUrl;
  });
});
