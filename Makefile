# yaml2py Makefile
# 用於管理項目的構建、測試、發布等任務

.PHONY: help install install-dev test test-verbose lint format clean build upload upload-test check-dist docs serve-docs

# 默認目標
help:
	@echo "yaml2py - Makefile 命令列表"
	@echo "=========================="
	@echo ""
	@echo "開發相關:"
	@echo "  install      - 安裝項目依賴"
	@echo "  install-dev  - 安裝開發依賴"
	@echo "  test         - 運行測試"
	@echo "  test-verbose - 運行詳細測試"
	@echo "  lint         - 運行代碼檢查"
	@echo "  format       - 格式化代碼"
	@echo ""
	@echo "構建相關:"
	@echo "  clean        - 清理構建文件"
	@echo "  build        - 構建發布包"
	@echo "  check-dist   - 檢查發布包"
	@echo ""
	@echo "發布相關:"
	@echo "  upload-test  - 上傳到 TestPyPI"
	@echo "  upload       - 上傳到 PyPI"
	@echo ""
	@echo "文檔相關:"
	@echo "  docs         - 生成文檔"
	@echo "  serve-docs   - 啟動文檔服務器"
	@echo ""
	@echo "示例:"
	@echo "  run-example  - 運行基本示例"

# 安裝項目依賴
install:
	pip install -e .

# 安裝開發依賴
install-dev:
	pip install -e .
	pip install pytest pytest-cov black isort flake8 mypy twine build

# 運行測試
test:
	python -m pytest tests/ --tb=short

# 運行詳細測試
test-verbose:
	python -m pytest tests/ -v --tb=long --durations=10

# 運行測試並生成覆蓋率報告
test-coverage:
	python -m pytest tests/ --cov=yaml2py --cov-report=html --cov-report=term

# 代碼風格檢查
lint:
	@echo "運行 flake8..."
	flake8 yaml2py/ tests/
	@echo "運行 mypy..."
	mypy yaml2py/ --ignore-missing-imports
	@echo "檢查 import 順序..."
	isort --check-only yaml2py/ tests/

# 格式化代碼
format:
	@echo "格式化 Python 代碼..."
	black yaml2py/ tests/
	@echo "排序 imports..."
	isort yaml2py/ tests/

# 清理構建文件
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 構建發布包
build: clean
	python -m build

# 檢查發布包
check-dist: build
	python -m twine check dist/*

# 上傳到 TestPyPI (測試)
upload-test: check-dist
	python -m twine upload --repository testpypi dist/*

# 上傳到 PyPI (正式發布)
upload: check-dist
	@echo "⚠️  即將發布到 PyPI，請確認版本號正確！"
	@read -p "確認發布? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		python -m twine upload dist/*; \
	else \
		echo "發布已取消"; \
	fi

# 生成並運行示例
run-example:
	@echo "運行基本示例..."
	cd examples/basic_usage && \
	yaml2py --config config.yaml --output ./generated && \
	python usage_example.py

# 運行高級示例
run-advanced-example:
	@echo "運行高級示例..."
	cd examples/advanced_usage && \
	yaml2py --config config.yaml --output ./generated && \
	python advanced_example.py

# 檢查項目設置
check-setup:
	@echo "檢查項目設置..."
	@echo "Python 版本: $$(python --version)"
	@echo "pip 版本: $$(pip --version)"
	@echo "項目版本: $$(python -c 'import yaml2py; print(yaml2py.__version__)')"

# 準備發布 (運行所有檢查)
prepare-release: clean format lint test build check-dist
	@echo "✅ 發布準備完成！"
	@echo "📦 發布包已生成在 dist/ 目錄"
	@echo ""
	@echo "下一步:"
	@echo "  測試發布: make upload-test"
	@echo "  正式發布: make upload"

# 完整的 CI 流程
ci: format lint test build check-dist
	@echo "✅ CI 流程完成！"

# 開發環境設置
dev-setup: install-dev
	@echo "🛠️  開發環境設置完成！"
	@echo ""
	@echo "可用命令:"
	@echo "  make test     - 運行測試"
	@echo "  make lint     - 代碼檢查"
	@echo "  make format   - 格式化代碼"
	@echo "  make build    - 構建包"

# 版本檢查
version:
	@python -c "import yaml2py; print(f'當前版本: {yaml2py.__version__}')"
	@echo "pyproject.toml 版本: $$(grep '^version' pyproject.toml | cut -d'\"' -f2)"

# 創建新版本標籤
tag-version:
	@VERSION=$$(python -c "import yaml2py; print(yaml2py.__version__)"); \
	echo "創建版本標籤: v$$VERSION"; \
	git tag -a "v$$VERSION" -m "Release version $$VERSION"; \
	echo "推送標籤到遠程倉庫..."; \
	git push origin "v$$VERSION"

# 安全檢查
security-check:
	@echo "運行安全檢查..."
	pip install safety bandit
	safety check
	bandit -r yaml2py/