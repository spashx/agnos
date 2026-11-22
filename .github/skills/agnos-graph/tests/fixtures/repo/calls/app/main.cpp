// Call-graph fixture: a caller outside both classes.
#include "../net/port.hpp"

int relay(net::Port& port, net::Session& x)
{
    x.send();
    port.write(3);
    log(1);
    log(2);
    return 0;
}
