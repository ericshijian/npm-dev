# test only

## 技术栈

- **框架**: Next.js 16+ (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **国际化**: next-intl
- **动画**: Framer Motion
- **图表**: Recharts
- **图标**: Lucide React

## 开发

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

静态导出产物目录为 `out/`，可直接部署到 GitHub Pages 或任意静态托管平台。

## GitHub Actions 一键部署

已提供工作流文件：`.github/workflows/deploy.yml`  
触发方式：
- 推送到 `main` 自动部署
- 在 GitHub Actions 页面手动点击 `Run workflow` 一键部署

### 1. 首次配置

在仓库 `Settings -> Pages` 中：
- `Source` 选择 `GitHub Actions`

无需配置服务器 SSH/PM2 Secrets。

### 2. 部署执行逻辑

工作流会自动执行：

```bash
npm ci
npm run build
```

然后把 `out/` 目录发布到 GitHub Pages。

### 3. 静态数据来源

数据直接从 `Content/Arena/` 目录下的 CSV 和 JSON 文件读取：

- `Content/Arena/List of Arenas ZH.csv` - 擂台基础信息（中文）
- `Content/Arena/List of Arenas EN.csv` - 擂台基础信息（英文）
- `Content/Arena/All Arenas/{folder}/overview.zh.json` - 中文概览
- `Content/Arena/All Arenas/{folder}/overview.en.json` - 英文概览
- `Content/Arena/All Arenas/{folder}/implementation.zh.json` - 中文实施方案
- `Content/Arena/All Arenas/{folder}/implementation.en.json` - 英文实施方案
- `Content/Arena/All Arenas/{folder}/tech-configuration.zh.json` - 中文技术配置
- `Content/Arena/All Arenas/{folder}/tech-configuration.en.json` - 英文技术配置

## 项目结构

```
├── app/
│   └── [locale]/          # 国际化路由
│       ├── layout.tsx     # 布局
│       ├── page.tsx       # 首页
│       └── arena/         # Arena页面
├── components/
│   ├── layout/           # 布局组件
│   └── ui/               # UI组件
├── lib/
│   ├── types.ts          # 类型定义
│   └── utils.ts          # 工具函数
├── locales/
│   ├── en.json           # 英文翻译
│   └── zh.json           # 中文翻译
├── Content/              # 内容文件
└── PRD/                  # 设计文档
```

## 特性

- ✅ 双语支持（中英）
- ✅ 响应式设计
- ✅ 现代化UI
- ✅ 可访问性
- ✅ SEO友好
- ✅ 类型安全
