#!/usr/bin/env python3
"""測試環境變數支援的範例"""
import os
import sys
from pathlib import Path

# 設定一些測試用的環境變數
os.environ['ENVIRONMENT'] = 'production'
os.environ['DB_PASSWORD'] = 'secret123'
os.environ['OPENAI_API_KEY'] = 'sk-test123'
os.environ['ENABLE_OPENAI'] = 'true'

# 假設已經生成了配置類別
sys.path.insert(0, str(Path(__file__).parent))

# 首先用 yaml2py 生成配置類別
# yaml2py -c config_with_env.yaml -o generated_config

try:
    from generated_config import ConfigManager
    
    # 創建配置管理器實例
    config = ConfigManager(config_path='config_with_env.yaml')
    
    print("=== 環境變數配置測試 ===\n")
    
    # 系統配置
    print(f"環境: {config.system.environment}")  # production (來自環境變數)
    print(f"日誌級別: {config.system.log_level}")  # INFO (使用預設值)
    print(f"調試模式: {config.system.debug}")  # false (使用預設值)
    
    print("\n--- 資料庫配置 ---")
    print(f"主機: {config.database.host}")  # localhost (使用預設值)
    print(f"連接埠: {config.database.port}")  # 5432 (使用預設值)
    print(f"資料庫名稱: {config.database.name}")  # asr_hub (使用預設值)
    
    # 敏感資料處理
    print("\n--- 敏感資料 ---")
    print(f"密碼（實際值）: {config.database.password}")  # secret123
    
    # 使用 print_all 方法（會遮罩敏感資料）
    print("\n--- 使用 print_all() 顯示所有配置（遮罩敏感資料）---")
    config.database.print_all()
    
    print("\n--- Provider 配置 ---")
    print(f"OpenAI 啟用: {config.providers.openai.enabled}")  # True
    print(f"OpenAI API Base: {config.providers.openai.api_base}")  # 使用預設值
    
    # 測試熱重載（修改環境變數不會自動重載，需要重啟程式）
    print("\n--- 提示 ---")
    print("1. 環境變數在程式啟動時載入")
    print("2. 修改 YAML 檔案會觸發熱重載")
    print("3. 修改環境變數需要重啟程式才能生效")
    
except ImportError as e:
    print(f"錯誤：請先執行 yaml2py 生成配置類別")
    print(f"執行命令：yaml2py -c config_with_env.yaml -o generated_config")
    print(f"\n詳細錯誤：{e}")
except Exception as e:
    print(f"發生錯誤：{e}")

# 測試嚴格模式
print("\n=== 測試嚴格模式 ===")
os.environ['YAML2PY_STRICT_ENV'] = 'true'
del os.environ['DB_PASSWORD']  # 刪除必要的環境變數

try:
    from generated_config import ConfigManager
    config2 = ConfigManager(config_path='config_with_env.yaml')
except Exception as e:
    print(f"預期的錯誤（嚴格模式）：{e}")