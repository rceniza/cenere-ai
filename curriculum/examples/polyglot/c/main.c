#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int compare_ints(const void *left, const void *right) {
    int a = *(const int *)left, b = *(const int *)right;
    return (a > b) - (a < b);
}

int main(void) {
    char input[65536];
    if (!fgets(input, sizeof input, stdin)) return 2;
    int values[8192]; size_t count = 0;
    size_t length = strcspn(input, "\r\n");
    input[length] = '\0';
    char *cursor = input;
    while (*cursor == ' ' || *cursor == '\t') cursor++;
    if (*cursor) {
        while (*cursor) {
            char *comma = strchr(cursor, ',');
            char *finish = comma ? comma : cursor + strlen(cursor);
            *finish = '\0';
            while (*cursor == ' ' || *cursor == '\t') cursor++;
            errno = 0; char *end = NULL; long value = strtol(cursor, &end, 10);
            while (end && (*end == ' ' || *end == '\t')) end++;
            if (errno || end == cursor || !end || *end || value < INT_MIN || value > INT_MAX || count == 8192) return 2;
            values[count++] = (int)value;
            if (!comma) break;
            if (comma[1] == '\0') return 2;
            cursor = comma + 1;
        }
    }
    qsort(values, count, sizeof values[0], compare_ints);
    putchar('[');
    for (size_t i = 0, written = 0; i < count; i++) {
        if (i && values[i] == values[i - 1]) continue;
        printf("%s%d", written++ ? "," : "", values[i]);
    }
    puts("]");
    return 0;
}
