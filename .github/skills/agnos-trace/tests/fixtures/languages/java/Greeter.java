// Call-graph fixture, Java: a package, an annotated method, an interface method without body.
package demo.shapes;

public class Greeter {
    // RQ-DEM-001
    @Override
    public String toString() {
        System.out.println(name());
        return name();
    }

    private String name() {
        return "x";
    }

    public Greeter() {
    }

    interface Shape {
        double area();
    }
}
