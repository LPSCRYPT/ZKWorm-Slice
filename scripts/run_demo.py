#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NARGO = Path(os.environ.get("NARGO_PATH", str(Path.home() / ".nargo/bin/nargo")))
BB = Path(os.environ.get("BB_PATH", str(Path.home() / ".bb/bb")))
N = 302
V0 = 18000
CA0 = 5000
G = 1000
VARS = {
    "open": ("brain_cook2019_full_hybrid_open_t1", "cook2019_full_hybrid_open_t1"),
    "poseidon": ("brain_cook2019_full_hybrid_poseidon_t1", "cook2019_full_hybrid_poseidon_t1"),
}


def pb(v: int, vh: int, kw: int) -> int:
    width = 2 * kw
    lo = vh - width if vh >= width else 0
    hi = vh + width
    if v >= hi:
        return G
    if v <= lo:
        return 0
    return (v - lo) * G // (hi - lo)


def pbi(v: int, vh: int, kw: int) -> int:
    return G - pb(v, vh, kw)


def arr(name: str, xs: list[int]) -> str:
    return f"{name} = [" + ", ".join(map(str, xs)) + "]"


def write_prover(circuit_dir: Path) -> None:
    n = [pb(V0, 109870, 15850)] * N
    p = [pb(V0, 81950, 7430)] * N
    q = [pbi(V0, 74350, 9970)] * N
    e = [pb(V0, 86640, 6750)] * N
    f = [pbi(V0, 115180, 5030)] * N
    lines = [
        arr("v_init", [V0] * N),
        arr("n_init", n),
        arr("p_init", p),
        arr("q_init", q),
        arr("e_init", e),
        arr("f_init", f),
        arr("cai_init", [CA0] * N),
        arr("randi_state_init", [0] * N),
        arr("hybrid_refractory_init", [0] * N),
        "i_ext = [",
        "  [" + ", ".join(["0"] * N) + "]",
        "]",
        "",
    ]
    (circuit_dir / "Prover.toml").write_text("\n".join(lines))


def time_metrics(stderr: str) -> dict[str, int | float]:
    data: dict[str, int | float] = {}
    for key, pattern in {
        "max_rss_bytes": r"(\d+)\s+maximum resident set size",
        "minor_faults": r"(\d+)\s+page reclaims",
        "page_faults": r"(\d+)\s+page faults",
    }.items():
        match = re.search(pattern, stderr)
        if match:
            data[key] = int(match.group(1))
    if "max_rss_bytes" in data:
        data["max_rss_mb"] = round(int(data["max_rss_bytes"]) / 1024 / 1024, 2)
    return data


