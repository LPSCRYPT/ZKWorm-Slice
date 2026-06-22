#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BB = Path(os.environ.get("BB_PATH", str(Path.home() / ".bb/bb")))
VARIANTS = {
    "open": {
        "package": "brain_cook2019_full_hybrid_open_t1",
        "fixture": "circuits/brain_cook2019_full_hybrid_open_t1/target/proof_dir",
    },
    "poseidon": {
        "package": "brain_cook2019_full_hybrid_poseidon_t1",
        "fixture": "circuits/brain_cook2019_full_hybrid_poseidon_t1/target/proof_dir",
    },
    "open_t10": {
        "package": "brain_cook2019_full_hybrid_open_t10",
        "fixture": "circuits/brain_cook2019_full_hybrid_open_t10/target/proof_dir",
        "demo_variant": "open_t10",
    },
    "poseidon_t10": {
        "package": "brain_cook2019_full_hybrid_poseidon_t10",
        "fixture": "circuits/brain_cook2019_full_hybrid_poseidon_t10/target/proof_dir",
        "demo_variant": "poseidon_t10",
    },
}


def run(cmd: list[str], cwd: Path = ROOT, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\nCWD: {cwd}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc.stdout.strip()


def ensure_artifacts(variant: str) -> None:
    package = VARIANTS[variant]["package"]
    circuit = ROOT / "circuits" / package
    if not (circuit / "target" / "vk").exists() or not (circuit / "target/proof_dir/proof").exists():
        demo_variant = VARIANTS[variant].get("demo_variant", variant)
        cmd = ["python3", "scripts/run_demo.py", "--variant", demo_variant, "--prove", "--run-id", "deploy_artifacts"]
        run(cmd)


def prepare_foundry_project(variant: str) -> Path:
    ensure_artifacts(variant)
    package = VARIANTS[variant]["package"]
    work = ROOT / "generated" / f"foundry_{variant}"
    if work.exists():
        shutil.rmtree(work)
    (work / "src").mkdir(parents=True)
    (work / "foundry.toml").write_text(
        '[profile.default]\n'
        'src = "src"\n'
        'out = "out"\n'
        'libs = ["lib"]\n'
        'solc_version = "0.8.30"\n'
        'evm_version = "cancun"\n'
        'optimizer = true\n'
        'optimizer_runs = 1\n'
        'bytecode_hash = "none"\n'
    )
    run([
        str(BB),
        "write_solidity_verifier",
        "-k",
        str(ROOT / "circuits" / package / "target" / "vk"),
        "-o",
        str(work / "src" / "HonkVerifier.sol"),
        "-t",
        "evm",
    ])
    run(["forge", "build"], cwd=work)
    return work


def hex_bytes(path: Path) -> str:
    return "0x" + path.read_bytes().hex()


def public_inputs(path: Path) -> list[str]:
    data = path.read_bytes()
    if len(data) % 32 != 0:
        raise SystemExit(f"public input file length is not 32-byte aligned: {path} ({len(data)} bytes)")
    return ["0x" + data[i : i + 32].hex() for i in range(0, len(data), 32)]


def cast_array(values: list[str]) -> str:
    return "[" + ",".join(values) + "]"


def forge_create(work: Path, target: str, rpc_url: str, private_key: str, libraries: list[str] | None = None) -> dict:
    cmd = [
        "forge",
        "create",
        target,
        "--rpc-url",
        rpc_url,
        "--private-key",
        private_key,
        "--broadcast",
        "--json",
    ]
    if libraries:
        for library in libraries:
            cmd.extend(["--libraries", library])
    out = run(cmd, cwd=work)
    return json.loads(out[out.find("{") :])


def deploy(work: Path, rpc_url: str, private_key: str) -> str:
    # Barretenberg's generated verifier dynamically links ZKTranscriptLib.
    lib = forge_create(work, "src/HonkVerifier.sol:ZKTranscriptLib", rpc_url, private_key)
    lib_addr = lib["deployedTo"]
    verifier = forge_create(
        work,
        "src/HonkVerifier.sol:HonkVerifier",
        rpc_url,
        private_key,
        [f"src/HonkVerifier.sol:ZKTranscriptLib:{lib_addr}"],
    )
    return verifier["deployedTo"]


def verify_tx(variant: str, address: str, rpc_url: str, private_key: str) -> str:
    fixture = ROOT / VARIANTS[variant]["fixture"]
    proof = hex_bytes(fixture / "proof")
    inputs = public_inputs(fixture / "public_inputs")
    sig = "verify(bytes,bytes32[])(bool)"
    return run([
        "cast",
        "send",
        address,
        sig,
        proof,
        cast_array(inputs),
        "--rpc-url",
        rpc_url,
        "--private-key",
        private_key,
        "--json",
    ])


def call_verify(variant: str, address: str, rpc_url: str) -> str:
    fixture = ROOT / VARIANTS[variant]["fixture"]
    proof = hex_bytes(fixture / "proof")
    inputs = public_inputs(fixture / "public_inputs")
    sig = "verify(bytes,bytes32[])(bool)"
    return run([
        "cast",
        "call",
        address,
        sig,
        proof,
        cast_array(inputs),
        "--rpc-url",
        rpc_url,
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate, deploy, and exercise a Solidity verifier.")
    parser.add_argument("--variant", choices=sorted(VARIANTS), required=True)
    parser.add_argument("--rpc-url", default=os.environ.get("RPC_URL"))
    parser.add_argument("--private-key", default=os.environ.get("PRIVATE_KEY"))
    parser.add_argument("--address", help="Use an existing verifier address instead of deploying.")
    args = parser.parse_args()
    if not args.rpc_url:
        raise SystemExit("missing --rpc-url or RPC_URL")
    if not args.private_key and not args.address:
        raise SystemExit("missing --private-key or PRIVATE_KEY for deployment")

    work = prepare_foundry_project(args.variant)
    address = args.address or deploy(work, args.rpc_url, args.private_key)
    static_result = call_verify(args.variant, address, args.rpc_url)
    tx_result = verify_tx(args.variant, address, args.rpc_url, args.private_key) if args.private_key else None
    result = {"variant": args.variant, "address": address, "generated_project": str(work.relative_to(ROOT)), "static_call": static_result, "transaction": json.loads(tx_result) if tx_result else None}
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
