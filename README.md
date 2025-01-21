# Nonebot Plugin Neuro Draw

一个简单的抽签插件，每天可以抽取一次今日运势，感受一下 **Neuro-sama** 式的运气！

> 素材来自于 [Lucky Neuro Game](https://neuro.nya.pub/game/luck/)

## 功能
| 命令 | 用途 | 示例 |
| --- | --- | --- |
| neuro_draw / 牛签 / 抽签 | 抽取今日运势 | /抽签 |

*   每天每个用户只能抽取一次。
*   抽签结果会显示文字和对应的图片。


## 安装方法
<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-neuro-draw

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-neuro-draw
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-neuro-draw
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-neuro-draw
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-neuro-draw
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_neuro_draw"]

</details>
