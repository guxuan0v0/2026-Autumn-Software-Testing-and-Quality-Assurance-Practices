# 模块二自动化测试脚本

本脚本对应测试用例 M2-01 至 M2-16，检查浏览器扩展的 Manifest 配置、CSS URL 提取、外链样式表处理、相对路径、网络分块、空地址和重复地址等问题。

## 运行方式

1. 将本目录放在 `cascading-spy-sheets-main` 仓库内，双击 `一键运行模块二测试.bat`。
2. 如果脚本无法自动找到源码，把源码根目录拖到该批处理文件上，或在命令行运行：

   `py -3 module2_ai_test_runner.py --source "你的路径\cascading-spy-sheets-main" --output results`

3. 结果保存在 `results/module2_results.json` 和 `results/module2_results.txt`。

## 运行条件

- Windows 10 或 Windows 11。
- Python 3.10 及以上。
- 不需要安装第三方 Python 包。

## 结果说明

- `OK`：当前源码满足该项源级检查。
- `NG`：脚本可稳定复现实现与预期的差异，应结合 Firefox Network 面板、扩展调试器和截图进一步确认。
- 该脚本不能替代 Firefox 中的最终人工执行。扩展安装、扩展开关对比和页面显示效果仍需按照 Excel 用例完成浏览器复核。
