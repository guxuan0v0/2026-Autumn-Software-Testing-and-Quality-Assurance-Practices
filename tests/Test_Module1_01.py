import os
import json
import time
import sys
import subprocess
import requests
from playwright.sync_api import sync_playwright


BASE_URL = "http://localhost:3000"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESULT_DIR = os.path.join(PROJECT_ROOT, "test_results")

BROWSER_DIR = os.path.join(PROJECT_ROOT, "evaluation", "browser")
SERVER_FILE = os.path.join(BROWSER_DIR, "server.py")

results = []

#lxy test_result record
def record(case_id, name, status, message):
    print(case_id, name, status, message)
    results.append({
        "case_id": case_id,
        "name": name,
        "status": status,
        "message": message
    })


def save_result():
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)

    file_path = os.path.join(RESULT_DIR, "result.json")

    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("测试结果已保存到：", file_path)#Module 1 Test

def start_server():
    p = subprocess.Popen(
        [sys.executable, SERVER_FILE],
        cwd=BROWSER_DIR
    )

    for i in range(10):
        try:
            r = requests.get(BASE_URL + "/calc", timeout=3)
            if r.status_code == 200:
                print("服务启动成功")
                return p
        except:
            pass

        time.sleep(1)

    print("服务可能没有正常启动，后面的测试可能失败")
    return p


def test_page_open():
    pages = ["/calc", "/env", "/props", "/container"]
    ok = True
    msg = ""

    for page in pages:
        try:
            r = requests.get(BASE_URL + page, timeout=5)
            msg += page + " 状态码=" + str(r.status_code) + "; "

            if r.status_code != 200:
                ok = False
        except Exception as e:
            ok = False
            msg += page + " 请求失败=" + str(e) + "; "

    if ok:
        record("M1-01", "访问浏览器实验页面", "OK", msg)
    else:
        record("M1-01", "访问浏览器实验页面", "NG", msg)


def test_html_suffix():
    try:
        r1 = requests.get(BASE_URL + "/calc", timeout=5)
        r2 = requests.get(BASE_URL + "/calc.html", timeout=5)

        msg = "/calc=" + str(r1.status_code) + ", /calc.html=" + str(r2.status_code)

        if r1.status_code == 200 and r2.status_code == 200:
            record("M1-02", "带与不带 html 后缀访问一致", "OK", msg)
        else:
            record("M1-02", "带与不带 html 后缀访问一致", "NG", msg)

    except Exception as e:
        record("M1-02", "带与不带 html 后缀访问一致", "NG", str(e))


def test_not_exist():
    try:
        r = requests.get(BASE_URL + "/not-exist", timeout=5)

        if r.status_code == 404:
            record("M1-03", "不存在页面返回错误", "OK", "返回 404")
        else:
            record("M1-03", "不存在页面返回错误", "NG", "实际状态码=" + str(r.status_code))

    except Exception as e:
        record("M1-03", "不存在页面返回错误", "NG", str(e))


def test_path_traversal():
    paths = [
        "/../server.py",
        "/%2e%2e/server.py",
        "/a/../../server.py"
    ]

    bad_paths = []
    msg = ""

    for path in paths:
        try:
            r = requests.get(BASE_URL + path, timeout=5)
            text = r.text.lower()
            msg += path + " 状态码=" + str(r.status_code) + "; "

            if "from flask" in text or "app.run" in text:
                bad_paths.append(path)

        except Exception as e:
            msg += path + " 请求异常=" + str(e) + "; "

    if len(bad_paths) == 0:
        record("M1-04", "拒绝目录穿越路径", "OK", msg + "未发现源码泄露")
    else:
        record("M1-04", "拒绝目录穿越路径", "NG", "这些路径可能泄露源码：" + str(bad_paths))


def test_missing_params():
    try:
        url = BASE_URL + "/report/full?experiment=calc&host=pc01&os=windows&browser=chrome"
        r = requests.post(url, json={"a": 1}, timeout=5)

        if r.status_code != 200:
            record("M1-05", "缺少必填查询参数", "OK", "缺少 release 参数时请求失败，状态码=" + str(r.status_code))
        else:
            record("M1-05", "缺少必填查询参数", "NG", "缺少参数仍然成功")

    except Exception as e:
        record("M1-05", "缺少必填查询参数", "NG", str(e))


