## 2026‑Autumn‑Software‑Testing‑and‑Quality‑Assurance‑Practices
HUST‑2026秋季｜软件测试与质量保证实践课程作业

小组名称：原神兴趣小组

组长：李梓豪 | 组员：冯籍平、刘修远、王宇钦

## 1. 仓库目录结构

```plaintext
2026-Autumn-Software-Testing-and-Quality-Assurance-Practices/
│
├── README.md                  #   项目说明、环境配置与测试运行方式
├── LICENSE                    #   仓库许可证
│
├── source/                    #   被测系统源代码
│   └── cascading-spy-sheets-main/
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
│   ├── Test_Module1_01.py     #   模块一完全自动化测试
│   └── Test_Module1_02.py     #   模块一半自动化测试记录
│
├── testcases/                 #   手工、自动化测试用例与分工说明
│   ├── 小组分工细则.md
│   ├── 测试用例清单_v1.xlsx
│   └── 测试用例清单_v2.xlsx
│
├── defects/                   #   Bug缺陷记录文档与截图
│   ├── 附录2：缺陷报告模板.doc
│   ├── BUG001.png
│   ├── BUG002.png
│   ├── BUG003.png
│   ├── BUG004.png
│   ├── BUG005.png
│   └── BUG2&3_solvation.png
│
├── docs/                      #   测试报告与汇报材料
│   ├── 无脚本浏览器指纹识别系统测试汇报.pptx
│   └── 附录3：测试报告模板（模块一）.docx
│
├── evidence/                  #   系统演示与测试运行证据
│   ├── 系统功能演示.mp4
│   └── 自动化测试演示.mp4
│
└── ai_logs/                   #   AI对话、Prompt记录
    └── .gitkeep               #   目录占位文件，待补充记录
```

## 2. 环境配置

### 2.1 硬件配置

| 类别 | 配置说明 |
| --- | --- |
| 测试主机 | 笔记本电脑 |
| 处理器 | 11th Gen Intel(R) Core(TM) i5-1155G7 @ 2.50 GHz |
| 内存 | 16.0 GB（15.8 GB 可用） |
| 显卡 | Intel(R) Iris(R) Xe Graphics（128 MB） |
| 操作系统 | Windows 11（64 位） |

### 2.2 软件及版本

以下为本次测试记录中的软件版本。

| 类别 | 软件或依赖库 | 版本 |
| --- | --- | --- |
| 编程语言 | Python | 3.13.1 |
| Web 框架 | Flask | 3.0.0 |
| 数据处理 | pandas | 2.2.2 |
| 数值计算 | numpy | 2.1.0 |
| 数据可视化 | matplotlib | 3.9.2 |
| 统计可视化 | seaborn | 0.13.2 |
| 图像处理 | Pillow | 10.4.0 |
| Web 工具库 | Werkzeug | 3.0.1 |
| User-Agent 解析 | user-agent-parser | 2.2.2 |

> 上述版本为测试环境记录；重新搭建环境时，应确认依赖与所用 Python 版本兼容。

## 3. 测试运行方式

以下命令使用 Windows 命令提示符（CMD）执行。除特别说明外，均在仓库根目录下运行。

### 3.1 获取项目

克隆仓库并进入仓库根目录：

```bat
git clone https://github.com/guxuan0v0/2026-Autumn-Software-Testing-and-Quality-Assurance-Practices.git
cd 2026-Autumn-Software-Testing-and-Quality-Assurance-Practices
```

也可下载仓库 ZIP 文件，解压后进入对应目录。

与本次测试相关的目录如下：

```text
2026-Autumn-Software-Testing-and-Quality-Assurance-Practices/
├── source/
│   └── cascading-spy-sheets-main/       # 被测系统根目录
│       ├── evaluation/
│       │   └── browser/
│       │       └── server.py           # 浏览器实验服务入口
│       ├── mitigation/                # 缓解方案及扩展代码
│       └── pocs/                      # PoC 演示页面
├── tests/
│   ├── Test_Module1_01.py              # 完全自动化测试
│   └── Test_Module1_02.py              # 半自动化测试记录
├── testcases/                         # 测试用例
├── defects/                           # 缺陷记录文档
├── evidence/                          # 截图及运行证据
└── test_results/                      # 测试脚本运行后生成
```

### 3.2 创建并启用 Python 虚拟环境

