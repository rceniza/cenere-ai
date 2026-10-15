using System;
using System.Collections.Generic;

public static class TagParser
{
    public static List<string> Parse(string input)
    {
        return new List<string>(input.Split(','));
    }
}
