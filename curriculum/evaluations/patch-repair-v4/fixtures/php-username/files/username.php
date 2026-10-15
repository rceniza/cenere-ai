<?php
function is_valid_username(string $username): bool
{
    return strlen($username) >= 3;
}
