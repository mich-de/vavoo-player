const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 375, height: 812 }, // iPhone X viewport
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
    });
    const page = await context.newPage();
    await page.goto('http://127.0.0.1:5000');

    // Wait for the UI
    await page.waitForSelector('#mobileMenuBtn', { timeout: 10000 });
    await page.waitForTimeout(1000);

    // 1. Click the mobile menu hamburger to open the drawer
    await page.click('#mobileMenuBtn');
    await page.waitForTimeout(1000); // Wait for CSS transition

    // 2. Now the channel list is visible, click the first channel
    await page.waitForSelector('.channel-item', { timeout: 5000 });
    await page.click('.channel-item');
    await page.waitForTimeout(2000);

    // 3. Ensure player controls are visible again by hovering the video
    await page.hover('#playerContainer');
    await page.waitForTimeout(500);

    // Take screenshot of the mobile layout showing player and controls
    await page.screenshot({ path: 'C:/Users/mdeangelis/.gemini/antigravity/brain/ca7b0879-92cf-4ac0-aa72-b0c0d42b7153/mobile_player_test.png' });

    // 4. Open the menu again to show the sidebar in the screenshot
    await page.click('#mobileMenuBtn');
    await page.waitForTimeout(1000);

    // Take screenshot of the open sidebar menu
    await page.screenshot({ path: 'C:/Users/mdeangelis/.gemini/antigravity/brain/ca7b0879-92cf-4ac0-aa72-b0c0d42b7153/mobile_sidebar_test.png' });

    console.log('Successfully saved mobile_player_test.png and mobile_sidebar_test.png');
    await browser.close();
})();
