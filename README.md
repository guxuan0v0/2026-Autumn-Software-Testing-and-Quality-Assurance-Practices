## 2026‑Autumn‑Software‑Testing‑and‑Quality‑Assurance‑Practices
HUST‑2026秋季｜软件测试与质量保证实践课程作业

小组名称：原神兴趣小组

组长：李梓豪 | 组员：冯籍平、刘修远、王宇钦

## 1. 仓库目录结构
```plaintext
2026‑Autumn‑Software‑Testing‑and‑Quality‑Assurance‑Practices/
│
├── source/                    #   被测系统源代码
│   └── cascading‑spy‑sheets‑main/
│       ├── evaluation/        #   核心数据采集与分析
│       │   ├── browser/       #   浏览器侧评估（采集脚本 + JSON结果 + 分析脚本）
│       │   ├── email/         #   邮件客户端侧评估（CSV数据集 + 收发脚本）
│       │   └── translate/     #   翻译扩展（i18n指纹研究）
│       │
│       ├── mitigation/        #   缓解方案 PoC
│       │   ├── browser/       #   浏览器扩展 + 性能开销测量评估
│       │   └── email/         #   邮件侧缓解代码
│       │
│       └── pocs/              #   公开 PoC 演示
│           ├── browser/       #   浏览器侧 PoC（Chrome/Firefox/Tor）
│           ├── email/         #   邮件侧 PoC（OS/print/office/style探测）
│           ├── examples/      #   单点能力示例
│           └── extensions/    #   扩展指纹 PoC
│
├── tests/                     #   测试自动化脚本
├── testcases/                 #   手工、自动化测试用例
├── defects/                   #   Bug缺陷记录文档
├── docs/                      #   方案、报告、说明文档
├── evidence/                  #   截图、数据集、运行证据
└── ai_logs/                   #   AI对话、Prompt记录
```
## 2. 环境配置
软件	版本说明
操作系统	 Windows11
Python	3.12
浏览器	Chrome / Edge / FireFox
Node.js	浏览器脚本运行依赖
