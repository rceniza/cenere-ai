using System;
using System.Collections.Generic;

internal static class Program
{
    private static void Main()
    {
        Assert(TagParser.Parse(" Blue,red,BLUE,, Red "), new[] { "Blue", "red" });
        Assert(TagParser.Parse(" , , "), Array.Empty<string>());
    }

    private static void Assert(List<string> actual, string[] expected)
    {
        if (actual.Count != expected.Length)
        {
            Environment.Exit(1);
        }
        for (var index = 0; index < expected.Length; index++)
        {
            if (actual[index] != expected[index])
            {
                Environment.Exit(1);
            }
        }
    }
}
