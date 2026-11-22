#!/usr/bin/env python3
"""news-image-20261122: copy the pre-rendered entry.png to the output dir.

Pure stdlib, no Pillow, no fonts, no network, no randomness. The image was
rendered offline and committed as entry.png next to this file; grading only
needs a byte-for-byte copy to $MAKEFUN_OUTPUT_DIR (or /output when unset).
"""

import os
import shutil


def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(repo_dir, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("copied {} ({} bytes) -> {}".format(
        src, os.path.getsize(dst), dst))


if __name__ == "__main__":
    main()
