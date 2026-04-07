#include <iostream>

long getFactorial(int number) {
    if (number <= 1) {
        return 1;
    }
    return number * getFactorial(number - 1);
}

int main() {
    int x = 6;
    std::cout << getFactorial(x) << std::endl;
    return 0;
}