def test_json_report():
    url = BASE_URL + "/report/full"

    params = {
        "experiment": "calc",
        "host": "pc01",
        "os": "windows",
        "browser": "chrome",
        "release": "test"
    }

    file_name = os.path.join(BROWSER_DIR, "report_calc_pc01_windows_chrome_test.json")

    if os.path.exists(file_name):
        os.remove(file_name)

    try:
        r = requests.post(
            url,
            params=params,
            json=[{"expression": "1+1", "result": "2px"}],
            timeout=5
        )

        if r.status_code == 200 and os.path.exists(file_name):
            record("M1-06", "合法 JSON 报告生成", "OK", "报告文件生成成功")
        else:
            record("M1-06", "合法 JSON 报告生成", "NG", "状态码=" + str(r.status_code) + "，报告文件没有生成")

    except Exception as e:
        record("M1-06", "合法 JSON 报告生成", "NG", str(e))

def test_create_append():
    params = {
        "experiment": "append",
        "host": "pc01",
        "os": "windows",
        "browser": "chrome",
        "release": "test"
    }

    file_name = os.path.join(BROWSER_DIR, "report_append_pc01_windows_chrome_test.txt")

    if os.path.exists(file_name):
        os.remove(file_name)

    try:
        requests.post(BASE_URL + "/report/create", params=params, timeout=5)
        requests.post(BASE_URL + "/report/append", params=params, data="line-1", timeout=5)
        requests.post(BASE_URL + "/report/append", params=params, data="line-2", timeout=5)

        if os.path.exists(file_name):
            text = open(file_name, encoding="utf-8", errors="ignore").read()

            if "line-1" in text and "line-2" in text:
                record("M1-07", "创建并连续追加文本报告", "OK", "追加内容成功")
                return

        record("M1-07", "创建并连续追加文本报告", "NG", "追加内容失败")

    except Exception as e:
        record("M1-07", "创建并连续追加文本报告", "NG", str(e))


def check_page_with_browser(case_id, name, url_path):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})

            response = page.goto(BASE_URL + url_path, timeout=10000)
            text = page.locator("body").inner_text()

            browser.close()

        if response.status == 200 and len(text.strip()) > 0:
            record(case_id, name, "OK", "页面能打开，正文不为空")
        else:
            record(case_id, name, "NG", "页面打开异常或正文为空")

    except Exception as e:
        record(case_id, name, "NG", str(e))


def test_calc_empty_input():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(BASE_URL + "/calc", timeout=10000)

            # 第一组：hostname 为空
            page.fill("#hostname", "")
            page.fill("#browserRelease", "test")
            page.select_option("#os", "windows")
            page.select_option("#browser", "chrome")
            page.click("button")

            request_happened = False

            try:
                response = page.wait_for_response(
                    lambda r: "/report/full" in r.url,
                    timeout=8000
                )
                request_happened = True
                status1 = response.status
            except:
                status1 = "无报告请求"

            # 第二组：browserRelease 为空
            page.goto(BASE_URL + "/calc", timeout=10000)
            page.fill("#hostname", "pc01")
            page.fill("#browserRelease", "")
            page.select_option("#os", "windows")
            page.select_option("#browser", "chrome")
            page.click("button")

            try:
                response = page.wait_for_response(
                    lambda r: "/report/full" in r.url,
                    timeout=8000
                )
                request_happened = True
                status2 = response.status
            except:
                status2 = "无报告请求"

            browser.close()

        msg = "hostname为空时=" + str(status1) + "；release为空时=" + str(status2)

        if not request_happened:
            record("M1-09", "空主机名和空版本校验", "OK", msg)
        else:
            record("M1-09", "空主机名和空版本校验", "POK", msg + "；页面未完全阻止提交，但服务端有响应")

    except Exception as e:
        record("M1-09", "空主机名和空版本校验", "NG", str(e))


