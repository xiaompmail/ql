# -*- coding: utf-8 -*-
"""
cron: 0 12 * * * tg_chat_once.py
new Env('TG发言-每个群发一条');
"""

import asyncio
import random
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogFiltersRequest

api_id = 2040
api_hash = "b18441a1ff607e10a989891a5462e627"

CHAT_FOLDER_NAME = "发言"

CHAT_MESSAGES = [
    "今天吃啥了",
    "抽奖",
    "周末去哪玩",
    "积分",
    "最近在忙啥",
    "今天心情如何",
    "天气真不错",
    "积分兑换",
    "大家周末好",
    "有什么好资源",
    "最近硬盘满了",
    "今天心情不错",
    "许愿中奖啦",
    "最近发现好东西",
    "这个怎么样",
    "有人在玩游戏吗",
    "最近更新快吗",
    "这个可以吗",
    "谁有推荐资源",
    "大家好久不见",
    "最近休息好么",
    "今天学习了吗",
    "有人收藏这个吗",
    "最近在折腾啥",
    "最近整理啥",
    "大家周末愉快",
    "最近有新发现",
    "许愿中奖",
    "福利不错的",
    "加油",
    "大家周末玩啥",
    "这个资源哪里找",
    "最近忙啥呢",
    "最近有新软件",
    "有人做笔记吗",
    "最近看啥",
    "谁有好资源",
    "今天过得怎么样",
    "大家在忙啥",
    "这个资源可用吗",
    "最近用什么",
    "谁有好的推荐",
    "努力",
    "大家周末计划",
    "不想努力了",
    "还久没去过",
    "最近发现啥了",
    "今天有什么好笑",
    "大家都在干嘛",
    "抽奖 抽奖",
    "最近抽奖中了吗",
    "大家好久没聊",
    "那个老师好",
    "大家好",
    "今天心情咋样",
    "谁有推荐好的",
    "大家周末计划呢",
    "上线参与一下",
    "谁收藏了这个",
    "大家休息好么",
    "最近有啥新资源",
    "谁发现好东西",
    "今天有没有好事",
    "大家都忙啥",
    "谁用过新版",
    "最近学习啥",
    "今天心情不错吧",
    "收藏",
    "谁有收藏资源",
    "参与必须安排",
    "谁发现新资源",
    "今天大家在干嘛",
    "最近在研究啥",
    "谁有好工具",
    "大家周末玩啥呢",
    "最近冲冲冲",
    "出击",
    "大家在干嘛呢",
    "最近在折腾啥",
    "谁去过这个",
    "今天有啥新发现",
    "大家休息如何",
    "最近在研究啥",
    "谁有新资源分享",
    "我想约的老师",
    "大家心情如何",
    "最近发现好资源",
    "谁去过这个",
    "今天有什么新资源",
    "大家都忙啥呢",
    "学习新姿势",
    "谁有好资源推荐",
    "今天在做啥",
    "大家周末愉快呀",
    "最近看啥资源",
    "推荐",
    "今天大家心情如何",
    "我太难了呀",
    "谁有推荐的",
    "今天大家在忙啥",
    "最近追剧了吗",
    "大家休息好吗",
    "今天心情如何呀",
    "最近在整理工具",
    "有好收藏分享下",
    "安排啥",
    "最近发现啥神器",
    "今天在忙啥呀",
    "大家学习如何",
    "最近有啥新发现",
    "一起聊天就好了",
    "今天在干啥呢",
    "大家心情不错吗",
    "谢谢分享",
    "收下了",
    "不错不错",
    "很好用",
    "已收藏",
    "不错啊",
    "真棒",
    "顶一下",
    "挺好",
    "了解了",
    "可以的",
    "赞一个",
    "哈哈哈",
    "稳稳的",
    "收到",
    "很实用",
    "厉害了",
    "棒棒哒",
    "太赞了",
    "不错哟",
    "ok啦",
    "棒啊",
    "👍",
    "👌",
    "哈哈",
    "感谢分享 👍",
    "这个不错",
    "求补档",
    "这个还有吗",
    "收藏了",
    "有没有类似的",
    "最近更新挺多",
    "这个质量可以",
]

# 群间延迟，防封
DELAY_MIN = 5
DELAY_MAX = 15


def peer_to_gid(p):
    if hasattr(p, "channel_id"):
        return int(f"-100{p.channel_id}")
    if hasattr(p, "chat_id"):
        return -p.chat_id
    return None


async def main():
    async with TelegramClient("auto_sign_safe", api_id, api_hash) as client:

        # 获取 dialogs 映射
        dialogs = {}
        async for d in client.iter_dialogs():
            dialogs[d.id] = d

        # 获取真实文件夹
        result = await client(GetDialogFiltersRequest())

        chat_groups = set()

        for f in result.filters:

            if not hasattr(f, "id"):
                continue

            title = f.title.text if hasattr(f.title, "text") else str(f.title)

            if title != CHAT_FOLDER_NAME:
                continue

            peers = []
            if f.pinned_peers:
                peers.extend(f.pinned_peers)
            if f.include_peers:
                peers.extend(f.include_peers)

            for p in peers:
                gid = peer_to_gid(p)
                if gid:
                    chat_groups.add(gid)

        if not chat_groups:
            print("没有发言群")
            return

        print(f"发言群数量: {len(chat_groups)}")

        # ⭐ 遍历每个群，发一条消息
        for gid in chat_groups:
            d = dialogs.get(gid)
            if not d:
                continue

            msg = random.choice(CHAT_MESSAGES)

            try:
                await client.send_message(gid, msg)
                print("已发言:", d.name, msg)
            except Exception as e:
                print("发言失败:", d.name, e)

            # 群间随机延迟
            await asyncio.sleep(random.randint(DELAY_MIN, DELAY_MAX))


if __name__ == "__main__":
    asyncio.run(main())