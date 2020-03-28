
def func(n):
    while True:
        for _ in range(n):
            yield 0
        yield 12


if __name__ == '__main__':
    f = func(5)
    for i in range(10):
        print(next(f))
