ROOT_DIR := $(abspath .)
BUILD_ROOT := $(ROOT_DIR)/MakefileBuild/SampleApp

# ビルド対象を選択: A, B, ALL（デフォルトはALL＝両方）
APP ?= ALL

.PHONY: all clean

all:
ifeq ($(APP),A)
	$(MAKE) -C sample/SampleApp-A BIN_DIR=$(BUILD_ROOT)/A/bin OBJ_DIR=$(BUILD_ROOT)/A/obj
else ifeq ($(APP),B)
	$(MAKE) -C sample/SampleApp-B BIN_DIR=$(BUILD_ROOT)/B/bin OBJ_DIR=$(BUILD_ROOT)/B/obj
else
	$(MAKE) -C sample/SampleApp-A BIN_DIR=$(BUILD_ROOT)/A/bin OBJ_DIR=$(BUILD_ROOT)/A/obj
	$(MAKE) -C sample/SampleApp-B BIN_DIR=$(BUILD_ROOT)/B/bin OBJ_DIR=$(BUILD_ROOT)/B/obj
endif

clean:
ifeq ($(APP),A)
	$(MAKE) -C sample/SampleApp-A clean BIN_DIR=$(BUILD_ROOT)/A/bin OBJ_DIR=$(BUILD_ROOT)/A/obj
else ifeq ($(APP),B)
	$(MAKE) -C sample/SampleApp-B clean BIN_DIR=$(BUILD_ROOT)/B/bin OBJ_DIR=$(BUILD_ROOT)/B/obj
else
	rm -rf $(ROOT_DIR)/MakefileBuild
endif