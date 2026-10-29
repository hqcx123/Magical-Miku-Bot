"""限制单次 LLM 请求里的图片数量。

背景：deepseek-flash 支持看图，但每张图要吃掉几百 token。群里连续刷图时
上下文会迅速膨胀、响应变慢，甚至触发上下文压缩丢历史。这里在请求真正发给
模型前做一次裁剪：当前消息最多保留 3 张，历史消息里超出的图片替换成
「[图片]」文字占位，保持上下文结构合法。
"""

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star, register

MAX_IMAGES = 3
PLACEHOLDER = "[图片]"


def _is_image_part(part: object) -> bool:
    return isinstance(part, dict) and part.get("type") == "image_url"


@register(
    "miku_image_limit",
    "qq:2757001649(有趣的生命)",
    "限制每次请求最多 3 张图，控制上下文膨胀",
    "1.0.0",
)
class MikuImageLimit(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.on_llm_request()
    async def limit_images(
        self, event: AstrMessageEvent, req: ProviderRequest
    ) -> None:
        budget = MAX_IMAGES
        dropped = 0

        # 1) 当前这条消息附带的图片：超过配额的部分直接丢掉
        if len(req.image_urls) > budget:
            dropped += len(req.image_urls) - budget
            req.image_urls = req.image_urls[:budget]
        budget -= len(req.image_urls)

        # 2) 历史上下文里的图片：从最新往回保留，超出配额的换成文字占位
        for msg in reversed(req.contexts):
            content = msg.get("content") if isinstance(msg, dict) else None
            if not isinstance(content, list):
                continue
            for i in range(len(content) - 1, -1, -1):
                part = content[i]
                if not _is_image_part(part):
                    continue
                if budget > 0:
                    budget -= 1
                else:
                    content[i] = {"type": "text", "text": PLACEHOLDER}
                    dropped += 1

        if dropped:
            logger.info(f"[image-limit] 本次请求丢弃 {dropped} 张图片，保留 {MAX_IMAGES} 张")
