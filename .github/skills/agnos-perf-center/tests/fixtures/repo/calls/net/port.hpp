// Call-graph fixture: methods defined in their class.
#pragma once
namespace net {
class Port {
public:
    /// RQ-DEM-001: a port sends what it writes.
    int send() { return write(1); }
    int write(int n) { return n; }
};
}  // namespace net
