#!/usr/bin/env python3
"""
開發工具腳本
提供各種開發輔助功能
"""

import os
import sys
from pathlib import Path

import requests


class DevTools:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent

    def check_pypi_name(self, package_name="yaml2py"):
        """檢查 PyPI 包名是否可用"""
        print(f"🔍 檢查包名 '{package_name}' 在 PyPI 的可用性...")

        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
            if response.status_code == 200:
                data = response.json()
                print(f"❌ 包名 '{package_name}' 已被使用")
                print(f"   當前版本: {data['info']['version']}")
                print(f"   作者: {data['info']['author']}")
                print(
                    "   上傳時間: "
                    + f"{data['releases'][data['info']['version']][0]['upload_time']}"
                )
                return False
            else:
                print(f"✅ 包名 '{package_name}' 可用!")
                return True
        except Exception as e:
            print(f"⚠️  檢查時發生錯誤: {e}")
            return None

    def get_package_stats(self, package_name="yaml2py"):
        """獲取包的統計信息"""
        print(f"📊 獲取 '{package_name}' 的統計信息...")

        try:
            # PyPI API
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
            if response.status_code == 200:
                data = response.json()
                info = data["info"]

                print("\n📦 包信息:")
                print(f"   名稱: {info['name']}")
                print(f"   版本: {info['version']}")
                print(f"   作者: {info['author']}")
                print(f"   描述: {info['summary']}")
                print(f"   主頁: {info['home_page']}")
                print(f"   許可證: {info['license']}")

                # 版本歷史
                releases = data["releases"]
                print("\n📈 版本歷史 (最近5個):")
                for version in list(releases.keys())[-5:]:
                    if releases[version]:
                        upload_time = releases[version][0]["upload_time"]
                        print(f"   {version}: {upload_time}")

            # 嘗試獲取下載統計 (pypistats.org)
            try:
                stats_response = requests.get(
                    f"https://pypistats.org/api/packages/{package_name}/recent"
                )
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    print("\n📈 下載統計:")
                    print(f"   最近一天: {stats_data['data']['last_day']:,}")
                    print(f"   最近一週: {stats_data['data']['last_week']:,}")
                    print(f"   最近一月: {stats_data['data']['last_month']:,}")
            except Exception:
                print("\n📈 下載統計: 暫時無法獲取")

        except Exception as e:
            print(f"❌ 獲取統計信息失敗: {e}")

    def validate_package(self):
        """驗證包的完整性"""
        print("🔍 驗證包完整性...")

        checks = []

        # 檢查必要文件
        required_files = [
            "pyproject.toml",
            "README.md",
            "LICENSE",
            "yaml2py/__init__.py",
            "yaml2py/cli.py",
        ]

        for file_path in required_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                checks.append(f"✅ {file_path}")
            else:
                checks.append(f"❌ {file_path} - 缺失")

        # 檢查版本一致性
        try:
            # 從 __init__.py 讀取版本
            init_file = self.root_dir / "yaml2py" / "__init__.py"
            with open(init_file, "r") as f:
                init_content = f.read()
                import re

                match = re.search(r'__version__ = ["\']([^"\']+)["\']', init_content)
                init_version = match.group(1) if match else "未找到"

            # 從 pyproject.toml 讀取版本
            pyproject_file = self.root_dir / "pyproject.toml"
            with open(pyproject_file, "r") as f:
                pyproject_content = f.read()
                match = re.search(r'version = ["\']([^"\']+)["\']', pyproject_content)
                pyproject_version = match.group(1) if match else "未找到"

            if init_version == pyproject_version:
                checks.append(f"✅ 版本一致性: {init_version}")
            else:
                checks.append(
                    f"❌ 版本不一致: __init__.py({init_version}) "
                    + f"vs pyproject.toml({pyproject_version})"
                )

        except Exception as e:
            checks.append(f"❌ 版本檢查失敗: {e}")

        # 輸出結果
        print("\n驗證結果:")
        for check in checks:
            print(f"  {check}")

    def setup_git_hooks(self):
        """設置 Git hooks"""
        print("🪝 設置 Git hooks...")

        hooks_dir = self.root_dir / ".git" / "hooks"
        if not hooks_dir.exists():
            print("❌ 沒有找到 .git/hooks 目錄")
            return

        # Pre-commit hook
        pre_commit_hook = hooks_dir / "pre-commit"
        pre_commit_content = """#!/bin/bash
# 運行測試和檢查
echo "🧪 運行 pre-commit 檢查..."

# 檢查代碼格式
echo "🔍 檢查代碼格式..."
black --check yaml2py/ tests/
if [ $? -ne 0 ]; then
    echo "❌ 代碼格式檢查失敗，請運行 'make format'"
    exit 1
fi

# 運行快速測試
echo "🧪 運行快速測試..."
python -m pytest tests/ -x -q
if [ $? -ne 0 ]; then
    echo "❌ 測試失敗"
    exit 1
fi

echo "✅ Pre-commit 檢查通過"
"""

        with open(pre_commit_hook, "w") as f:
            f.write(pre_commit_content)

        # 設置執行權限
        os.chmod(pre_commit_hook, 0o755)

        print("✅ Git hooks 設置完成")

    def clean_project(self):
        """清理項目文件"""
        print("🧹 清理項目文件...")

        # 要清理的文件和目錄
        clean_patterns = [
            "build/",
            "dist/",
            "*.egg-info/",
            "__pycache__/",
            ".pytest_cache/",
            "htmlcov/",
            ".coverage",
            "*.pyc",
        ]

        import glob
        import shutil

        cleaned = []
        for pattern in clean_patterns:
            for path in glob.glob(pattern, recursive=True):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                        cleaned.append(f"📁 {path}")
                    else:
                        os.remove(path)
                        cleaned.append(f"📄 {path}")
                except Exception as e:
                    print(f"⚠️  無法刪除 {path}: {e}")

        if cleaned:
            print("已清理:")
            for item in cleaned:
                print(f"  {item}")
        else:
            print("✨ 項目已經很乾淨了!")

    def generate_requirements(self):
        """生成 requirements 文件"""
        print("📋 生成 requirements 文件...")

        # 開發依賴
        dev_requirements = [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "isort>=5.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "twine>=4.0",
            "build>=0.10",
        ]

        # 生產依賴（從 pyproject.toml 讀取）
        try:
            import tomli

            with open(self.root_dir / "pyproject.toml", "rb") as f:
                data = tomli.load(f)
                prod_requirements = data["project"]["dependencies"]
        except Exception:
            prod_requirements = ["click>=8.0", "watchdog>=2.1.6"]

        # 寫入文件
        with open(self.root_dir / "requirements.txt", "w") as f:
            f.write("# Production dependencies\n")
            for req in prod_requirements:
                f.write(f"{req}\n")

        with open(self.root_dir / "requirements-dev.txt", "w") as f:
            f.write("# Development dependencies\n")
            f.write("-r requirements.txt\n\n")
            for req in dev_requirements:
                f.write(f"{req}\n")

        print("✅ Requirements 文件已生成:")
        print("  📄 requirements.txt")
        print("  📄 requirements-dev.txt")


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/dev-tools.py <command>")
        print("\n可用命令:")
        print("  check-name [package_name]  - 檢查 PyPI 包名可用性")
        print("  stats [package_name]       - 獲取包統計信息")
        print("  validate                   - 驗證包完整性")
        print("  setup-hooks               - 設置 Git hooks")
        print("  clean                     - 清理項目文件")
        print("  requirements              - 生成 requirements 文件")
        sys.exit(1)

    command = sys.argv[1]
    tools = DevTools()

    if command == "check-name":
        package_name = sys.argv[2] if len(sys.argv) > 2 else "yaml2py"
        tools.check_pypi_name(package_name)

    elif command == "stats":
        package_name = sys.argv[2] if len(sys.argv) > 2 else "yaml2py"
        tools.get_package_stats(package_name)

    elif command == "validate":
        tools.validate_package()

    elif command == "setup-hooks":
        tools.setup_git_hooks()

    elif command == "clean":
        tools.clean_project()

    elif command == "requirements":
        tools.generate_requirements()

    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
