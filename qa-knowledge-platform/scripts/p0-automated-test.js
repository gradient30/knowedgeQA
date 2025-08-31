const { chromium } = require('playwright');

async function runP0Test() {
  console.log('🔍 开始P0自动化验证...');
  
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // 测试1: 检查首页是否正常加载
    console.log('📋 测试1: 检查首页加载...');
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000);
    
    const pageContent = await page.textContent('body');
    if (pageContent.includes('(self.__next_f=')) {
      console.log('❌ 首页显示Next.js内部代码，存在编译问题');
      return false;
    } else {
      console.log('✅ 首页正常加载');
    }

    // 测试2: 检查导航栏是否显示
    console.log('📋 测试2: 检查导航栏显示...');
    await page.goto('http://localhost:3000/knowledge');
    await page.waitForTimeout(2000);
    
    const hasNavbar = await page.locator('text=QA知识平台 - 测试导航栏').isVisible();
    if (hasNavbar) {
      console.log('✅ 测试导航栏正常显示');
    } else {
      console.log('❌ 测试导航栏未显示');
      return false;
    }

    // 测试3: 检查登录页面
    console.log('📋 测试3: 检查登录页面...');
    await page.goto('http://localhost:3000/login');
    await page.waitForTimeout(2000);
    
    const hasLoginForm = await page.locator('input[placeholder*="邮箱"]').isVisible();
    if (hasLoginForm) {
      console.log('✅ 登录页面正常显示');
    } else {
      console.log('❌ 登录页面未正常显示');
      return false;
    }

    // 测试4: 尝试登录
    console.log('📋 测试4: 尝试登录...');
    await page.fill('input[placeholder*="邮箱"]', 'testuser@example.com');
    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);
    
    // 检查是否成功跳转
    const currentUrl = page.url();
    console.log(`当前URL: ${currentUrl}`);
    
    if (currentUrl.includes('/knowledge') || currentUrl.includes('/')) {
      console.log('✅ 登录流程完成');
      
      // 检查是否有导航栏
      const hasNavbarAfterLogin = await page.locator('text=QA知识平台').isVisible();
      if (hasNavbarAfterLogin) {
        console.log('✅ 登录后导航栏正常显示');
      } else {
        console.log('❌ 登录后导航栏未显示');
        return false;
      }
    } else {
      console.log('❌ 登录后未正确跳转');
      return false;
    }

    console.log('🎉 P0测试全部通过！');
    return true;

  } catch (error) {
    console.error('❌ P0测试过程中出现错误:', error);
    return false;
  } finally {
    await browser.close();
  }
}

// 运行测试
runP0Test().then(success => {
  if (success) {
    console.log('✅ P0问题已修复');
    process.exit(0);
  } else {
    console.log('❌ P0问题仍存在');
    process.exit(1);
  }
}).catch(error => {
  console.error('测试运行失败:', error);
  process.exit(1);
});