<?php
require __DIR__ . '/../username.php';

$valid = ['Aaa', 'user_01', 'Z' . str_repeat('a', 19)];
$invalid = ['', 'ab', 'A' . str_repeat('a', 20), '1user', '_user', 'user-name', 'two words', 'Åbc', 'aßc'];
foreach ($valid as $value) {
    if (!is_valid_username($value)) {
        fwrite(STDERR, 'expected valid username: ' . $value . PHP_EOL);
        exit(1);
    }
}
foreach ($invalid as $value) {
    if (is_valid_username($value)) {
        fwrite(STDERR, 'expected invalid username: ' . $value . PHP_EOL);
        exit(1);
    }
}
