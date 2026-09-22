#include <iostream>

#include "mathutils.h"

int main() {
    int a = 6;
    int b = 7;

    std::cout << "add(" << a << ", " << b << ") = " << mathutils::add(a, b) << std::endl;
    std::cout << "multiply(" << a << ", " << b << ") = " << mathutils::multiply(a, b) << std::endl;

    return 0;
}
