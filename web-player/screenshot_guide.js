const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('http://127.0.0.1:5000');

    await page.waitForSelector('.channel-item', { timeout: 10000 });

    // Click first channel to start video
    await page.click('.channel-item');

    await page.waitForTimeout(3000);

    // Click the new Guide button to open the EPG overlay
    await page.click('#btnGuide');

    await page.waitForTimeout(500);

    // Take screenshot of the player area showing the overlay
    await page.screenshot({ path: 'C:/Users/mdeangelis/.gemini/antigravity/brain/ca7b0879-92cf-4ac0-aa72-b0c0d42b7153/epg_overlay_test.png', clip: { x: 300, y: 0, width: 980, height: 720 } });

    console.log('Successfully saved epg_overlay_test.png');
    await browser.close();
})();
