import os
import json


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT_DIR = os.path.join(PROJECT_ROOT, "test_results")


cases = [
    {
        "case_id": "M1-11",
        "title": "浏览器选项与真实环境一致性",
        "module": "calc 实验 / 浏览器选项",
        "steps": [
            "打开 http://localhost:3000/calc",
            "选择当前真实浏览器名称",
            "运行一次测试",
            "检查报告中的 browser 是否与选择一致"
        ]
    },
    {
        "case_id": "M1-13",
        "title": "Chrome 页面识别 Windows 11",
        "module": "pocs/browser/poc_chrome.html",
        "steps": [
            "使用 Chrome 打开 pocs/browser/poc_chrome.html",
            "观察页面是否只显示 Windows 11 标签",
            "记录实际显示结果"
        ]
    },
    {
        "case_id": "M1-14",
        "title": "Firefox 页面识别 Windows 11",
        "module": "pocs/browser/poc_firefox.html",
        "steps": [
            "使用 Firefox 打开 pocs/browser/poc_firefox.html",
            "观察页面是否只显示 Windows 11 标签",
            "记录实际显示结果"
        ]
    },
    {
        "case_id": "M1-15",
        "title": "Tor 与 Chrome 翻译分支",
        "module": "pocs/browser/poc_tor.html / poc_chrome_translate.html",
        "steps": [
            "如果安装 Tor，打开 pocs/browser/poc_tor.html",
            "使用 Chrome 打开 pocs/browser/poc_chrome_translate.html",
            "分别测试翻译关闭、德语翻译、加泰罗尼亚语翻译",
            "记录页面最终显示的标签"
        ]
    },
    {
        "case_id": "M1-18",
        "title": "env 缩放边界下结果稳定",
        "module": "evaluation/browser/static/env.html",
        "steps": [
            "打开 http://localhost:3000/env",
            "分别设置浏览器缩放为 90%、100%、110%",
            "每次刷新后运行采集",
            "记录结果是否正常生成"
        ]
    },
    {
        "case_id": "M1-25",
        "title": "container 90% 缩放下尺寸采集",
        "module": "evaluation/browser/static/container.html",
        "steps": [
            "打开 http://localhost:3000/container",
            "设置浏览器缩放为 90%",
            "刷新页面并运行采集",
            "与 100% 基线结果比较"
        ]
    },
    {
        "case_id": "M1-26",
        "title": "container 110% 缩放下尺寸采集",
        "module": "evaluation/browser/static/container.html",
        "steps": [
            "打开 http://localhost:3000/container",
            "设置浏览器缩放为 110%",
            "刷新页面并运行采集",
            "与 100% 基线结果比较"
        ]
    },
    {
        "case_id": "M1-27",
        "title": "默认字体大小变化",
        "module": "evaluation/browser/static/container.html",
        "steps": [
            "打开浏览器字体设置",
            "分别设置小、中、大字体",
            "每次刷新 http://localhost:3000/container 并运行采集",
            "记录字体相关尺寸是否变化"
        ]
    },
    {
        "case_id": "M1-29",
        "title": "扫描 style 标签并预加载外部资源",
        "module": "mitigation/browser/extension/content.js",
        "steps": [
            "在 Firefox 临时加载 mitigation/browser/extension",
            "打开 mitigation/browser/testcases/index.html",
            "打开浏览器网络面板",
            "检查 style 标签中的资源是否被请求"
        ]
    },
    {
        "case_id": "M1-30",
        "title": "处理行内样式、image-set 与 data URL",
        "module": "mitigation/browser/extension/content.js",
        "steps": [
            "加载浏览器扩展",
            "打开包含 style 属性和 image-set 的测试页",
            "检查外部图片资源是否被请求",
            "确认 data URL 没有产生外部请求"
        ]
    },
    {
        "case_id": "M1-31",
        "title": "拦截外部样式表并转发资源地址",
        "module": "mitigation/browser/extension/background.js",
        "steps": [
            "加载浏览器扩展",
            "打开引用 external.css 的页面",
            "查看浏览器网络请求和扩展后台日志",
            "确认 CSS 中的图片资源被预加载"
        ]
    },
    {
        "case_id": "M1-32",
        "title": "CSS 地址跨响应分块时仍能识别",
        "module": "mitigation/browser/extension/background.js",
        "steps": [
            "准备一个可以分块返回 CSS 的本地服务",
            "将 url('/img/split.png') 拆成两段返回",
            "打开测试页面",
            "检查 split.png 是否被成功请求"
        ]
    }
]


def save_result(results):
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    file_path = os.path.join(RESULT_DIR, "manual_result.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("半自动化测试结果已保存到：", file_path)


def input_status():
    while True:
        status = input("请输入状态 OK/POK/NG/NT：").strip().upper()

        if status in ["OK", "POK", "NG", "NT"]:
            return status

        print("输入错误，只能输入 OK、POK、NG、NT")


def main():
    results = []

    print("模块一半自动化测试记录")
    print("执行方式：按照步骤人工测试，然后输入实际结果。")

    for case in cases:
        print()
        print("====================================")
        print("用例编号：", case["case_id"])
        print("用例标题：", case["title"])
        print("测试模块：", case["module"])
        print("操作步骤：")

        for i, step in enumerate(case["steps"], start=1):
            print(str(i) + ". " + step)

        actual_result = input("请输入实际结果：")
        status = input_status()
        remark = input("请输入备注，可为空：")

        results.append({
            "case_id": case["case_id"],
            "title": case["title"],
            "module": case["module"],
            "actual_result": actual_result,
            "status": status,
            "remark": remark
        })

    save_result(results)


if __name__ == "__main__":
    main()