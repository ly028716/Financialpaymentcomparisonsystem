# OCR服务部署指南

## 概述

本系统使用阿里云通义千问视觉API（DashScope）实现银行回单的OCR识别功能。本文档介绍如何配置和部署OCR服务。

---

## 1. 阿里云账号注册

### 1.1 注册阿里云账号

1. 访问 [阿里云官网](https://www.aliyun.com/)
2. 点击右上角"免费注册"
3. 按照提示完成账号注册和实名认证

### 1.2 开通DashScope服务

1. 登录阿里云控制台
2. 搜索"DashScope"或访问 [DashScope控制台](https://dashscope.console.aliyun.com/)
3. 点击"开通服务"
4. 阅读并同意服务协议

---

## 2. 获取API密钥

### 2.1 创建API Key

1. 进入 [DashScope API密钥管理页面](https://dashscope.console.aliyun.com/apiKey)
2. 点击"创建新的API-KEY"
3. 输入密钥名称（如：`payment-ocr-prod`）
4. 点击"确定"生成密钥
5. **重要**：立即复制并保存API Key，页面关闭后无法再次查看

### 2.2 API Key安全建议

- ✅ 使用环境变量存储，不要硬编码到代码中
- ✅ 不同环境使用不同的API Key（开发/测试/生产）
- ✅ 定期轮换API Key
- ✅ 限制API Key的访问权限
- ❌ 不要将API Key提交到版本控制系统

---

## 3. 环境变量配置

### 3.1 开发环境配置

#### Linux/macOS

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

然后执行：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

#### Windows

**方法1：命令行临时设置**
```cmd
set DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

**方法2：PowerShell临时设置**
```powershell
$env:DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

**方法3：系统环境变量（永久）**
1. 右键"此电脑" → "属性"
2. 点击"高级系统设置"
3. 点击"环境变量"
4. 在"用户变量"或"系统变量"中新建
5. 变量名：`DASHSCOPE_API_KEY`
6. 变量值：`sk-xxxxxxxxxxxxxxxxxxxxxxxx`

### 3.2 生产环境配置

#### Docker部署

在 `docker-compose.yml` 中配置：

```yaml
services:
  backend:
    image: payment-comparison-backend:latest
    environment:
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
    env_file:
      - .env.production
```

在 `.env.production` 文件中：
```
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

#### Kubernetes部署

创建Secret：
```bash
kubectl create secret generic dashscope-api-key \
  --from-literal=DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

在Deployment中引用：
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-backend
spec:
  template:
    spec:
      containers:
      - name: backend
        image: payment-comparison-backend:latest
        env:
        - name: DASHSCOPE_API_KEY
          valueFrom:
            secretKeyRef:
              name: dashscope-api-key
              key: DASHSCOPE_API_KEY
```

#### 云服务器部署

使用systemd服务配置：

创建 `/etc/systemd/system/payment-backend.service`：
```ini
[Unit]
Description=Payment Comparison Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/payment-comparison/backend
Environment="DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx"
ExecStart=/opt/payment-comparison/venv/bin/gunicorn payment_comparison.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 4. 验证配置

### 4.1 检查环境变量

```bash
# Linux/macOS
echo $DASHSCOPE_API_KEY

# Windows CMD
echo %DASHSCOPE_API_KEY%

# Windows PowerShell
echo $env:DASHSCOPE_API_KEY
```

### 4.2 Django Shell验证

```bash
cd backend
python manage.py shell
```

```python
from django.conf import settings

# 检查API Key是否配置
print(f"API Key: {settings.DASHSCOPE_API_KEY[:10]}...")
print(f"OCR Enabled: {settings.OCR_ENABLED}")

# 测试OCR服务初始化
from payment_comparison.apps.payments.ocr_service import AliOCRService
service = AliOCRService(settings.DASHSCOPE_API_KEY)
print("OCR服务初始化成功")
```

### 4.3 API接口测试

使用curl测试：

```bash
curl -X POST http://localhost:8000/api/payments/ocr/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/bank_receipt.jpg"
```

预期响应：
```json
{
  "code": 200,
  "message": "OCR识别成功",
  "data": {
    "payee_name": "...",
    "payee_account": "...",
    "amount": 50000.00,
    "confidence": 0.95
  }
}
```

---

## 5. 常见问题排查

### 5.1 OCR服务未配置

**错误信息：**
```json
{
  "code": 503,
  "message": "OCR服务未配置，请设置DASHSCOPE_API_KEY环境变量"
}
```

**解决方法：**
1. 检查环境变量是否正确设置
2. 重启Django应用使环境变量生效
3. 确认 `settings.OCR_ENABLED` 为 `True`

### 5.2 API密钥无效

**错误信息：**
```json
{
  "code": 500,
  "message": "OCR识别失败: API调用失败: InvalidParameter - Invalid API key"
}
```

**解决方法：**
1. 检查API Key是否正确复制（无多余空格）
2. 确认API Key未过期或被删除
3. 在DashScope控制台重新生成API Key

### 5.3 dashscope库未安装

**错误信息：**
```
OCR识别失败: dashscope库未安装，请运行: pip install dashscope
```

**解决方法：**
```bash
cd backend
pip install dashscope>=1.14.0
# 或
pip install -r requirements.txt
```

### 5.4 API调用超时

**错误信息：**
```json
{
  "code": 500,
  "message": "OCR识别失败: API调用超时"
}
```

**可能原因：**
- 网络连接不稳定
- 图片文件过大
- DashScope服务响应慢

**解决方法：**
1. 检查服务器网络连接
2. 压缩图片大小（建议 < 5MB）
3. 增加超时时间（修改 `settings.OCR_TIMEOUT`）
4. 重试请求

### 5.5 识别准确率低

**现象：**
- `confidence` 值 < 0.8
- 部分字段识别为空

**解决方法：**
1. 确保图片清晰、光线充足
2. 避免图片倾斜或变形
3. 使用标准银行回单格式
4. 对于低置信度结果，引导用户手动复核

### 5.6 权限被拒绝

**错误信息：**
```json
{
  "code": 403,
  "message": "您没有权限执行此操作"
}
```

**解决方法：**
- 确认用户角色为"出纳"或"系统管理员"
- 检查JWT Token是否有效
- 确认用户已通过身份验证

---

## 6. 性能优化建议

### 6.1 图片预处理

在上传前对图片进行优化：
- 压缩图片大小（推荐 1-3MB）
- 转换为JPG格式（比PNG更小）
- 裁剪无关区域

### 6.2 缓存策略

对于相同图片的重复识别，可以考虑：
- 基于图片哈希值缓存识别结果
- 设置合理的缓存过期时间（如1小时）

### 6.3 异步处理

对于批量识别场景，建议：
- 使用Celery等任务队列异步处理
- 避免阻塞主请求线程
- 提供识别进度查询接口

---

## 7. 监控与告警

### 7.1 关键指标

建议监控以下指标：
- OCR API调用次数
- 识别成功率
- 平均识别时间
- API费用消耗

### 7.2 日志记录

系统已配置日志记录，查看方式：

```bash
# 查看OCR相关日志
tail -f logs/payment_comparison.log | grep OCR

# 查看错误日志
tail -f logs/payment_comparison.log | grep ERROR
```

### 7.3 费用控制

DashScope按调用次数计费，建议：
- 设置每日调用次数上限
- 配置费用预警通知
- 定期审查API使用情况

---

## 8. 安全注意事项

### 8.1 数据安全

- ✅ 上传的银行回单图片不会永久存储在阿里云
- ✅ 识别完成后立即删除临时文件
- ✅ 敏感信息不记录到日志文件

### 8.2 访问控制

- ✅ 仅出纳和管理员可访问OCR接口
- ✅ 所有请求需要JWT身份验证
- ✅ 实施接口访问频率限制

### 8.3 合规性

- 确保符合数据保护法规（如GDPR、个人信息保护法）
- 获得用户授权后再处理银行回单
- 定期进行安全审计

---

## 9. 技术支持

### 9.1 阿里云技术支持

- 官方文档：https://help.aliyun.com/zh/dashscope/
- 工单系统：https://workorder.console.aliyun.com/
- 技术论坛：https://developer.aliyun.com/ask/

### 9.2 项目技术支持

如遇到项目相关问题，请联系：
- 技术负责人：[联系方式]
- 项目文档：`docs/` 目录
- Issue跟踪：[项目仓库地址]

---

## 附录：API费用说明

### 计费方式

DashScope通义千问视觉API按调用次数计费：
- 免费额度：新用户赠送一定调用次数
- 按量付费：超出免费额度后按次计费
- 具体价格请参考：https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-vl-plus-api

### 成本估算

假设每天处理100笔付款：
- 每月调用次数：100 × 30 = 3000次
- 预估月费用：[根据实际价格计算]

建议定期检查费用账单，避免超支。
