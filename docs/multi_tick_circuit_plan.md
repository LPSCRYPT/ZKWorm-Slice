# Multi-tick circuit plan

## Source diagnostic being mirrored

`brain/ACTIVITY_TRACE_HANDOFF.md` in the source repository documents the all-neuron activity-trace diagnostic:

- Four sensory probes: salt/ASE, odor/AWA-AWC, gentle touch, harsh touch.
- Default duration: 60 seconds.
- Main timestep: 5 ms.
- Neural substeps per main timestep: 5.
- Per probe: 12,000 main timesteps and 60,000 neural integration substeps.
- Input current is scripted, not loaded from an external environment dataset.
- Each timestep applies: stimulus injection -> Randi slow modulation from the current voltage state -> synaptic gain update -> neural step(s) -> trace sampling.

That full 60-second figure is a Python model-validity diagnostic, not a proof artifact. Proving all default trace steps as one unrolled SNARK is not practical in this repository's current Noir/BB setup: it would multiply the one-tick circuit by 12,000 per probe before accounting for the 5 neural substeps used by the Python diagnostic.

## Feasible circuit shape

The feasible starting point is a fixed-width unrolled batched circuit over a small number of ticks. This proves continuity inside one proof: the state produced by tick `t` is the exact state consumed by tick `t+1` because the next iteration uses the previous iteration's local variables directly, not a caller-provided copy.

Per tick, the circuit carries the same recurrent/reservoir state as the one-tick circuit:

- `v`, `n`, `p`, `q`, `e`, `f`, `cai` for all 302 neurons.
- Randi slow-modulator state for all 302 neuron slots.
- Hybrid spike/refractory state for all 302 neuron slots.
- Per-tick external current vector `i_ext[t][302]` as private witness input.

Each tick computes:

1. `randi_update(v, randi_state)`.
2. `neural_step(v, n, p, q, e, f, cai, i_ext[t], syn_gain)`.
3. `apply_hybrid_spikes(...)`.
4. `motor_outputs(v)`.
5. A per-tick Poseidon commitment for auditability.

The final tick output is then exposed either as:

- Poseidon mode: one final public commitment.
- Open mode: final public commitment plus final full public output vector.

## Implemented first batch target

This repo implements a 10-tick batch for both public-output schemes:

- `brain_cook2019_full_hybrid_poseidon_t10`
- `brain_cook2019_full_hybrid_open_t10`

The 10-tick circuit is intentionally not the 60-second diagnostic. It is a tractable continuity proof and benchmark target that can later be scaled to 100 ticks if resources allow, or replaced by recursive composition when proof aggregation becomes the priority.

## Expected scaling

For a same-shape unrolled circuit, constraints and proving memory are expected to grow approximately linearly with tick count. Public input size remains one field for Poseidon mode and 3143 fields for the final-state open mode. If all intermediate traces are publicly exposed, public input size also grows linearly and becomes unsuitable for on-chain verification.
