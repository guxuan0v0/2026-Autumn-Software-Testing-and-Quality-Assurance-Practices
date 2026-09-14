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
