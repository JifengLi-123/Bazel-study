#!/usr/bin/env python3
"""
CmakeBuild.py - SampleApp-A / SampleApp-B の CMake ビルドラッパー

使い方:
    python3 CmakeBuild.py --app A            # SampleApp-A のみビルド
    python3 CmakeBuild.py --app B            # SampleApp-B のみビルド
    python3 CmakeBuild.py --app ALL          # 両方ビルド（デフォルト）
    python3 CmakeBuild.py --clean-only       # ビルドディレクトリを削除
    python3 CmakeBuild.py --clean --app A    # クリーン後、Aのみ再ビルド
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# このスクリプトが development/ 直下にある前提
ROOT_DIR = Path(__file__).resolve().parent
SOURCE_DIR = ROOT_DIR / "sample"
CMAKEBUILD_DIR = ROOT_DIR / "CmakeBuild"
BUILD_DIR = CMAKEBUILD_DIR / "Build_cmake"
EXECUTABLE_DIR = CMAKEBUILD_DIR / "Executable"


def run(cmd: list[str]) -> None:
    print(f"[CmakeBuild] $ {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"[CmakeBuild] コマンドが失敗しました (exit code {result.returncode})")
        sys.exit(result.returncode)


def clean() -> None:
    if BUILD_DIR.exists():
        print(f"[CmakeBuild] クリーンアップ: {BUILD_DIR} を削除します")
        shutil.rmtree(BUILD_DIR)
    else:
        print(f"[CmakeBuild] {BUILD_DIR} は存在しません。クリーンアップ不要です")

    if EXECUTABLE_DIR.exists():
        print(f"[CmakeBuild] クリーンアップ: {EXECUTABLE_DIR} を削除します")
        shutil.rmtree(EXECUTABLE_DIR)


def configure(app: str) -> None:
    EXECUTABLE_DIR.mkdir(parents=True, exist_ok=True)
    run([
        "cmake",
        "-S", str(SOURCE_DIR),
        "-B", str(BUILD_DIR),
        f"-DBUILD_APP={app}",
        f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY={EXECUTABLE_DIR}",
    ])


def build() -> None:
    run(["cmake", "--build", str(BUILD_DIR)])


def main() -> None:
    parser = argparse.ArgumentParser(description="SampleApp-A/B CMake ビルドラッパー")
    parser.add_argument(
        "--app",
        choices=["A", "B", "ALL"],
        default="ALL",
        help="ビルド対象を選択 (デフォルト: ALL)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="ビルドディレクトリを削除する（--appと併用可。併用時はクリーン後にビルド実行）",
    )
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="クリーンのみ実行し、ビルドは行わない",
    )
    args = parser.parse_args()

    if args.clean or args.clean_only:
        clean()
        if args.clean_only:
            return

    configure(args.app)
    build()
    print(f"[CmakeBuild] 完了: BUILD_APP={args.app}")
    print(f"[CmakeBuild] 実行ファイル出力先: {EXECUTABLE_DIR}")


if __name__ == "__main__":
    main()