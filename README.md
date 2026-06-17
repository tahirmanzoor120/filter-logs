# Filter Logs

A small Python utility for extracting all log lines related to a device IMEI.

The script scans one log file, or all files in the current directory, finds session IDs associated with the provided IMEI, then writes every line for those sessions to an output log file.

## Requirements

- Python 3

No third-party Python packages are required.

## Usage

Run the script with an IMEI:

```bash
./filter.py 123456789012345
```

If no input or output file is provided, the script prompts for them interactively. The default input file is `tracker-server.log`, and the default output file is `<imei>.log`.

Filter a specific file:

```bash
./filter.py 123456789012345 tracker-server.log
```

Filter a specific file and choose the output file:

```bash
./filter.py 123456789012345 tracker-server.log output.log
```

Scan all non-hidden files in the current directory:

```bash
./filter.py 123456789012345 '*'
```

Quote `*` so your shell does not expand it before Python receives the argument.

## How It Works

1. The script searches the input log lines for the IMEI.
2. For matching lines, it reads the session ID from the fourth whitespace-separated field.
3. It scans the logs again and collects every line whose session ID matches one of the discovered sessions.
4. It writes the collected lines to the output file.

Session IDs are expected to look like 8 hexadecimal characters, optionally prefixed with `T`.
