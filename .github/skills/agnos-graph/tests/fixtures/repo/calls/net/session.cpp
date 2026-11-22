// Call-graph fixture: out-of-class definitions, a constructor, an operator, an external call.
#include "port.hpp"
#include <cstdio>

namespace net {

struct Session {
    int send();
    int write(int n);
    Session();
};

// TASK-DEM-001: sending logs.
int Session::send()
{
    return log(2);
}

int Session::write(int n) { return n; }

Session::Session() {}

}  // namespace net

static int log(int level) { printf("%d", level); return level; }

bool operator==(const net::Session&, const net::Session&) { return true; }
