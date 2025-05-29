# inkr 🖋️ — Invisible Watermarking for Text

**inkr** is a lightweight Python CLI tool for embedding invisible watermarks into text using zero-width characters. Inspired by ink on paper, the watermark is imperceptible but traceable, helping verify the source of distributed content.

## ✨ Features

- Deterministic watermarking based on user ID and seed
- Zero-width character encoding (invisible in most editors)
- Embed watermark for a single or multiple users
- Detect embedded watermark from a list of candidates

## 🔧 Installation

```bash
git clone https://github.com/yourusername/inkr.git
cd inkr
pip install -r requirements.txt  # Only if you add any requirements
```

This project uses only the Python standard library.

# 🚀 Usage

Run `python inkr.py --help` to see all available commands.

### 📥 Embed a watermark

```bash
python inkr.py embed --user USER123 -i input.txt -o output.txt
```

#### Embed Options

| Option            | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `--user`          | Embed a watermark for a single user ID                                      |
| `--user-list`     | Path to a file containing multiple user IDs (one per line)                  |
| `-i`, `--input`   | Input file path (default: stdin)                                             |
| `-o`, `--output`  | Output file path or output directory (used with `--multi-out`)               |
| `--multi-out`     | If set, writes one output file per user in the specified directory           |
| `--seed`          | Optional seed for watermarking (deterministic positions, default: `default_seed`) |

> ⚠️ You must specify either `--user` or `--user-list`.

### 📤 Detect a watermark

```bash
python inkr.py detect --user-list users.txt -i watermarked.txt
```

#### Detect Options

| Option            | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `--user`          | Check for a watermark matching a single user ID                             |
| `--user-list`     | Path to a file with candidate user IDs (one per line)                       |
| `-i`, `--input`   | Watermarked text input file (default: stdin)                                |
| `--seed`          | Seed used during embedding (must match the one used in `embed`)             |

> ⚠️ You must specify either `--user` or `--user-list`.

## 🧪 Example

```bash
# Embed for a single user
python inkr.py embed --user alice -i original.txt -o watermarked.txt

# Detect the embedded watermark
python inkr.py detect --user alice -i watermarked.txt
```

## 🔍 Help Commands

For more detailed options and usage:

```bash
python inkr.py embed --help
python inkr.py detect --help
```

## 🔐 How It Works

- The user ID is hashed to produce a 64-bit binary string.
- Each bit is embedded at a pseudo-random position as either:
  - `​` (zero-width space) for `1`
  - `‌` (zero-width non-joiner) for `0`
- Embed positions are generated using a deterministic random seed.

## 📄 License

MIT License