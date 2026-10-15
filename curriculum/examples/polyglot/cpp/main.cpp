#include <algorithm>
#include <iostream>
#include <set>
#include <sstream>
#include <string>

int main() {
    std::string line;
    if (!std::getline(std::cin, line)) return 2;
    auto last = line.find_last_not_of(" \t\r");
    if (last != std::string::npos && line[last] == ',') return 2;
    std::set<int> values;
    if (line.find_first_not_of(" \t\r") != std::string::npos) {
        std::stringstream input(line);
        std::string token;
        while (std::getline(input, token, ',')) {
            try {
                size_t consumed = 0;
                int value = std::stoi(token, &consumed);
                if (token.find_first_not_of(" \t\r", consumed) != std::string::npos) return 2;
                values.insert(value);
            } catch (...) { return 2; }
        }
    }
    std::cout << '[';
    bool first = true;
    for (int value : values) { if (!first) std::cout << ','; std::cout << value; first = false; }
    std::cout << "]\n";
}
