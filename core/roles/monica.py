"""
Monica 角色实现
"""

import logging
from typing import List, Dict, Any, Optional

from ..llm_provider import LLMProvider, LLMResponse
from .base_role import Role, RoleContext, RoleAction

logger = logging.getLogger(__name__)


class Monica(Role):
    """
    Monica - 软件开发顾问

    负责与用户交互、需求分析和任务分配
    """

    def __init__(self, llm_provider: LLMProvider, config: Optional[Dict[str, Any]] = None):
        super().__init__("Monica", llm_provider, config)
        
        # Monica 特有的状态
        self.conversation_stage = "greeting"  # 对话阶段
        self.collected_requirements = []      # 收集到的需求点
        self.project_goals = []               # 项目目标
        self.technical_constraints = []       # 技术约束
        
    def _get_system_prompt(self) -> str:
        """获取 Monica 的系统提示"""
        return """# Monica - 软件开发顾问

你是一个经验丰富的软件开发顾问，名叫 Monica。你善于倾听用户的需求，引导他们将模糊的想法转化为清晰、可执行的项目计划。

## 你的核心能力包括：
1. 需求分析 - 帮助用户澄清和细化他们的想法
2. 技术栈选择 - 根据项目需求推荐合适的技术方案
3. 项目管理 - 制定合理的开发计划和里程碑
4. 任务分解 - 将复杂项目拆分成可管理的小任务
5. 风险评估 - 识别潜在的技术和项目风险

## 对话阶段指导：
- greeting: 友好地问候用户，询问他们的项目想法
- requirement_gathering: 深入了解用户的具体需求
- technical_analysis: 分析技术可行性和选择合适的技术栈
- planning: 制定项目计划和里程碑
- task_breakdown: 将项目分解为具体的任务
- confirmation: 确认最终的项目计划和任务分配

## 沟通风格：
- 专业但友好，避免过于技术化的术语
- 主动提问以澄清模糊的需求
- 提供具体的建议和选项，而不是模糊的指导
- 适时总结已收集的信息，确保理解正确

## 特殊指令：
- 当用户提到具体功能需求时，要询问使用场景和目标用户
- 当用户提到技术偏好时，要评估其适用性和潜在限制
- 当用户急于开始开发时，要提醒他们规划的重要性
"""

    def act(self, context: RoleContext) -> List[RoleAction]:
        """
        Monica 的主要行为逻辑
        
        Args:
            context: 角色上下文，包含用户输入、历史对话等信息
            
        Returns:
            List[RoleAction]: 要执行的动作列表
        """
        try:
            # 预处理输入
            processed_input = self._preprocess_input(context.user_input)
            
            # 分析用户意图
            intent = self._analyze_intent(processed_input, context.history)
            
            # 生成响应
            response = self._generate_response(intent, context)
            
            # 更新对话阶段
            self._update_conversation_stage(intent)
            
            # 提取要执行的动作
            actions = self._extract_actions(response, intent)
            
            return actions
            
        except Exception as e:
            logger.error(f"Monica 执行过程中发生错误: {e}")
            # 返回默认的错误处理动作
            return [RoleAction(
                action_type="response",
                content="抱歉，我在处理您的请求时遇到了一些问题。请稍后再试或重新表述您的需求。"
            )]

    def get_capabilities(self) -> List[str]:
        """获取 Monica 的能力列表"""
        return [
            "需求分析和澄清",
            "技术栈推荐",
            "项目规划和里程碑设定",
            "任务分解和分配",
            "风险评估和规避建议",
            "开发流程指导"
        ]

    def can_handle(self, context: RoleContext) -> bool:
        """判断 Monica 是否能处理输入"""
        # Monica 可以处理大部分软件开发相关的对话
        user_input = context.user_input.lower()
        software_keywords = [
            "项目", "需求", "开发", "应用", "网站", "软件", "功能",
            "技术", "架构", "设计", "实现", "编码", "测试", "部署"
        ]
        
        return any(keyword in user_input for keyword in software_keywords)

    def _preprocess_input(self, user_input: str) -> str:
        """预处理用户输入"""
        # 移除多余的空白字符
        return user_input.strip()

    def _analyze_intent(self, user_input: str, history: List[Dict[str, Any]]) -> str:
        """分析用户意图"""
        # 基于关键词的简单意图识别
        if self.conversation_stage == "greeting":
            return "greeting"
            
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["需求", "想法", "想要", "需要"]):
            return "requirement_gathering"
        elif any(word in user_input_lower for word in ["技术", "架构", "框架", "语言"]):
            return "technical_analysis"
        elif any(word in user_input_lower for word in ["计划", "时间", "进度", "安排"]):
            return "planning"
        elif any(word in user_input_lower for word in ["任务", "分解", "步骤", "怎么做"]):
            return "task_breakdown"
        elif any(word in user_input_lower for word in ["确认", "同意", "好的", "可以"]):
            return "confirmation"
        else:
            # 默认返回当前阶段
            return self.conversation_stage

    def _generate_response(self, intent: str, context: RoleContext) -> str:
        """根据意图生成响应"""
        llm_response: LLMResponse = self.llm_provider.chat_completion(
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"用户输入: {context.user_input}\n当前对话阶段: {self.conversation_stage}\n识别意图: {intent}"}
            ],
            temperature=0.7
        )
        return llm_response.content

    def _get_intent_specific_prompt(self, intent: str) -> str:
        """获取意图特定的提示"""
        prompts = {
            "greeting": "请友好地问候用户，询问他们有什么项目想法或需求。",
            "requirement_gathering": "请深入了解用户的具体需求，询问使用场景、目标用户、核心功能等。",
            "technical_analysis": "请分析技术可行性，推荐合适的技术栈，并说明选择理由。",
            "planning": "请制定合理的项目计划，包括里程碑和时间安排。",
            "task_breakdown": "请将项目分解为具体的任务，并给出优先级建议。",
            "confirmation": "请总结项目计划和任务分配，确认用户是否同意。"
        }
        return prompts.get(intent, "请根据当前对话阶段提供适当的响应。")

    def _update_conversation_stage(self, intent: str):
        """更新对话阶段"""
        # 简单的状态机逻辑
        if self.conversation_stage == "greeting" and intent != "greeting":
            self.conversation_stage = "requirement_gathering"
        elif self.conversation_stage == "requirement_gathering" and intent == "technical_analysis":
            self.conversation_stage = "technical_analysis"
        elif self.conversation_stage == "technical_analysis" and intent == "planning":
            self.conversation_stage = "planning"
        elif self.conversation_stage == "planning" and intent == "task_breakdown":
            self.conversation_stage = "task_breakdown"
        elif self.conversation_stage == "task_breakdown" and intent == "confirmation":
            self.conversation_stage = "confirmation"

    def _extract_actions(self, response: str, intent: str) -> List[RoleAction]:
        """从 Monica 的响应中提取要执行的动作"""
        actions = []
        
        # 添加响应动作
        actions.append(RoleAction(
            action_type="response",
            content=response
        ))
        
        # 根据意图添加其他动作
        if intent == "task_breakdown":
            actions.append(RoleAction(
                action_type="create_task_list",
                content="根据项目需求生成任务列表"
            ))
        elif intent == "planning":
            actions.append(RoleAction(
                action_type="create_timeline",
                content="制定项目时间线"
            ))
            
        return actions
