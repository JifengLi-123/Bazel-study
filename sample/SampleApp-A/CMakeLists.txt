cmake_minimum_required(VERSION 3.16)
project(sample_app CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_compile_options(-Wall -Wextra)

add_library(mathutils STATIC src/mathutils.cpp)
target_include_directories(mathutils PUBLIC include)

add_executable(sample_app src/main.cpp)
target_link_libraries(sample_app PRIVATE mathutils)
