import json
import random
import aiohttp
from pathlib import Path
from datetime import date
from nonebot.log import logger
from nonebot.adapters import Event, Bot
from nonebot import on_command, require
from typing import Dict, Optional, Tuple
from nonebot.plugin import PluginMetadata
from nonebot.plugin import inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store
from nonebot_plugin_alconna import Image, UniMessage


__plugin_meta__ = PluginMetadata(
    name="NeuroDraw",
    description="Neuro-sama 的每日一签",
    usage="/neuro_draw 或 /牛签 或 /抽签",
    type="application",
    homepage="https://github.com/zhaomaoniu/nonebot-plugin-neuro-draw",
    config=None,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)


class LuckDrawConfig:
    """抽签配置类"""

    LUCK_IMAGES = {
        "大吉": "https://neuro.nya.pub/game/luck/luck%20(1).png",
        "吉": "https://neuro.nya.pub/game/luck/luck%20(2).png",
        "中吉": "https://neuro.nya.pub/game/luck/luck%20(3).png",
        "小吉": "https://neuro.nya.pub/game/luck/luck%20(4).png",
        "末吉": "https://neuro.nya.pub/game/luck/luck%20(5).png",
        "凶": "https://neuro.nya.pub/game/luck/luck%20(6).png",
    }


class UserLuckManager:
    """用户抽签数据管理类"""

    def __init__(self, data_file: Path):
        self.data_file = data_file
        self._ensure_data_file()

    def _ensure_data_file(self) -> None:
        """确保数据文件存在"""
        if not self.data_file.exists():
            self.save_data({})

    def load_data(self) -> Dict:
        """加载用户数据"""
        try:
            return json.loads(self.data_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_data(self, data: Dict) -> None:
        """保存用户数据"""
        self.data_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8"
        )

    def get_user_luck(self, user_id: str) -> Optional[Dict]:
        """获取用户的抽签记录"""
        data = self.load_data()
        return data.get(user_id)

    def update_user_luck(self, user_id: str, luck_type: str) -> None:
        """更新用户的抽签记录"""
        data = self.load_data()
        data[user_id] = {"date": date.today().isoformat(), "luck": luck_type}
        self.save_data(data)


class ImageManager:
    """图片管理类"""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get_image(self, url: str, name: str) -> Path:
        """获取图片，如果缓存中没有则下载"""
        cache_path = self.cache_dir / f"{name}.png"
        if cache_path.exists():
            return cache_path

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    cache_path.write_bytes(data)
                    return cache_path
                raise Exception(
                    f"Failed to download image: {url}, status: {resp.status}"
                )


class LuckDrawHandler:
    """抽签处理类"""

    def __init__(self):
        self.user_manager = UserLuckManager(
            store.get_plugin_data_dir() / "user_luck.json"
        )
        self.image_manager = ImageManager(store.get_plugin_cache_dir())

    async def handle_luck_draw(self, user_id: str) -> Tuple[str, Path]:
        """处理抽签请求"""
        today = date.today().isoformat()
        user_luck = self.user_manager.get_user_luck(user_id)

        # 检查是否已经抽过签
        if user_luck and user_luck["date"] == today:
            luck_type = user_luck["luck"]
            image_path = await self.image_manager.get_image(
                LuckDrawConfig.LUCK_IMAGES[luck_type], luck_type
            )
            return f"你今天已经抽过签啦，结果是「{luck_type}」哦！", image_path

        # 随机抽取新的签
        luck_type = random.choice(list(LuckDrawConfig.LUCK_IMAGES.keys()))
        image_path = await self.image_manager.get_image(
            LuckDrawConfig.LUCK_IMAGES[luck_type], luck_type
        )

        # 更新用户记录
        self.user_manager.update_user_luck(user_id, luck_type)
        return f"你今天的运势是「{luck_type}」哦！", image_path


# 初始化抽签处理器和命令
draw_handler = LuckDrawHandler()
draw_luck = on_command("neuro_draw", aliases={"牛签", "抽签"}, priority=10)


@draw_luck.handle()
async def handle_draw_luck(bot: Bot, event: Event):
    """处理抽签命令"""
    try:
        message, image_path = await draw_handler.handle_luck_draw(event.get_user_id())
        await draw_luck.send(
            await UniMessage([message, Image(path=image_path)]).export(bot)
        )
    except Exception as e:
        await draw_luck.send(f"抽签失败：{str(e)}")
        logger.error(f"Failed to draw luck: {e}")
