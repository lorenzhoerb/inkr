from typing import List, Tuple, Optional
import random
import hashlib
import click
import math
import os

# Constants
NUM_WATERMARK_BITS = 64
EMBED_CHAR_TRUE = '\u200B'
EMBED_CHAR_FALSE = '\u200C'
DEFAULT_SEED= 'default_seed'

def get_max_rand(num_bits: int, spacing_factor=4) -> int:
    return num_bits * spacing_factor # over-provisioning to reduces collision risk

def deterministic_seed(seed: str, user_id: str) -> int:
    """Creates a deterministic integer seed based on input strings."""
    combined = (seed + user_id).encode("utf-8")
    return int(hashlib.sha256(combined).hexdigest(), 16)

def hash_to_bits(user_id: str) -> str:
    """Converts the SHA-256 hash of the user_id to a binary string (first byte only)."""
    n_bytes = math.ceil(NUM_WATERMARK_BITS / 8)
    digest = hashlib.sha256(user_id.encode('utf-8')).digest()[0:n_bytes]
    return ''.join(f'{byte:08b}' for byte in digest)

def embed_watermark_bit(text: str, bit: str, position: int) -> str:
    """Embeds a single bit into the text at the given position."""
    embed_char = EMBED_CHAR_TRUE if bit == '1' else EMBED_CHAR_FALSE
    return text[:position] + embed_char + text[position:]

def extract_watermark_bit(text: str, position: int) -> str:
    """Extracts a watermark bit from the given position in the text."""
    return '1' if text[position] == EMBED_CHAR_TRUE else '0'

def generate_embed_positions(user_id: str, seed: str, num_bits: int, spacing_factor=4) -> List[Tuple[int, int]]:
    """Generates non-colliding embed positions for watermark bits."""
    rng = random.Random(deterministic_seed(seed, user_id))
    max_rand = get_max_rand(num_bits, spacing_factor)
    positions = sorted(
        [(i, rng.randint(1, max_rand)) for i in range(num_bits)],
        key=lambda x: x[1],
    )

    # Resolve collisions by shifting forward
    for i in range(len(positions) - 1):
        if positions[i][1] >= positions[i + 1][1]:
            positions[i + 1] = (positions[i + 1][0], positions[i][1] + 1)
    return positions

def embed_watermark(text: str, user_id: str, seed: str) -> str:
    """Embeds a watermark derived from user_id into the given text."""
    watermark_bits = hash_to_bits(user_id)
    positions = generate_embed_positions(user_id, seed, len(watermark_bits))

    for bit_index, position in positions:
        text = embed_watermark_bit(text, watermark_bits[bit_index], position)
    return text

def detect_watermark(text: str, seed: str, candidate_ids: List[str]) -> Optional[str]:
    """Tries to detect and match an embedded watermark against a list of candidate user IDs."""
    for candidate_id in candidate_ids:
        expected_bits = hash_to_bits(candidate_id)
        positions = generate_embed_positions(candidate_id, seed, len(expected_bits))

        extracted_bits = [''] * len(expected_bits)
        for bit_index, position in positions:
            extracted_bits[bit_index] = extract_watermark_bit(text, position)

        if ''.join(extracted_bits) == expected_bits:
            return candidate_id  # Match found
    return None

@click.group()
def cli():
    """Watermark CLI tool for embedding and detecting binary watermarks."""
    pass

@cli.command()
@click.option("--user", type=str, help="Single user ID.")
@click.option("--user-list", type=click.File('r'), help="File with user IDs (one per line).")
@click.option("-i", "--input", type=click.File('r'), default="-", help="Input text (default: stdin).")
@click.option("-o", "--output", type=str, help="Output file path OR directory (if --multi-out is used).")
@click.option("--multi-out", is_flag=True, help="Write separate files per user into --output directory.")
@click.option("--seed", type=str, default=DEFAULT_SEED, help="Seed for deterministic embedding.")
def embed(user, user_list, input, output, multi_out, seed):
    """Embed watermark(s) into input text for one or more users."""
    if seed == DEFAULT_SEED:
        click.secho("⚠️  Warning: Using default seed. Use --seed to customize watermarking.", fg="yellow", err=True)

    text = input.read()

    # Collect user IDs
    users = []
    if user:
        users = [user]
    elif user_list:
        users = [line.strip() for line in user_list if line.strip()]
    else:
        raise click.UsageError("Please provide --user or --user-list.")

    if multi_out:
        if not output:
            raise click.UsageError("Please provide --output directory when using --multi-out.")
        os.makedirs(output, exist_ok=True)

        for uid in users:
            marked = embed_watermark(text, uid, seed)
            out_path = os.path.join(output, f"{uid}.txt")
            with open(out_path, "w") as f:
                f.write(marked)
    else:
        result = ""
        for uid in users:
            marked = embed_watermark(text, uid, seed)
            result += f"----- {uid} -----\n{marked}\n"

        if output:
            if os.path.isdir(output):
                # Use first user ID for single file output inside directory
                target_file = os.path.join(output, "watermarked.txt")
            else:
                target_file = output

            with open(target_file, "w") as out_file:
                out_file.write(result)
        else:
            click.echo(result)


@cli.command()
@click.option("--user", type=str, help="User ID to check for.")
@click.option("--user-list", type=click.File('r'), help="File with candidate user IDs.")
@click.option("-i", "--input", type=click.File('r'), default="-", help="Watermarked text input (default: stdin).")
@click.option("--seed", type=str, default=DEFAULT_SEED, help="Seed used during embedding.")
def detect(user, user_list, input, seed):
    """Detect watermark in input text."""
    text = input.read()

    # Collect candidate IDs
    candidates = []
    if user:
        candidates = [user]
    elif user_list:
        candidates = [line.strip() for line in user_list if line.strip()]
    else:
        raise click.UsageError("Please provide --user or --user-list.")

    result = detect_watermark(text, seed, candidates)
    if result:
        click.secho(f"✅ Detected user ID: {result}", fg="green")
    else:
        click.secho("❌ No watermark match found.", fg="red")

if __name__ == "__main__":
    cli()
