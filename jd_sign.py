import os
import requests
import json
import time

import sys

# ----------------- 路径配置 -----------------
ql_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ql_root)

from notify import send  # 青龙 notify 推送

# ==========================================
# 1. 基础配置与 Cookie 获取
# ==========================================
cookie = os.environ.get("JD_COOKIE")

if not cookie:
    print("❌ 错误: 未找到 JD_COOKIE 环境变量，请在 GitHub Secrets 中配置。")
    exit(1)

# 通用 Header，部分任务会进行覆盖
base_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": cookie
}

# ==========================================
# 2. 辅助函数
# ==========================================
def parse_jsonp(text):
    try:
        if "jsonp_" in text:
            start = text.find('(') + 1
            end = text.rfind(')')
            return json.loads(text[start:end])
        return json.loads(text)
    except:
        return None

# ==========================================
# 3. 任务一：京东每日签到 (领京豆)
#    (基于你提供的旧代码)
# ==========================================
def jd_bean_sign():
    print("\n🚀 [任务1] 开始执行：京东签到 (领京豆)...")
    url = "https://api.m.jd.com/client.action"

    body = {
        "fp": "-1",
        "shshshfp": "-1",
        "shshshfpa": "-1",
        "referUrl": "-1",
        "userAgent": "-1",
        "jda": "-1",
        "rnVersion": "3.9"
    }

    params = {
        "functionId": "signBeanAct",
        "body": json.dumps(body, separators=(',', ':')),
        "appid": "ld",
        "client": "apple",
        "clientVersion": "10.0.4",
        "networkType": "wifi",
        "osVersion": "14.8.1",
        "uuid": str(int(time.time() * 1000)),
        "openudid": str(int(time.time() * 1000)),
        "jsonp": "jsonp_" + str(int(time.time() * 1000)) + "_58482"
    }

    try:
        # 使用你原代码中的 params 传参方式
        response = requests.post(url, params=params, headers=base_headers, timeout=10)
        data = parse_jsonp(response.text)

        if data:
            code = str(data.get("code"))
            if code == "0":
                print("✅ 签到成功！")
                try:
                    daily_award = data.get("data", {}).get("dailyAward", {})
                    award_count = daily_award.get('beanAward', {}).get('beanCount', '0')
                    print(f"🎉 获得奖励: {award_count} 京豆")
                except:
                    send("京东签到失败",data)
                    print("🎉 签到成功 (具体奖励解析失败)")
            elif code == "3":
                print("❌ 签到失败: Cookie 已失效")
                send("京东签到失败",data)
            else:
                msg = data.get("errorMessage", "无错误信息")
                if "已签到" in str(data) or "已签到" in response.text:
                    print("✅ 今天已经签到过了")
                else:
                    print(f"⚠️ 签到未成功: {msg}")
        else:
            print("❌ 无法解析服务器响应")
            send("京东签到失败","无法解析服务器响应")

    except Exception as e:
        print(f"❌ 领京豆请求错误: {e}")
        send("京东签到失败",f"❌ 领京豆请求错误: {e}")

def jd_bean_sign2():
    print("\n🚀 [任务2] 开始执行：京东刮卡 (领京豆)...")

    url = "https://api.m.jd.com/api?functionId=bff_rightsCenter_interaction&scene=commonDoInteractiveAssignment"

    payload = {
        "appid": "plus_business",
        "functionId": "bff_rightsCenter_interaction",
        "body": json.dumps({
            "scene": "commonDoInteractiveAssignment",
            "activityCode": "beanDailySign",
            "businessScenario": "jingDouCenter",
            "assignmentId": "3G2hqBX9ueg6QJDogBqa367uz3ij",
            "actionType": "100",
            "itemId": ""
        }),
        "loginType": "2",
        "xAPIClientLanguage": "zh_CN"
    }

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://pro.m.jd.com",
        "Referer": "https://pro.m.jd.com/",
        "User-Agent": "jdapp;android;13.8.6",
        "Cookie": cookie,
        "X-Requested-With": "com.jingdong.app.mall"
    }

    try:
        res = requests.post(url, headers=headers, data=payload, timeout=10)
        #print(res.text)

        data = res.json()
        code = str(data.get("code"))
        display_msg = data.get("displayMsg") or data.get("msg") or "未知返回"

        if code == "0":
            assignment_info = data.get("rs", {}).get("assignmentInfo", {})
            rewards_info = data.get("rs", {}).get("rewardsInfo", {})

            # 成功奖励
            success_rewards = rewards_info.get("successRewards", {})
            fail_rewards = rewards_info.get("failRewards", [])

            # 判断今天是否已签到
            if "已完成" in display_msg or assignment_info.get("completionCnt",0) >= 1:
                print(f"ℹ️ 今日已签到: {display_msg}")

            # 打印获得的京豆
            if success_rewards:
                # 遍历奖励字典
                for k, v in success_rewards.items():
                    reward_name = v.get("rewardName") or v.get("msg") or "京豆"
                    print(f"✅ 刮卡签到成功，获得: {reward_name}")
            elif fail_rewards:
                # 如果失败奖励里有信息，也打印提示
                for reward in fail_rewards:
                    reward_msg = reward.get("msg") or "未获得京豆"
                    print(f"⚠️ 刮卡信息: {reward_msg}")
            else:
                print("❌ 刮卡失败:", display_msg)
                send("京东签到失败", display_msg)

            # 休息2秒，避免请求过快
            time.sleep(2)
            #获取签到奖励
            jd_bean_reward_node();

    except Exception as e:
        print("❌ 请求异常:", e)
        send("京东签到失败",e)