def run(label: str, cmd: list[Path | str], cwd: Path, run_dir: Path, timeout: int) -> dict:
    start = time.time()
    proc = subprocess.run(
        ["/usr/bin/time", "-l"] + [str(x) for x in cmd],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = time.time() - start
    (run_dir / f"{label}.stdout.log").write_text(proc.stdout)
    (run_dir / f"{label}.stderr.log").write_text(proc.stderr)
    record = {
        "label": label,
        "command": " ".join(shlex.quote(str(x)) for x in cmd),
        "cwd": str(cwd.relative_to(ROOT)),
        "exit_code": proc.returncode,
        "wall_seconds": round(elapsed, 3),
        "time_l": time_metrics(proc.stderr),
        "stdout_log": str((run_dir / f"{label}.stdout.log").relative_to(ROOT)),
        "stderr_log": str((run_dir / f"{label}.stderr.log").relative_to(ROOT)),
    }
    if proc.returncode:
        record["stdout_tail"] = proc.stdout[-2000:]
        record["stderr_tail"] = proc.stderr[-4000:]
    return record


def version(path: Path) -> str:
    return subprocess.check_output([str(path), "--version"], text=True).strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_outputs(run_dir: Path) -> list[str]:
    text = (run_dir / "nargo_execute.stdout.log").read_text()
    idx = text.find("Circuit output:")
    return [] if idx < 0 else re.findall(r"0x[0-9a-fA-F]+|\b\d+\b", text[idx:])


def artifact_sizes(circuit_dir: Path, package: str) -> dict[str, int]:
    paths = {
        "compiled_circuit_json": circuit_dir / "target" / f"{package}.json",
        "witness_gz": circuit_dir / "target" / f"{package}.gz",
        "verification_key": circuit_dir / "target" / "vk",
        "proof": circuit_dir / "target/proof_dir/proof",
        "public_inputs": circuit_dir / "target/proof_dir/public_inputs",
    }
    return {key: value.stat().st_size for key, value in paths.items() if value.exists()}


def run_one(variant: str, prove: bool, run_id: str | None) -> dict:
    package, brain_version = VARS[variant]
    circuit_dir = ROOT / "circuits" / package
    run_dir = ROOT / "runs" / brain_version / (run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    run_dir.mkdir(parents=True, exist_ok=True)
    write_prover(circuit_dir)

    records = [run("nargo_check", [NARGO, "check"], circuit_dir, run_dir, 900)]
    if records[-1]["exit_code"] == 0:
        records.append(run("nargo_compile", [NARGO, "compile"], circuit_dir, run_dir, 3600))
    if records[-1]["exit_code"] == 0:
        records.append(run("nargo_execute", [NARGO, "execute"], circuit_dir, run_dir, 3600))
    pubs = public_outputs(run_dir) if records[-1]["exit_code"] == 0 else []

    if prove and records[-1]["exit_code"] == 0:
        target = circuit_dir / "target"
        records.append(run("bb_write_vk", [BB, "write_vk", "-b", target / f"{package}.json", "-o", target, "--scheme", "ultra_honk", "--oracle_hash", "keccak"], circuit_dir, run_dir, 2400))
        if records[-1]["exit_code"] == 0:
            (target / "proof_dir").mkdir(exist_ok=True)
            records.append(run("bb_prove", [BB, "prove", "-b", target / f"{package}.json", "-w", target / f"{package}.gz", "-o", target / "proof_dir", "-k", target / "vk", "--scheme", "ultra_honk", "--oracle_hash", "keccak"], circuit_dir, run_dir, 10800))
        if records[-1]["exit_code"] == 0:
            records.append(run("bb_verify", [BB, "verify", "-k", target / "vk", "-p", target / "proof_dir/proof", "-i", target / "proof_dir/public_inputs", "--scheme", "ultra_honk", "--oracle_hash", "keccak"], circuit_dir, run_dir, 2400))

    source = json.loads((circuit_dir / "MODEL_SOURCE.json").read_text())
    manifest = {
        "schema_version": 1,
        "brain_version": brain_version,
        "run_id": run_dir.name,
        "circuit_package": package,
        "variant": variant,
        "proof_statement": f"Cook 2019 one-tick full documented current model with dynamic Randi modulation, hybrid calcium-spike/refractory hook, and motor outputs, {variant} public output scheme",
        "source_reference": source,
        "toolchain": {
            "nargo_version": version(NARGO),
            "bb_version": version(BB) if prove else None,
            "nargo_sha256": sha(NARGO),
            "bb_sha256": sha(BB) if prove else None,
        },
        "witness": {
            "stimulus": "zero",
            "ticks": 1,
            "state_len": N,
            "randi_state_init": "all signed-magnitude zero",
            "hybrid_refractory_init": "all zero, encoded ms*1000",
            "i_ext": "all zero; nonzero thresholds use v6 integer pA-compatible units",
            "public_output_fields": source["public_output_count"],
        },
        "artifacts": {
            "circuit": f"circuits/{package}/src/main.nr",
            "model_source": f"circuits/{package}/MODEL_SOURCE.json",
            "prover_toml": f"circuits/{package}/Prover.toml",
            "logs": str(run_dir.relative_to(ROOT)),
        },
        "public_outputs": {
            "count": len(pubs),
            "final_state_hash": pubs[0] if pubs else None,
            "sample": pubs[:16],
        },
        "artifact_sizes_bytes": artifact_sizes(circuit_dir, package),
        "records": records,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return {
        "manifest": str((run_dir / "manifest.json").relative_to(ROOT)),
        "run_dir": str(run_dir.relative_to(ROOT)),
        "last_exit": records[-1]["exit_code"],
        "public_output_count": len(pubs),
        "final_state_hash": pubs[0] if pubs else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the ZKWorm one-tick demo in open-output and/or Poseidon commitment mode.")
    parser.add_argument("--variant", choices=["open", "poseidon", "both"], default="both")
    parser.add_argument("--prove", action="store_true", help="Also run bb write_vk/prove/verify after Nargo execution.")
    parser.add_argument("--run-id", help="Optional deterministic run directory name.")
    args = parser.parse_args()
    variants = ["open", "poseidon"] if args.variant == "both" else [args.variant]
    results = [run_one(variant, args.prove, args.run_id) for variant in variants]
    print(json.dumps(results, indent=2))
    return 0 if all(result["last_exit"] == 0 for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
