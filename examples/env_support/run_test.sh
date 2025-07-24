#!/bin/bash
# 一鍵測試環境變數支援功能

echo "=== yaml2py 環境變數支援測試 ==="
echo ""

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步驟 1：檢查 yaml2py 是否已安裝
echo -e "${YELLOW}步驟 1: 檢查 yaml2py 安裝${NC}"
if command -v yaml2py &> /dev/null; then
    echo -e "${GREEN}✓ yaml2py 已安裝${NC}"
else
    echo -e "${RED}✗ yaml2py 未安裝${NC}"
    echo "請先在專案根目錄執行: pip install -e ."
    exit 1
fi
echo ""

# 步驟 2：設定測試環境變數
echo -e "${YELLOW}步驟 2: 設定測試環境變數${NC}"
export DB_PASSWORD="test_db_password_123"
export OPENAI_API_KEY="sk-test-abc123xyz"
export ENVIRONMENT="testing"
export LOG_LEVEL="DEBUG"
export ENABLE_OPENAI="true"
export DEBUG_MODE="true"
export GOOGLE_PROJECT_ID="test-project-123"
export HOT_RELOAD="false"
export API_TOKEN="test-api-token"
export SECRET_KEY="test-secret-key"

echo "已設定以下環境變數："
echo "  DB_PASSWORD=test_db_password_123"
echo "  OPENAI_API_KEY=sk-test-abc123xyz"
echo "  ENVIRONMENT=testing"
echo "  LOG_LEVEL=DEBUG"
echo "  ENABLE_OPENAI=true"
echo "  其他測試用環境變數..."
echo ""

# 步驟 3：清理舊的生成檔案
echo -e "${YELLOW}步驟 3: 清理舊檔案${NC}"
if [ -d "generated_config" ]; then
    rm -rf generated_config
    echo -e "${GREEN}✓ 已清理舊的生成檔案${NC}"
fi
echo ""

# 步驟 4：生成配置類別
echo -e "${YELLOW}步驟 4: 生成配置類別${NC}"
yaml2py -c config_with_env.yaml -o generated_config
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 配置類別生成成功${NC}"
else
    echo -e "${RED}✗ 配置類別生成失敗${NC}"
    exit 1
fi
echo ""

# 步驟 5：執行 Python 測試
echo -e "${YELLOW}步驟 5: 執行 Python 測試${NC}"
python test_env_support.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Python 測試執行成功${NC}"
else
    echo -e "${RED}✗ Python 測試執行失敗${NC}"
    exit 1
fi
echo ""

# 步驟 6：測試嚴格模式
echo -e "${YELLOW}步驟 6: 測試嚴格模式（預期會失敗）${NC}"
export YAML2PY_STRICT_ENV=true
unset DB_PASSWORD
echo "已啟用嚴格模式並移除 DB_PASSWORD 環境變數"
echo ""

# 嘗試重新生成（應該失敗）
echo "嘗試在嚴格模式下生成..."
yaml2py -c config_with_env.yaml -o generated_config_strict 2>&1 | grep -E "(Error:|提示：)"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 嚴格模式正確攔截了缺少的環境變數${NC}"
    rm -rf generated_config_strict
else
    echo -e "${RED}✗ 嚴格模式測試異常${NC}"
fi
echo ""

# 清理
echo -e "${YELLOW}步驟 7: 清理測試檔案${NC}"
rm -rf generated_config
echo -e "${GREEN}✓ 測試完成！${NC}"
echo ""

# 恢復環境
unset YAML2PY_STRICT_ENV
echo "提示：環境變數仍然保留，如需清除請手動 unset"