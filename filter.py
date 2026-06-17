#!/usr/bin/env python3
import sys
import re
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Filter log lines by IMEI.",
    epilog=(
        "Examples:\n"
        "  %(prog)s 123456789012345\n"
        "  %(prog)s 123456789012345 tracker-server.log\n"
        "  %(prog)s 123456789012345 tracker-server.log output.log\n"
        "  %(prog)s 123456789012345 *"
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument("imei", nargs="?", help="IMEI to filter by")
parser.add_argument("input_file", nargs="?", default=None, help="Input log file, or * for all files in current directory (default: tracker-server.log)")
parser.add_argument("output_file", nargs="?", default=None, help="Output file (default: <imei>.log)")
args = parser.parse_args()

if not args.imei:
    try:
        args.imei = input("Enter IMEI to filter by: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        parser.print_usage()
        sys.exit(1)
    if not args.imei:
        parser.error("imei is required")

if not args.input_file:
    try:
        value = input("Enter input log file [tracker-server.log], or * for all files: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        parser.print_usage()
        sys.exit(1)
    args.input_file = value or "tracker-server.log"

if not args.output_file:
    default_out = f"{args.imei}.log"
    try:
        value = input(f"Enter output file [{default_out}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        parser.print_usage()
        sys.exit(1)
    args.output_file = value or default_out

imei = args.imei
output_file = Path(args.output_file)

if args.input_file == "*":
    input_files = sorted(
        p for p in Path(".").iterdir()
        if p.is_file()
        and not p.name.startswith(".")
        and p.resolve() != output_file.resolve()
        and p.name != Path(__file__).name
    )
    if not input_files:
        print("No files found in current directory.")
        sys.exit(1)
    print(f"Reading {len(input_files)} file(s): {', '.join(p.name for p in input_files)}")
else:
    input_files = [Path(args.input_file)]
    if not input_files[0].exists():
        print(f"Error: {input_files[0]} not found.")
        sys.exit(1)

regex = re.compile(r'^T?[0-9a-fA-F]{8}$')
sessions = set()

# First pass: collect all session IDs associated with the IMEI
for input_file in input_files:
    try:
        with input_file.open("r", encoding="utf-8") as f:
            for line in f:
                if imei in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        candidate = parts[3].strip("[:]")
                        if regex.match(candidate) and candidate not in sessions:
                            sessions.add(candidate)
                            print(f"Session found: {candidate} (in {input_file.name})")
    except UnicodeDecodeError:
        print(f"Skipping {input_file.name}: not a text file.")

if not sessions:
    print(f"No sessions found for IMEI {imei}.")
    sys.exit(0)

# Second pass: collect all lines belonging to any of those sessions
filtered_lines = []
for input_file in input_files:
    try:
        with input_file.open("r", encoding="utf-8") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 4:
                    candidate = parts[3].strip("[:]")
                    if candidate in sessions:
                        filtered_lines.append(line)
    except UnicodeDecodeError:
        pass

# Write to output file
with output_file.open("w", encoding="utf-8") as f:
    f.writelines(filtered_lines)

print(f"{len(filtered_lines)} line(s) written to {output_file}")
