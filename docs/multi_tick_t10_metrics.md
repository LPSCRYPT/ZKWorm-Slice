# Ten-tick circuit metrics

## Summary

The ten-tick circuits prove an internally continuous, unrolled brain-slice rollout. Each tick consumes the exact state produced by the previous tick, carrying:

- 302-neuron `v`, `n`, `p`, `q`, `e`, `f`, `cai` state arrays.
- 302-slot Randi slow-modulator state.
- 302-slot hybrid refractory state.
- A private `i_ext[t][302]` current schedule.

The canonical benchmark uses all-zero external current for all ten ticks. The output commitment is unchanged from the one-tick rest benchmark because the all-rest/all-zero-current state is a fixed point under this integer circuit approximation.

Input-data caveat: these proof inputs are benchmark inputs, not embodied sensory observations. They verify circuit correctness, output layout, and resource use at a deterministic rest/zero-current fixed point. They do not claim chemotaxis, learning, or spontaneous behaviour. The source Python activity-trace and embodied simulations use scripted or environment-generated currents separately from this benchmark witness.

```text
0x1776657d57959fdcdeda347473a0bb38272678bdedd23818ab601b078ee4433f
```

## Feasibility note

The full activity-trace diagnostic in `brain/ACTIVITY_TRACE_HANDOFF.md` is 12,000 main timesteps per probe, with 60,000 neural substeps per probe. That is not currently practical as a single unrolled Noir circuit. The implemented ten-tick circuits are the tractable continuity proof target.

Local macOS compilation OOMed. The successful run used the existing Vast instance `zkworm-brain-t100`, an x86_64 Ubuntu host with about 251 GiB RAM.

## Toolchain

```text
nargo 1.0.0-beta.19
bb 5.0.0-nightly.20260419
```

Linux builder binary hashes:

```text
nargo sha256: a6d9646d3cbbab0601a190d86ad939fbd1bd091dc5baa52d1985b0ee9a4f938b
bb sha256:    92dd0928b7c9064369172341c18334c916ff39d403301ee44e15b429ef221862
```

## Metrics

Run id: `vast_t10_20260619_b`

| Variant | Public outputs | Proof size | Public-input size | nargo compile peak RAM / time | nargo execute peak RAM / time | bb write_vk peak RAM / time | bb prove peak RAM / time | bb verify peak RAM / time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `brain_cook2019_full_hybrid_poseidon_t10` | 1 field | 11,456 B | 32 B | 46,900.94 MB / 1015.83 s | 3340.82 MB / 25.19 s | 8771.15 MB / 28.47 s | 10,457.50 MB / 43.02 s | 9.27 MB / 0.018 s |
| `brain_cook2019_full_hybrid_open_t10` | 3143 fields | 11,456 B | 100,576 B | 49,973.37 MB / 1023.44 s | 3344.19 MB / 25.43 s | 8857.45 MB / 37.26 s | 10,489.85 MB / 42.81 s | 10.02 MB / 0.020 s |

## Artifacts

- Poseidon manifest: `runs/cook2019_full_hybrid_poseidon_t10/vast_t10_20260619_b/manifest.json`
- Open manifest: `runs/cook2019_full_hybrid_open_t10/vast_t10_20260619_b/manifest.json`
- Poseidon circuit: `circuits/brain_cook2019_full_hybrid_poseidon_t10/src/main.nr`
- Open circuit: `circuits/brain_cook2019_full_hybrid_open_t10/src/main.nr`


## Fidelity roadmap

The t10 proof is a brain-slice continuity benchmark. Increasing experiment fidelity means progressively circuitizing the existing source-model brain -> body -> environment -> brain loop: motor outputs drive the body model, body pose samples arena/source fields and wall contacts, sensory/proprioceptive transduction produces the next brain input, and the resulting state is committed on-chain. The long-term target is a standalone on-chain C. elegans-like lifeform whose world line is a sequence of verified brain/body/environment transitions rather than isolated neural ticks.