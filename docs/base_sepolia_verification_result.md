# Base Sepolia verification result

Date: 2026-06-21

Network:

```text
RPC: https://sepolia.base.org
Chain: Base Sepolia
Sender: 0x1b43AFe43afC74bF9D0EBd764787eFD7CCcC2B6F
```

The deployment script generated a Barretenberg Solidity verifier per variant, deployed the dynamically linked `ZKTranscriptLib`, deployed `HonkVerifier`, checked the proof with `cast call`, and sent an actual verification transaction.

## Poseidon mode

```text
verifier:       0x4C8dDe9847DaB578175514584CFe32E5DC55Cec9
static_call:    true
tx status:      0x1
tx hash:        0x09026f39dd7027c10e62e7b420994b97a9fde66f8c8262cdfbaec14d751c9f03
block number:   0x2926ee8
gas used:       0x40a3a6 (4,236,198)
```

## Open-output mode

```text
verifier:       0x0E5e9A3FEF33a807C56F7E01f8edA205e853f394
static_call:    true
tx status:      0x1
tx hash:        0x4c724719d9ef44b0f69c6fa7db965d42f4bf55b33248c9348a9aec53c906d611
block number:   0x2926ef2
gas used:       0x8ca80f (9,218,063)
```

Both on-chain POC transactions verified the canonical v7 proof generated from the rest/zero-stimulus witness with final hash:

```text
0x1776657d57959fdcdeda347473a0bb38272678bdedd23818ab601b078ee4433f
```
