/* RQ-DEM-002: helpers in C.
   A block comment of two lines. */
static int helper(void) { return 1; }

int **table(void) { return 0; }

int run(int (*fp)(void))
{
    return helper() + (*fp)() + puts("x");
}
