#include <iostream>

#include "mathutils.h"

int main() {
    int a = 6;
    int b = 3;

    std::cout << "subtract(" << a << ", " << b << ") = " << mathutils::subtract(a, b) << std::endl;
    std::cout << "divide(" << a << ", " << b << ") = " << mathutils::divide(a, b) << std::endl;

    return 0;
}
