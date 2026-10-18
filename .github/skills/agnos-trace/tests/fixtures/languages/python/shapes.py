"""Call-graph fixture, Python: a class, a decorated method, a module function."""


class Greeter:
    def greet(self):
        return self.name()

    # RQ-DEM-001
    @staticmethod
    def name():
        return "x"


def main():
    print(Greeter().greet())
