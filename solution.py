import os
import time
from collections import Counter
from dataclasses import dataclass
from operator import itemgetter
from random import choices, randint

def clear_console():
    """Macro to clear the console"""
    os.system("cls" if os.name == "nt" else "clear")

def green(text):
    """Macro to change the text color to green using ANSI escape codes"""
    return "\033[32m" + text + "\033[0m"

@dataclass
class Cluster:
    x1: int
    y1: int
    x2: int
    y2: int
    size: int

def make_matrix(size, weights=(0.5, 0.5)):
    values = ('0', '1')
    return [choices(values, weights=weights, k=size) for _ in range(size)]

def get_clusters(matrix, min_size=2, max_only=True):
    """Return a list of all clusters of the maximum size"""
    def all_high(n, start, end):
        n &= (1 << (end + 1)) - 1
        n >>= start
        return not n ^ ((1 << (end - start + 1)) - 1)

    size = len(matrix)
    # The string is reversed since bit indexing will start from the right
    int_matrix = [int(''.join(row)[::-1], base=2) for row in matrix]
    clusters = []
    min_size -= 1
    max_size = min_size
    for y1 in range(size - min_size + 1):
        for x1 in range(size - min_size + 1):
            for y2, x2 in zip(range(y1 + min_size, size), range(x1 + min_size, size)):
                if (
                    all(all_high(int_matrix[i], x1, x2) for i in range(y1, y2 + 1))
                    or all(all_high(~int_matrix[i], x1, x2) for i in range(y1, y2 + 1))
                ):
                    if not max_only or y2 - y1 == max_size:
                        clusters.append(Cluster(x1, y1, x2, y2, x2 - x1 + 1))
                    elif y2 - y1 > max_size:
                        max_size = y2 - y1
                        clusters.clear()
                        clusters.append(Cluster(x1, y1, x2, y2, x2 - x1 + 1))
                else:
                    # There's no need checking larger squares starting at (x1, y1)
                    break
    return clusters

def print_result(matrix, clusters, overlap=False):
    if not overlap:
        print(f"Cleaning up overlapping clusters...", end=' ', flush=True)
        start = time.process_time_ns()
        i = 0
        while i < len(clusters) - 1:
            a = clusters[i]
            j = i + 1
            while j < len(clusters):
                b = clusters[j]
                if not (a.y2 < b.y1 or a.y1 > b.y2 or a.x2 < b.x1 or a.x1 > b.x2):
                    if a.size < b.size:
                        del clusters[i]
                        break
                    else:
                        del clusters[j]
                else:
                    j += 1
            else:
                i += 1
        print(f"Done in {(time.process_time_ns() - start) / 1000000:.2f}ms!")

        counts = Counter()
        # matrix = [bytearray(''.join(row), "ascii") for row in matrix]
        for c in clusters:
            counts[c.size] += 1
            x = randint(1, 7)
            for i in range(c.y1, c.y2 + 1):
                row  = matrix[i]
                row[c.x1] = "\033[4%dm" % x + row[c.x1]
                row[c.x2] += "\033[0m"
    else:
        ...

    print()
    for size, count in sorted(counts.items(), key=itemgetter(0)):
        print(green(f"Found {count} {size}x{size} clusters!"))
    print()
    print('\n'.join(' '.join(row) for row in matrix))

def run(size, min_size=2, weights=(0.5, 0.5), max_only=True, overlap=False):
    # clear_console()  # clearing once can fix ANSI escape codes on windows
    print("Clusters are " + green("fun"))

    print(f"Generating a {size}x{size} matrix...", end=' ', flush=True)
    start = time.process_time_ns()
    matrix = make_matrix(size, weights)
    print(f"Done in {(time.process_time_ns() - start) / 1000000:.2f}ms!")

    print(
        "Getting",
        "largest" if max_only else "all",
        f"clusters (above {min_size}x{min_size}) in the matrix...",
        end=' ',
        flush=True,
    )
    start = time.process_time_ns()
    clusters = get_clusters(matrix, min_size, max_only)
    print(f"Done in {(time.process_time_ns() - start) / 1000000:.2f}ms!")

    print_result(matrix, clusters, overlap)


if __name__ == "__main__":
    while True:
        try:
            choice = int(input(
                "1 -> Run\n"
                "2 -> Quit\n"
                "Choice: "
                ))
        except ValueError:
            continue

        if 1 <= choice <= 2:
            print()
            if choice == 1:
                size = input("Matrix size (min=10): ")
                if not size.isdigit() or int(size) < 10:
                    continue
                size = int(size)
                min_size = input(f"Minimum cluster size (min=2, max={size}): ")
                if not min_size.isdigit() or not 1 < int(min_size) <= size:
                    continue
                max_only = input("All clusters (y/N)? ").lower() != "y"
                overlap = input("Overlap (y/N)? ").lower() == "y"
                print()
                run(size, int(min_size), (0.2, 0.8), max_only, overlap)
            elif choice == 2:
                break
        print()
