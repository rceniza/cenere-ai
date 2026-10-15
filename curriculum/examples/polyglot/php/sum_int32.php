<?php
$line = fgets(STDIN);
if ($line === false) exit(2);
$parts = preg_split('/\s+/', trim($line), -1, PREG_SPLIT_NO_EMPTY);
if (count($parts) !== 2) exit(2);
$values = [];
foreach ($parts as $part) {
    if (!preg_match('/^[+-]?\d+$/', $part)) exit(2);
    $value = filter_var($part, FILTER_VALIDATE_INT);
    if ($value === false || $value < -2147483648 || $value > 2147483647) exit(2);
    $values[] = $value;
}
$sum = $values[0] + $values[1];
if ($sum < -2147483648 || $sum > 2147483647) exit(2);
echo $sum, "\n";