def jd_bean_reward_node():
    print("\n🎁 [节点奖励] 开始领取刮卡节点奖励...")

    url = "https://api.m.jd.com/api"

    payload = {
        "appid": "plus_business",
        "functionId": "bff_rightsCenter_interaction",
        "body": json.dumps({
            "scene": "commonDoInteractiveAssignment",
            "activityCode": "beanRewardNode",
            "businessScenario": "jingDouCenter",
            "assignmentId": "1",
            "actionType": "0",
            "itemId": ""
        }),
        "loginType": "2",
        "xAPIClientLanguage": "zh_CN"
    }

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://pro.m.jd.com",
        "Referer": "https://pro.m.jd.com/",
        "User-Agent": "jdapp;android;13.8.6",
        "Cookie": cookie,
        "X-Requested-With": "com.jingdong.app.mall"
    }

    try:
        res = requests.post(url, headers=headers, data=payload, timeout=10)
        print(res.text)

        # ===== JSON 防炸 =====
        try:
            data = res.json()
        except Exception:
            print("❌ rewardNode 非JSON返回")
            send("京东节点奖励失败", res.text[:200])
            return

        code = str(data.get("code"))
        msg = data.get("displayMsg") or data.get("msg") or "未知返回"

        # ===== 风控判断 =====
        if "火爆" in msg or "稍后再试" in msg:
            print(f"⚠️ 可能风控: {msg}")
            send("京东节点奖励风控", msg)
            return

        if code != "0":
            print(f"ℹ️ 节点奖励状态: {msg}")
            return

        print(f"✅ 节点接口成功: {msg}")

        # ===== 奖励解析（核心）=====
        rs = data.get("rs", {})
        rewards_info = rs.get("rewardsInfo", {})
        success_rewards = rewards_info.get("successRewards")

        got_reward = False

        if isinstance(success_rewards, dict):
            for reward_group in success_rewards.values():

                # ⭐ list 结构（最常见）
                if isinstance(reward_group, list):
                    for reward in reward_group:
                        reward_name = reward.get("rewardName") or reward.get("prizeName") or "奖励"
                        quantity = reward.get("quantity", "")
                        print(f"🎉 节点获得: {reward_name} x {quantity}")
                        got_reward = True

                # ⭐ dict 结构（少见）
                elif isinstance(reward_group, dict):
                    reward_name = reward_group.get("rewardName") or reward_group.get("prizeName") or "奖励"
                    quantity = reward_group.get("quantity", "")
                    print(f"🎉 节点获得: {reward_name} x {quantity}")
                    got_reward = True

        # ===== 无奖励提示 =====
        if not got_reward:
            print("ℹ️ 节点无奖励（可能已领 / 未触发）")

    except Exception as e:
        print("❌ 节点奖励异常:", e)
        send("京东节点奖励异常", str(e))

# ==========================================
# 5. 主程序入口
# ==========================================
if __name__ == "__main__":
    # 京东秒杀
    jd_bean_sign()

    # 休息2秒，避免请求过快
    time.sleep(2)

    # 京东刮卡
    jd_bean_sign2()

    #jd_bean_reward_node()