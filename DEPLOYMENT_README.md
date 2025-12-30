# 电影推荐应用 - PythonAnywhere部署指南

## 完整部署步骤

### 步骤1：上传和解压项目文件

#### 方法A：通过网页界面上传（推荐）
1. 访问 https://pythonanywhere.com
2. 登录你的账户
3. 点击顶部菜单的 "Files" 选项卡
4. 在文件浏览器中，点击右上角的 "Upload" 按钮
5. 选择你的项目ZIP文件（如：film_recommendation_deploy.zip）
6. 上传完成后，找到上传的ZIP文件
7. 点击ZIP文件右侧的解压按钮（通常是一个带拉链图标的按钮）
8. 如果没有解压按钮，选择ZIP文件后点击 "Unzip" 选项

#### 方法B：通过命令行解压（如果网页解压失败）
```bash
# 1. 打开Bash控制台
# 在PythonAnywhere的"Files"页面，点击"Open bash console here"

# 2. 导航到文件所在目录（通常是主目录）
cd ~

# 3. 列出文件，找到你的ZIP文件
ls -la *.zip

# 4. 解压ZIP文件（假设文件名是 film_recommendation_deploy.zip）
unzip film_recommendation_deploy.zip

# 或者如果是tar.gz格式：
# tar -xzf your_project.tar.gz

# 5. 重命名解压后的文件夹（如果需要）
# mv film_recommendation_deploy film_recommendation
```

### 步骤2：设置虚拟环境
```bash
# 进入项目目录
cd film_recommendation

# 创建Python虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip（可选但推荐）
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 步骤3：配置Web应用
1. 返回PythonAnywhere控制面板
2. 点击顶部菜单的 "Web" 选项卡
3. 点击 "Add a new web app"
4. 选择 "Flask"
5. 选择 Python 3.x 版本（推荐3.8或更高）
6. 点击 "Next"
7. 在 "Code" 部分设置：
   - Source code: /home/yourusername/film_recommendation
   - Working directory: /home/yourusername/film_recommendation
   - WSGI configuration file: /home/yourusername/film_recommendation/wsgi.py
8. 点击 "Next"

### 步骤4：设置环境变量
在Web选项卡的 "Environment variables" 部分，添加以下变量：
```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
```

### 步骤5：初始化数据库
```bash
# 在Bash控制台中运行（确保虚拟环境已激活）
cd film_recommendation
source venv/bin/activate
python scripts/seed_database.py
```

### 步骤6：重新加载应用
1. 返回Web选项卡
2. 点击绿色的 "Reload" 按钮
3. 等待应用重新加载完成

## 验证部署

部署成功后，你会得到一个URL，比如：
```
https://yourusername.pythonanywhere.com
```

访问这个URL，你应该能看到电影推荐应用的主页！

## 测试功能

1. 注册新用户
2. 登录账户
3. 浏览电影列表
4. 查看电影详情
5. 点赞/评分/评论电影
6. 查看个性化推荐

## 常见问题及解决方法

### 1. 解压失败
问题: 网页界面没有解压按钮，或解压失败
解决:
```bash
# 使用命令行解压
unzip your_project.zip
# 或
tar -xzf your_project.tar.gz
```

### 2. 静态文件不加载
问题: CSS/JS文件无法加载
解决:
- 检查Web配置中的Source code路径是否正确
- 确保static文件夹在项目根目录下
- 重新加载Web应用

### 3. 数据库错误
问题: 应用启动时数据库错误
解决:
```bash
# 确保数据库已初始化
cd film_recommendation
source venv/bin/activate
python scripts/seed_database.py
```

### 4. 导入错误
问题: ModuleNotFoundError
解决:
- 检查requirements.txt中的依赖是否都已安装
- 确保Python路径配置正确
- 检查__init__.py文件是否存在

### 5. 权限错误
问题: 无法写入文件
解决:
- PythonAnywhere的文件权限通常是正确的
- 确保数据库文件在instance目录中

### 6. 应用无法启动
问题: 500 Internal Server Error
解决:
- 检查WSGI配置是否正确
- 查看错误日志：/var/log/pythonanywhere/error.log
- 确保所有依赖都已安装

## 监控和维护

### 查看日志
```bash
# PythonAnywhere错误日志
tail -f /var/log/pythonanywhere/error.log

# 应用自定义日志（如果有）
tail -f logs/app.log
```

### 备份数据
```bash
# 定期备份数据库
cp instance/app.db instance/backup_$(date +%Y%m%d_%H%M%S).db
```

### 更新应用
```bash
# 激活虚拟环境
source venv/bin/activate

# 拉取最新代码（如果适用）
# git pull origin main

# 重新安装依赖（如果requirements.txt有更新）
pip install -r requirements.txt

# 重新加载Web应用
```

## 部署检查清单

- [ ] ZIP文件已上传到PythonAnywhere
- [ ] 文件已解压到正确目录
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖已安装
- [ ] Web应用已配置
- [ ] 环境变量已设置
- [ ] 数据库已初始化
- [ ] 应用已重新加载
- [ ] 网站可正常访问
- [ ] 所有功能正常工作

## 获取帮助

如果遇到问题：
1. 检查PythonAnywhere的帮助文档
2. 查看错误日志
3. 确认所有步骤都按顺序完成
4. 尝试重新加载应用

祝部署顺利！
