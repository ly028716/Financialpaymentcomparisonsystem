# 财务付款对比系统 - 系统架构设计

## 1. 业务流程图

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  部门   │────▶│  会计   │────▶│  出纳   │────▶│ 系统校验 │
│ 申请人  │     │ 审核人  │     │ 付款人  │     │ 对比引擎 │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
    │               │               │               │
    ▼               ▼               ▼               ▼
付款申请单      付款申请表      实际付款记录      差异报告
```

## 2. 核心功能模块

### 2.1 付款申请模块
**功能：**
- 部门提交付款申请
- 填写收款方信息（户名、账号、开户行）
- 填写付款金额、用途、附件

**字段设计：**
```json
{
  "申请单号": "FK202604060001",
  "申请部门": "技术部",
  "申请人": "张三",
  "申请日期": "2026-04-06",
  "收款方户名": "北京XX科技有限公司",
  "收款方账号": "6222021234567890123",
  "收款方开户行": "中国工商银行北京分行",
  "付款金额": 50000.00,
  "付款用途": "服务器采购款",
  "附件": ["合同.pdf", "发票.pdf"],
  "状态": "待审核"
}
```

### 2.2 会计审核模块
**功能：**
- 审核付款申请的合规性
- 生成标准付款申请表
- 批量导出付款清单（Excel/PDF）

**审核检查项：**
- [ ] 收款方信息完整性
- [ ] 账号格式校验（银行卡号Luhn算法）
- [ ] 金额大小写一致性
- [ ] 附件完整性（合同、发票）
- [ ] 预算额度检查

### 2.3 出纳付款模块
**功能：**
- 查看待付款清单
- 记录实际付款信息
- 上传银行回单/付款截图
- 标记付款完成状态

**实际付款记录：**
```json
{
  "付款单号": "FK202604060001",
  "实际付款日期": "2026-04-06 14:30:00",
  "实际收款户名": "北京XX科技有限公司",
  "实际收款账号": "6222021234567890123",
  "实际付款金额": 50000.00,
  "付款渠道": "网银转账",
  "银行流水号": "20260406143012345678",
  "付款凭证": ["回单.jpg"],
  "经办人": "李四"
}
```

### 2.4 智能对比引擎（核心）
**对比维度：**

| 对比项 | 会计申请表 | 出纳实际付款 | 匹配规则 |
|--------|-----------|-------------|---------|
| 收款户名 | 标准户名 | 实际户名 | 完全匹配 / 模糊匹配（相似度>95%） |
| 收款账号 | 标准账号 | 实际账号 | 完全匹配 |
| 付款金额 | 申请金额 | 实际金额 | 完全匹配（误差<0.01元） |
| 开户行 | 标准开户行 | 实际开户行 | 模糊匹配（关键词匹配） |

**对比算法：**
```python
def compare_payment(expected, actual):
    """
    对比会计申请表和出纳实际付款
    """
    result = {
        "match": True,
        "differences": []
    }

    # 1. 账号完全匹配
    if expected["账号"] != actual["账号"]:
        result["match"] = False
        result["differences"].append({
            "field": "账号",
            "expected": expected["账号"],
            "actual": actual["账号"],
            "severity": "CRITICAL"
        })

    # 2. 户名模糊匹配（处理空格、括号等）
    name_similarity = calculate_similarity(
        normalize_name(expected["户名"]),
        normalize_name(actual["户名"])
    )
    if name_similarity < 0.95:
        result["match"] = False
        result["differences"].append({
            "field": "户名",
            "expected": expected["户名"],
            "actual": actual["户名"],
            "similarity": name_similarity,
            "severity": "HIGH"
        })

    # 3. 金额精确匹配
    if abs(expected["金额"] - actual["金额"]) > 0.01:
        result["match"] = False
        result["differences"].append({
            "field": "金额",
            "expected": expected["金额"],
            "actual": actual["金额"],
            "difference": actual["金额"] - expected["金额"],
            "severity": "CRITICAL"
        })

    return result
