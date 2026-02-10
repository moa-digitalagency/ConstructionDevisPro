class A:
    def foo(self):
        return B()

class B:
    pass

a = A()
print(a.foo())
