// Call-graph fixture, C#: a block namespace and a local function.
namespace Demo.Data
{
    public struct Store
    {
        public int Count()
        {
            int Twice(int n) { return n * 2; }
            return Twice(1);
        }
    }
}
