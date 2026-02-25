# -*- coding: utf-8 -*-
import asyncio
import datetime
import json
import httpx
import sys
import os

# ----------------- 路径配置 -----------------
ql_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ql_root)

from notify import send  # 青龙 notify 推送

# 保存最新推送时间戳的文件
LAST_PUSH_FILE = os.path.join(os.path.dirname(__file__), "last_push_time.txt")

# ----------------- 配置区 -----------------
JSON_URL = "https://www.cninfo.com.cn/new/fulltextSearch/full?searchkey=%E8%82%A1%E4%B8%9C%E5%9B%9E%E9%A6%88&sdate=&edate=&isfulltext=false&sortName=pubdate&sortType=desc&pageNum=1&pageSize=20&type="
# -----------------------------------------

async def extract_announcements(json_url):
    """获取公告列表"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(json_url, timeout=10)
            response.raise_for_status()
            json_data = response.json()
    except httpx.RequestError as e:
        raise ConnectionError(f"获取 JSON 数据失败：{e}")
    except json.JSONDecodeError:
        raise ValueError("获取的内容不是有效的 JSON 格式")

    if isinstance(json_data, dict) and "announcements" in json_data and isinstance(json_data["announcements"], list):
        announcement_list = json_data["announcements"]
    else:
        raise ValueError("JSON 数据不包含 'announcements' 列表")

    required_fields = ["secCode", "announcementTitle", "orgId", "announcementId", "announcementTime"]
    valid_announcements = [
        item for item in announcement_list
        if all(f in item and item[f] is not None for f in required_fields)
    ]

    # 排序，最新在前
    valid_announcements.sort(key=lambda x: x["announcementTime"], reverse=True)
    return valid_announcements

def read_last_push_time():
    if os.path.exists(LAST_PUSH_FILE):
        with open(LAST_PUSH_FILE, "r", encoding="utf-8") as f:
            ts_str = f.read().strip()
            return int(ts_str)
    return 0

def write_last_push_time(timestamp):
    with open(LAST_PUSH_FILE, "w", encoding="utf-8") as f:
        f.write(str(int(timestamp)))

async def main():
    try:
        announcements = await extract_announcements(JSON_URL)
        if not announcements:
            print("没有获取到公告")
            return

        last_push_time = read_last_push_time()
        to_push = [ann for ann in announcements if ann["announcementTime"] > last_push_time]

        if not to_push:
            print(f"没有新公告，跳过推送 (上次推送时间戳: {last_push_time})")
            return

        # 逐条推送，先旧后新
        for ann in reversed(to_push):
            ann_time_str = datetime.datetime.fromtimestamp(ann["announcementTime"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            title = f"{ann['secCode']} {ann_time_str}"
            content = f"公告标题：{ann['announcementTitle']}\n公告链接：https://www.cninfo.com.cn/new/disclosure/detail?orgId={ann['orgId']}&announcementId={ann['announcementId']}&announcementTime={ann_time_str}"
            send(title, content)
            print(f"已推送: {title}")

        # 更新最新推送时间
        newest_time = max(ann["announcementTime"] for ann in announcements)
        write_last_push_time(newest_time)
        print(f"已更新 last_push_time 为 {newest_time}")

    except Exception as e:
        print(f"脚本执行失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())