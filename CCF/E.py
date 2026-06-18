import sys


def solve() -> None:
    data = sys.stdin.buffer.read().split()
    it = iter(data)
    t = int(next(it))
    out = []
    for _ in range(t):
        n = int(next(it))
        max_so_far = 0
        ans = 0
        for _ in range(n):
            a = int(next(it))
            if a < max_so_far:
                diff = max_so_far - a
                if diff > ans:
                    ans = diff
            elif a > max_so_far:
                max_so_far = a
        out.append(str(ans))
    sys.stdout.write('\n'.join(out))


if __name__ == '__main__':
    solve()