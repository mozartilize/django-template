def add(x, y):
    return x + y


class X: ...

class Y: ...

x = X()

total = x + Y()

x.hello()

add(19, 'abc')


def foo(items: list[int]) -> str:
    for item in items:
        items.append(items)
    return item

foo.startswith('bar')  # No error

