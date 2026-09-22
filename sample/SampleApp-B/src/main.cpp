#include <iostream>

#include "mathutils.h"

int main() {
    int a = 6;
    int b = 7;

    std::cout << "subtract(" << a << ", " << b << ") = " << mathutils::subtract(a, b) << std::endl;
    std::cout << "divide(" << b << ", " << a << ") = " << mathutils::divide(b, a) << std::endl;

    return 0;
}
