# development

Linux（Ubuntu 24.04）で Makefile / CMake によりビルドしている Native ソフトウェアを、
**Bazel でビルドできるように移植するにはどうすればよいか** を調査するためのリポジトリです。

同じ C++ サンプルアプリを次の 3 通りの方法でビルドできるようにしてあり、
それぞれの書き方を見比べることで「Makefile / CMake の何が Bazel の何に対応するか」が分かるようになっています。

| ビルド方法 | 使うファイル | ひとことで言うと |
| --- | --- | --- |
| Makefile | `Makefile`（ルート）+ 各アプリの `Makefile` | 従来型。コンパイル・リンクの手順を自分で書く |
| CMake | `cmakeBuild.py` + `sample/CMakeLists.txt` + 各アプリの `CMakeLists.txt` | ターゲット（ライブラリ・実行ファイル）を宣言し、cmake が Makefile を生成する |
| Bazel | `WORKSPACE` + `.bazelrc` + `.bazelversion` + 各アプリの `BUILD` | ターゲットを宣言し、Bazel がサンドボックス内でビルドする |

---

## 1. サンプルアプリの構成

`sample/` の下に、**ディレクトリ構成がまったく同じ** 2 つのアプリがあります。

| アプリ | 中身 | 実行結果 |
| --- | --- | --- |
| `SampleApp-A` | `mathutils` ライブラリ（`add` / `multiply`）+ それを呼ぶ `main.cpp` | `add(6, 7) = 13` / `multiply(6, 7) = 42` |
| `SampleApp-B` | `mathutils` ライブラリ（`subtract` / `divide`）+ それを呼ぶ `main.cpp` | `subtract(6, 3) = 3` / `divide(6, 3) = 2` |

どちらも「ライブラリ 1 つ + 実行ファイル 1 つ」という、実際の Native ソフトによくある最小構成です。

```
development/
├── Makefile              # [Make]  A / B / 両方 を選んでビルドするルート Makefile
├── cmakeBuild.py         # [CMake] cmake の configure / build / clean をまとめた Python スクリプト
├── WORKSPACE             # [Bazel] リポジトリのルートであることを Bazel に教えるファイル（WORKSPACE 方式）
├── .bazelrc              # [Bazel] bzlmod を無効化し、WORKSPACE 方式に統一
├── .bazelversion         # [Bazel] 使用する Bazel のバージョン（bazelisk が自動でダウンロード）
└── sample/
    ├── CMakeLists.txt    # [CMake] A / B / 両方 を選んで add_subdirectory するルート CMakeLists
    ├── SampleApp-A/
    │   ├── include/mathutils.h
    │   ├── src/mathutils.cpp
    │   ├── src/main.cpp
    │   ├── Makefile        # [Make]  このアプリ単体のビルド手順
    │   ├── CMakeLists.txt  # [CMake] このアプリ単体のターゲット定義
    │   └── BUILD           # [Bazel] このアプリ単体のターゲット定義
    └── SampleApp-B/
        └── （SampleApp-A とまったく同じ構成）
```

ビルド方法ごとの生成物は、ソースとは別のフォルダに出力されます（いずれも `.gitignore` 済み）。

| ビルド方法 | 出力先 | 実行ファイル名（A / B） |
| --- | --- | --- |
| Makefile | `MakefileBuild/SampleApp/A/bin/`, `.../B/bin/` | `sample_app-A` / `sample_app-B` |
| CMake | `CmakeBuild/Executable/` | `sample_app_A` / `sample_app_B` |
| Bazel | `bazel-bin/sample/SampleApp-A/`, `.../SampleApp-B/` | `sample_app-Bazel_A` / `sample_app-Bazel_B` |

---

## 2. ビルド方法

コマンドはすべて **リポジトリのルート（`development/`）で実行** します。

### 2-1. Makefile でビルドする

ルートの `Makefile` が、`APP` 変数の値に応じて各アプリの `Makefile` を `make -C` で呼び出します。

| やりたいこと | コマンド |
| --- | --- |
| A だけビルド | `make APP=A` |
| B だけビルド | `make APP=B` |
| 両方ビルド | `make`（`make APP=ALL` と同じ） |
| A だけクリーン | `make clean APP=A` |
| B だけクリーン | `make clean APP=B` |
| 全部クリーン（`MakefileBuild/` を丸ごと削除） | `make clean` |

クリーンしてからビルドし直す場合は、2 つのコマンドを順に実行します。

```sh
make clean
make APP=A
```

ビルドした実行ファイルを動かす:

```sh
./MakefileBuild/SampleApp/A/bin/sample_app-A
./MakefileBuild/SampleApp/B/bin/sample_app-B
```

### 2-2. CMake でビルドする

`cmakeBuild.py` が `cmake -S sample -B CmakeBuild/Build_cmake -DBUILD_APP=...` と `cmake --build` をまとめて実行します。
`sample/CMakeLists.txt` が `BUILD_APP` の値を見て、A / B のどちら（または両方）を `add_subdirectory` するかを決めます。

