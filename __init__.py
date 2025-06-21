# src/plugins/makeplugin/__init__.py
from .actions.makeplugin import MakePlugin  # 从actions目录导入动作类

__all__ = ["MakePlugin"]  # 声明暴露的类（框架通过__all__识别插件动作）