#!/usr/bin/env python3
"""模块二浏览器扩展源级自动化检查。

默认使用 Python 标准库，不需要安装第三方包。脚本读取模块二源代码和测试页，
按 M2-01 至 M2-16 输出可复现的检查结果。浏览器集成场景仍需在 Firefox 中复核。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable
from urllib.parse import urljoin


@dataclass
class Result:
    case_id: str
    title: str
    status: str
    actual: str
    expected: str


class ExtensionModel:
    """按 content.js/background.js 当前实现复现 URL 提取过程。"""

    pattern = re.compile(r"url\(.*?\)|image\(.*?\)|image-set\(.*?\)", re.MULTILINE)

    @classmethod
    def extract(cls, css: str) -> list[str]:
        urls: list[str] = []
        for found in cls.pattern.findall(css):
            value = found.replace("'", "").replace('"', "")
            value = re.sub(r"\s\d+x", "", value)
            value = value.replace("image-set(", "")
            value = value.replace("image(", "")
            value = value.replace("url(", "")
            value = value.replace(")", "")
            value = re.sub(r"type\(.*\)", "", value)
            if value.startswith("data:"):
                continue
            urls.extend(value.split(","))
        return urls

    @classmethod
    def resolved_on_page(cls, css: str, page_url: str) -> list[str]:
        # HTMLImageElement.src 会在页面上下文中解析相对地址，并处理首尾空白。
        return [urljoin(page_url, value.strip()) for value in cls.extract(css)]


def locate_source(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    here = Path.cwd().resolve()
    script_dir = Path(__file__).resolve().parent
    for base in [here, script_dir, *here.parents, *script_dir.parents]:
        candidates.extend([
            base,
            base / "source" / "cascading-spy-sheets-main",
            base / "cascading-spy-sheets-main",
        ])
    for candidate in candidates:
        if (candidate / "mitigation" / "browser" / "extension" / "manifest.json").is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        "未找到源码目录。请使用 --source 指定包含 mitigation/browser 的 cascading-spy-sheets-main 目录。"
    )


def make_result(case_id: str, title: str, ok: bool, actual: str, expected: str) -> Result:
    return Result(case_id, title, "OK" if ok else "NG", actual, expected)


def run_checks(source: Path) -> list[Result]:
    browser = source / "mitigation" / "browser"
    extension = browser / "extension"
    testcases = browser / "testcases"
    manifest = json.loads((extension / "manifest.json").read_text(encoding="utf-8"))
    content_js = (extension / "content.js").read_text(encoding="utf-8")
    background_js = (extension / "background.js").read_text(encoding="utf-8")
    index_html = (testcases / "index.html").read_text(encoding="utf-8")
    external_css = (testcases / "external.css").read_text(encoding="utf-8")
    results: list[Result] = []

    required_permissions = {"activeTab", "webRequest", "webRequestBlocking", "<all_urls>"}
    actual_permissions = set(manifest.get("permissions", []))
    ok = (
        manifest.get("manifest_version") == 2
        and manifest.get("background", {}).get("scripts") == ["background.js"]
        and required_permissions.issubset(actual_permissions)
    )
    results.append(make_result(
        "M2-01", "Firefox 临时安装扩展前的 manifest 完整性", ok,
        f"manifest_version={manifest.get('manifest_version')}，permissions={sorted(actual_permissions)}",
        "Manifest V2、background.js 已注册，且四项必要权限齐全。",
    ))

    scripts = manifest.get("content_scripts", [])
    ok = bool(scripts) and scripts[0].get("matches") == ["<all_urls>"] and scripts[0].get("run_at") == "document_start"
    results.append(make_result(
        "M2-02", "content script 注入范围与时机", ok,
        f"content_scripts={scripts}",
        "content.js 对普通页面按 <all_urls> 匹配，并在 document_start 注册。",
    ))

    assets = {f"{name}.jpg" for name in ("one", "two", "three", "four", "five")}
    present_assets = {p.name for p in testcases.glob("*.jpg")}
    ok = assets.issubset(present_assets) and "external.css" in index_html
    results.append(make_result(
        "M2-03", "关闭扩展时的网络请求基线准备", ok,
        f"测试页图片={sorted(present_assets)}，引用external.css={'external.css' in index_html}",
        "基线页包含 one.jpg 至 five.jpg，并引用 external.css，能够执行扩展开关对比。",
    ))

    uses_source_tab = "details.tabId" in background_js and "tabs.query({ active: true, currentWindow: true })" not in background_js
    results.append(make_result(
        "M2-04", "预取消息发送到请求来源标签页", uses_source_tab,
        "background.js 使用当前窗口的活动标签页发送 fetch 消息。" if not uses_source_tab else "使用 details.tabId 发送消息。",
        "预取消息必须发送给 details.tabId 指向的请求来源标签页，不能误发给另一活动标签页。",
    ))

    css = "a{background:url(/a.png)}b{background:url('/b.png')}c{background:url(\"/c.png\")}d{background:url( /d.png )}"
    resolved = ExtensionModel.resolved_on_page(css, "http://localhost:3000/index.html")
    expected = {f"http://localhost:3000/{x}.png" for x in "abcd"}
    results.append(make_result(
        "M2-05", "url() 引号与空格变体", set(resolved) == expected,
        f"解析结果={resolved}", "a.png 至 d.png 均应得到规范化地址。",
    ))

    css = """.a{background-image:image-set(
      '/image-1x.jpg' 1x,
      '/image-2x.jpg' 2x,
      '/image-3x.jpg' 3x
    )}"""
    extracted = [value.strip() for value in ExtensionModel.extract(css) if value.strip()]
    ok = extracted == ["/image-1x.jpg", "/image-2x.jpg", "/image-3x.jpg"]
    results.append(make_result(
        "M2-06", "多行 image-set 倍率候选", ok,
        f"解析结果={extracted}", "多行 image-set 中三个不带 url() 的候选地址都应被识别。",
    ))

    css = "image-set(url('image1.avif') type('image/avif'), url('image2.jpg') type('image/jpeg'))"
    extracted = [value.strip() for value in ExtensionModel.extract(css) if value.strip()]
    ok = "image1.avif" in extracted and "image2.jpg" in extracted
    results.append(make_result(
        "M2-07", "嵌套 url() 与 type() 的 image-set", ok,
        f"解析结果={extracted}", "image1.avif 与 image2.jpg 均应被识别，MIME 提示不得进入 URL。",
    ))

    css = "image('/imagea.jpg', '/fallbacka.jpg')"
    extracted = [value.strip() for value in ExtensionModel.extract(css) if value.strip()]
    ok = extracted == ["/imagea.jpg", "/fallbacka.jpg"]
    results.append(make_result(
        "M2-08", "image() 多候选地址", ok,
        f"解析结果={extracted}", "主候选和回退候选均应被单独识别。",
    ))

    extracted = {value.strip() for value in ExtensionModel.extract(external_css)}
    ok = "/three.jpg" in extracted and "/four.jpg" in extracted
    results.append(make_result(
        "M2-09", "外链 CSS 媒体分支资源", ok,
        f"是否包含three/four={('/three.jpg' in extracted, '/four.jpg' in extracted)}",
        "three.jpg 与 four.jpg 均应被发现，不受媒体条件影响。",
    ))

    ok = "/style.css" in extracted
    results.append(make_result(
        "M2-10", "外链 CSS 的 @import 资源", ok,
        f"解析结果包含/style.css={ok}", "@import url('/style.css') 应被发现。",
    ))

    raw = "a{background:url('img/a.png')}"
    actual_url = ExtensionModel.resolved_on_page(raw, "http://localhost:3000/index.html")[0]
    expected_url = "http://localhost:3000/css/img/a.png"
    results.append(make_result(
        "M2-11", "外链 CSS 相对 URL 基准路径", actual_url == expected_url,
        f"当前页面上下文解析为 {actual_url}", f"应以 /css/external.css 为基准解析为 {expected_url}",
    ))

    part1, part2 = ".a{background:url('/img/spl", "it.png')}"
    per_chunk = ExtensionModel.extract(part1) + ExtensionModel.extract(part2)
    ok = any("split.png" in value for value in per_chunk)
    results.append(make_result(
        "M2-12", "URL 跨响应分块", ok,
        f"逐块解析结果={per_chunk}", "跨分块的 /img/split.png 应在响应结束后被完整识别。",
    ))

    style_blocks = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", index_html, flags=re.I | re.S))
    extracted_inline = {value.strip() for value in ExtensionModel.extract(style_blocks)}
    ok = "/one.jpg" in extracted_inline and "/two.jpg" in extracted_inline
    results.append(make_result(
        "M2-13", "内联 style 媒体查询资源", ok,
        f"解析结果={sorted(extracted_inline)}", "one.jpg 与 two.jpg 均应被发现。",
    ))

    style_values = re.findall(r"style=[\"'](.*?)[\"']", index_html, flags=re.I | re.S)
    extracted_attrs = {value.strip() for css_value in style_values for value in ExtensionModel.extract(css_value)}
    ok = "/five.jpg" in extracted_attrs
    results.append(make_result(
        "M2-14", "行内 style 属性资源", ok,
        f"解析结果={sorted(extracted_attrs)}", "five.jpg 应从 style 属性中被发现。",
    ))

    css = "a{background:url(data:image/png;base64,AAAA)}b{background:url('')}c{background:url(   )}d{background:url('/ok.png')}"
    resolved = ExtensionModel.resolved_on_page(css, "http://localhost:3000/index.html")
    unwanted = "http://localhost:3000/index.html" in resolved or any(value.startswith("data:") for value in resolved)
    ok = not unwanted and resolved.count("http://localhost:3000/ok.png") == 1
    results.append(make_result(
        "M2-15", "data URL 与空 URL", ok,
        f"页面上下文最终地址={resolved}", "data URL 和空 URL 应跳过，只有 /ok.png 被预取。",
    ))

    css = "a{background:url('/valid.png')}b{background:url('/valid.png')}c{background:url('#fragment')}"
    resolved = ExtensionModel.resolved_on_page(css, "http://localhost:3000/index.html")
    valid = "http://localhost:3000/valid.png"
    ok = resolved.count(valid) == 1 and not any("#fragment" in value for value in resolved)
    results.append(make_result(
        "M2-16", "重复 URL 与片段 URL 容错", ok,
        f"页面上下文最终地址={resolved}", "相同资源只预取一次，片段 URL 不应触发资源请求。",
    ))

    return results


def write_outputs(results: list[Result], source: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    counts = {status: sum(item.status == status for item in results) for status in ("OK", "NG")}
    payload = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": source.name,
        "scope": "模块二浏览器扩展源级自动化检查；Firefox 浏览器集成结果需另行人工复核",
        "summary": {"total": len(results), **counts},
        "results": [asdict(item) for item in results],
    }
    (output_dir / "module2_results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "模块二 AI 测自动化检查结果",
        f"总数：{len(results)}  OK：{counts['OK']}  NG：{counts['NG']}",
        "说明：本结果为源级自动化检查，Firefox 浏览器集成场景需另行复核。",
        "",
    ]
    for item in results:
        lines.extend([
            f"[{item.status}] {item.case_id} {item.title}",
            f"实际：{item.actual}",
            f"预期：{item.expected}",
            "",
        ])
    (output_dir / "module2_results.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="模块二浏览器扩展源级自动化检查")
    parser.add_argument("--source", help="cascading-spy-sheets-main 源码根目录")
    parser.add_argument("--output", default="results", help="结果输出目录，默认 results")
    args = parser.parse_args()
    try:
        source = locate_source(args.source)
        results = run_checks(source)
        write_outputs(results, source, Path(args.output).resolve())
    except Exception as exc:
        print(f"运行失败：{exc}", file=sys.stderr)
        return 2

    print("模块二自动化检查完成")
    for item in results:
        print(f"[{item.status}] {item.case_id} {item.title}")
    ng = sum(item.status == "NG" for item in results)
    print(f"总数={len(results)}，OK={len(results) - ng}，NG={ng}")
    print(f"结果目录：{Path(args.output).resolve()}")
    return 1 if ng else 0


if __name__ == "__main__":
    raise SystemExit(main())
