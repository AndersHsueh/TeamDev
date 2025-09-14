# TUI界面开发指南

## 界面组件规范

### 1. AgentList组件

用于显示所有Agent的信息和状态。

```json
{
  "id": "agent_list",
  "type": "list",
  "position": {
    "x": 0,
    "y": 5
  },
  "size": {
    "width": 20,
    "height": 15
  },
  "props": {
    "title": "Agents",
    "items": [
      {
        "id": "monica",
        "name": "Monica",
        "role": "需求分析员/产品经理"
      },
      {
        "id": "jacky",
        "name": "Jacky",
        "role": "架构师"
      },
      {
        "id": "happen",
        "name": "Happen",
        "role": "全栈工程师"
      },
      {
        "id": "fei",
        "name": "Fei",
        "role": "数据库专家"
      },
      {
        "id": "peipei",
        "name": "Peipei",
        "role": "测试工程师"
      }
    ]
  }
}
```

### 2. WorkArea组件

用于显示工作区内容，包括系统消息和Agent的活动状态。

```json
{
  "id": "work_area",
  "type": "text",
  "position": {
    "x": 20,
    "y": 5
  },
  "size": {
    "width": 70,
    "height": 30
  },
  "props": {
    "title": "工作区",
    "content": "[System] 欢迎使用TeamDev平台\n\n[Agent Monica] Started analysis...\n\n[Agent Jacky] Awaiting requirements...\n\n[Agent Happen] Awaiting architecture design...\n\n[Agent Fei] Awaiting database design...\n\n[Agent Peipei] Awaiting test plan...",
    "wrap": true
  }
}
```

### 3. TaskList组件

用于显示任务列表和分配情况。

```json
{
  "id": "task_list",
  "type": "list",
  "position": {
    "x": 90,
    "y": 5
  },
  "size": {
    "width": 30,
    "height": 30
  },
  "props": {
    "title": "Tasks",
    "items": [
      {
        "id": "task1",
        "name": "Draft PRD",
        "status": "in-progress",
        "assignee": "monica"
      },
      {
        "id": "task2",
        "name": "System Design",
        "status": "pending",
        "assignee": "jacky"
      },
      {
        "id": "task3",
        "name": "Database Design",
        "status": "pending",
        "assignee": "fei"
      },
      {
        "id": "task4",
        "name": "API Development",
        "status": "pending",
        "assignee": "happen"
      },
      {
        "id": "task5",
        "name": "Frontend Development",
        "status": "pending",
        "assignee": "happen"
      },
      {
        "id": "task6",
        "name": "Unit Testing",
        "status": "pending",
        "assignee": "peipei"
      },
      {
        "id": "task7",
        "name": "Integration Testing",
        "status": "pending",
        "assignee": "peipei"
      }
    ]
  }
}
```

## 界面布局说明

主界面采用三栏布局：
1. 左侧：Agent列表 (20列)
2. 中间：工作区 (70列)
3. 右侧：任务列表 (30列)

底部包含状态栏和命令输入框。

## 交互设计

- 用户可以通过命令输入框与系统交互
- 点击Agent可以查看详细信息
- 点击任务可以查看任务详情和进度
- 系统会实时更新Agent状态和工作区内容
