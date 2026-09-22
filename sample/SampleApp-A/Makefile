CXX := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -Iinclude

BIN_DIR := bin
OBJ_DIR := obj
TARGET := $(BIN_DIR)/sample_app-A

SRCS := src/mathutils.cpp src/main.cpp
OBJS := $(SRCS:src/%.cpp=$(OBJ_DIR)/%.o)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS) | $(BIN_DIR)
	$(CXX) $(OBJS) -o $(TARGET)

$(OBJ_DIR)/%.o: src/%.cpp | $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BIN_DIR) $(OBJ_DIR):
	mkdir -p $@

clean:
	rm -rf $(BIN_DIR) $(OBJ_DIR)
