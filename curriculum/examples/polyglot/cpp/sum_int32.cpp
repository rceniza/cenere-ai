#include <charconv>
#include <iostream>
#include <limits>
#include <sstream>
#include <string>

int main() {
    std::string line, extra;
    if (!std::getline(std::cin, line)) return 2;
    std::istringstream input(line);
    long long a, b;
    if (!(input >> a >> b) || (input >> extra)) return 2;
    const auto low = std::numeric_limits<int>::min();
    const auto high = std::numeric_limits<int>::max();
    if (a < low || a > high || b < low || b > high) return 2;
    const long long sum = a + b;
    if (sum < low || sum > high) return 2;
    std::cout << sum << '\n';
}
