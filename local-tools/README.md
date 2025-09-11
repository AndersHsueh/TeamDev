# Local Tools - 本地工具接口

这是一个完整的本地工具接口实现，提供文件操作、命令执行、HTTP 请求等功能。所有工具都遵循统一的安全和权限控制规范。

## 目录结构

```
local-tools/
├── tools/                 # 工具实现
│   ├── file_read.py      # 文件读取工具
│   ├── file_write.py     # 文件写入工具
│   ├── file_delete.py    # 文件删除工具
│   ├── list_directory.py # 目录列举工具
│   ├── execute_command.py # 命令执行工具
│   ├── http_request.py   # HTTP 请求工具
│   └── __init__.py
├── permissions/          # 权限管理
│   └── permission_manager.py
├── tests/               # 单元测试
│   ├── test_file_read.py
│   ├── test_file_write.py
│   ├── test_file_delete.py
│   ├── test_list_directory.py
│   ├── test_execute_command.py
│   ├── test_http_request.py
│   └── test_tool_runner.py
└── tool_runner.py       # 统一调度器
```

## 快速开始

```python
from local_tools.tool_runner import get_tool_runner

# 获取工具调度器
runner = get_tool_runner()

# 示例：读取文件
request = {
    "tool": "FileRead",
    "args": {
        "path": "/path/to/file.txt",
        "user_id": "admin"
    }
}

result = runner.run_tool(request)
if result["success"]:
    print("文件内容:", result["output"]["content"])
else:
    print("错误:", result["error"]["message"])
```

## 工具列表

### 1. FileRead - 文件读取

**权限要求**: `read:file`

**输入参数**:
```json
{
  "path": "string",        // 必需：文件路径
  "encoding": "string?",   // 可选：文件编码，默认为 "utf-8"
  "user_id": "string"      // 必需：用户ID
}
```

**成功输出**:
```json
{
  "success": true,
  "output": {
    "content": "文件内容字符串"
  }
}
```

**示例**:
```python
result = runner.run_tool({
    "tool": "FileRead",
    "args": {
        "path": "/tmp/example.txt",
        "user_id": "admin"
    }
})
```

### 2. FileWrite - 文件写入

**权限要求**: `write:file`

**输入参数**:
```json
{
  "path": "string",           // 必需：文件路径
  "content": "string",        // 必需：要写入的内容
  "encoding": "string?",      // 可选：文件编码，默认为 "utf-8"
  "overwrite": "boolean?",    // 可选：是否覆盖现有文件，默认为 false
  "user_id": "string"         // 必需：用户ID
}
```

**成功输出**:
```json
{
  "success": true,
  "output": {
    "path": "写入的文件路径"
  }
}
```

### 3. FileDelete - 文件删除

**权限要求**: `delete:file`

**输入参数**:
```json
{
  "path": "string",        // 必需：文件或目录路径
  "recursive": "boolean?", // 可选：是否递归删除目录，默认为 false
  "user_id": "string"      // 必需：用户ID
}
```

**成功输出**:
```json
{
  "success": true,
  "output": {
    "path": "删除的路径"
  }
}
```

### 4. ListDirectory - 目录列举

**权限要求**: `read:file`

**输入参数**:
```json
{
  "path": "string",           // 必需：目录路径
  "include_hidden": "boolean?", // 可选：是否包含隐藏文件，默认为 false
  "user_id": "string"         // 必需：用户ID
}
```

**成功输出**:
```json
{
  "success": true,
  "output": {
    "entries": [
      {
        "name": "文件名",
        "type": "file|directory",
        "size": 1024,
        "last_modified": "2024-01-01T12:00:00"
      }
    ]
  }
}
```

### 5. ExecuteCommand - 命令执行

**权限要求**: `execute:command`

**输入参数**:
```json
{
  "cmd": "string",         // 必需：要执行的命令
  "cwd": "string?",        // 可选：当前工作目录
  "timeout": "number?",    // 可选：超时时间（秒），默认为 60
  "env": "object?",        // 可选：环境变量
  "user_id": "string"      // 必需：用户ID
}
```

**成功输出**:
```json
{
  "success": true,
  "output": {
    "stdout": "标准输出",
    "stderr": "标准错误",
    "exit_code": 0
  }
}
```

### 6. HttpRequest - HTTP 请求

**权限要求**: `network:outbound`

**输入参数**:
```json
{
  "url": "string",         // 必需：请求 URL
  "method": "string?",     // 可选：HTTP 方法，默认为 "GET"
  "headers": "object?",    // 可选：请求头
  "body": "string|object?", // 可选：请求体
  "timeout": "number?",    // 可选：超时时间（秒），默认为 30
  "user_id": "string"      // 必需：用户ID
}
```

**成功输出**:
```json
{
  "success": true,
  "output": {
    "status_code": 200,
    "headers": {"content-type": "application/json"},
    "body": {"message": "success"}
  }
}
```

## 权限管理

### 权限类型

- `read:file` - 读取文件权限
- `write:file` - 写入文件权限
- `delete:file` - 删除文件权限
- `execute:command` - 执行命令权限
- `network:outbound` - 网络访问权限

### 默认用户权限

系统预定义了几个默认用户角色：

- `admin` - 拥有所有权限
- `user` - 拥有文件读写和命令执行权限
- `readonly` - 仅拥有文件读取权限

### 权限检查示例

```python
from local_tools.permissions.permission_manager import get_permission_manager

pm = get_permission_manager()

# 为用户添加权限
pm.add_user_permission("user123", "read:file")

# 检查用户权限
has_permission = pm.check_permission("user123", "read:file")  # True
```

## 错误码列表

| 错误码 | 含义 |
|--------|------|
| `PERMISSION_DENIED` | 用户没有相应权限 |
| `NOT_FOUND` | 文件或目录不存在 |
| `INVALID_INPUT` | 输入参数无效或格式错误 |
| `ALREADY_EXISTS` | 文件已存在（当 overwrite=false 时） |
| `TIMEOUT` | 操作超时 |
| `EXECUTION_ERROR` | 命令执行失败 |
| `NETWORK_ERROR` | 网络请求失败 |
| `IO_ERROR` | 文件读写错误 |

## 安全特性

1. **路径安全检查**: 防止访问系统受保护目录（如 `/etc`, `/usr/bin` 等）
2. **命令过滤**: 过滤危险命令和特殊字符
3. **网络安全**: 防止访问本地地址和内网
4. **超时控制**: 防止长时间运行的操作
5. **权限验证**: 每个操作都需要相应权限

## 运行测试

```bash
cd local-tools
python -m pytest tests/
# 或者
python -m unittest discover tests/
```

## 依赖要求

- Python >= 3.8
- requests (可选，用于 HTTP 请求，如果不可用会使用 urllib 后备方案)

## 日志记录

所有工具调用都会被记录，包括：
- 调用时间
- 用户ID
- 工具名称
- 执行结果
- 性能指标

```python
# 查看调用历史
history = runner.get_call_history(user_id="admin", limit=10)
```

## 扩展工具

要添加新工具，请遵循以下步骤：

1. 在 `tools/` 目录下创建新工具文件
2. 实现 `run(args: dict) -> dict` 函数
3. 在 `tools/__init__.py` 中添加导入
4. 在 `tool_runner.py` 中注册工具
5. 编写相应的单元测试

新工具必须遵循统一的输入输出格式和错误处理规范。
