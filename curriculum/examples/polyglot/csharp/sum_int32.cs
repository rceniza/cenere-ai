using System;
using System.Globalization;

string input = Console.In.ReadToEnd();
string[] tokens = input.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries);

if (tokens.Length != 2 ||
    !int.TryParse(tokens[0], NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out int left) ||
    !int.TryParse(tokens[1], NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out int right))
{
    return 2;
}

try
{
    Console.WriteLine(checked(left + right));
    return 0;
}
catch (OverflowException)
{
    return 2;
}
