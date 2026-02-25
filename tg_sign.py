# -*- coding: utf-8 -*-
"""
cron: 0 12 * * * tg_auto_sign_safe.py
new Env('TG自动群签到-安全版');
"""

import asyncio
import random
from telethon import TelegramClient

# ===== 官方 Desktop App ID（公共方案）=====
api_id = 2040
api_hash = "b18441a1ff607e10a989891a5462e627"

# ===== 排除群关键字 =====
EXCLUDE_KEYWORDS = [
    "公告",
    "频道",
    "机器人",
]

# ===== 排除群ID =====
EXCLUDE_IDS = [
    -1003014564944,
    -1002709773262,
    -1002447327328,
    -1003305349155,
    -1003440786823,
    -1002154955235,
    -1002609360212,
    -1002627969430,
    -1001827827438,
    -5022848893
]

# ===== 签到内容（固定）=====
SIGN_TEXT = "签到"

# ===== ⭐ 文件夹签到（只处理该文件夹）=====
SIGN_FOLDER_ID = 1

# ===== 延迟配置（防封核心）=====
DELAY_MIN = 3
DELAY_MAX = 8

# ===== 分批（进一步防封）=====
BATCH_SIZE = 20
BATCH_SLEEP_MIN = 20
BATCH_SLEEP_MAX = 60


def need_skip(name, gid):
    if gid in EXCLUDE_IDS:
        return True

    for k in EXCLUDE_KEYWORDS:
        if k and k in (name or ""):
            return True
    return False


async def main():
    async with TelegramClient("auto_sign_safe", api_id, api_hash) as client:

        groups = []
        async for d in client.iter_dialogs():
            if d.is_group:
                groups.append(d)

        print("发现群数量:", len(groups))

        count = 0

        for d in groups:

            # ⭐⭐⭐ 只签到指定文件夹（新增）
            if getattr(d, "folder_id", None) != SIGN_FOLDER_ID:
                continue

            if need_skip(d.name, d.id):
                print("跳过:", d.name)
                continue

            try:
                await client.send_message(d.id, SIGN_TEXT)
                print("已签到:", d.name)
                count += 1
            except Exception as e:
                print("失败:", d.name, e)

            # ===== 群间随机延迟 =====
            delay = random.randint(DELAY_MIN, DELAY_MAX)
            await asyncio.sleep(delay)

            # ===== 分批休息（非常重要）=====
            if count > 0 and count % BATCH_SIZE == 0:
                sleep_time = random.randint(BATCH_SLEEP_MIN, BATCH_SLEEP_MAX)
                print(f"批次休息 {sleep_time}s（防风控）")
                await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    asyncio.run(main())