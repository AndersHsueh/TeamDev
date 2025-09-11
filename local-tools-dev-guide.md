

# 开发指导 Dev Guide for local-tools

以下是一个完整的开发指导，目的是在项目中的 `./local-tools` 目录下，实现一组工具接口（Tools），包括文件操作、执行命令、HTTP 请求等。请 grok-code-fast-1 按照这个规范来生成代码、测试、权限控制和文档。

---

## 一、目录结构建议
project-root/
├── local-tools/
│   ├── tools/
│   │   ├── file_read.py
│   │   ├── file_write.py
│   │   ├── file_delete.py
│   │   ├── list_directory.py
│   │   ├── execute_command.py
│   │   ├── http_request.py
│   │   └── init.py
│   ├── permissions/
│   │   └── permission_manager.py
│   ├── tests/
│   │   ├── test_file_read.py
│   │   ├── test_file_write.py
│   │   └── test_http_request.py
│   └── tool_runner.py
├── README.md
└── other project files…

- `local-tools/tools/` 存放各个工具实现。
- `local-tools/permissions/permission_manager.py` 用来做权限检查。
- `local-tools/tests/` 放单元测试。
- `local-tools/tool_runner.py` 是统一入口／工具调度器，Agent 或外层系统通过这个调用各个工具。

---

## 二、工具接口规范

每个工具模块（如 `file_read.py`）必须实现如下：

