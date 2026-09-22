cc_library(
    name = "mathutils",
    srcs = ["src/mathutils.cpp"],
    hdrs = ["include/mathutils.h"],
    includes = ["include"],
)

cc_binary(
    name = "sample_app",
    srcs = ["src/main.cpp"],
    deps = [":mathutils"],
)
