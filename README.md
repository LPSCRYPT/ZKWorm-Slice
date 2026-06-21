# ZKWorm-Slice

Standalone public demo slice for the ZKWorm v7 one-tick brain circuit.

This repository contains two self-contained Noir circuits generated from the ZKWorm current-model v7 benchmark:

- `brain_v7_cook2019_full_hybrid_open_t1`: exposes the full public output vector.
- `brain_v7_cook2019_full_hybrid_poseidon_t1`: exposes only the Poseidon commitment.

Both circuits prove one tick of the documented Cook 2019 brain model with dynamic Randi slow modulation, the hybrid spike/refractory hook, generated synaptic gains, and WormAtlas motor-adapter outputs.

## Toolchain

These versions are intentionally specific. Other Nargo/BB versions can fail to compile/prove the generated circuits or produce incompatible artifacts.

```text
nargo 1.0.0-beta.19
bb 5.0.0-nightly.20260419
```

Reference binary hashes from the originating benchmark machine:

```text
nargo sha256: 3d01d542e86ef05cf28c3b7862f2941192c695b5067cc5caaf40e4f080eb0f4e
bb sha256:    d11fb1cba3928155c4c060c7723d06aeaece12196d127b21ad6b4a69d61e1569
```

The demo runner defaults to:

```text
~/.nargo/bin/nargo
~/.bb/bb
```

Override paths if needed:

```sh
NARGO_PATH=/path/to/nargo BB_PATH=/path/to/bb python3 scripts/run_v7_demo.py --variant both --prove
```

## Quick start

Compile and execute both variants without proving:

```sh
python3 scripts/run_v7_demo.py --variant both
```

Compile, execute, prove, and verify both variants:

```sh
python3 scripts/run_v7_demo.py --variant both --prove
```

Run only one mode:

```sh
python3 scripts/run_v7_demo.py --variant open --prove
python3 scripts/run_v7_demo.py --variant poseidon --prove
```

Artifacts and logs are written under `runs/`.

## Foundry verifier demo

Generate a Solidity verifier, deploy it, and execute proof-verification transactions with Foundry:

```sh
# Terminal 1
anvil --code-size-limit 1000000

# Terminal 2
export PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
python3 scripts/deploy_and_verify.py --variant poseidon --rpc-url http://127.0.0.1:8545
python3 scripts/deploy_and_verify.py --variant open --rpc-url http://127.0.0.1:8545
```

Base Sepolia usage is documented in `docs/foundry_deployment.md`.

## Expected canonical outputs

Canonical rest/zero-stimulus witness final hash for both modes:

```text
0x1776657d57959fdcdeda347473a0bb38272678bdedd23818ab601b078ee4433f
```

Expected public-output counts:

```text
open:     3143 fields
poseidon: 1 field
```

Reference proof/public-input binaries and manifests from the originating full repository are in `docs/`.

## Open-output public layout

```text
pub [Field; 3143]
[0]          final_state_hash
[1..302]     v[0..301]
[303..604]   n[0..301]
[605..906]   p[0..301]
[907..1208]  q[0..301]
[1209..1510] e[0..301]
[1511..1812] f[0..301]
[1813..2114] cai[0..301]
[2115..2416] randi_state signed-magnitude[0..301]
[2417..2718] syn_gain[0..301] scale=1000
[2719..3020] hybrid_refractory_out[0..301] ms*1000
[3021..3094] muscle[0..73] scale=1000
[3095..3142] quadrants[12][4] flattened segment-major, scale=1000
```

The Poseidon variant returns only `final_state_hash`.

## Model boundary

The circuits are generated artifacts, so this slice does not require the full Python model or the original connectome spreadsheets at runtime. The circuits encode the generated current-model constants directly.

Included model components:

- 302-neuron Cook 2019 connectome transition.
- 3,709 chemical edges and 2,199 directed gap-junction entries.
- Randi slow modulation with 796 source edges, 160 matched neurons, and signed-magnitude state encoding.
- Hybrid spike/refractory hook for `AVL`, `AWAL`, `AWAR`, `DVB` after neural state update and before motor output.
- WormAtlas motor adapter with 74 muscle landmarks, 357 motor targets, and 12x4 quadrant aggregation.

Known boundary: sigmoid/exponential dynamics are deterministic fixed-point approximations of the source Python floating-point model, not bit-for-bit Python-float emulation.

## Reference provenance

Originating repository commit for the generated v7 circuit metadata:

```text
d8454642be654ea3d6a2e8e18e4c788f4d86185f
```

The standalone slice was extracted from `LPSCRYPT/zkworm-working` after the v7 artifacts were committed there.
