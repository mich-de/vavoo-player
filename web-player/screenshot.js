const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('http://127.0.0.1:5000');

    // Wait for channels to load
    await page.waitForSelector('.channel-item', { timeout: 10000 });

    // Find and click Rete 4
    const channels = await page.$$('.channel-item');
    for (const channel of channels) {
        const text = await channel.textContent();
        if (text.includes('RETE 4')) {
            await channel.click();
            break;
        }
    }

    // Wait for the stream to start loading and EPG to fetch
    await page.waitForTimeout(4000);

    // Force the OSD overlay to become visible permanently for the screenshot
    await page.evaluate(() => {
        document.querySelector('.controls-overlay').classList.add('visible');
        document.querySelector('.controls-overlay').style.opacity = '1';
    });

    await page.waitForTimeout(500);

    // Take screenshot of the top portion of the player overlay
    await page.screenshot({ path: 'C:/Users/mdeangelis/.gemini/antigravity/brain/ca7b0879-92cf-4ac0-aa72-b0c0d42b7153/rete4_osd_desc_test.png', clip: { x: 300, y: 0, width: 900, height: 400 } });

    console.log('Screenshot saved successfully to the system generated directory.');
    await browser.close();
})();
