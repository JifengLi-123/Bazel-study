# development

## Native ビルド → Bazel 移植調査サンプル

Ubuntu 24.04 上の Native ビルド（Makefile / CMake）を Bazel に移植する方法を検証するためのサンプル一式。`sample/` に同一内容の C++ サンプル（`mathutils` ライブラリ + `sample_app` 実行ファイル）を、3つのビルド方式で用意している。

```
sample/
  include/mathutils.h
  src/mathutils.cpp
  src/main.cpp
  Makefile        # Make 版
  CMakeLists.txt  # CMake 版
  BUILD           # Bazel 版
WORKSPACE          # Bazel（WORKSPACE レガシー方式）
.bazelrc           # bzlmod 無効化（WORKSPACE方式に統一）
.bazelversion      # Bazel バージョン固定（bazelisk 用）
```

ビルド方法:

```sh
# Make
cd sample && make && ./bin/sample_app

# CMake
cd sample && cmake -S . -B build_cmake && cmake --build build_cmake && ./build_cmake/sample_app

# Bazel（リポジトリルートで実行）
bazel build //sample:sample_app && ./bazel-bin/sample/sample_app
```

3方式とも同じ出力（`add(6, 7) = 13` / `multiply(6, 7) = 42`）になることを確認済み。

### Makefile から Bazel への移植方法

Makefile は「コンパイル対象・オプション・依存関係・リンク」を全て自分で書き下すが、Bazel はそれらを `cc_library` / `cc_binary` ルールの宣言に置き換える。対応関係は以下の通り。

| Makefile の要素 | Bazel での対応 |
| --- | --- |
| `CXXFLAGS`（`-std=c++17 -Wall -Wextra`） | `cc_library`/`cc_binary` の `copts`、または `.bazelrc` に `build --cxxopt=-std=c++17` 等でまとめて指定 |
| `-Iinclude`（インクルードパス） | `cc_library` の `includes = ["include"]`（または `hdrs` を公開するだけで足りる場合は不要） |
| 個別の `*.o` コンパイルルール | 記述不要（Bazel が `srcs`/`hdrs` から自動でコンパイルアクションを生成） |
| ライブラリを作る部分（`ar` や `.o` のまとめ） | `cc_library(name, srcs, hdrs)` |
| 実行ファイルへのリンク（`$(CXX) $(OBJS) -o $(TARGET)`） | `cc_binary(name, srcs, deps)` の `deps` にライブラリターゲットを指定 |
| `make clean`（`rm -rf bin obj`） | `bazel clean`（Bazel が管理する `bazel-*` 出力を削除） |
| `.PHONY` ターゲットでの補助タスク | 必要なら `genrule` やカスタム `sh_binary` に置き換え、またはターゲットをそのまま `bazel run` で実行 |

移植手順:
1. Makefile が生成しているバイナリ・ライブラリの単位を確認し、それぞれを `cc_library` / `cc_binary` として切り出す（本サンプルでは `mathutils` ライブラリと `sample_app` 実行ファイルの2つ）。
2. `srcs` / `hdrs` に実ファイルを列挙し、インクルードパスは `includes` で表現する。
3. Makefile 内のリンク順（どの `.o`/ライブラリが誰に必要か）を `deps` の依存関係として書き直す。
4. `CXXFLAGS` 等のコンパイルオプションは `copts`（ターゲット単位）か `.bazelrc`（リポジトリ全体）に移す。
5. `bazel build //path:target` でビルドし、Makefile 版と出力を比較して一致を確認する。

### CMake から Bazel への移植方法

CMake は「ターゲットとその依存関係」というモデルが Bazel に近く、Makefile よりも機械的に対応付けやすい。

| CMakeLists.txt の要素 | Bazel での対応 |
| --- | --- |
| `add_library(mathutils STATIC src/...)` | `cc_library(name = "mathutils", srcs = [...])` |
| `add_executable(sample_app src/...)` | `cc_binary(name = "sample_app", srcs = [...])` |
| `target_include_directories(... PUBLIC include)` | `cc_library`/`cc_binary` の `includes = ["include"]`、公開ヘッダは `hdrs` |
| `target_link_libraries(sample_app PRIVATE mathutils)` | `cc_binary` の `deps = [":mathutils"]` |
| `set(CMAKE_CXX_STANDARD 17)` | `.bazelrc` の `build --cxxopt=-std=c++17`、またはターゲットの `copts` |
| `add_compile_options(-Wall -Wextra)` | 各ターゲットの `copts = ["-Wall", "-Wextra"]`、または `.bazelrc` |
| `find_package(...)` で外部依存を解決 | WORKSPACE 方式では `new_local_repository`/`http_archive` 等、bzlmod 方式では `MODULE.bazel` の `bazel_dep` に置き換え |
| out-of-source ビルドディレクトリ（`build/`） | Bazel は常に `bazel-bin`/`bazel-out` に出力するため対応不要 |

移植手順:
1. CMakeLists.txt 内の `add_library` / `add_executable` を、対応する `cc_library` / `cc_binary` に1:1で書き換える。
2. `target_include_directories` の内容を `includes`（または `hdrs` の配置）に移す。
3. `target_link_libraries` の依存関係を `deps` にそのまま転記する（CMake のターゲットグラフと Bazel のターゲットグラフはほぼ同型）。
4. `find_package` 等で外部ライブラリに依存している場合は、その部分だけ WORKSPACE（もしくは bzlmod）側の外部依存定義に置き換える必要がある。
5. `bazel build //path:target` でビルドし、CMake 版と出力を比較して一致を確認する。

いずれの移植でも、既存のビルドがライブラリ／実行ファイルの単位で整理されているほど Bazel への移行は機械的になる。逆に、単一の巨大な `.o` 集合を一度にリンクしているような構成では、先に論理的な単位へ分割してから移植する方がスムーズ。