# 🔐 推送到 Gitee 认证指南

## ❌ 当前问题

推送时遇到认证错误：
```
fatal: could not read Username for 'https://gitee.com': No such device or address
```

这是因为 Gitee 需要认证，但当前环境无法交互式输入用户名和密码。

---

## ✅ 解决方案（三种方法）

### 方法 1：使用 Personal Access Token（推荐）

#### 步骤 1：获取 Token

1. 访问 Gitee：https://gitee.com
2. 登录账号
3. 进入：https://gitee.com/profile/personal_access_tokens
4. 点击"生成新令牌"
5. 填写信息：
   - 令牌描述：`Restaurant System Deploy`
   - 权限选择：`projects`（必须勾选）
   - 有效期：选择一个合理的期限（如 30 天）
6. 点击"提交"
7. **复制生成的 Token**（只显示一次！）

#### 步骤 2：使用 Token 推送

```bash
# 在沙盒环境执行
git remote set-url gitee https://<your-token>@gitee.com/lijun75/restaurant.git
git push gitee main
```

**示例**：
```bash
# 假设你的 Token 是: abcdef123456
git remote set-url gitee https://abcdef123456@gitee.com/lijun75/restaurant.git
git push gitee main
```

---

### 方法 2：使用 SSH 密钥

#### 步骤 1：生成 SSH 密钥

```bash
# 在沙盒环境执行
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# 一路按 Enter（不设置密码）
```

#### 步骤 2：查看公钥

```bash
cat ~/.ssh/id_rsa.pub
```

#### 步骤 3：添加到 Gitee

1. 访问：https://gitee.com/profile/sshkeys
2. 点击"添加公钥"
3. 粘贴上一步查看到的公钥内容
4. 点击"确定"

#### 步骤 4：更改 remote URL 为 SSH

```bash
git remote set-url gitee git@gitee.com:lijun75/restaurant.git
git push gitee main
```

---

### 方法 3：在您的本地机器推送

如果您有本地访问权限，可以在您的本地机器执行：

```bash
# 1. 克隆当前项目（从 GitHub）
git clone https://github.com/wczlee9-bit/restaurant-system.git

# 2. 进入项目目录
cd restaurant-system

# 3. 添加 Gitee remote
git remote add gitee https://gitee.com/lijun75/restaurant.git

# 4. 推送到 Gitee（会要求输入用户名和密码）
git push gitee main
```

---

## 🎯 推荐：使用 Personal Access Token

这是最简单、最安全的方式：

### 快速操作步骤

1. **获取 Token**（2分钟）
   ```
   访问：https://gitee.com/profile/personal_access_tokens
   → 生成新令牌
   → 复制 Token
   ```

2. **推送代码**（1分钟）
   ```bash
   git remote set-url gitee https://<your-token>@gitee.com/lijun75/restaurant.git
   git push gitee main
   ```

---

## 📝 推送成功后的验证

推送成功后，访问 Gitee 仓库验证：
- 仓库地址：https://gitee.com/lijun75/restaurant
- 检查文件是否同步成功
- 检查提交记录是否完整

---

## 🆘 如果还有问题

### 问题 1：Token 无效

**原因**：Token 可能已过期或权限不足

**解决**：重新生成 Token，确保勾选 `projects` 权限

### 问题 2：推送被拒绝

**错误**：```
! [rejected] main -> main (fetch first)
error: failed to push some refs
```

**解决**：
```bash
git pull gitee main --rebase
git push gitee main
```

### 问题 3：仓库不存在

**错误**：```
fatal: repository 'https://gitee.com/lijun75/restaurant.git' not found
```

**解决**：
1. 确认仓库地址正确
2. 确认您有该仓库的访问权限
3. 可能需要先在 Gitee 创建仓库

---

## 🎉 推送成功后

推送成功后，可以开始部署到腾讯云：

```bash
# 连接到腾讯云
ssh root@129.226.196.76

# 在腾讯云上执行
cd /opt
git clone https://gitee.com/lijun75/restaurant.git restaurant-system
cd restaurant-system
bash deploy_all_in_one.sh
```

---

## 📊 推送检查清单

使用此清单确保推送成功：

### 准备阶段
- [ ] Gitee 账号已登录
- [ ] 有仓库访问权限
- [ ] 已获取 Personal Access Token

### 推送阶段
- [ ] Gitee remote 已添加
- [ ] 使用 Token 更新 remote URL
- [ ] 代码成功推送
- [ ] 推送验证通过

### 验证阶段
- [ ] 访问 Gitee 仓库
- [ ] 检查文件同步
- [ ] 检查提交记录

---

## 📞 需要帮助？

- Gitee 文档：https://gitee.com/help/articles/4129
- Token 生成：https://gitee.com/profile/personal_access_tokens
- 仓库地址：https://gitee.com/lijun75/restaurant

---

**准备好 Token 后，告诉我，我来帮您推送！** 🚀
