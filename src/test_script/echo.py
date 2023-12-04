import sys
import time


def echo(times: int) -> None:
    for i in range(times // 2):
        print(f"stdout: {i}")
        time.sleep(1)
    for i in range(times - times // 2):
        print(f"stderr: {i}", file=sys.stderr)
        time.sleep(1)


if __name__ == "__main__":
    echo(int(sys.argv[1]))
