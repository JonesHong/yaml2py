"""Environment variable support for YAML loading"""

import os
import re
from typing import Any, Dict, Union


class EnvironmentVariableError(Exception):
    """當環境變數未設定且無預設值時拋出"""

    pass


def replace_env_vars(text: str, strict: bool = False) -> str:
    """
    替換文本中的環境變數引用

    支援語法：
    - ${VAR}：必須存在的環境變數
    - ${VAR:default}：帶預設值的環境變數

    參數：
        text: 要處理的文本
        strict: 是否嚴格模式（True 時缺少變數會拋出異常）

    返回：
        處理後的文本
    """
    pattern = re.compile(r"\$\{([^}]+)\}")

    def replacer(match):
        env_content = match.group(1)

        # 支援 ${VAR:default} 語法
        if ":" in env_content:
            var_name, default_value = env_content.split(":", 1)
            return os.getenv(var_name, default_value)
        else:
            value = os.getenv(env_content)
            if value is None and strict:
                raise EnvironmentVariableError(
                    f"環境變數 '{env_content}' 未設定。"
                    f"請設定環境變數或使用預設值語法：${{{env_content}:default_value}}"
                )
            return value or ""

    return pattern.sub(replacer, text)


def process_yaml_value(value: Any, strict: bool = False) -> Any:
    """
    遞迴處理 YAML 值中的環境變數

    參數：
        value: YAML 值（可能是字串、列表或字典）
        strict: 是否嚴格模式

    返回：
        處理後的值
    """
    if isinstance(value, str):
        # 只處理包含環境變數語法的字串
        if "${" in value:
            return replace_env_vars(value, strict)
        return value
    elif isinstance(value, dict):
        return {k: process_yaml_value(v, strict) for k, v in value.items()}
    elif isinstance(value, list):
        return [process_yaml_value(item, strict) for item in value]
    else:
        return value


def load_yaml_with_env(yaml_content: Union[str, Dict], strict: bool = False) -> Dict:
    """
    載入 YAML 並處理環境變數

    參數：
        yaml_content: YAML 字串或已解析的字典
        strict: 是否嚴格模式（缺少環境變數時拋出異常）

    返回：
        處理後的 YAML 資料
    """
    import yaml

    # 如果是字串，先替換環境變數再解析
    if isinstance(yaml_content, str):
        processed_content = replace_env_vars(yaml_content, strict)
        data = yaml.safe_load(processed_content)
    else:
        # 如果已經是字典，直接處理值
        data = yaml_content

    # 遞迴處理所有值
    return process_yaml_value(data, strict)
