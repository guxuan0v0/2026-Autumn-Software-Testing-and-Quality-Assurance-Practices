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
