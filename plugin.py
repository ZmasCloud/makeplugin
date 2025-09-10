from src.common.logger_manager import get_logger
from src.chat.focus_chat.planners.actions.plugin_action import BaseAction, ActionActivationType, ChatMode
from typing import Tuple, Dict, Any
import time
import asyncio
from openai import OpenAI
import requests

logger = get_logger("plugin_generator")

class PluginGenerator(BaseAction):
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
    activation_type = ActionActivationType.LLM_JUDGE
    mode_enable = ChatMode.ALL
    associated_types = ["text"]
    parallel_action = False
    llm_judge_prompt = (
        "判定是否需要使用插件生成器的条件：\n"
        "1. 用户明确要求生成MaiBot插件代码\n"
        "2. 用户需要根据功能描述创建新的插件\n"
        "3. 用户询问如何编写特定功能的插件\n"
        "请回答\"是\"或\"否\"。\n"
    )

    async def execute(self) -> Tuple[bool, str]:
        """生成插件代码并通过表达器发送"""
        start_time = time.time()
        
        # 验证必要参数
        plugin_name = self.action_data.get("plugin_name")
        description = self.action_data.get("description")
        if not plugin_name or not description:
            error_msg = "请提供插件名称和功能描述"
            logger.error(f"{self.log_prefix} {error_msg}")
            await self.send_text(error_msg)
            return False, ""
        
        # 构建提示词
        prompt = f"""
如何编写MaiBot插件 
前言 
目前插件系统为最新版本，基于Action组件系统实现
Action是给麦麦在回复之外提供额外功能的智能组件，由麦麦的决策系统自主选择是否使用

基本步骤 
1. 在src/plugins/你的插件名/actions/目录下创建插件文件
2. 继承BaseAction基类
3. 实现execute方法
4. 在src/plugins/你的插件名/__init__.py中导入你的插件类，确保插件能被正确加载

插件结构示例 
from src.common.logger_manager import get_logger
from src.chat.focus_chat.planners.actions.plugin_action import BaseAction, ActionActivationType, ChatMode
from typing import Tuple

logger = get_logger("your_action_name")

class YourAction(BaseAction):
    # 你的动作描述
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
    activation_type = ActionActivationType.ALWAYS  # 激活类型
    mode_enable = ChatMode.ALL  # 聊天模式
    associated_types = ["text", "emoji"]  # 该插件会发送的消息类型
    parallel_action = False  # 是否允许与其他Action并行执行

    async def execute(self) -> Tuple[bool, str]:
        # 插件核心逻辑
        # 你的代码逻辑...，一定要写，一定要发送消息
        return True, "执行结果"

可用的API方法 
插件可以使用BaseAction基类提供的以下API：
1. 直接发送消息 
#发送文本
await self.send_text("你好")
#发送表情
await self.send_emoji(base64_emoji_string)
#发送图片
await self.send_image(base64_image_string)
#发送命令（需要adapter支持）
await self.send_command(
    command_name="GROUP_BAN",
    args={{"qq_id": str(user_id), "duration": duration_str}},
)

2. 获取配置信息
config_value = self.get_config("config_key", "default_value")

3. 等待新消息
new_message, is_timeout = await self.wait_for_new_message(timeout=1200)

4. 获取动作参数 
param_value = self.action_data.get("param_name", "默认值")

5. 使用表达器发送消息（如果需要）
await self.send_custom("expressor", "你好", typing=False)

日志记录 
logger.info(f"{{self.log_prefix}} 你的日志信息")
logger.warning("警告信息")
logger.error("错误信息")

返回值说明 
execute方法必须返回一个元组，包含两个元素：
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
5. 避免操作底层系统，尽量使用BaseAction提供的API

请根据以上规范，生成一个名为"{plugin_name}"的MaiBot插件，功能描述如下：
"{description}"

要求:
1. 继承BaseAction基类，实现execute方法
2. 包含完整的错误处理和日志记录
3. 返回纯Python代码，无需解释
4. 一定要写完整的逻辑！！！
5. 必须符合最新的Action组件规范
6. 必须包含activation_type, mode_enable, associated_types等新属性
"""
    
        # 配置参数
        baseurl = "https://api.siliconflow.cn/v1"  # 用硅基流动不用改
        model = "deepseek-ai/DeepSeek-V3"
        basetoken = "sk-msxxxxxxxxxxxxxx"  # 请替换为您的实际API token

        # 初始化客户端
        client = OpenAI(
            api_key=basetoken, 
            base_url=baseurl
        )
        
        try:
            # 发送非流式API请求
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False  # 关流式响应
                )
            )
            logger.info("已尝试生成插件")
            
            # 提取内容
            if hasattr(response, 'choices') and response.choices:
                main_content = response.choices[0].message.content.strip()
                data = self._clean_code(main_content)
                logger.info(f"{self.log_prefix} 成功获取代码，长度: {len(data)}")
            else:
                raise ValueError("API响应格式错误，缺少choices属性")
            
            # 清理并发送代码
            cleaned_code = self._clean_code(data)
            await self.send_text(f"代码写好:\n{cleaned_code}")
            logger.info(f"{self.log_prefix} 插件正在生成")
            return True, "插件代码已生成并发送"
            
        except Exception as e:
            logger.error(f"API请求失败: {str(e)}")
            error_msg = f"生成插件时出现错误: {str(e)}"
            await self.send_text(error_msg)
            return False, error_msg

    def _clean_code(self, code: str) -> str:
        """清理生成的代码，移除Markdown标记"""
        code = code.strip()
        if code.startswith("```python") and code.endswith("```"):
            return code[10:-3].strip()  # 修正索引，从第10个字符开始
        if code.startswith("```") and code.endswith("```"):
            return code[3:-3].strip()
        return code
