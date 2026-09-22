# ビルド対象を選択: A, B, ALL（デフォルトはALL＝両方）
APP ?= ALL

.PHONY: all clean

all:
ifeq ($(APP),A)
	$(MAKE) -C SampleApp-A
else ifeq ($(APP),B)
	$(MAKE) -C SampleApp-B
else
	$(MAKE) -C SampleApp-A
	$(MAKE) -C SampleApp-B
endif

clean:
ifeq ($(APP),A)
	$(MAKE) -C SampleApp-A clean
else ifeq ($(APP),B)
	$(MAKE) -C SampleApp-B clean
else
	$(MAKE) -C SampleApp-A clean
	$(MAKE) -C SampleApp-B clean
endif
