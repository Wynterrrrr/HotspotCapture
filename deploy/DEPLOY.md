# 🔥 热点数据定时抓取部署指南

## 一、环境要求

- Python 3.10+
- uv（Python包管理器）
- Git（已配置GitHub登录）

## 二、服务器部署

### 1. 克隆项目

```bash
cd /opt
git clone https://github.com/YOUR_REPO/HotspotCapture.git
cd HotspotCapture
```

### 2. 安装依赖

```bash
uv install
```

### 3. 配置GitHub

确保服务器已配置Git可推送至目标仓库：

```bash
# 配置Git用户信息
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 测试SSH连接
ssh -T git@github.com

# 或使用Personal Access Token
git config --global credential.helper store
```

### 4. 首次运行测试

```bash
uv run python scheduler.py
```

检查 `hotnews_output/` 目录是否生成MD文件，并确认GitHub推送成功。

---

## 三、定时任务配置

### 方案A：使用 Systemd Timer（推荐）

#### 1. 复制服务文件

```bash
sudo cp deploy/hotnews-scheduler.service /etc/systemd/system/
```

#### 2. 创建 Timer 文件

```bash
sudo tee /etc/systemd/system/hotnews-scheduler.timer << 'EOF'
[Unit]
Description=Run Hot News Scheduler 4 times daily (Beijing Time)

[Timer]
# 北京时间 6:00 = UTC 22:00 (前一天)
OnCalendar=*-*-* 22:00:00 Asia/Shanghai
# 北京时间 11:00 = UTC 3:00
OnCalendar=*-*-* 03:00:00 Asia/Shanghai
# 北京时间 16:00 = UTC 8:00
OnCalendar=*-*-* 08:00:00 Asia/Shanghai
# 北京时间 21:00 = UTC 13:00
OnCalendar=*-*-* 13:00:00 Asia/Shanghai

Persistent=true
Unit=hotnews-scheduler.service

[Install]
WantedBy=timers.target
EOF
```

#### 3. 启用定时器

```bash
# 重载systemd
sudo systemctl daemon-reload

# 启用并启动定时器
sudo systemctl enable hotnews-scheduler.timer
sudo systemctl start hotnews-scheduler.timer

# 查看定时器状态
sudo systemctl list-timers | grep hotnews
```

---

### 方案B：使用 Crontab

```bash
crontab -e
```

添加以下内容：

```cron
# 北京时间 6:00, 11:00, 16:00, 21:00 执行
# 注意：crontab使用服务器时区，请确认服务器时区为Asia/Shanghai
0 6 * * * cd /opt/HotspotCapture && /usr/bin/uv run python scheduler.py >> /var/log/hotnews.log 2>&1
0 11 * * * cd /opt/HotspotCapture && /usr/bin/uv run python scheduler.py >> /var/log/hotnews.log 2>&1
0 16 * * * cd /opt/HotspotCapture && /usr/bin/uv run python scheduler.py >> /var/log/hotnews.log 2>&1
0 21 * * * cd /opt/HotspotCapture && /usr/bin/uv run python scheduler.py >> /var/log/hotnews.log 2>&1
```

检查服务器时区：

```bash
timedatectl
# 如果不是Asia/Shanghai，设置时区
sudo timedatectl set-timezone Asia/Shanghai
```

---

## 四、日志查看

### Systemd 日志

```bash
# 查看最近执行日志
sudo journalctl -u hotnews-scheduler.service -n 100

# 实时查看日志
sudo journalctl -u hotnews-scheduler.service -f
```

### Crontab 日志

```bash
tail -f /var/log/hotnews.log
```

---

## 五、手动执行

```bash
cd /opt/HotspotCapture
uv run python scheduler.py
```

---

## 六、文件结构

执行后生成：

```
HotspotCapture/
├── hotnews_output/           # MD文件输出目录
│   ├── 2025-03-14_06-00.md
│   ├── 2025-03-14_11-00.md
│   ├── 2025-03-14_16-00.md
│   ├── 2025-03-14_21-00.md
│   └── ObsdianDrive/         # 克隆的GitHub仓库
│       └── hotnews/          # 推送目标目录
│           └── *.md
└── ...
```

---

## 七、故障排查

### 1. Git推送失败

```bash
# 检查SSH密钥
ssh -T git@github.com

# 或使用Token重新认证
git clone https://YOUR_TOKEN@github.com/Wynterrrrr/ObsdianDrive.git
```

### 2. 某平台抓取失败

检查该平台的API是否可用，可在 `routers/` 目录下对应的文件中调整请求参数。

### 3. 时区问题

确保服务器时区正确：

```bash
timedatectl set-timezone Asia/Shanghai
```

---

## 八、GitHub结果

执行成功后，可在以下位置查看结果：

**https://github.com/Wynterrrrr/ObsdianDrive/tree/main/hotnews**