```

### 2.5 差异预警模块
**预警级别：**
- **CRITICAL（严重）**：账号错误、金额错误
- **HIGH（高）**：户名不匹配
- **MEDIUM（中）**：开户行不匹配
- **LOW（低）**：付款日期延迟

**预警方式：**
- 系统内消息通知
- 邮件通知（会计、出纳、财务主管）
- 微信/钉钉机器人推送
- 短信通知（严重错误）

### 2.6 OCR识别模块（可选）
**功能：**
- 识别银行回单图片
- 自动提取户名、账号、金额
- 减少出纳手工录入错误

**技术方案：**
- 百度OCR / 腾讯OCR / 阿里OCR
- 自训练模型（针对常见银行回单格式）

## 3. 数据库设计

### 3.1 付款申请表 (payment_applications)
```sql
CREATE TABLE payment_applications (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    application_no VARCHAR(50) UNIQUE NOT NULL COMMENT '申请单号',
    department VARCHAR(100) NOT NULL COMMENT '申请部门',
    applicant VARCHAR(50) NOT NULL COMMENT '申请人',
    application_date DATE NOT NULL COMMENT '申请日期',

    payee_name VARCHAR(200) NOT NULL COMMENT '收款方户名',
    payee_account VARCHAR(50) NOT NULL COMMENT '收款方账号',
    payee_bank VARCHAR(200) NOT NULL COMMENT '收款方开户行',

    amount DECIMAL(15,2) NOT NULL COMMENT '付款金额',
    purpose TEXT COMMENT '付款用途',
    attachments JSON COMMENT '附件列表',

    status ENUM('draft', 'pending', 'approved', 'rejected', 'paid', 'verified') DEFAULT 'draft',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_application_no (application_no),
    INDEX idx_status (status),
    INDEX idx_department (department)
) COMMENT='付款申请表';
```

### 3.2 实际付款记录表 (actual_payments)
```sql
CREATE TABLE actual_payments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    application_id BIGINT NOT NULL COMMENT '关联申请单ID',
    payment_no VARCHAR(50) UNIQUE NOT NULL COMMENT '付款单号',

    actual_payee_name VARCHAR(200) NOT NULL COMMENT '实际收款户名',
    actual_payee_account VARCHAR(50) NOT NULL COMMENT '实际收款账号',
    actual_payee_bank VARCHAR(200) COMMENT '实际开户行',
    actual_amount DECIMAL(15,2) NOT NULL COMMENT '实际付款金额',

    payment_channel VARCHAR(50) COMMENT '付款渠道',
    bank_serial_no VARCHAR(100) COMMENT '银行流水号',
    payment_voucher JSON COMMENT '付款凭证（图片URL）',

    operator VARCHAR(50) NOT NULL COMMENT '经办人',
    payment_date TIMESTAMP NOT NULL COMMENT '付款时间',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id) REFERENCES payment_applications(id),
    INDEX idx_application_id (application_id),
    INDEX idx_payment_no (payment_no)
) COMMENT='实际付款记录表';
```

### 3.3 对比结果表 (comparison_results)
```sql
CREATE TABLE comparison_results (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    application_id BIGINT NOT NULL,
    payment_id BIGINT NOT NULL,

    is_match BOOLEAN NOT NULL COMMENT '是否匹配',
    differences JSON COMMENT '差异详情',

    verified_by VARCHAR(50) COMMENT '复核人',
    verified_at TIMESTAMP COMMENT '复核时间',
    verification_note TEXT COMMENT '复核说明',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id) REFERENCES payment_applications(id),
    FOREIGN KEY (payment_id) REFERENCES actual_payments(id),
    INDEX idx_is_match (is_match)
) COMMENT='对比结果表';
```

## 4. 技术栈选型

### 4.1 后端
**推荐方案1：Java + Spring Boot**
- 适合企业级应用
- 生态成熟，安全性高
- 便于集成OA系统

**推荐方案2：Python + Django**
- 快速开发
- 数据处理能力强
- OCR集成方便

**推荐方案3：Go + Gin**
- 高性能
- 部署简单
- 适合微服务架构

### 4.2 前端
- **框架**：Vue 3 + Element Plus / React + Ant Design
- **表格组件**：AG Grid（支持Excel导入导出）
- **图表**：ECharts（统计分析）

### 4.3 数据库
- **主库**：MySQL 8.0 / PostgreSQL 14
- **缓存**：Redis（会话、临时数据）

### 4.4 文件存储
- **本地部署**：MinIO
- **云存储**：阿里云OSS / 腾讯云COS

### 4.5 OCR服务
- 百度智能云 - 通用文字识别
- 腾讯云 - 票据识别
- 阿里云 - 印刷文字识别

## 5. 安全设计

### 5.1 权限控制
```
角色          权限
─────────────────────────────────
部门申请人    提交申请、查看本部门申请
会计          审核申请、生成付款表、查看所有记录
出纳          记录付款、上传凭证、查看待付款清单
财务主管      查看所有记录、复核差异、导出报表
系统管理员    用户管理、系统配置
```

### 5.2 数据安全
- 敏感字段加密（账号、金额）
- 操作日志记录（谁、何时、做了什么）
- 数据备份（每日自动备份）
- 访问审计（登录日志、操作日志）

### 5.3 流程控制
- 付款申请不可修改（只能撤销重新提交）
- 实际付款记录不可删除（只能标记作废）
- 对比结果需财务主管复核确认

## 6. 部署方案

### 6.1 本地部署（推荐）
```
服务器配置：
- CPU: 4核
- 内存: 8GB
- 硬盘: 500GB SSD
- 操作系统: Ubuntu 22.04 LTS / CentOS 8

