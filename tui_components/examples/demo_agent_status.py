"""
Agent 状态组件独立演示
展示单个组件的功能和用法
"""

import sys
import os
import time
import threading
from typing import Dict, Any

# 添加父目录到路径，以便导入组件
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base_component import BaseComponent
from core.theme import set_theme, Themes
from components.agent_status import AgentStatusComponent, AgentStatus


class AgentStatusDemo(BaseComponent):
    """Agent 状态演示应用程序"""
    
    def __init__(self):
        super().__init__("agent_status_demo")
        
        # 设置主题
        set_theme(Themes.get_dark_theme())
        
        # 创建多个 Agent 状态组件
        self.agents = []
        self._create_agents()
        
        # 设置布局
        self._setup_layout()
        
        # 启动状态变化模拟
        self._start_status_simulation()
    
    def _create_agents(self):
        """创建多个 Agent 状态组件"""
        # Agent 1: Claude
        claude = AgentStatusComponent("claude")
        claude.set_agent_info("Claude", "🤖")
        claude.set_status(AgentStatus.IDLE, "等待指令")
        claude.set_display_options(show_avatar=True, show_status_light=True, 
                                 show_name=True, show_message=True)
        self.agents.append(claude)
        
        # Agent 2: GPT
        gpt = AgentStatusComponent("gpt")
        gpt.set_agent_info("GPT-4", "🧠")
        gpt.set_status(AgentStatus.THINKING, "分析问题...")
        gpt.set_display_options(show_avatar=True, show_status_light=True, 
                              show_name=True, show_message=True)
        self.agents.append(gpt)
        
        # Agent 3: Gemini
        gemini = AgentStatusComponent("gemini")
        gemini.set_agent_info("Gemini", "💎")
        gemini.set_status(AgentStatus.WORKING, "生成代码...")
        gemini.set_display_options(show_avatar=True, show_status_light=True, 
                                 show_name=True, show_message=True)
        self.agents.append(gemini)
        
        # Agent 4: 离线 Agent
        offline_agent = AgentStatusComponent("offline_agent")
        offline_agent.set_agent_info("Offline Agent", "🔌")
        offline_agent.set_status(AgentStatus.OFFLINE, "连接断开")
        offline_agent.set_display_options(show_avatar=True, show_status_light=True, 
                                        show_name=True, show_message=True)
        self.agents.append(offline_agent)
        
        # Agent 5: 错误状态 Agent
        error_agent = AgentStatusComponent("error_agent")
        error_agent.set_agent_info("Error Agent", "⚠️")
        error_agent.set_status(AgentStatus.ERROR, "处理失败")
        error_agent.set_display_options(show_avatar=True, show_status_light=True, 
                                      show_name=True, show_message=True)
        self.agents.append(error_agent)
        
        # 添加所有 Agent 到容器
        for agent in self.agents:
            self.add_child(agent)
    
    def _setup_layout(self):
        """设置布局"""
        # 垂直排列所有 Agent
        for i, agent in enumerate(self.agents):
            agent.set_position(0, i * 2)  # 每个 Agent 占用 2 行
            agent.set_size(60, 2)
    
    def _start_status_simulation(self):
        """启动状态变化模拟"""
        def simulate_claude():
            while True:
                time.sleep(2)
                self.agents[0].set_status(AgentStatus.THINKING, "分析用户输入...")
                time.sleep(3)
                self.agents[0].set_status(AgentStatus.WORKING, "生成响应...")
                time.sleep(2)
                self.agents[0].set_status(AgentStatus.IDLE, "等待指令")
        
        def simulate_gpt():
            while True:
                time.sleep(3)
                self.agents[1].set_status(AgentStatus.WORKING, "处理请求...")
                time.sleep(2)
                self.agents[1].set_status(AgentStatus.THINKING, "优化输出...")
                time.sleep(2)
                self.agents[1].set_status(AgentStatus.IDLE, "准备就绪")
        
        def simulate_gemini():
            while True:
                time.sleep(4)
                self.agents[2].set_status(AgentStatus.THINKING, "理解上下文...")
                time.sleep(2)
                self.agents[2].set_status(AgentStatus.WORKING, "执行任务...")
                time.sleep(3)
                self.agents[2].set_status(AgentStatus.IDLE, "任务完成")
        
        # 启动模拟线程
        claude_thread = threading.Thread(target=simulate_claude, daemon=True)
        gpt_thread = threading.Thread(target=simulate_gpt, daemon=True)
        gemini_thread = threading.Thread(target=simulate_gemini, daemon=True)
        
        claude_thread.start()
        gpt_thread.start()
        gemini_thread.start()
    
    def render(self) -> str:
        """渲染演示界面"""
        if not self.visible:
            return ""
        
        lines = []
        
        # 标题
        title = "Agent 状态组件演示"
        lines.append(f"{'=' * len(title)}")
        lines.append(title)
        lines.append(f"{'=' * len(title)}")
        lines.append("")
        
        # 说明
        lines.append("这个演示展示了 Agent 状态组件的各种状态：")
        lines.append("")
        lines.append("• 🤖 Claude - 模拟 AI 助手的思考和工作过程")
        lines.append("• 🧠 GPT-4 - 展示不同的工作状态")
        lines.append("• 💎 Gemini - 演示状态转换")
        lines.append("• 🔌 Offline Agent - 离线状态")
        lines.append("• ⚠️ Error Agent - 错误状态")
        lines.append("")
        lines.append("状态说明：")
        lines.append("  ● 空闲 (灰色) - Agent 等待指令")
        lines.append("  ◐ 思考 (蓝色) - Agent 正在分析")
        lines.append("  ◑ 工作 (绿色) - Agent 正在执行任务")
        lines.append("  ✗ 错误 (红色) - Agent 遇到错误")
        lines.append("  ○ 离线 (灰色) - Agent 连接断开")
        lines.append("")
        lines.append("按 Ctrl+C 退出演示")
        lines.append("")
        lines.append("-" * 60)
        
        # 渲染所有 Agent
        for agent in self.agents:
            agent_lines = agent.render().split('\n')
            lines.extend(agent_lines)
            lines.append("")  # 添加空行分隔
        
        return '\n'.join(lines)
    
    def update(self, data: Any = None) -> None:
        """更新演示状态"""
        for agent in self.agents:
            agent.update(data)
    
    def handle_key(self, key: str) -> bool:
        """处理键盘输入"""
        # 处理退出
        if key == "ctrl+c":
            return True
        
        # 处理其他组件的键盘输入
        for agent in self.agents:
            if agent.handle_key(key):
                return True
        
        return False
    
    def handle_mouse(self, x: int, y: int, button: int) -> bool:
        """处理鼠标事件"""
        for agent in self.agents:
            if agent.handle_mouse(x, y, button):
                return True
        
        return False


def main():
    """主函数"""
    print("启动 Agent 状态组件演示...")
    print("=" * 50)
    
    # 创建演示应用程序
    demo = AgentStatusDemo()
    demo.set_size(80, 30)
    demo.set_visible(True)
    
    # 模拟主循环
    try:
        while True:
            # 清屏
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # 渲染演示
            print(demo.render())
            
            # 等待一段时间
            time.sleep(0.5)
            
            # 更新演示
            demo.update()
            
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示出错: {e}")
    finally:
        print("演示结束")


if __name__ == "__main__":
    main()
