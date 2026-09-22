cmake_minimum_required(VERSION 3.16)
project(sample_app_A CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_compile_options(-Wall -Wextra)

add_library(mathutils_A STATIC src/mathutils.cpp)
target_include_directories(mathutils_A PUBLIC include)

add_executable(sample_app_A src/main.cpp)
target_link_libraries(sample_app_A PRIVATE mathutils_A)
