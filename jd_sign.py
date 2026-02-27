# -*- coding: utf-8 -*-
"""
cron: 0 12 * * * tg_sign_by_folder.py
new Env('TG签到-真实文件夹');
"""

import asyncio
import random
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogFiltersRequest

api_id = 2040
api_hash = "b18441a1ff607e10a989891a5462e627"

SIGN_TEXT = "签到"
SIGN_FOLDER_NAME = "签到群"

DELAY_MIN = 3
DELAY_MAX = 8


def peer_to_gid(p):
    if hasattr(p, "channel_id"):
        return int(f"-100{p.channel_id}")
    if hasattr(p, "chat_id"):
        return -p.chat_id
    return None


async def main():
    async with TelegramClient("auto_sign_safe", api_id, api_hash) as client:

        # dialogs 映射
        dialogs = {}
        async for d in client.iter_dialogs():
            dialogs[d.id] = d

        result = await client(GetDialogFiltersRequest())

        sign_groups = set()

        for f in result.filters:

            if not hasattr(f, "id"):
                continue

            title = f.title.text if hasattr(f.title, "text") else str(f.title)

            if title != SIGN_FOLDER_NAME:
                continue

            peers = []
            if f.pinned_peers:
                peers.extend(f.pinned_peers)
            if f.include_peers:
                peers.extend(f.include_peers)

            for p in peers:
                gid = peer_to_gid(p)
                if gid:
                    sign_groups.add(gid)

        print("签到群数量:", len(sign_groups))

        for gid in sign_groups:
            d = dialogs.get(gid)
            if not d:
                continue

            try:
                await client.send_message(gid, SIGN_TEXT)
                print("已签到:", d.name)
            except Exception as e:
                print("签到失败:", d.name, e)

            await asyncio.sleep(random.randint(DELAY_MIN, DELAY_MAX))


if __name__ == "__main__":
    asyncio.run(main())