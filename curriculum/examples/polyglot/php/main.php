<?php
$line = fgets(STDIN);
if ($line === false) exit(2);
$line = trim($line);
$values = [];
if ($line !== '') {
    foreach (explode(',', $line) as $part) {
        $token = trim($part);
        if (!preg_match('/^[+-]?\d+$/', $token)) exit(2);
        $value = filter_var($token, FILTER_VALIDATE_INT);
        if ($value === false || $value < -2147483648 || $value > 2147483647) exit(2);
        $values[] = $value;
    }
}
$values = array_values(array_unique($values));
sort($values, SORT_NUMERIC);
echo json_encode($values, JSON_THROW_ON_ERROR), "\n";
