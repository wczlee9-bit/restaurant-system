const fs = require('fs');
const html = fs.readFileSync('customer_order_v3.html', 'utf8');

// 提取script标签内容
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) {
    console.log('未找到script标签');
    process.exit(1);
}

const jsCode = scriptMatch[1];

// 检查常见问题
console.log('=== 语法检查 ===');
console.log('1. 检查Promise.all是否包含非async函数...');

const promiseAllMatch = jsCode.match(/Promise\.all\(\[([\s\S]*?)\]\)/);
if (promiseAllMatch) {
    const promiseContent = promiseAllMatch[1];
    const functions = promiseContent.match(/this\.(\w+)\(\)/g) || [];
    console.log('   Promise.all中调用的函数:', functions);
    
    // 检查loadShopInfo是否在Promise.all中
    if (promiseContent.includes('loadShopInfo()')) {
        console.log('   ❌ 错误: loadShopInfo() 不是async函数，不应该在Promise.all中');
    } else {
        console.log('   ✅ loadShopInfo() 已从Promise.all中移除');
    }
}

// 检查是否有Vue和ElementPlus
console.log('2. 检查Vue和ElementPlus引用...');
const hasVue = html.includes('vue.global.prod.js');
const hasElementPlus = html.includes('element-plus');
console.log('   Vue:', hasVue ? '✅' : '❌');
console.log('   ElementPlus:', hasElementPlus ? '✅' : '❌');

// 检查axios
console.log('3. 检查axios引用...');
const hasAxios = html.includes('axios.min.js');
console.log('   axios:', hasAxios ? '✅' : '❌');

console.log('\n=== 检查完成 ===');
