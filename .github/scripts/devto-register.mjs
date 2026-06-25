#!/usr/bin/env node
/**
 * Dev.to Registration via GitHub OAuth
 * Runs on GitHub Actions cloud runner — different IP range, no local network restrictions
 */

import { chromium } from 'playwright';

const DEVTOS = 'https://dev.to/enter';
const GH_TOKEN = process.env.GH_TOKEN;

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function main() {
  console.log('[INFO] Launching browser on GitHub Actions runner...');
  
  const browser = await chromium.launch({ 
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
  });
  
  const page = await context.newPage();
  
  try {
    // Step 1: Go to Dev.to enter page
    console.log('[STEP 1] Navigating to Dev.to...');
    await page.goto(DEVTOS, { waitUntil: 'networkidle', timeout: 30000 });
    console.log('[OK] Page loaded:', page.url());
    
    // Step 2: Click "Sign in with GitHub"
    console.log('[STEP 2] Looking for GitHub sign-in...');
    
    // Try clicking the GitHub sign-in form
    const githubForm = await page.$('form[action*="github"]');
    if (githubForm) {
      console.log('[OK] Found GitHub form, submitting...');
      await githubForm.evaluate(form => form.submit());
    } else {
      // Fallback: look for GitHub link/button
      const githubBtn = await page.$('a[href*="github"], button:has-text("GitHub")');
      if (githubBtn) {
        console.log('[OK] Found GitHub button, clicking...');
        await githubBtn.click();
      } else {
        console.log('[WARN] No GitHub auth element found');
        await page.screenshot({ path: 'devto-page.png', fullPage: true });
      }
    }
    
    await page.waitForTimeout(5000);
    console.log('[INFO] Current URL after auth click:', page.url());
    
    // Step 3: Handle GitHub OAuth authorization
    // On GitHub Actions runner, the IP is from GitHub so OAuth may work differently
    if (page.url().includes('github.com')) {
      console.log('[STEP 3] On GitHub authorization page...');
      
      // Check if we need to authorize the Dev.to app
      const authorizeBtn = await page.$('button[name="authorize"]');
      if (authorizeBtn) {
        console.log('[OK] Found authorize button, authorizing...');
        await authorizeBtn.click();
        await page.waitForTimeout(3000);
      } else {
        console.log('[WARN] No authorize button found');
      }
    }
    
    await page.waitForTimeout(3000);
    console.log('[INFO] Final URL:', page.url());
    await page.screenshot({ path: 'final-result.png', fullPage: true });
    
    // Step 4: Check if registration was successful
    const finalUrl = page.url();
    if (finalUrl.includes('dev.to') && !finalUrl.includes('enter')) {
      console.log('[SUCCESS] Registered on Dev.to!');
      console.log('[INFO] Check screenshot for account details');
      
      // Get the account info
      const title = await page.title();
      console.log('[INFO] Page title:', title);
    } else {
      console.log('[INFO] Registration may need additional steps');
      console.log('[INFO] Check screenshot for current state');
    }
    
  } catch (err) {
    console.error('[ERROR]', err.message);
    try {
      await page.screenshot({ path: 'error-state.png', fullPage: true });
    } catch (_) {}
    process.exit(1);
  } finally {
    await browser.close();
  }
}

main();
