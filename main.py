from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.all import Image
import aiohttp
import asyncio
import random
import json


# 返回 JSON 格式的 API（需要解析图片 URL）
JSON_API_LIST = [
    "https://v2.xxapi.cn/api/baisi",
    "https://v2.xxapi.cn/api/heisi",
    "https://v2.xxapi.cn/api/jk",
    "https://v2.xxapi.cn/api/yscos",
    "https://api.lolimi.cn/API/meizi/api"
]

# 直接返回图片的 API
IMAGE_API_LIST = [
    "https://api.xk.ee/cosplay",
]

# 随机提示语列表
WAITING_MESSAGES = [
    "稍等一下哦",
    "等我一下，马上就好~",
    "这样啊,给你看个好东西吧v(￣▽￣)v",
    "刚准备好，等等哦~",
    "巧了，我也不得劲",
    "希望这能让你心情好一点",
]


@register(
    "astrbot_plugin_psychological",
    "YourName",
    "心理委员插件，输入 /心理委员 获取随机3次元美女图片",
    "1.0.0",
)
class PsychologicalPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """插件初始化方法"""
        pass

    async def _fetch_json_api(self, session: aiohttp.ClientSession, api_url: str, headers: dict) -> str | None:
        """处理返回 JSON 格式的 API，解析并返回图片 URL"""
        try:
            async with session.get(api_url, headers=headers, allow_redirects=False) as response:
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "").lower()
                
                # 检查是否为 JSON 响应
                if "json" in content_type:
                    json_data = await response.json()
                    # 根据 API 返回格式解析图片 URL
                    # 格式: {"code": 200, "msg": "...", "data": "图片URL", ...}
                    if isinstance(json_data, dict):
                        img_url = json_data.get("data")
                        if img_url and isinstance(img_url, str) and (img_url.startswith("http://") or img_url.startswith("https://")):
                            logger.info(f"从 JSON API 获取到图片 URL: {img_url}")
                            return img_url
                        else:
                            logger.warning(f"JSON API 返回的数据字段无效: {json_data}")
                            return None
                    else:
                        logger.warning(f"JSON API 返回的不是字典格式: {type(json_data)}")
                        return None
                else:
                    logger.warning(f"JSON API 返回的内容类型不是 JSON: {content_type}")
                    return None
        except Exception as e:
            logger.error(f"处理 JSON API 时发生错误: {str(e)}")
            return None

    async def _fetch_image_api(self, session: aiohttp.ClientSession, api_url: str, headers: dict) -> bytes | None:
        """处理直接返回图片的 API，返回图片数据"""
        try:
            async with session.get(api_url, headers=headers, allow_redirects=True) as response:
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "").lower()
                
                # 检查是否为图片响应
                if "image" in content_type:
                    img_data = await response.read()
                    if img_data and len(img_data) >= 100:
                        logger.info(f"从图片 API 获取到图片数据，大小: {len(img_data)} bytes")
                        return img_data
                    else:
                        logger.warning("获取的图片数据无效或太小")
                        return None
                # 某些 API 可能返回纯文本 URL
                elif "text" in content_type:
                    text_content = await response.text()
                    text_content = text_content.strip()
                    if text_content.startswith("http://") or text_content.startswith("https://"):
                        logger.info(f"图片 API 返回了 URL，再次请求: {text_content}")
                        # 再次请求图片
                        async with session.get(text_content, headers=headers) as img_response:
                            img_response.raise_for_status()
                            img_data = await img_response.read()
                            if img_data and len(img_data) >= 100:
                                return img_data
                else:
                    logger.warning(f"图片 API 返回的内容类型不是图片: {content_type}")
                    return None
        except Exception as e:
            logger.error(f"处理图片 API 时发生错误: {str(e)}")
            return None

    @filter.command("心理委员")
    async def psychological(self, event: AstrMessageEvent):
        """心理委员指令，随机返回一张图片"""
        # 随机选择一条提示语
        waiting_msg = random.choice(WAITING_MESSAGES)
        yield event.plain_result(waiting_msg)

        # 合并所有 API 列表并打乱，增加随机性
        all_apis = []
        for api_url in JSON_API_LIST:
            all_apis.append(("json", api_url))
        for api_url in IMAGE_API_LIST:
            all_apis.append(("image", api_url))
        random.shuffle(all_apis)

        # 创建会话
        timeout = aiohttp.ClientTimeout(total=60, connect=10)
        connector = aiohttp.TCPConnector(limit=10)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # 尝试每个API，直到成功
        last_error = None
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            for api_type, api_url in all_apis:
                try:
                    logger.info(f"尝试使用 {api_type.upper()} API: {api_url}")

                    if api_type == "json":
                        # 处理返回 JSON 的 API
                        img_url = await self._fetch_json_api(session, api_url, headers)
                        if img_url:
                            # 使用 Image.fromURL 发送图片
                            yield event.chain_result([Image.fromURL(img_url)])
                            logger.info("图片发送成功（通过 URL）")
                            return
                    else:
                        # 处理直接返回图片的 API
                        img_data = await self._fetch_image_api(session, api_url, headers)
                        if img_data:
                            # 使用 Image.fromBytes 发送图片
                            yield event.chain_result([Image.fromBytes(img_data)])
                            logger.info("图片发送成功（通过字节数据）")
                            return

                except (asyncio.TimeoutError, aiohttp.ServerTimeoutError) as e:
                    last_error = f"请求超时: {api_url}"
                    logger.warning(f"API请求超时: {api_url}")
                    continue
                except aiohttp.ClientError as e:
                    last_error = f"网络错误: {str(e) or type(e).__name__}"
                    logger.warning(f"API请求错误 ({api_url}): {str(e) or type(e).__name__}")
                    continue
                except Exception as e:
                    last_error = f"未知错误: {str(e) or type(e).__name__}"
                    logger.error(f"处理API时发生错误 ({api_url}): {str(e) or type(e).__name__}", exc_info=True)
                    continue

        # 所有API都失败了
        error_msg = last_error or "所有API都无法访问"
        logger.error(f"所有API都失败，最后错误: {error_msg}")
        yield event.plain_result(f"获取图片失败，请稍后再试")

    async def terminate(self):
        """插件销毁方法"""
        pass
