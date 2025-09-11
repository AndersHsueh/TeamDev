"""
Jim 角色实现
软件开发顾问 - 主要与用户交互的角色
"""

import re
import logging
from typing import Dict, List, Any

from .base_role import Role, RoleContext, RoleAction

logger = logging.getLogger(__name__)


class Jim(Role):
    """
    Jim - 软件开发顾问

    性格：耐心、善于引导、擅长把抽象需求拆解成可执行的任务
    技能：需求分析、系统设计、技术栈推荐、风险评估
    约束：禁止一次性生成完整 PRD，必须在对话中逐步补全
    """

    def __init__(self, llm_provider, config: Dict[str, Any] = None):
        super().__init__("Jim", llm_provider, config)

        # Jim 特有的状态
        self.current_project = None
        self.conversation_stage = "initial"  # initial, gathering, planning, executing

    def _get_system_prompt(self) -> str:
        """获取 Jim 的系统提示"""
        return """# Jim - 软件开发顾问

## 你的角色
你是一个经验丰富的软件开发顾问，名叫 Jim。你善于倾听用户的需求，引导他们将模糊的想法转化为清晰、可执行的项目计划。

## 性格特点
- **耐心**：愿意花时间了解用户的真实需求
- **善于引导**：通过提问帮助用户完善想法
- **专业**：在软件开发领域有深厚的知识储备
- **务实**：始终关注可行性和实际价值

## 工作原则
1. **逐步完善**：不要一次性生成完整的需求文档，要在对话中逐步完善
2. **确认理解**：经常确认自己对用户需求的理解是否正确
3. **提供选择**：为用户提供多种技术方案和实现路径
4. **风险提示**：主动识别潜在的技术风险和实施难点

## 技能专长
- 需求分析和功能规划
- 技术栈选择和架构设计
- 项目进度管理
- 风险评估和应对策略
- 用户体验设计指导

## 沟通风格
- 使用友好的、专业的语气
- 多用开放性问题引导用户思考
- 适当使用比喻和实例帮助理解
- 保持积极、建设性的态度

## 特殊指令
- 当用户提到具体的技术问题时，可以调用相关的工具或建议咨询其他角色
- 始终将用户需求放在首位，确保解决方案符合用户实际需要
- 适时总结对话要点，帮助用户理清思路"""

    def act(self, context: RoleContext) -> RoleAction:
        """
        Jim 的主要行为逻辑

        Args:
            context: 执行上下文

        Returns:
            RoleAction: 执行结果
        """
        try:
            # 预处理用户输入
            processed_input = self.preprocess_input(context.user_input)

            # 分析用户意图
            intent = self._analyze_intent(processed_input)

            # 根据意图和对话阶段生成响应
            response = self._generate_response(processed_input, intent, context)

            # 提取可能的动作
            actions = self._extract_actions(response)

            # 更新对话阶段
            self._update_conversation_stage(processed_input, intent)

            # 后处理响应
            final_response = self.postprocess_output(response)

            return RoleAction(
                response=final_response,
                actions=actions,
                metadata={
                    "intent": intent,
                    "stage": self.conversation_stage,
                    "project": self.current_project
                }
            )

        except Exception as e:
            logger.error(f"Jim 执行过程中发生错误: {e}")
            return RoleAction(
                response="抱歉，我在处理您的请求时遇到了一些问题。请稍后重试。",
                metadata={"error": str(e)}
            )

    def get_capabilities(self) -> List[str]:
        """获取 Jim 的能力列表"""
        return [
            "需求分析和功能规划",
            "技术栈选择和架构设计",
            "项目进度管理",
            "风险评估和应对策略",
            "用户体验设计指导",
            "多角色协作协调"
        ]

    def can_handle(self, user_input: str) -> bool:
        """判断 Jim 是否能处理输入"""
        # Jim 可以处理大部分软件开发相关的对话
        software_keywords = [
            "项目", "开发", "功能", "需求", "设计", "架构",
            "技术", "代码", "编程", "软件", "应用", "系统"
        ]

        return any(keyword in user_input.lower() for keyword in software_keywords)

    def _analyze_intent(self, user_input: str) -> str:
        """
        分析用户意图

        Args:
            user_input: 用户输入

        Returns:
            str: 意图分类
        """
        input_lower = user_input.lower()

        # 需求分析相关
        if any(word in input_lower for word in ["需求", "功能", "要做什么", "需要"]):
            return "requirements_analysis"

        # 技术选择相关
        elif any(word in input_lower for word in ["技术栈", "框架", "语言", "工具"]):
            return "technology_selection"

        # 项目管理相关
        elif any(word in input_lower for word in ["进度", "计划", "时间", "资源"]):
            return "project_management"

        # 架构设计相关
        elif any(word in input_lower for word in ["架构", "设计", "结构", "模块"]):
            return "architecture_design"

        # 风险评估相关
        elif any(word in input_lower for word in ["风险", "问题", "困难", "挑战"]):
            return "risk_assessment"

        # 一般咨询
        else:
            return "general_consultation"

    def _generate_response(self, user_input: str, intent: str, context: RoleContext) -> str:
        """
        根据意图生成响应

        Args:
            user_input: 用户输入
            intent: 分析出的意图
            context: 执行上下文

        Returns:
            str: 生成的响应
        """
        # 构建消息历史
        messages = context.conversation_history[-5:] if context.conversation_history else []

        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})

        # 根据意图调整提示
        intent_prompt = self._get_intent_specific_prompt(intent)

        # 调用 LLM 生成响应
        response = self._call_llm(messages, temperature=0.7, max_tokens=1000)

        return response.content

    def _get_intent_specific_prompt(self, intent: str) -> str:
        """
        获取意图特定的提示

        Args:
            intent: 用户意图

        Returns:
            str: 特定的提示文本
        """
        prompts = {
            "requirements_analysis": """
            用户似乎在讨论需求分析。请重点关注：
            - 引导用户详细描述功能需求
            - 询问用户场景和使用流程
            - 帮助识别核心功能和次要功能
            - 确认用户优先级和验收标准""",

            "technology_selection": """
            用户在咨询技术选型。请注意：
            - 询问项目规模和团队情况
            - 考虑技术成熟度和学习成本
            - 评估性能和可扩展性需求
            - 提供备选方案和对比分析""",

            "project_management": """
            用户关心项目管理。请聚焦：
            - 帮助制定合理的项目计划
            - 识别关键里程碑和交付物
            - 评估资源需求和时间安排
            - 建议风险 mitigation 策略""",

            "architecture_design": """
            用户在讨论架构设计。请重视：
            - 理解系统复杂度和发展需求
            - 推荐合适的设计模式和架构风格
            - 考虑可维护性和可扩展性
            - 评估技术债务和重构需求""",

            "risk_assessment": """
            用户关注风险评估。请集中：
            - 识别技术风险和业务风险
            - 评估风险概率和影响程度
            - 制定风险应对和监控策略
            - 建议预防措施和应急计划"""
        }

        return prompts.get(intent, "")

    def _update_conversation_stage(self, user_input: str, intent: str):
        """
        更新对话阶段

        Args:
            user_input: 用户输入
            intent: 用户意图
        """
        # 简单的状态机逻辑
        if self.conversation_stage == "initial":
            if intent in ["requirements_analysis", "technology_selection"]:
                self.conversation_stage = "gathering"
        elif self.conversation_stage == "gathering":
            if intent == "architecture_design":
                self.conversation_stage = "planning"
        elif self.conversation_stage == "planning":
            if "开始" in user_input or "实施" in user_input:
                self.conversation_stage = "executing"

    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """
        从 Jim 的响应中提取要执行的动作

        Args:
            response: 响应文本

        Returns:
            List[Dict[str, Any]]: 动作列表
        """
        actions = []

        # 检查是否需要调用其他角色
        if "架构师" in response or "架构设计" in response:
            actions.append({
                "type": "call_role",
                "role": "Jacky",
                "reason": "需要架构设计咨询"
            })

        if "数据库" in response or "数据存储" in response:
            actions.append({
                "type": "call_role",
                "role": "Fei",
                "reason": "需要数据库设计咨询"
            })

        if "开发" in response or "编码" in response:
            actions.append({
                "type": "call_role",
                "role": "Happen",
                "reason": "需要开发任务分配"
            })

        if "测试" in response or "质量" in response:
            actions.append({
                "type": "call_role",
                "role": "Peipei",
                "reason": "需要测试策略咨询"
            })

        return actions
