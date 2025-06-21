# makeplugin

#### 介绍
麦麦插件生成器


# 使用前**必读** ***！！！***
[麦麦开发文档](https://docs.mai-mai.org/develop/plugin_develop/plugin_examples)
## ***目前插件生成器最新稳定版本为0.4！***
>修改配置时使用硅基流动的用户只需修改167行的apikey（sk-xxxxxxxxx）为您的apikey（sk-开头）即可！
>>~~记得别把引号删了！~~
##### 插件生成器生成的插件并不包含__init__.py，所以请按照一下步骤手动创建
1. 在src/plugins/你的插件名/actions/目录下创建插件文件
2. 新建**插件名.py**文件
3. 在src/plugins/你的插件名/__init__.py中导入你的插件类
```python
# src/plugins/你的插件名/__init__.py
from .actions.your_action import YourAction#your_action是是你的插件文件，例如插件a.py，这里就是.actions.a

__all__ = ["YourAction"]#这一行是麦麦主程序显示的动作名称
```

