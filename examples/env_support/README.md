# 環境變數支援測試指南

本資料夾包含測試 yaml2py 環境變數支援功能的範例檔案。

## 檔案說明

- **config_with_env.yaml** - 包含環境變數語法的範例 YAML 配置
- **test_env_support.py** - 測試環境變數功能的 Python 腳本
- **run_test.sh** - 一鍵執行測試的腳本

## 測試步驟

### 步驟 1：安裝 yaml2py（開發模式）

```bash
# 在專案根目錄執行
cd ../..
pip install -e .
```

### 步驟 2：設定測試環境變數

```bash
# 必要的環境變數
export DB_PASSWORD="my_secret_password"
export OPENAI_API_KEY="sk-test123456"

# 可選的環境變數（有預設值）
export ENVIRONMENT="production"
export LOG_LEVEL="DEBUG"
export ENABLE_OPENAI="true"
```

### 步驟 3：生成配置類別

```bash
# 在 examples/env_support 目錄下執行
cd examples/env_support
yaml2py -c config_with_env.yaml -o generated_config
```

成功後會看到：
```
Reading YAML configuration from: /path/to/config_with_env.yaml
Generating schema.py...
Successfully generated generated_config/schema.py
Generating manager.py...
Successfully generated generated_config/manager.py

YAML configuration generation complete!
```

### 步驟 4：執行測試腳本

```bash
python test_env_support.py
```

預期輸出：
```
=== 環境變數配置測試 ===

環境: production
日誌級別: DEBUG
調試模式: false

--- 資料庫配置 ---
主機: localhost
連接埠: 5432
資料庫名稱: asr_hub

--- 敏感資料 ---
密碼（實際值）: my_secret_password

--- 使用 print_all() 顯示所有配置（遮罩敏感資料）---
database Configuration:
  host: localhost
  port: 5432
  name: asr_hub
  user: postgres
  password: my_s************

--- Provider 配置 ---
OpenAI 啟用: True
OpenAI API Base: https://api.openai.com

--- 提示 ---
1. 環境變數在程式啟動時載入
2. 修改 YAML 檔案會觸發熱重載
3. 修改環境變數需要重啟程式才能生效
```

### 步驟 5：測試嚴格模式

```bash
# 啟用嚴格模式
export YAML2PY_STRICT_ENV=true

# 刪除必要的環境變數
unset DB_PASSWORD

# 重新生成（應該會報錯）
yaml2py -c config_with_env.yaml -o generated_config
```

預期錯誤：
```
Error: 環境變數 'DB_PASSWORD' 未設定。請設定環境變數或使用預設值語法：${DB_PASSWORD:default_value}
提示：您可以設定環境變數 YAML2PY_STRICT_ENV=false 來忽略缺少的環境變數
```

## 一鍵測試

使用提供的測試腳本快速執行所有測試：

```bash
./run_test.sh
```

## 測試不同場景

### 場景 1：使用預設值
```bash
# 不設定任何環境變數
unset ENVIRONMENT LOG_LEVEL DB_PASSWORD OPENAI_API_KEY
./run_test.sh
```

### 場景 2：部分環境變數
```bash
# 只設定必要的環境變數
export DB_PASSWORD="test123"
export OPENAI_API_KEY="sk-test"
./run_test.sh
```

### 場景 3：覆蓋所有預設值
```bash
export ENVIRONMENT="staging"
export LOG_LEVEL="ERROR"
export DB_HOST="remote-db.example.com"
export DB_PORT="3306"
./run_test.sh
```

## 清理測試檔案

```bash
# 刪除生成的配置類別
rm -rf generated_config/
```

## 注意事項

1. 環境變數名稱區分大小寫
2. 布林值會自動轉換（"true"/"false" → True/False）
3. 數字會自動轉換類型（"8080" → 8080）
4. 空字串是有效值，與未設定不同