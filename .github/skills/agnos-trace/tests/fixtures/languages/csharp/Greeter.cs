// Call-graph fixture, C#: a file-scoped namespace, an attributed method, an expression-bodied one.
using System;

namespace Demo.Shapes;

public class Greeter
{
    // RQ-DEM-001
    [Obsolete]
    public void Greet()
    {
        Console.WriteLine(Name());
    }

    private string Name() => "x";

    public Greeter() { }
}

public interface IShape
{
    double Area();
}
