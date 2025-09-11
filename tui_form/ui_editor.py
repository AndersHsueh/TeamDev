import sys
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box


console = Console()

def load_form(json_path: str) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def render_panel(node: dict) -> Panel:
    """根据 JSON 节点生成 Rich Panel"""
    title = f"{node.get('id', '')} [{node.get('component', node.get('type'))}]"
    content = ""

    if "content" in node:
        content = node["content"]

    elif node.get("component") == "AgentList":
        agents = node.get("data", {}).get("agents", [])
        table = Table(show_header=True, header_style="bold cyan", expand=True)
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Role")
        table.add_column("Status")
        for a in agents:
            table.add_row(a["id"], a["name"], a["role"], a["status"])
        return Panel(table, title=title, expand=True)

    elif node.get("component") == "TaskList":
        tasks = node.get("data", {}).get("items", [])
        table = Table(show_header=True, header_style="bold green", expand=True)
        table.add_column("Step")
        table.add_column("Agent")
        table.add_column("Status")
        table.add_column("Title")
        for t in tasks:
            table.add_row(str(t["step"]), t["agent"], t["status"], t["title"])
        return Panel(table, title=title, expand=True)

    elif node.get("component") == "WorkArea":
        lines = node.get("data", {}).get("lines", [])
        content = "\n".join(lines)

    elif node.get("component") == "InputBox":
        prompt = node.get("data", {}).get("prompt", "> ")
        placeholder = node.get("data", {}).get("placeholder", "")
        content = f"{prompt}{placeholder}"

    elif node.get("component") == "StatusBar":
        content = node.get("data", {}).get("text", "")

    return Panel(content, title=title, expand=True, box=None)


def build_layout(node: dict) -> Layout:
    """递归解析 JSON，构建 Rich Layout"""
    if node["type"] in ("form", "split"):
        layout = Layout(name=node.get("id", "root"))

        if node["type"] == "form" and node.get("layout") == "vertical":
            layout.split(*(build_layout(child) for child in node["children"]))
        elif node["type"] == "form" and node.get("layout") == "horizontal":
            layout.split_row(*(build_layout(child) for child in node["children"]))
        elif node["type"] == "split":
            if node.get("direction") == "horizontal":
                layout.split_row(*(build_layout(child) for child in node["children"]))
            else:
                layout.split(*(build_layout(child) for child in node["children"]))

        return layout

    elif node["type"] == "panel":
        return Layout(render_panel(node), name=node.get("id", "panel"))

    else:
        return Layout(Panel(f"Unknown type: {node['type']}"), name="error")

def preview_form(json_path: str):
    form = load_form(json_path)
    layout = build_layout(form)
    console.print(layout)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python ui_editor.py gui_form/mainform.json")
        sys.exit(1)
    preview_form(sys.argv[1])

    