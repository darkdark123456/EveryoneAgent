import logging
import os
import sys
from datetime import datetime
from typing   import Optional

class SingletonLogger:
    """单例日志类"""
    _instance: Optional["SingletonLogger"] = None
    _logger:Optional[logging.Logger] = None
    
    def __new__(cls, *args, **kwargs) -> "SingletonLogger":
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_dir="logs", log_level=logging.DEBUG):
        if self._logger is not None:
            return 
        self.log_dir = log_dir
        self.log_level = log_level
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self._setup_logger()

    def _setup_logger(self)->None:
        logger = logging.getLogger("EveryoneAgent")
        logger.setLevel(self.log_level)
        logger.handlers.clear() 
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)-8s] [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        log_file = os.path.join(self.log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        self._logger = logger
        
    def debug(self, msg: str, *args, **kwargs) -> None:
        if self._logger:
            self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        if self._logger:
            self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        if self._logger:
            self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        if self._logger:
            self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        if self._logger:
            self._logger.critical(msg, *args, **kwargs)
    def get_logger(self) -> logging.Logger:
        if self._logger is None:
            self._setup_logger()
        assert self._logger is not None
        return self._logger