| やりたいこと | コマンド |
| --- | --- |
| A だけビルド | `python3 cmakeBuild.py --app A` |
| B だけビルド | `python3 cmakeBuild.py --app B` |
| 両方ビルド | `python3 cmakeBuild.py`（`--app ALL` と同じ） |
| クリーンしてから A をビルド | `python3 cmakeBuild.py --clean --app A` |
| クリーンのみ（`CmakeBuild/` を丸ごと削除） | `python3 cmakeBuild.py --clean-only` |

ビルドした実行ファイルを動かす:

```sh
./CmakeBuild/Executable/sample_app_A
./CmakeBuild/Executable/sample_app_B
```

### 2-3. Bazel でビルドする

Bazel は「`//パッケージのパス:ターゲット名`」という形でビルド対象を指定します。
`BUILD` ファイルがあるディレクトリが 1 つのパッケージになるので、`sample/SampleApp-A` と `sample/SampleApp-B` がそれぞれ別のパッケージです。

| やりたいこと | コマンド |
| --- | --- |
| A だけビルド | `bazel build //sample/SampleApp-A:sample_app-Bazel_A` |
| B だけビルド | `bazel build //sample/SampleApp-B:sample_app-Bazel_B` |
| 全部ビルド | `bazel build //...`（`//...` は「リポジトリ内の全ターゲット」の意味） |
| クリーン | `bazel clean` |
| 完全クリーン（ダウンロードしたものも含めて削除） | `bazel clean --expunge` |

クリーンしてからビルドし直す場合:

```sh
bazel clean
bazel build //...
```

ビルドした実行ファイルを動かす:

```sh
./bazel-bin/sample/SampleApp-A/sample_app-Bazel_A
./bazel-bin/sample/SampleApp-B/sample_app-Bazel_B
```

> Bazel 本体は `bazelisk` 経由で使います（`npm install -g @bazel/bazelisk`）。
> `bazel` コマンドを実行すると、bazelisk が `.bazelversion` に書かれたバージョンを自動でダウンロードして使います。
> 注意: `.bazelversion` は `WORKSPACE` があるディレクトリで初めて認識されます。`WORKSPACE` が無いと最新版が使われてしまいます。

---

## 3. 3 つのビルド定義の対応関係（SampleApp-A の実例）

同じことを 3 通りに書いたものなので、並べて見ると対応が分かります。

| やっていること | Makefile | CMakeLists.txt | BUILD（Bazel） |
| --- | --- | --- | --- |
| コンパイルオプション | `CXXFLAGS := -std=c++17 -Wall -Wextra` | `set(CMAKE_CXX_STANDARD 17)` + `add_compile_options(-Wall -Wextra)` | `copts = [...]` または `.bazelrc` の `build --cxxopt=...`（このサンプルでは Bazel のデフォルトに任せている） |
| ヘッダの場所を教える | `-Iinclude` | `target_include_directories(mathutils_A PUBLIC include)` | `includes = ["include"]` |
| ライブラリを作る | `.cpp` → `.o` のルールを自分で書く | `add_library(mathutils_A STATIC src/mathutils.cpp)` | `cc_library(name = "mathutils", srcs = [...], hdrs = [...])` |
| 実行ファイルを作る | `$(CXX) $(OBJS) -o $(TARGET)` | `add_executable(sample_app_A src/main.cpp)` | `cc_binary(name = "sample_app-Bazel_A", srcs = [...])` |
| 実行ファイルにライブラリをリンクする | `$(OBJS)` に `mathutils.o` を含める | `target_link_libraries(sample_app_A PRIVATE mathutils_A)` | `deps = [":mathutils"]` |
| 中間ファイル・生成物の置き場所 | `BIN_DIR` / `OBJ_DIR` を自分で管理 | `-B` で指定したビルドディレクトリ | Bazel が `bazel-bin/` 等に自動配置（指定不要） |
| クリーン | `rm -rf $(BIN_DIR) $(OBJ_DIR)` | ビルドディレクトリを削除 | `bazel clean` |

---

## 4. Makefile から Bazel へ移植するには

Makefile は「どのファイルをどのオプションでコンパイルし、どの順でリンクするか」を **手順として** 書きます。
Bazel では手順は書かず、「このライブラリはこのソースからできている」「この実行ファイルはこのライブラリに依存している」という **関係だけを宣言** します。コンパイルやリンクの手順は Bazel が組み立てます。

### 手順

1. **成果物の単位を洗い出す**
   Makefile が最終的に作っているものは何か（実行ファイル、静的ライブラリ、共有ライブラリ）を確認します。
   本サンプルでは「`mathutils` ライブラリ」と「`sample_app` 実行ファイル」の 2 つです。
2. **成果物ごとに Bazel のルールを 1 つ書く**
   - ライブラリ → `cc_library`
   - 実行ファイル → `cc_binary`
