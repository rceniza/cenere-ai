using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text.Json;

string line = Console.In.ReadLine() ?? string.Empty;
if (string.IsNullOrWhiteSpace(line))
{
    Console.WriteLine("[]");
    return 0;
}

string[] tokens = line.Split(',', StringSplitOptions.None);
var values = new List<int>(tokens.Length);
foreach (string token in tokens)
{
    if (!int.TryParse(token.Trim(), NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out int value))
    {
        return 2;
    }
    values.Add(value);
}

Console.WriteLine(JsonSerializer.Serialize(values.Distinct().OrderBy(value => value)));
return 0;
