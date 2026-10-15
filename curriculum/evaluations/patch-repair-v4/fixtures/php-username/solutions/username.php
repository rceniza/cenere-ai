<?php
function is_valid_username(string $username): bool
{
    return preg_match('/\A[A-Za-z][A-Za-z0-9_]{2,19}\z/', $username) === 1;
}
