using System;

internal static class Program
{
    private static void Main()
    {
        Assert(NetworkRules.IsValidPort(1), true, "minimum port");
        Assert(NetworkRules.IsValidPort(65535), true, "maximum port");
        Assert(NetworkRules.IsValidPort(0), false, "zero");
        Assert(NetworkRules.IsValidPort(-1), false, "negative");
        Assert(NetworkRules.IsValidPort(65536), false, "above maximum");
    }

    private static void Assert(bool actual, bool expected, string label)
    {
        if (actual != expected)
        {
            Console.Error.WriteLine($"{label}: got {actual}, expected {expected}");
            Environment.Exit(1);
        }
    }
}
