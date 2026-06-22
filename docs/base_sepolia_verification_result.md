# Base Sepolia verification result

Date: 2026-06-21

Network:

```text
RPC: https://sepolia.base.org
Chain: Base Sepolia
Sender: 0x1b43AFe43afC74bF9D0EBd764787eFD7CCcC2B6F
```

The deployment script generated a Barretenberg Solidity verifier per variant, deployed the dynamically linked `ZKTranscriptLib`, deployed `HonkVerifier`, checked the proof with `cast call`, and sent an actual verification transaction. The ten-tick verifiers are separate contracts from the one-tick verifiers because the proving keys and circuit relations differ.

## One-tick Poseidon mode

```text
verifier:       0x4C8dDe9847DaB578175514584CFe32E5DC55Cec9
static_call:    true
tx status:      0x1
tx hash:        0x09026f39dd7027c10e62e7b420994b97a9fde66f8c8262cdfbaec14d751c9f03
block number:   0x2926ee8
gas used:       0x40a3a6 (4,236,198)
```

## One-tick open-output mode

```text
verifier:       0x0E5e9A3FEF33a807C56F7E01f8edA205e853f394
static_call:    true
tx status:      0x1
tx hash:        0x4c724719d9ef44b0f69c6fa7db965d42f4bf55b33248c9348a9aec53c906d611
block number:   0x2926ef2
gas used:       0x8ca80f (9,218,063)
```

## Ten-tick Poseidon mode

```text
verifier:       0x7a7AACF9f9D748C5C64a267338D011bB57FEA055
static_call:    true
tx status:      0x1
tx hash:        0x6c9cb32166d07f519732059464e6ea76b9854f2812332621a63579c3f1e344a1
block number:   0x292d389
gas used:       0x453bbc (4,537,276)
```

## Ten-tick open-output mode

```text
verifier:       0x6c806386c6580937895aB209F0e610AED0aCc332
static_call:    true
tx status:      0x1
tx hash:        0xabc21ca8db947231a5fee3cb59f0d1f8f89b8c6c032d37caf9f10e0ddfe5ae1e
block number:   0x292d396
gas used:       0x91578e (9,525,134)
```

Both on-chain POC transactions verified the canonical proof generated from the rest/zero-stimulus witness with final hash:

```text
0x1776657d57959fdcdeda347473a0bb38272678bdedd23818ab601b078ee4433f
```
