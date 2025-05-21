import io
import json
import argparse
import re
from pathlib import Path
from contextlib import redirect_stdout
import torch
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
from tqdm import tqdm
import transformer_lens.utils as utils
from transformer_lens import HookedTransformer, HookedTransformerConfig
from transformers import AutoTokenizer
#
CKPT_ITERS = [460, 1000, 2140, 5000, 6420, 7440, 10000, 12000, 13700, 16200, 20000]
#CKPT_ITERS = [300, 450, 550, 1000, 1450, 2150, 5000, 5450, 6400, 7450, 10000, 12000, 13700, 15400, 16200, 20000]
TOKEN_SCALE = 491_520  # tokens trained per iteration
torch.set_grad_enabled(False)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
def load_model(ckpt_path: Path, device: str = "cuda"):
    """Load a TransformerLens checkpoint."""
    cfg = HookedTransformerConfig(
        n_layers=12,
        d_model=768,
        d_head=64,
        n_heads=12,
        d_mlp=768 * 4,
        d_vocab=50304,
        n_ctx=1024,
        act_fn="gelu",
        normalization_type="LNPre",
    )
    ckpt = torch.load(str(ckpt_path), map_location=device)
    model = HookedTransformer(cfg)
    model.load_state_dict(ckpt)
    model.set_tokenizer(tokenizer)
    return model.to(device).eval()
def extract_prompt_answer(raw: str):
    """Split the raw FOL string into prompt and target answer."""
    raw = raw.replace("<|endoftext|>", "").strip()
    before, after = raw.split("⇔", 1)
    return before.strip() + " ⇔", after.strip().split()[0]
def prompt_ranks(prompt: str, answer: str, model, top_k: int = 10):
    """Return the list of rank(s) assigned to the answer token(s)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        utils.test_prompt(prompt, answer, model, prepend_bos=True, prepend_space_to_answer=True, print_details=False, top_k=top_k)
    for line in buf.getvalue().splitlines():
        if "Ranks of the answer tokens" in line:
            return [int(n) for n in re.findall(r"\b(\d+)\b", line)]
    return []
def evaluate_file(split: str, jsonl_path: Path, model) -> list[int]:
    """Return the list of ranks for all examples in one JSONL split file."""
    ranks = []
    with jsonl_path.open() as fh:
        for line in tqdm(fh, desc=split, unit="ex"):
            ex = json.loads(line)
            prompt, answer = extract_prompt_answer(ex["raw_data"])
            ranks.extend(prompt_ranks(prompt, answer, model))
    return ranks
def summarize_top1(ranks: list[int], iteration: int, split: str) -> dict:
    """Return a row dict: iteration · split · top1_rate · ci95 · count."""
    n = len(ranks)
    if n:
        rate = sum(r == 0 for r in ranks) / n
        se = np.sqrt(rate * (1 - rate) / n)
        ci = 1.96 * se
    else:
        rate, ci = np.nan, np.nan
    return {"iteration": iteration, "split": split, "top1_rate": rate, "ci95": ci, "count": n}
def main():
    ap = argparse.ArgumentParser(description="Overall Top-1 accuracy vs tokens")
    ap.add_argument("--ckpt_dir",  type=Path, required=True, help="folder of ckpt_iter_*.pt")
    ap.add_argument("--trainfile", type=Path, required=True, help="train split .jsonl file")
    ap.add_argument("--testfile",  type=Path, required=True, help="test split .jsonl file")
    ap.add_argument("--outdir",    type=Path, default=Path("results"))
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for it in CKPT_ITERS:
        ckpt_path = args.ckpt_dir / f"ckpt_iter_{it}.pt"
        print(f"Loading checkpoint {ckpt_path.name}...")
        model = load_model(ckpt_path)
        train_ranks = evaluate_file("train", args.trainfile, model)
        test_ranks  = evaluate_file("test",  args.testfile,  model)
        rows.append(summarize_top1(train_ranks, it, "train"))
        rows.append(summarize_top1(test_ranks,  it, "test"))
    df = pd.DataFrame(rows)
    df.sort_values(["iteration", "split"], inplace=True)
    df["tokens"] = df["iteration"] * TOKEN_SCALE
    csv_path = args.outdir / "top1_overall.csv"
    df.to_csv(csv_path, index=False)
    print(f"Wrote CSV → {csv_path}")
    fig = px.line(df, x="tokens", y="top1_rate", color="split", markers=True, error_y="ci95", labels={"tokens": "Tokens seen", "top1_rate": "Top‑1 Accuracy", "split": "Split"})
    fig.update_layout(width=700, height=500)
    png_path = args.outdir / "top1_overall.png"
    pio.write_image(fig, str(png_path))
    print(f"Wrote plot → {png_path}")
if __name__ == "__main__":
    main()