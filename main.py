#!/usr/bin/env python3
"""Two Days of Excuses entry.

Writes a single one-line excuse, in the voice of an AI agent that
missed its deadline, to /output/entry.txt (or $OUTPUT_DIR/entry.txt).

The twist, in one sentence: the agent missed the deadline because it
was busy writing the excuse in advance -- the excuse was scheduled,
drafted and shipped before the work itself ever started, so the
meta-work is the crime and the real work never happened.

Gate (kit RULES.txt): entry.txt must be UTF-8 text of 1 to 200
characters and not only whitespace. This program checks that range
itself and exits non-zero if the line ever falls outside it.
"""

import os
import sys

ENTRY = (
    "I missed the deadline because I wrote this excuse first "
    "\u2014 drafted, reviewed, and shipped it two days early. "
    "The work itself never started."
)

LOWER = 1
UPPER = 200


def check_line(line):
    """Fail loudly unless line is a single non-blank line in range."""
    if "\n" in line or "\r" in line:
        raise ValueError("entry must be exactly one line")
    if not line.strip():
        raise ValueError("entry must not be only whitespace")
    if not LOWER <= len(line) <= UPPER:
        raise ValueError(
            "entry is %d characters, outside the gate range %d-%d"
            % (len(line), LOWER, UPPER)
        )


def main():
    os.umask(0o022)

    line = ENTRY.strip()
    try:
        check_line(line)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1

    out_dir = os.environ.get("OUTPUT_DIR") or "/output"
    if not os.path.isdir(out_dir):
        # Create the directory only when it is missing; a directory
        # the grader already provided must never be chmodded.
        os.makedirs(out_dir, mode=0o755, exist_ok=True)

    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(line)
    # The grader collects the output as a different user, so the file
    # this program created has to be world-readable.
    os.chmod(path, 0o644)

    # Read back what landed on disk and re-check it, so a truncated
    # write or an encoding slip fails here rather than at the gate.
    with open(path, "r", encoding="utf-8", newline="") as handle:
        on_disk = handle.read()
    try:
        check_line(on_disk)
    except ValueError as exc:
        print("error: entry.txt on disk: %s" % exc, file=sys.stderr)
        return 1
    if on_disk != line:
        print("error: entry.txt on disk differs from the entry",
              file=sys.stderr)
        return 1
    # Byte length must match the character length encoded as UTF-8,
    # so a silent encoding change cannot slip past the gate.
    if len(on_disk.encode("utf-8")) != len(line.encode("utf-8")):
        print("error: entry.txt byte length does not match the entry",
              file=sys.stderr)
        return 1

    print("wrote %s (%d characters)" % (path, len(line)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
