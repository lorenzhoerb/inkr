# Fingerprint Embedding — Examples & Evaluation

This section documents how the CLI tool was used to embed and detect invisible fingerprints in textual messages, and how various scenarios were evaluated for robustness and correctness.

 ## Example Input

We created spy-themed plaintext examples to simulate real-world use cases such as secure internal emails or intelligence memos. These provide sufficient text length and realistic formatting.

## Files & Overview

| File/Folder         | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `example.txt`       | A sample secret message to be fingerprinted                                 |
| `uids.txt`          | Contains the user ID to embed: `agent43@agency.gov`                         |
| `marked.txt`        | The output after fingerprinting `example.txt` with the seed `secret`        |
| `scenarios/`        | Folder containing scenario-specific versions of the fingerprinted message   |


## Embedding Fingerprint

To embed a fingerprint for all user IDs in `uids.txt`:

```bash
python python ../inkr.py embed --seed=secret --user-list=uids.txt -i example.txt -o marked.txt
```

## Detecting Fingerprint

To detect the fingerprint in any scenario-specific file:

```bash
python ../inkr.py detect --seed=secret --user-list=uids.txt -i scenarios/[fingerprinted text input]
```

```bash
python ../inkr.py detect --seed=secret --user-list=uids.txt -i scenarios/apple-mail.txt
```

## Results

| Scenario                  | Result      | Notes                                                                 |
|---------------------------|-------------|-----------------------------------------------------------------------|
| `apple-mail.txt`          | ✅ Preserved | Characters survive the round-trip                                     |
| `docx-to-pdf.txt`         | ❌ Lost      | PDF export stripped invisible characters                              |
| `gmail.txt`               | ❌ Fails     | Character shifts break detection                                      |
| `google-docs-copy.txt`    | ✅ Preserved | Copy-paste from Google Docs preserves characters                       |
| `google-docs-pdf.txt`     | ✅ Preserved | Export from Google Docs keeps invisible characters                     |
| `ms-word-copy.txt`        | ❌ Lost      | MS Word removes invisible Unicode characters                          |
| `plain-copy-editor.txt`   | ✅ Preserved | Most plaintext editors preserve the watermark                         |
| `plain-copy-intellij.txt` | ✅ Preserved | IntelliJ copy-paste works as expected                                 |
| `whats-app.txt`           | ⚠️ Partial   | First hidden character is removed — workaround: start at position 1   |