# v7_cook2019_full_hybrid_open_t1

One-tick full documented current-model circuit with dynamic Randi slow modulation, hybrid calcium-spike/refractory hook, and WormAtlas motor outputs exposed publicly.

## Source model

- Source commit: `d8454642be654ea3d6a2e8e18e4c788f4d86185f`
- Source hook: `brain/zkworm_neurons.py::_apply_hybrid_spikes`
- Source bundle: `brain/_current_model/`

## Circuit

- Package: `circuit/circuits/brain_v7_cook2019_full_hybrid_open_t1/`
- Generator: `circuit/tools/brain/generate_cook2019_full_hybrid_t1_circuits.py`
- Runner: `circuit/tools/brain/run_cook2019_full_hybrid_t1_circuit.py`
- Fixture: `circuit/contracts/test/fixtures/brain/v7_cook2019_full_hybrid_open_t1/`
- Logs: `circuit/contracts/test/fixtures/brain/v7_cook2019_full_hybrid_open_t1/logs/20260621T180725Z_worker_prove/`

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

The hook runs after the neural step and before motor outputs, so motor readout consumes post-hybrid voltage.

## Public output layout

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

The commitment absorbs neural state, Randi state, generated synaptic gains, hybrid refractory state, 74 muscle outputs, and 48 quadrant outputs.

## Canonical run

```text
run_id: 20260621T180725Z_worker_prove
nargo check/compile/execute: passed
bb write_vk/prove/verify: passed
final_state_hash: 0x1776657d57959fdcdeda347473a0bb38272678bdedd23818ab601b078ee4433f
```

Peak RAM:

```text
nargo_compile: 433.08 MB
nargo_execute: 511.86 MB
bb_write_vk:   973.58 MB
bb_prove:      1267.81 MB
bb_verify:     16.55 MB
```

Artifacts:

```text
proof:         10304 bytes
public_inputs: 100576 bytes
```

## Boundary

This is the current most complete open-output benchmark. It includes Cook 2019 neural dynamics, dynamic Randi modulation, generated synaptic gains, hybrid refractory state update, and WormAtlas motor outputs. Sigmoid/exponential operations remain deterministic fixed-point approximations.