- 一个 main 函数／类方法，标准签名，例如：

  ```python
  def run( args: dict ) -> dict:
      """
      接收一个 args 字典，返回一个 dict，其中包含：
      - 成功时 output 键
      - 失败时 error 键（带 error_code, message）
      """

	•	输入参数约定：
	•	参数类型要明确（string, int, bool, dict 等）
	•	必要参数 vs 可选参数要标注
	•	对路径参数要限定，例如不能越出某个 base path；执行命令要限制 command 内容。
	•	输出格式约定：
成功返回例子：
{
  "success": true,
  "output": { /* 工具具体的返回内容 */ }
}
失败返回例子：
{
  "success": false,
  "error": {
    "error_code": "SOME_ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* 可选，内部详情，不敏感 */ }
  }
}

三、权限与安全控制
	•	定义权限类型，例如：
        read:file
        write:file
        delete:file
        execute:command
        network:outbound
	•	permission_manager.py 提供函数：
def check_permission( user_id: str, permission: str ) -> bool:
    """
    返回 True 如果 user_id 有该权限，否则 False
    """
	•	在每个工具 run 里要先调用权限检查（可以通过传入 context，比如 user_id），如果权限不够，立即返回错误 PERMISSION_DENIED。
	•	对敏感操作做额外限制，例如：
	•	文件路径不能指向系统关键目录（例如 /etc, /usr/bin 等／windows 的系统目录）
	•	执行命令不能带某些危险标志或者需要白名单

四、具体工具合同（Tool Contract）定义

下面是每个工具的输入／输出约定草案。
FileRead
	•	输入 args 字段：

        {
        "path": string,        // 必填，文件路径
        "encoding": string?,    // 可选，默认为 "utf-8"
        "user_id": string       // 必填，用于权限检查
        }
	•	行为：
	•	权限需包含 read:file
	•	如果文件不存在，返回错误 NOT_FOUND
	•	如果路径越界或权限不足，返回 PERMISSION_DENIED 或 INVALID_INPUT
	•	读文件内容，以指定 encoding 解码

    •	输出：
        {
        "success": true,
        "output": {
            "content": "文件内容字符串"
        }
        }
        或者失败：
        {
        "success": false,
        "error": {
            "error_code": "NOT_FOUND",
            "message": "...",
            "details": { /* 可选 */ }
        }
        }

FileWrite
	•	输入：
        {
        "path": string,
        "content": string,
        "encoding": string?,        // 可选，默认为 utf-8
        "overwrite": bool?,         // 可选，默认 false，如果 false 且文件已存在则报错
        "user_id": string
        }
	•	行为：
	•	权限需包含 write:file
	•	检查路径安全／越界
	•	如果 overwrite=false 且文件存在，则返回错误 ALREADY_EXISTS
	•	写入内容；若目录不存在，可能先创建目录或返回错误（视策略）
	•	输出类似 FileRead：
    成功：
        {
        "success": true,
        "output": { "path": "所写文件的路径" }
        }
    失败：
        {
        "success": false,
        "error": { "error_code": "...", "message": "..." }
        }

FileDelete
	•	输入：
        {
        "path": string,
        "recursive": bool?,   // 可选，默认 false
        "user_id": string
        }
	•	行为：
	•	权限 delete:file
	•	如果路径不存在 -> NOT_FOUND
	•	如果不是目录但 recursive=true，不报错，只删除文件
	•	如果是目录且 recursive=false，与策略决定是报错还是只删除空目录
	•	安全检查路径
	•	输出同样 success/error struct

ListDirectory
	•	输入：
    {
    "path": string,
    "include_hidden": bool?,  // 可选，默认 false
    "user_id": string
    }
	•	行为：
	•	权限 read:file
	•	安全路径检查
	•	罗列目录内容，返回名字 + 类型 + 大小 + last_modified 时间等
	•	输出：
    {
    "success": true,
    "output": {
        "entries": [
        { "name": "...", "type": "file"|"directory", "size": int, "last_modified": string }
        // ...
        ]
    }
    }
    ExecuteCommand
	•	输入：
    {
  "cmd": string,
  "cwd": string?,    // 可选，用作当前目录
  "timeout": number?, // 秒，默认如 60
  "env": dict?,     // 可选，环境变量覆盖／扩展
  "user_id": string
}
	•	行为：
	•	权限 execute:command
	•	检查 cmd 是否在白名单或不包含危险字符／语句
	•	cwd 必须在允许目录范围内
	•	超时控制
	•	捕获 stdout, stderr, exit code
	•	输出：
    {
  "success": true,
  "output": {
    "stdout": "…",
    "stderr": "…",
    "exit_code": 0
  }
}
HTTPRequest
	•	输入：
{
  "url": string,
  "method": string?,   // GET/POST/PUT/DELETE/PATCH, 默认 GET
  "headers": dict?,    // 可选
  "body": string|dict?,// 可选
  "timeout": number?,  // 秒，默认比如 30
  "user_id": string
}
	•	行为：
	•	权限 network:outbound
	•	验证 URL（协议 http 或 https；防止访问本地文件 system 或内网私有网络，如果这是政策限制的话）
	•	执行 HTTP 请求
	•	捕获状态码、响应头、body；如果 body 可解析为 JSON，可返回 JSON 否则原文字符串
	•	输出：
{
  "success": true,
  "output": {
    "status_code": int,
    "headers": { … },
    "body": string|object
  }
}

五、统一调度器 /入口 tool_runner.py
	•	接收调用 request，比如：
{
  "tool": "FileRead",     // 工具名
  "args": { … },          // 上面的输入参数结构
}
	•	执行权限检查 + 安全检查 + 命令校验等
	•	调用相应的工具模块的 run 方法
	•	捕获异常，封装为标准输出结构（success / error）
	•	日志调用记录：时间、caller/user_id、tool 名称、输入 args（脱敏敏感部分）、输出或错误码

六、测试
	•	每个工具写单元测试，覆盖以下情况：
	1.	正常路径（正确输入 + 权限足够）
	2.	缺少权限情况 → 应该返回 PERMISSION_DENIED
	3.	输入非法情况（path 越界、URL 格式错、cmd 空或者包含危险字符等）→ INVALID_INPUT
	4.	文件不存在 /目录不存在 → NOT_FOUND
	5.	超时情况（对 ExecuteCommand 和 HTTPRequest 测试 timeout）
	6.	特殊边界情况（空文件、空目录、隐藏文件、large file etc）
	•	可以使用 pytest 或你们现有的测试框架。

⸻

七、文档与示例
	•	在 local-tools/README.md 中写明如何使用这些工具，包括每个工具的接口输入／输出示例、权限要求、错误码列表。
	•	在每个工具的模块文件头部，用 docstring 注明功能、输入参数、返回格式、可能的错误码。

⸻

八、提示给 grok 的生成指令建议

在提示中明确以下内容：
	•	需要用 Python（或你们偏好的语言）来实现
	•	所有模块在 ./local-tools 目录下
	•	接口规范如上
	•	安全和权限检查是必需的
	•	写测试文件
	•	写文档示例（docstring + README）
	•	保持代码风格一致（例如遵守 PEP8 或者你团队已有风格）

⸻

九、示例错误码清单

下面是一些预定义／建议的错误码：
错误码  含义
PERMISSION_DENIED   权限不够
NOT_FOUND   文件／目录／命令目标不存在
INVALID_INPUT   输入参数无效 / 格式不正确 / 越界等
ALREADY_EXISTS  文件已存在但 overwrite=false
TIMEOUT 操作超时
EXECUTION_ERROR cmd 执行失败 / stderr 有内容 /非零退出码（视策略）
NETWORK_ERROR   HTTP 请求失败／连接问题／响应不可达
IO_ERROR    文件读写问题（权限／磁盘满等）

十、代码风格与依赖
	•	Python 版本建议：>=3.8
	•	使用标准库优先，如果需第三方库（如 requests），需在项目中声明依赖（例如 requirements.txt 或 pyproject.toml）
	•	日志使用标准库 logging
	•	异常要被捕获，不要让未捕获异常传播到调用者

