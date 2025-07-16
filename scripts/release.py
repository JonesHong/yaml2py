#!/usr/bin/env python3
"""
發布準備腳本
自動化版本更新和發布流程
"""

import re
import subprocess
import sys
from pathlib import Path


class ReleaseManager:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.pyproject_path = self.root_dir / "pyproject.toml"
        self.init_path = self.root_dir / "yaml2py" / "__init__.py"
        self.changelog_path = self.root_dir / "CHANGELOG.md"

    def get_current_version(self):
        """獲取當前版本號"""
        with open(self.init_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        raise ValueError("Cannot find version in __init__.py")

    def update_version(self, new_version):
        """更新版本號"""
        print(f"📝 更新版本號到 {new_version}")

        # 更新 __init__.py
        with open(self.init_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(
            r'__version__ = ["\'][^"\']+["\']',
            f'__version__ = "{new_version}"',
            content,
        )

        with open(self.init_path, "w", encoding="utf-8") as f:
            f.write(content)

        # 更新 pyproject.toml
        with open(self.pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(
            r'version = ["\'][^"\']+["\']', f'version = "{new_version}"', content
        )

        with open(self.pyproject_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ 版本號已更新到 {new_version}")

    def run_tests(self):
        """運行測試"""
        print("🧪 運行測試...")
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/"], capture_output=True, text=True
        )
        if result.returncode != 0:
            print("❌ 測試失敗:")
            print(result.stdout)
            print(result.stderr)
            return False
        print("✅ 測試通過")
        return True

        # def run_lint(self):
        #     """運行代碼檢查"""
        #     print("🔍 運行代碼檢查...")

        #     # 運行 black 檢查
        #     result = subprocess.run(
        #         ["black", "--check", "yaml2py/", "tests/"], capture_output=True, text=True
        #     )
        #     if result.returncode != 0:
        #         print("❌ 代碼格式檢查失敗，運行 'make format' 修復")
        #         return False

        #     # 運行 flake8
        #     result = subprocess.run(
        #         ["flake8", "yaml2py/", "tests/"], capture_output=True, text=True
        #     )
        #     if result.returncode != 0:
        #         print("❌ Flake8 檢查失敗:")
        #         print(result.stdout)
        #         return False

        #     print("✅ 代碼檢查通過")
        #     return True

    def build_package(self):
        """構建包"""
        print("📦 構建包...")

        # 清理舊的構建文件
        subprocess.run(["make", "clean"], cwd=self.root_dir)

        # 構建新包
        result = subprocess.run(
            ["python", "-m", "build"], capture_output=True, text=True, cwd=self.root_dir
        )
        if result.returncode != 0:
            print("❌ 構建失敗:")
            print(result.stdout)
            print(result.stderr)
            return False

        # 檢查包
        result = subprocess.run(
            ["python", "-m", "twine", "check", "dist/*"],
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.root_dir,
        )
        if result.returncode != 0:
            print("❌ 包檢查失敗:")
            print(result.stdout)
            print(result.stderr)
            return False

        print("✅ 包構建成功")
        return True

    def create_git_tag(self, version):
        """創建 Git 標籤"""
        print(f"🏷️  創建 Git 標籤 v{version}")

        # 檢查是否有未提交的更改
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        )
        if result.stdout.strip():
            print("❌ 有未提交的更改，請先提交:")
            print(result.stdout)
            return False

        # 創建標籤
        subprocess.run(
            ["git", "tag", "-a", f"v{version}", "-m", f"Release version {version}"]
        )
        print(f"✅ 標籤 v{version} 已創建")
        return True

    def update_changelog(self, version):
        """更新 CHANGELOG"""
        print("📝 請手動更新 CHANGELOG.md")
        print(f"   - 將 [Unreleased] 改為 [{version}] - {self.get_today()}")
        print("   - 添加新的 [Unreleased] 部分")

        input("按 Enter 繼續...")

    def get_today(self):
        """獲取今天的日期"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d")

    def full_release_process(self, new_version):
        """完整的發布流程"""
        current_version = self.get_current_version()
        print("🚀 開始發布流程")
        print(f"   當前版本: {current_version}")
        print(f"   新版本: {new_version}")
        print()

        # 1. 運行測試
        if not self.run_tests():
            return False

        # 2. 運行代碼檢查
        # if not self.run_lint():
        #     return False

        # 3. 更新版本號
        self.update_version(new_version)

        # 4. 更新 CHANGELOG
        self.update_changelog(new_version)

        # 5. 構建包
        if not self.build_package():
            return False

        print("\n🎉 發布準備完成!")
        print("\n下一步:")
        print(
            "1. 檢查並提交更改: git add . && git commit -m 'Bump version to {}'".format(
                new_version
            )
        )
        print("2. 推送到遠程: git push origin main")
        print("3. 創建標籤: make tag-version")
        print("4. 推送標籤: git push origin v{}".format(new_version))
        print("5. 在 GitHub 上創建 Release")

        return True


def main():
    if len(sys.argv) != 2:
        print("用法: python scripts/release.py <new_version>")
        print("例如: python scripts/release.py 0.2.0")
        sys.exit(1)

    new_version = sys.argv[1]

    # 驗證版本格式
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print("❌ 版本號格式錯誤，請使用 x.y.z 格式")
        sys.exit(1)

    manager = ReleaseManager()

    try:
        success = manager.full_release_process(new_version)
        if success:
            print("\n✅ 發布準備成功完成!")
        else:
            print("\n❌ 發布準備失敗")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發布過程中發生錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
