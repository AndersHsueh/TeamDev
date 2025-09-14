"""
TeamDev 日志系统模块

提供按小时轮转的日志功能，支持多级别日志记录
格式: log-YYYY-MM-DD-HH.log

功能特性:
- 按小时自动轮转日志文件
- 支持多个日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 自动创建日志目录
- 统一的日志格式
- 性能优化的日志处理

使用方式:
    from core.logging_system import setup_logging, get_logger
    
    # 系统启动时初始化日志
    setup_logging()
    
    # 在各模块中使用
    logger = get_logger(__name__)
    logger.info("这是一条信息日志")
    logger.error("这是一条错误日志")
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class HourlyRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    按小时轮转的文件处理器
    
    生成格式为 log-YYYY-MM-DD-HH.log 的日志文件
    """
    
    def __init__(self, logs_dir: str):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        
        # 生成当前小时的日志文件名
        current_time = datetime.now()
        filename = self._get_log_filename(current_time)
        filepath = self.logs_dir / filename
        
        # 初始化父类，设置按小时轮转
        super().__init__(
            filename=str(filepath),
            when='H',  # 按小时轮转
            interval=1,  # 每1小时轮转一次
            backupCount=24 * 7,  # 保留7天的日志
            encoding='utf-8'
        )
        
        # 设置文件名生成器
        self.namer = self._generate_filename
    
    def _get_log_filename(self, dt: datetime) -> str:
        """生成日志文件名"""
        return f"log-{dt.strftime('%Y-%m-%d-%H')}.log"
    
    def _generate_filename(self, default_name: str) -> str:
        """
        自定义文件名生成器
        
        TimedRotatingFileHandler 会调用这个方法来生成轮转后的文件名
        """
        # 从默认名称中提取时间信息
        # 默认名称格式类似: /path/to/log-2025-09-15-14.log.2025-09-15_15-00-00
        base_name = default_name.split('.')[0]  # 去掉时间戳后缀
        
        # 如果已经是我们想要的格式，直接返回
        if base_name.endswith('.log'):
            return default_name
        
        # 否则生成新的文件名
        current_time = datetime.now()
        filename = self._get_log_filename(current_time)
        return str(self.logs_dir / filename)


class TeamDevFormatter(logging.Formatter):
    """
    TeamDev 专用日志格式化器
    """
    
    def __init__(self):
        # 定义日志格式
        fmt = '[%(asctime)s] %(levelname)-8s %(name)-20s %(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'
        super().__init__(fmt=fmt, datefmt=datefmt)
    
    def format(self, record):
        """格式化日志记录"""
        # 添加额外的上下文信息
        if hasattr(record, 'module_name'):
            record.name = getattr(record, 'module_name')
        
        return super().format(record)


class LoggingSystem:
    """
    TeamDev 日志系统管理器
    """
    
    def __init__(self):
        self.logs_dir = Path('./logs')
        self.is_initialized = False
        self._loggers = {}
    
    def setup(self, 
              level: str = 'INFO',
              console_output: bool = False,
              logs_dir: Optional[str] = None) -> None:
        """
        初始化日志系统
        
        Args:
            level: 日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            console_output: 是否同时输出到控制台
            logs_dir: 日志文件目录，默认为 './logs'
        """
        if self.is_initialized:
            return
        
        if logs_dir:
            self.logs_dir = Path(logs_dir)
        
        # 确保日志目录存在
        self.logs_dir.mkdir(exist_ok=True)
        
        # 设置日志级别
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        
        # 创建根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        
        # 清除现有的处理器
        root_logger.handlers.clear()
        
        # 创建文件处理器 (按小时轮转)
        file_handler = HourlyRotatingFileHandler(str(self.logs_dir))
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(TeamDevFormatter())
        root_logger.addHandler(file_handler)
        
        # 可选的控制台处理器
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(TeamDevFormatter())
            root_logger.addHandler(console_handler)
        
        self.is_initialized = True
        
        # 记录初始化信息
        logger = logging.getLogger(__name__)
        logger.info(f"TeamDev 日志系统初始化完成")
        logger.info(f"日志目录: {self.logs_dir.absolute()}")
        logger.info(f"日志级别: {level}")
        logger.info(f"控制台输出: {console_output}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取命名日志器
        
        Args:
            name: 日志器名称，通常使用 __name__
            
        Returns:
            logging.Logger: 配置好的日志器
        """
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def cleanup_old_logs(self, days_to_keep: int = 7):
        """
        清理旧的日志文件
        
        Args:
            days_to_keep: 保留多少天的日志
        """
        if not self.logs_dir.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        
        cleaned_count = 0
        for log_file in self.logs_dir.glob('log-*.log'):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    cleaned_count += 1
                except OSError:
                    pass
        
        if cleaned_count > 0:
            logger = self.get_logger(__name__)
            logger.info(f"清理了 {cleaned_count} 个旧日志文件")
    
    def get_log_files(self) -> list:
        """
        获取所有日志文件列表
        
        Returns:
            list: 日志文件路径列表
        """
        if not self.logs_dir.exists():
            return []
        
        return sorted(self.logs_dir.glob('log-*.log'))
    
    def get_current_log_file(self) -> Optional[Path]:
        """
        获取当前正在使用的日志文件
        
        Returns:
            Optional[Path]: 当前日志文件路径
        """
        current_time = datetime.now()
        filename = f"log-{current_time.strftime('%Y-%m-%d-%H')}.log"
        filepath = self.logs_dir / filename
        
        return filepath if filepath.exists() else None


# 全局日志系统实例
_logging_system = LoggingSystem()


def setup_logging(level: str = 'INFO', 
                  console_output: bool = False,
                  logs_dir: Optional[str] = None) -> None:
    """
    设置 TeamDev 日志系统
    
    Args:
        level: 日志级别
        console_output: 是否输出到控制台
        logs_dir: 日志目录
    """
    _logging_system.setup(level, console_output, logs_dir)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        logging.Logger: 配置好的日志器
    """
    return _logging_system.get_logger(name)


def cleanup_old_logs(days_to_keep: int = 7):
    """清理旧日志文件"""
    _logging_system.cleanup_old_logs(days_to_keep)


def get_log_files() -> list:
    """获取所有日志文件"""
    return _logging_system.get_log_files()


def get_current_log_file() -> Optional[Path]:
    """获取当前日志文件"""
    return _logging_system.get_current_log_file()


# 便捷的日志记录函数
def log_info(message: str, logger_name: str = 'teamdev'):
    """记录信息日志"""
    get_logger(logger_name).info(message)


def log_error(message: str, logger_name: str = 'teamdev'):
    """记录错误日志"""
    get_logger(logger_name).error(message)


def log_warning(message: str, logger_name: str = 'teamdev'):
    """记录警告日志"""
    get_logger(logger_name).warning(message)


def log_debug(message: str, logger_name: str = 'teamdev'):
    """记录调试日志"""
    get_logger(logger_name).debug(message)