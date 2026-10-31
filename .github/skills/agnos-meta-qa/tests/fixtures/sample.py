"""A fixture of the agnos-meta-qa tests with one known finding per kind (RQ-QLT-002, RQ-QLT-004)."""
import os

VALUE = None
# agnos-qa-exception: E711 kept for the test
SAME = VALUE == None


def heavy(a, b, c, d):
    total = 0
    for i in a:
        if i:
            for j in b:
                if j:
                    for k in c:
                        if k:
                            for m in d:
                                if m:
                                    total += 1
    return total
