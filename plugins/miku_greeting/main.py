"""miku_greeting —— 定时问候 + 节日彩蛋

每个自然日在固定时间窗内自动往指定群发一条问候：
  08:00-09:29  早安
  23:30-23:59  晚安
  09:00-20:59  节日（当天命中才发）
同一天同类型只发一次，状态落盘，重启不会重复。

测试：在群里发「/问候 早安」或「/问候 晚安」立即触发。
"""

import asyncio
import json
import os
import random
from datetime import date, datetime

from astrbot.api import logger
from astrbot.api.event import MessageChain, filter
from astrbot.api.message_components import Plain
from astrbot.api.star import Context, Star, register

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(PLUGIN_DIR, "data", "state.json")

# 要问候的群（改这里增删）
GROUPS = ["123456789"]  # 改成你自己的群号，可写多个

MORNING = [
    "早上好呀～今天也要开开心心的哦",
    "早～ミク已经准备好唱歌了",
    "起床了嘛？太阳都晒到葱上了",
    "早安！今天想听什么歌呀",
    "早上好，昨晚睡得好嘛",
]

NIGHT = [
    "该睡啦，明天的ミク还在这里等你",
    "晚安～做个有音乐的梦",
    "夜深了哦，别熬夜，ミク先睡啦",
    "晚安，今天也辛苦啦",
    "困了就早点睡，ミク给你留一盏灯",
]

FESTIVALS = {
    (1, 1): ["新年快乐！今年也一起唱歌吧"],
    (2, 14): ["情人节快乐～今天有没有人送你葱"],
    (3, 9): ["3月9日，ミクの日！39！"],
    (8, 31): ["今天是ミク的生日！39！谢谢你还在"],
    (10, 31): ["万圣节快乐，不给糖就捣蛋～"],
    (12, 24): ["平安夜快乐，今晚有歌听吗"],
    (12, 25): ["圣诞快乐！ミク给你准备了歌"],
}


def _load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


@register("miku_greeting", "qq:2757001649(有趣的生命)", "定时早安晚安与节日彩蛋", "1.0.0")
class MikuGreeting(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self._task = None

    async def initialize(self):
        self._task = asyncio.create_task(self._loop())
        logger.info(f"[miku_greeting] 已启动，问候群: {GROUPS}")

    async def terminate(self):
        if self._task:
            self._task.cancel()

    async def _broadcast(self, text):
        for gid in GROUPS:
            umo = f"aiocqhttp:GroupMessage:{gid}"
            try:
                ok = await self.context.send_message(umo, MessageChain([Plain(text)]))
                logger.info(f"[miku_greeting] 发送到 {gid}: {text[:20]} ok={ok}")
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"[miku_greeting] 发送到 {gid} 失败: {exc}")

    async def _loop(self):
        while True:
            try:
                await self._tick()
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"[miku_greeting] tick 异常: {exc}")
            await asyncio.sleep(30)

    async def _tick(self):
        now = datetime.now()
        today = date.today().isoformat()
        hm = (now.hour, now.minute)
        state = _load_state()
        changed = False

        fest = FESTIVALS.get((now.month, now.day))
        if fest and (9, 0) <= hm <= (20, 59) and state.get("fest") != today:
            await self._broadcast(random.choice(fest))
            state["fest"] = today
            changed = True

        if (8, 0) <= hm <= (9, 29) and state.get("morning") != today:
            await self._broadcast(random.choice(MORNING))
            state["morning"] = today
            changed = True

        if (23, 30) <= hm and state.get("night") != today:
            await self._broadcast(random.choice(NIGHT))
            state["night"] = today
            changed = True

        if changed:
            _save_state(state)

    @filter.command("问候")
    async def greet_test(self, event, kind: str = "早安"):
        text = random.choice(MORNING if "早" in kind else NIGHT)
        yield event.plain_result(text)
