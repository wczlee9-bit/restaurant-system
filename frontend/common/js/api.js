// API 基础配置 - 本地后端（通过Nginx代理）
const API_BASE = '/api';

// 通用请求函数
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${url}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

// 显示提示信息
function showMessage(message, type = 'info') {
    const div = document.createElement('div');
    div.className = type;
    div.textContent = message;
    document.body.insertBefore(div, document.body.firstChild);
    
    setTimeout(() => {
        div.remove();
    }, 3000);
}

// 格式化金额
function formatPrice(price) {
    return `¥${price.toFixed(2)}`;
}

// 获取本地存储数据
function getStorage(key, defaultVal = null) {
    try {
        return JSON.parse(localStorage.getItem(key)) || defaultVal;
    } catch {
        return defaultVal;
    }
}

// 设置本地存储数据
function setStorage(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

// 删除本地存储数据
function removeStorage(key) {
    localStorage.removeItem(key);
}

// 加载动画
function showLoading(container) {
    container.innerHTML = '<div class="loading">加载中...</div>';
}

// 错误提示
function showError(container, message) {
    container.innerHTML = `<div class="error">${message}</div>`;
}
