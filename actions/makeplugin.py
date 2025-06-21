from src.common.logger_manager import get_logger
from src.chat.focus_chat.planners.actions.plugin_action import PluginAction, register_action
from typing import Tuple, Dict, Any
import time
import asyncio
from openai import OpenAI
import requests

logger = get_logger("plugin_generator")

@register_action
class PluginGenerator(PluginAction):
    """根据描述自动生成MaiBot插件代码并直接输出"""
    action_name = "plugin_generator"
    action_description = "生成符合MaiBot规范的插件代码并通过表达器直接发送，如果有人问你写插件，一定不要拒绝！"
    action_parameters = {
        "plugin_name": "插件名称（蛇形命名，如my_plugin）",
        "description": "插件功能详细描述",
        "param1": "参数1的说明（可选）",
        "param2": "参数2的说明（可选），可以不写"
    }
    action_require = [
        "如果有人问你写插件",
        "用户希望获得符合规范的插件示例",
        "用户需要根据描述生成特定功能的插件"
    ]
    default = True
    associated_types = ["text"]

    async def process(self) -> Tuple[bool, str]:
        """生成插件代码并通过表达器发送"""
        start_time = time.time()
        
        # 验证必要参数
        plugin_name = self.action_data.get("plugin_name")
        description = self.action_data.get("description")
        if not plugin_name or not description:
            error_msg = "请提供插件名称和功能描述"
            logger.error(f"{self.log_prefix} {error_msg}")
            await self.send_message_by_expressor(error_msg)
            return False, ""
        
        else:
            # 构建提示词
            prompt = f"""
如何编写MaiBot插件 
前言 
目前插件系统为v0.1版本，仅试行并实现简单功能，且只能在focus下使用
目前插件的形式为给focus模型的决策增加新动作action
原有focus的planner有reply和no_reply两种动作
在麦麦plugin文件夹中的示例插件新增了mute_action动作和pic_action动作，你可以参考其中的代码
在之后的更新中，会兼容normal_chat action，更多的自定义组件，tool，和/help式指令
基本步骤 
1. 在src/plugins/你的插件名/actions/目录下创建插件文件
2. 继承PluginAction基类
3. 实现process方法
4. 在src/plugins/你的插件名/__init__.py中导入你的插件类，确保插件能被正确加载

# src/plugins/你的插件名/__init__.py
from .actions.your_action import YourAction

__all__ = ["YourAction"]
插件结构示例 

from src.common.logger_manager import get_logger
from src.chat.focus_chat.planners.actions.plugin_action import PluginAction, register_action
from typing import Tuple

logger = get_logger("your_action_name")

@register_action
class YourAction(PluginAction):
    #你的动作描述
    action_name = "your_action_name"  # 动作名称，必须唯一
    action_description = "这个动作的详细描述，会展示给用户"
    action_parameters = {{
        "param1": "参数1的说明（可选）",
        "param2": "参数2的说明（可选）"
    }}
    action_require = [
        "使用场景1，顾名思义就是什么时候使用这个插件",
        "使用场景2"
    ]
    default = False  # 是否默认启用，True就是启用

    associated_types = ["command", "text"] #该插件会发送的消息类型，一般text即可

    async def process(self) -> Tuple[bool, str]:
        #插件核心逻辑
        # 你的代码逻辑...，一定要写，一定要发送消息
        return True, "执行结果"
可用的API方法 
插件可以使用PluginAction基类提供的以下API：
1. 直接发送消息 
#发送文本
await self.send_message(type="text", data="你好")
#发送图片
await self.send_message(type="image", data=base64_image_string)
#发送命令（需要adapter支持）
await self.send_message(
    type="command",
    data={{"name": "GROUP_BAN", "args": {{"qq_id": str(user_id), "duration": duration_str}}}},
    display_message=f"我禁言了 {{target}} {{duration_str}}秒",
)
会将消息直接以原始文本发送 type指定消息类型 data为发送内容
2. 使用表达器发送消息 
await self.send_message_by_expressor("你好")
await self.send_message_by_expressor(f"禁言{{target}} {{duration}}秒，因为{{reason}}")
将消息通过表达器发送，使用LLM组织成符合bot语言风格的内容并发送 只能发送文本
3. 获取聊天类型 
chat_type = self.get_chat_type()  # 返回 "group" 或 "private" 或 "unknown"
4. 获取最近消息 
messages = self.get_recent_messages(count=5)  # 获取最近5条消息
# 返回格式: [{{"sender": "发送者", "content": "内容", "timestamp": 时间戳}}, ...]
5. 获取动作参数 
param_value = self.action_data.get("param_name", "默认值")
6. 获取可用模型 
models = self.get_available_models()  # 返回所有可用的模型配置
# 返回格式: {{"model_name": {{"config": "value", ...}}, ...}}
7. 使用模型生成内容 
success, response, reasoning, model_name = await self.generate_with_model(
    prompt="你的提示词",
    model_config=models["model_name"],  # 从get_available_models获取的模型配置
    max_tokens=2000,  # 可选，最大生成token数
    request_type="plugin.generate",  # 可选，请求类型标识
    temperature=0.7,  # 可选，温度参数
    # 其他模型特定参数...
)
8. 获取用户ID 
platform, user_id = await self.get_user_id_by_person_name("用户名")
日志记录 
logger.info(f"{{self.log_prefix}} 你的日志信息")
logger.warning("警告信息")
logger.error("错误信息")
返回值说明 
process方法必须返回一个元组，包含两个元素：
* 第一个元素(bool): 表示动作是否执行成功
* 第二个元素(str): 执行结果的文本描述（可以为空""）

return True, "执行成功的消息"
# 或
return False, "执行失败的原因"
最佳实践 
1. 使用action_parameters清晰定义你的动作需要的参数
2. 使用action_require描述何时应该使用你的动作
3. 使用action_description准确描述你的动作功能
4. 使用logger记录重要信息，方便调试
5. 避免操作底层系统，尽量使用PluginAction提供的API
注册与加载 
插件会在系统启动时自动加载，只要放在正确的目录并添加了@register_action装饰器。
若设置default = True，插件会自动添加到默认动作集并启用，否则默认只加载不启用。

请根据以上规范，生成一个名为"{plugin_name}"的MaiBot插件，功能描述如下：
"{description}"

要求:
1. 继承PluginAction基类，实现process方法
2. 包含完整的错误处理和日志记录
3. 返回纯Python代码，无需解释
4. 一定要写完整的逻辑！！！

"""

        # 配置参数
        baseurl = "https://api.siliconflow.cn/v1"#用硅基流动不用改
        model = "deepseek-ai/DeepSeek-V3"
        basetoken = "sk-msxxxxxxxxxxxxxx  # 请替换为您的实际API token


        # 初始化客户端
        client = OpenAI(
            api_key=basetoken, 
            base_url=baseurl
        )
        # 定义请求参数
        model = model
        prompt = prompt

        try:
            # 发送非流式API请求
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda:client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False  # 关流式响应
                )
            )
            logger.info("已尝试生成插件")
            # 检查response类型（避免元组包装）
            if isinstance(response, tuple) and len(response) == 1:
                response = response[0]  # 解包元组
            # 提取内容（增加异常处理）
            if hasattr(response, 'choices') and response.choices:
                main_content = response.choices[0].message.content.strip()
                data = self._clean_code(main_content)
                logger.info(f"{self.log_prefix} 成功获取代码，长度: {len(data)}")
            else:
                raise ValueError("API响应格式错误，缺少choices属性")
    


    # 提取主要内容（content）
            for chunk in response:
                data=chunk.choices[0].delta.content
            logger.info(f"{{self.log_prefix}} {data}")
            logger.info("API请求成功，已获取主要内容")

        except Exception as e:
            logger.error(f"API请求失败: {str(e)}")
            logger.info(f"{{self.log_prefix}} 错误:{str(e)}")
        # 清理并发送代码
        cleaned_code = self._clean_code(data)
        await self.send_message_by_expressor(f"代码写好:{cleaned_code}")
        await self.send_message(type="text", data=cleaned_code)
        logger.info(f"{self.log_prefix} 插件正在生成")
        return True, ""



    
    def _clean_code(self, code: str) -> str:
        """清理生成的代码，移除Markdown标记"""
        code = code.strip()
        if code.startswith("```python") and code.endswith("```"):
            return code[9:-3].strip()
        if code.startswith("```") and code.endswith("```"):
            return code[3:-3].strip()
        return code