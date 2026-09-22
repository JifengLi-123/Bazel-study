cmake_minimum_required(VERSION 3.16)
project(SampleRoot LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ビルド対象を選択: A, B, ALL（デフォルトはALL＝両方）
set(BUILD_APP "ALL" CACHE STRING "Which app to build: A, B, or ALL")
set_property(CACHE BUILD_APP PROPERTY STRINGS A B ALL)

if(BUILD_APP STREQUAL "A" OR BUILD_APP STREQUAL "ALL")
    add_subdirectory(SampleApp-A)
endif()

if(BUILD_APP STREQUAL "B" OR BUILD_APP STREQUAL "ALL")
    add_subdirectory(SampleApp-B)
endif()