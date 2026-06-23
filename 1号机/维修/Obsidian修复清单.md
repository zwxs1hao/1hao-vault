# 1号机 Obsidian 修复清单

## 当前问题
- Obsidian 工作台三连叉（realclaudian 读到 Administrator 会话）
- .obsidian 配置含 2号机 Administrator 路径
- .claudian 会话残留 2号机数据
- 开机自启带 Obsidian + 可能 PM2 残留

## 修复步骤（CMD 逐条执行）

### 1. 拉最新代码
```
cd /d D:\ob1 && git pull
```

### 2. 删掉被污染的配置
```
rmdir /s /q D:\ob1\.obsidian
rmdir /s /q D:\ob1\.claudian
```

### 3. 清理开机自启
```
dir "C:\Users\Admin\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
```
看到 Obsidian、pm2、bot、watcher 相关的就删。

### 4. 重开 Obsidian
选 D:\ob1 库 → 自动重建干净配置

### 5. 装 Claudian 插件
设置 → 第三方插件 → 浏览 → 搜 Claudian → 安装

### 6. 检查 PM2
1号机不需要 bot/watcher。确认：
```
tasklist | findstr pm2
schtasks /query /fo LIST /v | findstr /i "pm2 bot watcher"
```
有就删。

## 修复后效果
- Obsidian 正常打开，右边工作台能用
- 不再三连叉
- 不会读到 2号机的 Administrator 配置