部署架构：
┌─────────────────────────────────┐
│         Nginx (反向代理)         │
└─────────────────────────────────┘
           │
┌──────────┴──────────┐
│                     │
▼                     ▼
应用服务器1          应用服务器2
(主)                 (备)
│                     │
└──────────┬──────────┘
           ▼
    MySQL主从复制
```

### 6.2 云部署
- 阿里云ECS + RDS + OSS
- 腾讯云CVM + TencentDB + COS
- 华为云ECS + RDS + OBS

## 7. 开发计划

### Phase 1: MVP（4周）
- [ ] 付款申请提交
- [ ] 会计审核流程
- [ ] 出纳付款记录
- [ ] 基础对比功能（账号、金额完全匹配）

### Phase 2: 增强（4周）
- [ ] 户名模糊匹配
- [ ] 差异预警通知
- [ ] 报表导出
- [ ] 权限管理

### Phase 3: 优化（4周）
- [ ] OCR识别
- [ ] 批量导入
- [ ] 高级报表
- [ ] 数据统计分析

## 8. 成本估算

### 8.1 开发成本
- 后端开发：2人 × 3个月 = 6人月
- 前端开发：1人 × 2个月 = 2人月
- 测试：1人 × 1个月 = 1人月
- **总计：9人月**

### 8.2 运营成本（年）
- 服务器：¥5,000/年（本地部署）
- OCR服务：¥2,000/年（按量付费）
- 维护：¥10,000/年
- **总计：¥17,000/年**

## 9. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 账号格式多样性 | 高 | 中 | 建立账号格式库，支持多种银行 |
| 户名不规范 | 高 | 中 | 模糊匹配算法，人工复核 |
| OCR识别错误 | 中 | 高 | 人工二次确认，不完全依赖OCR |
| 系统性能瓶颈 | 低 | 中 | 数据库优化，缓存策略 |
| 数据安全泄露 | 低 | 高 | 加密存储，权限控制，审计日志 |

## 10. 后续扩展

### 10.1 集成方向
- 对接财务软件（用友、金蝶）
- 对接银企直连系统

### 10.2 功能扩展
- 预算管理
- 合同管理
- 发票管理
- 资金计划
- 现金流预测
