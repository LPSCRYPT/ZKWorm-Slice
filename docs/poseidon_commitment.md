# cook2019_full_hybrid_poseidon_t1

One-tick full documented current-model circuit with compact Poseidon2 commitment over neural state, dynamic Randi state/gains, hybrid refractory state, and WormAtlas motor outputs.

## Source model

- Source commit: `d8454642be654ea3d6a2e8e18e4c788f4d86185f`
- Source hook: `brain/zkworm_neurons.py::_apply_hybrid_spikes`
- Source bundle: `brain/_current_model/`

## Circuit

- Package: `circuit/circuits/brain_cook2019_full_hybrid_poseidon_t1/`
- Generator: `circuit/tools/brain/generate_cook2019_full_hybrid_t1_circuits.py`
- Runner: `circuit/tools/brain/run_cook2019_full_hybrid_t1_circuit.py`
- Fixture: `circuit/contracts/test/fixtures/brain/cook2019_full_hybrid_poseidon_t1/`
- Logs: `circuit/contracts/test/fixtures/brain/cook2019_full_hybrid_poseidon_t1/logs/20260621T180725Z_worker_prove/`

## Hybrid hook

```text
hybrid names:              AVL, AWAL, AWAR, DVB
hybrid indices:            70, 72, 73, 111
refractory encoding:       u32 milliseconds * 1000
per-tick refractory decay: 500
AWA voltage threshold:     52000
AVL/DVB voltage threshold: 65000
AWA current threshold:     2
AVL/DVB current threshold: 20
AWA/AVL spike voltage:     95000
DVB spike voltage:         110000
Cai spike delta:           40000
Cai max:                   500000
AWA refractory reset:      220000
AVL/DVB refractory reset:  400000
```

## Public output layout

```text
pub Field final_state_hash
```

The commitment absorbs:

```text
v, n, p, q, e, f, cai,
randi_state,
syn_gain,
hybrid_refractory_out,
74 muscle activations,
48 quadrant activations
```

## Canonical run

```text
run_id: 20260621T180725Z_worker_prove
nargo check/compile/execute: passed
bb write_vk/prove/verify: passed
final_state_hash: 0x1776657d57959fdcdeda347473a0bb38272678bdedd23818ab601b078ee4433f
```

Peak RAM:

```text
nargo_compile: 463.89 MB
nargo_execute: 482.31 MB
bb_write_vk:   1022.27 MB
bb_prove:      1231.66 MB
bb_verify:     15.02 MB
```

Artifacts:

```text
proof:         10304 bytes
public_inputs: 32 bytes
```

## Boundary

This is the current most complete compact commitment benchmark. It proves the same constrained computation as `cook2019_full_hybrid_open_t1` while exposing only the final commitment. Sigmoid/exponential operations remain deterministic fixed-point approximations.
