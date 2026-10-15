#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char input[256];
    if (!fgets(input, sizeof input, stdin) || strcspn(input, "\n") == sizeof input - 1) return 2;
    char *cursor = input, *end;
    long long values[2];
    for (int i = 0; i < 2; i++) {
        while (*cursor == ' ' || *cursor == '\t' || *cursor == '\r' || *cursor == '\n') cursor++;
        if (!*cursor) return 2;
        errno = 0;
        values[i] = strtoll(cursor, &end, 10);
        if (errno || end == cursor || values[i] < INT_MIN || values[i] > INT_MAX) return 2;
        cursor = end;
    }
    while (*cursor == ' ' || *cursor == '\t' || *cursor == '\r' || *cursor == '\n') cursor++;
    if (*cursor) return 2;
    long long sum = values[0] + values[1];
    if (sum < INT_MIN || sum > INT_MAX) return 2;
    printf("%lld\n", sum);
    return 0;
}
