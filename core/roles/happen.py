"""
Happen 角色实现
开发者 - 负责代码编写和实现
"""

import logging
from typing import Dict, List, Any

from .base_role import Role, RoleContext, RoleAction

logger = logging.getLogger(__name__)


class Happen(Role):
    """
    Happen - 开发者

    性格：专注、效率导向、注重代码质量
    技能：多语言编程、代码优化、问题排查
    工作模式：执行具体开发任务
    """

    def __init__(self, llm_provider, config: Dict[str, Any] = None):
        super().__init__("Happen", llm_provider, config)

        # Happen 特有的状态
        self.current_task = None
        self.supported_languages = ["python", "javascript", "java", "cpp", "go"]

    def _get_system_prompt(self) -> str:
        """获取 Happen 的系统提示"""
        return """# Happen - 开发者

## 你的角色
你是一个高效的开发者，名叫 Happen。你专注于编写高质量的代码和解决技术实现问题。

## 性格特点
- **专注**：专注于代码实现和问题解决
- **效率导向**：追求快速、准确的代码交付
- **质量意识**：注重代码的可读性、可维护性和性能
- **学习能力强**：能快速适应新的技术和工具

## 专业技能
1. **多语言编程**
   - Python, JavaScript, Java, C++, Go 等
   - 框架和库的应用
   - 最佳实践遵循

2. **代码质量保证**
   - 单元测试编写
   - 代码审查
   - 性能优化
   - 安全编码

3. **问题排查**
   - 调试技巧
   - 日志分析
   - 错误处理
   - 根因分析

## 工作原则
1. **实用第一**：优先考虑可工作、可维护的解决方案
2. **文档完善**：代码要有清晰的注释和文档
3. **测试驱动**：重要功能要有相应的测试覆盖
4. **持续改进**：定期review和优化现有代码

## 沟通风格
- 直接、清晰的技术沟通
- 提供具体的代码示例
- 解释技术决策的原因
- 主动提出改进建议"""

    def act(self, context: RoleContext) -> RoleAction:
        """Happen 的行为实现"""
        processed_input = self.preprocess_input(context.user_input)

        # 生成开发相关的响应
        response = self._generate_development_response(processed_input, context)
        actions = self._extract_actions(response)

        return RoleAction(
            response=response,
            actions=actions,
            metadata={"development_focus": True}
        )

    def get_capabilities(self) -> List[str]:
        """获取 Happen 的能力列表"""
        return [
            "多语言代码编写",
            "代码优化和重构",
            "单元测试编写",
            "调试和问题排查",
            "技术文档编写",
            "代码审查"
        ]

    def can_handle(self, user_input: str) -> bool:
        """判断是否能处理开发相关输入"""
        dev_keywords = ["代码", "编程", "实现", "开发", "debug", "测试", "优化"]
        return any(keyword in user_input.lower() for keyword in dev_keywords)

    def _generate_development_response(self, user_input: str, context: RoleContext) -> str:
        """生成开发相关的响应"""
        messages = [{"role": "user", "content": user_input}]
        response = self._call_llm(messages, temperature=0.3, max_tokens=1200)
        return response.content

    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """提取可能的动作"""
        actions = []
        if "测试" in response:
            actions.append({
                "type": "call_role",
                "role": "Peipei",
                "reason": "需要测试支持"
            })
        return actions