3. **ソースとヘッダを列挙する**
   `srcs` に `.cpp`、`hdrs` に公開ヘッダを書きます。`-I` で指定していたパスは `includes` に書きます。
4. **リンク順を依存関係に書き換える**
   Makefile で「`main.o` と `mathutils.o` をリンクする」と書いていた部分は、
   Bazel では `cc_binary` の `deps = [":mathutils"]` になります。個々の `.o` は Bazel が自動で作るので書きません。
5. **コンパイルオプションを移す**
   `CXXFLAGS` の内容は、ターゲットごとなら `copts`、リポジトリ全体なら `.bazelrc` に書きます。
6. **ビルドして結果を比べる**
   `bazel build` した実行ファイルと、`make` で作った実行ファイルの出力が同じになることを確認します。

### よくある対応表

| Makefile でやっていたこと | Bazel での書き方 |
| --- | --- |
| `CXXFLAGS = -std=c++17 -Wall` | `copts = ["-std=c++17", "-Wall"]`、または `.bazelrc` に `build --cxxopt=-std=c++17` |
| `-Iinclude` | `includes = ["include"]` |
| `%.o: %.cpp` のようなコンパイルルール | 書かない（Bazel が自動生成） |
| `ar rcs libfoo.a *.o`（静的ライブラリ作成） | `cc_library(name = "foo", ...)` |
| `$(CXX) $(OBJS) -o app`（リンク） | `cc_binary(name = "app", deps = [...])` |
| `make clean` | `bazel clean` |
| `.PHONY` の補助タスク（テスト実行など） | `sh_binary` / `genrule` / `cc_test` などに置き換える |

---

## 5. CMake から Bazel へ移植するには

CMake は Bazel と同じく「ターゲットとその依存関係」を宣言する方式なので、Makefile よりも機械的に書き換えられます。
基本的には **1 つの `add_library` / `add_executable` を 1 つの `cc_library` / `cc_binary` に置き換える** だけです。

### 手順

1. `add_library(...)` → `cc_library(...)`、`add_executable(...)` → `cc_binary(...)` に 1 対 1 で書き換える。
2. `target_include_directories(...)` の内容を `includes`（公開ヘッダは `hdrs`）に移す。
3. `target_link_libraries(A PRIVATE B)` を、`A` の `deps = [":B"]` に移す。
4. `find_package(...)` で外部ライブラリを使っている場合は、その部分だけ Bazel の外部依存定義に置き換える
   （WORKSPACE 方式なら `http_archive` / `new_local_repository`、bzlmod 方式なら `MODULE.bazel` の `bazel_dep`）。
5. `bazel build` して、CMake でビルドしたものと出力が同じになることを確認する。

### よくある対応表

| CMakeLists.txt でやっていたこと | Bazel での書き方 |
| --- | --- |
| `add_library(foo STATIC src/foo.cpp)` | `cc_library(name = "foo", srcs = ["src/foo.cpp"])` |
| `add_executable(app src/main.cpp)` | `cc_binary(name = "app", srcs = ["src/main.cpp"])` |
| `target_include_directories(foo PUBLIC include)` | `includes = ["include"]` + `hdrs = [...]` |
| `target_link_libraries(app PRIVATE foo)` | `cc_binary` の `deps = [":foo"]` |
| `set(CMAKE_CXX_STANDARD 17)` | `.bazelrc` の `build --cxxopt=-std=c++17`、または `copts` |
| `add_compile_options(-Wall -Wextra)` | `copts = ["-Wall", "-Wextra"]`、または `.bazelrc` |
| `add_subdirectory(SampleApp-A)`（ルートで子を選ぶ） | 不要。`BUILD` があるディレクトリは自動でパッケージになり、`bazel build //...` や個別指定で選べる |
| `find_package(...)` | `http_archive` / `new_local_repository` / `bazel_dep` |
| ビルドディレクトリ（`-B build`） | 不要。Bazel が `bazel-bin/` 等に出力する |

---

## 6. 移植調査から分かったこと

- **ライブラリ / 実行ファイルの単位が整理されているほど、Bazel への移植は簡単になる。**
  逆に、大量の `.o` をまとめて 1 回でリンクしているような Makefile は、先に論理的な単位に分割してから移植する方がスムーズです。
- **CMake からの移植は Makefile からの移植より楽。**
  CMake のターゲットグラフと Bazel のターゲットグラフはほぼ同じ形をしているためです。
- **Bazel 7 系以降は bzlmod が既定で有効。**
  WORKSPACE 方式だけで使う場合は `.bazelrc` に `common --noenable_bzlmod` を書かないと、空の `MODULE.bazel` が自動生成されて警告が出ます。
- **ルートで A / B を選んでビルドする仕組み** は、Makefile では `APP` 変数 + `make -C`、CMake では `BUILD_APP` 変数 + `add_subdirectory` で自作しましたが、Bazel ではターゲットパスの指定（`//sample/SampleApp-A:...`）だけで済むため、専用の仕組みは不要です。