def test_os_options():
    try:
        expected = ["windows", "macos", "linux", "chromeos", "android", "ios"]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(BASE_URL + "/calc", timeout=10000)

            values = page.eval_on_selector_all(
                "#os option",
                "options => options.map(o => o.value)"
            )

            browser.close()

        missing = []

        for item in expected:
            if item not in values:
                missing.append(item)

        if len(missing) == 0:
            record("M1-10", "操作系统选项覆盖", "OK", "操作系统选项完整：" + str(values))
        else:
            record("M1-10", "操作系统选项覆盖", "NG", "缺少选项：" + str(missing))

    except Exception as e:
        record("M1-10", "操作系统选项覆盖", "NG", str(e))


def test_calc_repeat():
    try:
        result_list = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            for i in range(3):
                page = browser.new_page(viewport={"width": 1280, "height": 800})
                page.goto(BASE_URL + "/calc", timeout=10000)

                page.fill("#hostname", "pc01")
                page.fill("#browserRelease", "test")
                page.select_option("#os", "windows")
                page.select_option("#browser", "chrome")

                # 为了不要跑太久，把页面里的 runs 改小一点
                page.evaluate("runs = 100")

                page.click("button")
                page.wait_for_timeout(3000)

                text = page.locator("#stat").inner_text()
                result_list.append(text)

                page.close()

            browser.close()

        if len(set(result_list)) == 1 and result_list[0] != "":
            record("M1-12", "同一环境重复运行稳定性", "OK", "三次结果一致：" + str(result_list))
        else:
            record("M1-12", "同一环境重复运行稳定性", "POK", "三次结果：" + str(result_list))

    except Exception as e:
        record("M1-12", "同一环境重复运行稳定性", "NG", str(e))


def test_props_form_style():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(BASE_URL + "/props", timeout=10000)
            page.wait_for_timeout(2000)

            count = page.evaluate("""
                () => {
                    let total = 0;
                    let names = ['input', 'button', 'select', 'textarea'];

                    for (let n of names) {
                        let list = document.querySelectorAll(n);
                        total += list.length;
                    }

                    for (let frame of document.querySelectorAll('iframe')) {
                        try {
                            let doc = frame.contentDocument;
                            for (let n of names) {
                                let list = doc.querySelectorAll(n);
                                total += list.length;
                            }
                        } catch(e) {}
                    }

                    return total;
                }
            """)

            browser.close()

        if count > 0:
            record("M1-21", "常用表单元素默认样式采集", "OK", "找到表单元素数量=" + str(count))
        else:
            record("M1-21", "常用表单元素默认样式采集", "NG", "没有找到 input/button/select/textarea 元素")

    except Exception as e:
        record("M1-21", "常用表单元素默认样式采集", "NG", str(e))


def test_props_repeat():
    try:
        text_lengths = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            for i in range(3):
                page = browser.new_page(viewport={"width": 1280, "height": 800})
                page.goto(BASE_URL + "/props", timeout=10000)
                page.wait_for_timeout(2000)

                text = page.locator("body").inner_text()
                text_lengths.append(len(text.strip()))

                page.close()

            browser.close()

        if len(set(text_lengths)) == 1 and text_lengths[0] > 0:
            record("M1-23", "重复采集一致性", "OK", "三次页面文本长度一致：" + str(text_lengths))
        else:
            record("M1-23", "重复采集一致性", "POK", "三次页面文本长度：" + str(text_lengths))

    except Exception as e:
        record("M1-23", "重复采集一致性", "NG", str(e))

def main():
    server = start_server()

    try:
        test_page_open()
        test_html_suffix()
        test_not_exist()
        test_path_traversal()
        test_missing_params()
        test_json_report()
        test_create_append()

        check_page_with_browser("M1-08", "calc 页面加载", "/calc")
        test_calc_empty_input()
        test_os_options()
        test_calc_repeat()

        check_page_with_browser("M1-16", "env 页面加载", "/env")
        check_page_with_browser("M1-20", "props 页面加载", "/props")
        test_props_form_style()
        test_props_repeat()

        check_page_with_browser("M1-24", "container 页面加载", "/container")

    finally:
        server.terminate()
        save_result()


if __name__ == "__main__":
    main()
