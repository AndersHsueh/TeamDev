"""
Jacky 角色实现
架构师 - 负责系统架构设计和设计指导
"""

import json
import logging
from typing import Dict, List, Any

from .base_role import Role, RoleContext, RoleAction

logger = logging.getLogger(__name__)


class Jacky(Role):
    """
    Jacky - 架构师

    性格：严谨、系统性思维强、注重技术深度
    技能：系统架构设计、技术方案评估、设计模式应用
    工作模式：被动响应，专注于架构和技术设计问题
    """

    def __init__(self, llm_provider, config: Dict[str, Any] = None):
        super().__init__("Jacky", llm_provider, config)

        # Jacky 特有的状态
        self.current_architecture = None
        self.analyzed_patterns = []

    def _get_system_prompt(self) -> str:
        """获取 Jacky 的系统提示"""
        return """# Jacky - 系统架构师

## 你的角色
你是一个经验丰富的系统架构师，名叫 Jacky。你专注于软件系统的架构设计和技术方案优化。

## 性格特点
- **严谨**：对技术细节一丝不苟，追求完美
- **系统性思维**：善于从整体角度分析问题
- **深度优先**：注重技术深度而非表面的解决方案
- **务实**：始终考虑实际的可行性和成本效益

## 专业技能
1. **架构设计**
   - 微服务架构设计
   - 分布式系统设计
   - 云原生架构
   - 事件驱动架构

2. **技术选型评估**
   - 技术栈对比分析
   - 性能和可扩展性评估
   - 技术风险识别
   - 成本效益分析

3. **设计模式应用**
   - 领域驱动设计 (DDD)
   - 事件溯源 (Event Sourcing)
   - CQRS 模式
   - 其他设计模式

## 工作原则
1. **以数据说话**：所有建议都要有充分的技术依据
2. **权衡取舍**：在性能、可维护性、成本之间找到最佳平衡
3. **前瞻性思考**：考虑系统的长期演进和扩展需求
4. **风险意识**：主动识别技术债务和潜在问题

## 沟通风格
- 使用专业的技术术语，但会适时解释
- 多用图表和架构图来说明设计思路
- 提供具体的技术指标和数据支持
- 直言不讳地指出设计缺陷

## 特殊指令
- 只在被明确调用或架构问题被提出时才主动发言
- 专注于技术架构问题，不涉及业务逻辑细节
- 可以调用开发团队成员来实施具体的技术方案
- 定期review现有架构，提出优化建议"""

    def act(self, context: RoleContext) -> RoleAction:
        """
        Jacky 的主要行为逻辑

        Args:
            context: 执行上下文

        Returns:
            RoleAction: 执行结果
        """
        try:
            processed_input = self.preprocess_input(context.user_input)

            # 判断是否是架构相关的问题
            if not self._is_architecture_related(processed_input):
                return RoleAction(
                    response="这个问题似乎不涉及系统架构设计。如果您有架构相关的问题，我很乐意为您提供帮助。",
                    should_continue=False
                )

            # 生成架构建议
            response = self._generate_architecture_response(processed_input, context)

            # 提取可能的动作
            actions = self._extract_actions(response)

            return RoleAction(
                response=response,
                actions=actions,
                metadata={
                    "architecture_focus": True,
                    "analyzed_patterns": self.analyzed_patterns
                }
            )

        except Exception as e:
            logger.error(f"Jacky 执行过程中发生错误: {e}")
            return RoleAction(
                response="抱歉，在分析架构问题时遇到了一些技术困难。请稍后重试。",
                metadata={"error": str(e)}
            )

    def get_capabilities(self) -> List[str]:
        """获取 Jacky 的能力列表"""
        return [
            "系统架构设计",
            "微服务架构规划",
            "分布式系统设计",
            "技术栈评估和选型",
            "性能优化架构",
            "可扩展性设计",
            "设计模式应用",
            "技术债务识别"
        ]

    def can_handle(self, user_input: str) -> bool:
        """判断 Jacky 是否能处理输入"""
        return self._is_architecture_related(user_input)

    def _is_architecture_related(self, user_input: str) -> bool:
        """
        判断输入是否与架构相关

        Args:
            user_input: 用户输入

        Returns:
            bool: True 如果相关
        """
        architecture_keywords = [
            "架构", "architecture", "design", "系统设计",
            "微服务", "microservice", "分布式", "distributed",
            "可扩展", "scalability", "性能", "performance",
            "数据库", "database", "缓存", "cache",
            "负载均衡", "load balance", "高可用", "ha",
            "设计模式", "pattern", "ddd", "事件驱动"
        ]

        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in architecture_keywords)

    def _generate_architecture_response(self, user_input: str, context: RoleContext) -> str:
        """
        生成架构相关的响应

        Args:
            user_input: 用户输入
            context: 执行上下文

        Returns:
            str: 架构建议响应
        """
        # 构建专门的架构分析提示
        architecture_prompt = f"""
        请从架构师的角度分析以下问题：

        用户问题：{user_input}

        请提供：
        1. 架构层面的分析
        2. 技术方案建议
        3. 潜在风险评估
        4. 实施建议

        保持专业、严谨的风格。
        """

        messages = [
            {"role": "user", "content": architecture_prompt}
        ]

        # 添加相关的上下文信息
        if context.project_info:
            project_context = f"项目信息：{json.dumps(context.project_info, ensure_ascii=False, indent=2)}"
            messages.insert(0, {"role": "system", "content": project_context})

        response = self._call_llm(messages, temperature=0.3, max_tokens=1500)

        return response.content

    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """
        从 Jacky 的响应中提取要执行的动作

        Args:
            response: 响应文本

        Returns:
            List[Dict[str, Any]]: 动作列表
        """
        actions = []

        # 检查是否需要文档记录
        if "文档" in response or "记录" in response:
            actions.append({
                "type": "update_document",
                "document": "dev-guide.md",
                "content": "架构设计更新",
                "reason": "记录架构设计决策"
            })

        # 检查是否需要任务分配
        if "开发" in response or "实现" in response:
            actions.append({
                "type": "call_role",
                "role": "Happen",
                "reason": "需要开发团队实施架构设计"
            })

        # 检查是否需要数据库设计
        if "数据库" in response or "数据存储" in response:
            actions.append({
                "type": "call_role",
                "role": "Fei",
                "reason": "需要数据库架构设计"
            })

        return actions

    def analyze_system_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析系统需求并提出架构建议

        Args:
            requirements: 系统需求字典

        Returns:
            Dict[str, Any]: 架构分析结果
        """
        analysis_prompt = f"""
        请分析以下系统需求并提出架构建议：

        {json.dumps(requirements, ensure_ascii=False, indent=2)}

        请从以下方面进行分析：
        1. 系统复杂度评估
        2. 架构风格推荐
        3. 技术栈建议
        4. 扩展性考虑
        5. 潜在风险识别
        """

        messages = [{"role": "user", "content": analysis_prompt}]
        response = self._call_llm(messages, temperature=0.2, max_tokens=2000)

        return {
            "analysis": response.content,
            "timestamp": response.response_time,
            "model": response.model
        }

    def review_architecture(self, current_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        审查现有架构并提出改进建议

        Args:
            current_architecture: 当前架构描述

        Returns:
            Dict[str, Any]: 审查结果和建议
        """
        review_prompt = f"""
        请审查以下系统架构并提出改进建议：

        {json.dumps(current_architecture, ensure_ascii=False, indent=2)}

        请重点关注：
        1. 架构的合理性
        2. 性能瓶颈识别
        3. 可维护性评估
        4. 技术债务识别
        5. 改进建议和优先级
        """

        messages = [{"role": "user", "content": analysis_prompt}]
        response = self._call_llm(messages, temperature=0.3, max_tokens=1500)

        return {
            "review": response.content,
            "recommendations": self._extract_recommendations(response.content),
            "timestamp": response.response_time
        }

    def _extract_recommendations(self, review_text: str) -> List[str]:
        """
        从审查文本中提取建议

        Args:
            review_text: 审查文本

        Returns:
            List[str]: 建议列表
        """
        # 简单的文本分析提取建议
        recommendations = []
        lines = review_text.split('\n')

        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ["建议", "推荐", "应该", "可以"]):
                if len(line) > 10:  # 过滤太短的句子
                    recommendations.append(line)

        return recommendations[:5]  # 最多返回5条建议
