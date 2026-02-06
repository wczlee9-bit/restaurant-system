# 📝 分步执行部署指南

## 🔧 步骤 1：打开终端

**Windows 用户**：
- 打开 PowerShell 或 CMD

**Mac/Linux 用户**：
- 打开 Terminal

---

## 🚀 步骤 2：复制并执行第一条命令

**复制下面的命令**（选中后按 Ctrl+C）：

```bash
ssh root@129.226.196.76
```

**粘贴到终端**（右键粘贴或 Ctrl+V），按回车

---

## 🔑 步骤 3：输入密码

系统会提示输入密码，输入您的腾讯云服务器密码

**注意**：输入密码时**不会显示任何字符**，这是正常的

输入完成后按回车

---

## ✅ 步骤 4：验证连接

如果连接成功，您会看到类似这样的提示：

```
Welcome to Ubuntu 20.04.x LTS (GNU/Linux 5.x.x-x-generic x86_64)

root@vm-xxx-xxx:~#
```

**表示您已经成功连接到腾讯云服务器！**

---

## 📥 步骤 5：下载并执行部署脚本

**复制这条完整的命令**（这是一条命令，要一次性复制）：

```bash
cd /tmp && curl -s https://raw.githubusercontent.com/wczlee9-bit/restaurant-system/main/quick_deploy_to_tencent_cloud.sh -o deploy.sh && chmod +x deploy.sh && bash deploy.sh
```

**粘贴到终端**，按回车

---

## ⏳ 步骤 6：等待部署完成

部署脚本会自动执行，您会看到类似这样的输出：

```
=========================================
  餐厅系统 - 极速部署
=========================================

[1/8] 准备部署环境...
[2/8] 备份现有系统...
[3/8] 清理旧项目...
[4/8] 从 GitHub 克隆代码...
[5/8] 创建虚拟环境...
[6/8] 安装依赖...
[7/8] 测试模块...
✅ 模块测试通过
[8/8] 配置并启动服务...
```

**这个过程需要 10-15 分钟，请耐心等待** ⏱️

---

## ✅ 步骤 7：验证部署

部署完成后，您会看到：

```
=========================================
  🎉 部署完成！
=========================================

访问地址：
  http://129.226.196.76

管理命令：
  查看状态: systemctl status restaurant
  查看日志: journalctl -u restaurant -f
  重启服务: systemctl restart restaurant
```

---

## 🌐 步骤 8：访问系统

在浏览器中打开：

```
http://129.226.196.76
```

**如果看到页面打开成功，恭喜您部署完成了！** 🎉

---

## 🔍 步骤 9：验证服务状态

**复制并执行**：

```bash
systemctl status restaurant
```

您应该看到：
```
● restaurant.service - Restaurant System
   Loaded: loaded (/etc/systemd/system/restaurant.service; enabled; vendor preset: enabled)
   Active: active (running) since ...
```

**Active: active (running)** 表示服务正常运行 ✅

---

## 🧪 步骤 10：测试 API

**复制并执行**：

```bash
curl http://localhost:8000/health
```

应该返回：
```json
{"status":"ok"}
```

---

## 📋 部署检查清单

使用这个清单确保部署成功：

- [ ] 步骤 1：打开终端
- [ ] 步骤 2：连接到腾讯云
- [ ] 步骤 3：输入密码
- [ ] 步骤 4：验证连接成功
- [ ] 步骤 5：下载并执行部署脚本
- [ ] 步骤 6：等待部署完成（10-15分钟）
- [ ] 步骤 7：看到部署完成提示
- [ ] 步骤 8：浏览器访问 http://129.226.196.76
- [ ] 步骤 9：验证服务状态
- [ ] 步骤 10：测试 API

---

## 🆘 常见问题

### Q1: 提示 "ssh: command not found"

**A**: Windows 用户需要先安装 SSH 客户端
- Windows 10/11 已经内置 SSH，直接使用即可
- 如果没有，需要安装 Git Bash 或 PuTTY

### Q2: 提示 "Connection refused"

**A**: 检查服务器 IP 是否正确
- 确认 IP 是：129.226.196.76
- 确认服务器正在运行
- 检查防火墙设置

### Q3: 提示 "Permission denied"

**A**: 密码输入错误
- 重新执行 `ssh root@129.226.196.76`
- 重新输入密码（注意大小写）

### Q4: 部署过程中断

**A**: 重新执行步骤 5 的命令即可
```bash
cd /tmp && curl -s https://raw.githubusercontent.com/wczlee9-bit/restaurant-system/main/quick_deploy_to_tencent_cloud.sh -o deploy.sh && chmod +x deploy.sh && bash deploy.sh
```

### Q5: 服务启动失败

**A**: 查看详细日志
```bash
journalctl -u restaurant -n 50
```

---

## 📞 需要帮助？

如果遇到问题，请：

1. 截图错误信息
2. 复制完整错误日志
3. 告诉我具体在哪一步失败

---

**现在开始第一步吧！打开您的终端！** 🚀
