const { chromium } = require('playwright');

const DASH = 'http://127.0.0.1:8030';
const OUT = 'C:/Users/Project Zero/Desktop/unified-ai-stack/docs/screenshots/';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const d = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1.25 });

  // re-activate timed idle window (30 min)
  const a = await d.request.post(DASH + '/api/presets/' + encodeURIComponent('Idle (timed)') + '/apply',
    { data: { duration_min: 30 } });
  console.log('idle apply:', a.status());

  await d.goto(DASH, { waitUntil: 'networkidle', timeout: 20000 });
  await d.waitForTimeout(2500);
  const bannerVisible = await d.evaluate(() => {
    const b = document.getElementById('idle-banner');
    return b && !b.classList.contains('hidden');
  });
  console.log('idle banner visible:', bannerVisible);
  await d.screenshot({ path: OUT + 'dashboard-idle.png', fullPage: true });
  console.log('dashboard-idle.png OK (fullPage)');

  // restore balanced for a clean final state
  await d.request.post(DASH + '/api/presets/' + encodeURIComponent('24-7 Balanced') + '/apply');
  console.log('restored balanced');
  await browser.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
