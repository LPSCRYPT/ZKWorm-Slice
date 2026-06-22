# Localhost verification result

Date: 2026-06-21

Environment:

```text
forge 1.5.1-Homebrew
anvil 1.5.1-Homebrew
cast 1.5.1-Homebrew
nargo 1.0.0-beta.19
bb 5.0.0-nightly.20260419
```

Anvil was run with an expanded code-size limit for the generated Barretenberg verifier:

```sh
anvil --host 127.0.0.1 --port 8545 --code-size-limit 1000000
```

## Poseidon mode

Command:

```sh
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
  python3 scripts/deploy_and_verify.py --variant poseidon --rpc-url http://127.0.0.1:8545
```

Result:

```text
verifier:       0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
static_call:    true
tx status:      0x1
tx hash:        0xd1cc310638b9cb1c0c5900012b2fe486d42b43e2ef6f9cb61a439857e61c0301
gas used:       0x2c0073 (2,883,699)
```

## Open-output mode

Command:

```sh
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
  python3 scripts/deploy_and_verify.py --variant open --rpc-url http://127.0.0.1:8545
```

Result:

```text
verifier:       0x0165878A594ca255338adfa4d48449f69242Eb8F
static_call:    true
tx status:      0x1
tx hash:        0x62b6407b4a67f550084395182529c36887ac8836ed5ec479939955ae8c3af16b
gas used:       0x7804dc (7,865,564)
```

Both modes verified the canonical proof generated from the rest/zero-stimulus witness with final hash:

```text
0x1776657d57959fdcdeda347473a0bb38272678bdedd23818ab601b078ee4433f
```
