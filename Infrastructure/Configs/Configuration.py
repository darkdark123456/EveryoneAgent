import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from pathlib import Path





"""每个Agent都需要一个config，使用tread_id来区分不同的Agent"""
config: RunnableConfig = {
    "configurable": {
        "thread_id": "1"
    }
}



class Configuration:
    def __init__(self) -> None:
        """_summary_ api_key和model

        Raises:
            ValueError: _description_
        """
        env_path: Path = Path(__file__).parent / ".env"
        load_dotenv(dotenv_path=env_path)
        self.api_key: str = os.getenv("DASHSCOPE_API_KEY") or ""
        self.model: str = os.getenv("MODEL") or "qwen-plus"
        if not self.api_key:
            raise ValueError("Cannot find DASHSCOPE_API_KEY")
    @staticmethod
    def load_servers(file_path: str="servers_config.json") -> Dict[str, Any]:
        """读取配置文件
        Args:
            file_path (str, optional): _description_. Defaults to "servers_config.json".

        Raises:
            ValueError: _description_ 找不到配置文件

        Returns:
            Dict[str, Any]: _description_ 返回配置文件
        """
        #if not os.path.exists(file_path):
        file_path_:str = str(Path(__file__).parent / file_path)
        if file_path_ == "":
            raise ValueError("Cannot find agent config file ")
        with open(file_path_, "r", encoding="utf-8") as f:
            return json.load(f).get("mcpServers", {})