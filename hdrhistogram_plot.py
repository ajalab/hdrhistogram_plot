#!/usr/bin/python3

import argparse
import sys

import matplotlib.pyplot as plt


class Histogram:
    def __init__(self, buckets):
        self.buckets = buckets

    def plot(self, ax, **kwargs):
        x = [bucket.inv_percentile for bucket in self.buckets]
        y = [bucket.value for bucket in self.buckets]
        ax.plot(x, y, **kwargs)

    @classmethod
    def from_file(cls, path):
        found_header = False
        buckets = []
        for line in open(path, 'r'):
            if len(line.strip()) == 0:
                continue

            if not found_header and cls.__is_header(line):
                found_header = True
                continue

            if found_header:
                try:
                    bucket = Bucket.from_line(line)
                    buckets.append(bucket)
                except Exception as e:
                    break

        return cls(buckets)

    @staticmethod
    def __is_header(line):
        fields = line.split()
        return len(fields) == 4 and fields[0] == 'Value' and fields[1] == 'Percentile'


class Bucket:
    def __init__(self, value, percentile, total_count, inv_percentile):
        self.value = value
        self.percentile = percentile
        self.total_count = total_count
        self.inv_percentile = inv_percentile

    @classmethod
    def from_line(cls, line):
        fields = line.split()
        if len(fields) != 4:
            raise ValueError("parse failure")

        return cls(float(fields[0]), float(fields[1]), int(fields[2]), float(fields[3]))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--out",
        help="output image file path"
    )
    parser.add_argument(
        "file",
        type=str,
        help="histogram file",
        nargs="+",
    )

    return parser.parse_args()


def main(files, out=None):
    fig, ax = plt.subplots(dpi=200)
    n_ticks = 7
    ticks = [10 ** k for k in range(n_ticks)]
    tick_labels = [
        "{:1.{p}%}".format(
            (1 - 10 ** -k),
            p=max(0, k - 2)
        )
        for k in range(n_ticks)
    ]
    ax.set_xscale('log')
    ax.set_xticks(ticks)
    ax.set_xlim(1, ticks[-1])
    ax.set_xticklabels(tick_labels)
    ax.set_xlabel("Percentile")
    ax.set_ylabel("Latency")

    for f in files:
        histogram = Histogram.from_file(f)
        histogram.plot(ax, label="hoge")

    if out is not None:
        fig.savefig(out)

    return 0


if __name__ == '__main__':
    args = parse_args()
    sys.exit(main(args.file, args.out))