在仓库根目录创建虚拟环境：

```bat
python -m venv .venv
```

启用虚拟环境：

```bat
.venv\Scripts\activate
```

后续各终端窗口执行 Python 命令前，均需启用该虚拟环境。

### 3.3 安装运行与测试依赖

安装浏览器实验服务和模块一测试脚本所需依赖：

```bat
python -m pip install Flask==3.0.0 Werkzeug==3.0.1 user-agent-parser==2.2.2 requests playwright
python -m playwright install chromium
```

第 2.2 节中的 pandas、numpy、matplotlib、seaborn 和 Pillow 为项目其他处理、分析任务涉及的依赖，运行对应模块时按需安装。

### 3.4 适配自动化测试脚本路径

当前源码位于 `source/cascading-spy-sheets-main/`，测试脚本位于 `tests/`。

运行前，需要将 `tests/Test_Module1_01.py` 中的：

```python
BROWSER_DIR = os.path.join(PROJECT_ROOT, "evaluation", "browser")
```

修改为：

```python
BROWSER_DIR = os.path.join(
    PROJECT_ROOT,
    "source",
    "cascading-spy-sheets-main",
    "evaluation",
    "browser",
)
```

保留原有 `PROJECT_ROOT`、`RESULT_DIR` 和 `SERVER_FILE` 的定义。这样，脚本能够定位被测服务，并将测试结果保存到仓库根目录下的 `test_results/`。

### 3.5 手动验证被测服务

从仓库根目录进入浏览器模块目录：

```bat
cd source\cascading-spy-sheets-main\evaluation\browser
python server.py
```

服务启动后，在浏览器中依次访问：

- [calc 实验页面](http://localhost:3000/calc)
- [env 实验页面](http://localhost:3000/env)
- [props 实验页面](http://localhost:3000/props)
- [container 实验页面](http://localhost:3000/container)

检查页面能否访问，并记录页面空白、内容缺失或加载异常等情况。

验证结束后，按 `Ctrl+C` 停止服务，再返回仓库根目录：

```bat
cd ..\..\..\..
```

### 3.6 执行完全自动化测试

确认已完成第 3.4 节的路径修改，并停止手动启动的服务，避免占用 `3000` 端口。

在仓库根目录执行：

```bat
python tests\Test_Module1_01.py
```

脚本会自动启动 `evaluation/browser/server.py`，执行接口与浏览器自动化测试，结束后停止服务并保存结果。

结果文件：

```text
test_results/result.json
```

### 3.7 执行半自动化测试记录

半自动化脚本负责展示测试步骤并记录人工输入，不会自动启动被测服务。

先在一个已启用虚拟环境的 CMD 窗口中启动服务：

```bat
cd source\cascading-spy-sheets-main\evaluation\browser
python server.py
```

再打开另一个 CMD 窗口，进入仓库根目录并执行：

```bat
.venv\Scripts\activate
python tests\Test_Module1_02.py
```

测试人员按脚本提示执行对应操作，输入实际结果、测试状态和备注。

| 状态 | 含义 |
| --- | --- |
| `OK` | 通过 |
| `POK` | 部分通过，需进一步复核 |
| `NG` | 不通过 |
| `NT` | 未测试 |

脚本中提及的 `pocs/`、`mitigation/` 和 `evaluation/` 路径，均相对于被测系统根目录 `source/cascading-spy-sheets-main/`。

涉及 Firefox、Tor、浏览器扩展或其他额外测试条件的用例，应先准备相应环境；未执行的用例记录为 `NT`，并注明原因。

完成全部录入后，结果保存到：

```text
test_results/manual_result.json
```

### 3.8 缺陷记录

结合以下结果文件中的 `NG`、`POK` 项及人工复核结果，筛选有效缺陷：

- `test_results/result.json`
- `test_results/manual_result.json`

缺陷报告保存在 `defects/`，相关截图和运行证据保存在 `evidence/`。

根据本次测试记录，已确认的主要缺陷包括：

| 缺陷编号 | 缺陷描述 |
| --- | --- |
| BUG-001 | 相同参数重复提交报告时，旧报告文件被覆盖 |
| BUG-002 | `/props` 页面正文为空 |
| BUG-003 | `/props` 连续三次采集结果均为空 |

缺陷报告应包含复现步骤、预期结果、实际结果、测试环境及关联证据，便于后续定位和回归验证。

