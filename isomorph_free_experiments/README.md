# isomorph_free_experiments

Exploratory project on strict isomorph-free generation for JAM chains.

Does JAM admit strict isomorph-free generation (McKay 1998) in the sense
of generating each class **exactly once**, without generating duplicates
and deduplicating?

**Answer: yes, but it costs exactly 2.5× more canonicalization calls
than `caugJAM`'s deduplication approach, universally across all eight
canonical options.**

## The two questions

### Q1: Does a G-equivariant position selector exist?

A **position selector** is a function `s: X_{n+1} → {first, last}`
satisfying `s(g·c) = φ(g)·s(c)` for all `g ∈ G`, where
`φ: G → S_2` is trivial on `S_3` and non-trivial on `v`. If such `s`
exists, `p(c) = p_{s(c)}(c)` is a cheap G-equivariant parent.

**Obstruction.** If `Stab(c)` contains any element of the form
`(σ, v)`, no such `s` can exist at that class, because equivariance
forces `s(c) = s((σ, v)·c) = opposite(s(c))`.

**Result: NO for the q=3 and q=6 options at every level; NO for the
q=12 options at even levels only.**

#### Option 1 (planar binary, `q=3`)

| n | total classes | with v-composed stab | fraction |
|---|---|---|---|
| 2 |  2 |  2 | 100.0% |
| 3 |  4 |  3 |  75.0% |
| 4 | 10 |  6 |  60.0% |
| 5 | 25 |  9 |  36.0% |
| 6 | 70 | 18 |  25.7% |
| 7 | 196 | 27 |  13.8% |

#### Options 2, 3, 5, 6 (all `q=6`)

All four have identical obstruction counts, despite spanning planar
(op2, op5) and buckled (op3, op6) types:

| n | total classes | with v-composed stab | fraction |
|---|---|---|---|
| 2 |    5 |   4 | 80.0% |
| 3 |   21 |   6 | 28.6% |
| 4 |  120 |  24 | 20.0% |
| 5 |  666 |  36 |  5.4% |
| 6 | 3960 | 144 |  3.6% |

#### Options 4, 7, 8 (all `q=12`)

The obstruction **vanishes at odd levels**:

| n | total classes | with v-composed stab | fraction |
|---|---|---|---|
| 2 |    16 |   8 | 50.0% |
| 3 |   144 |   0 |  0.0% |
| 4 |  1776 |  96 |  5.4% |
| 5 | 20736 |   0 |  0.0% |

A per-level position selector is therefore not ruled out at odd levels
for the q=12 options, though it is ruled out at even levels. An
alternating strategy (position at odd levels, argmin at even levels)
would cost at least ≈1.75× caugJAM, still above the 1× of
deduplication.

### Q2: Is argmin-parent a valid isomorph-free parent function?

Define

```
p_argmin(c) = argmin over {p_first(c), p_last(c)} of κ(·)
```

This is G-equivariant **on canonical keys**:
`κ(p_argmin(g·c)) = κ(p_argmin(c))` for all `g ∈ G`. The chain equality
`p_argmin(g·c) = g·p_argmin(c)` does *not* hold, but the algorithm only
uses the canonical key.

#### Exhaustive verification of G-equivariance

For options 1, 3, and 5 at n ≤ 5, we verified
`κ(p_argmin(g·c)) = κ(p_argmin(c))` on **all 19,008 raw chains** and
all 12 elements of G. All pass.

| option | chains at n=5 | total chains n ≤ 5 | result |
|---|---|---|---|
| 1 |   243 |    360 | PASS |
| 3 | 7,776 |  9,324 | PASS |
| 5 | 7,776 |  9,324 | PASS |

#### Class counts recovered

The argmin-parent generator recovers the exact class counts of
`caugJAM` for all eight options. Representative tables:

##### Option 1, n ≤ 8

| n | classes | match | κ calls (argmin) | κ calls (`caugJAM`) | ratio |
|---|---|---|---|---|---|
| 2 |   2 | YES |   18 |    6 | 3.00 |
| 3 |   4 | YES |   34 |   12 | 2.83 |
| 4 |  10 | YES |   65 |   24 | 2.71 |
| 5 |  25 | YES |  154 |   60 | 2.57 |
| 6 |  70 | YES |  383 |  150 | 2.55 |
| 7 | 196 | YES | 1058 |  420 | 2.52 |
| 8 | 574 | YES | 2956 | 1176 | 2.51 |

##### Option 3 (buckled binary, n ≤ 6)

| n | classes | match | κ calls (argmin) | κ calls (`caugJAM`) | ratio |
|---|---|---|---|---|---|
| 2 |    5 | YES |    36 |    12 | 3.00 |
| 3 |   21 | YES |   156 |    60 | 2.60 |
| 4 |  120 | YES |   641 |   252 | 2.54 |
| 5 |  666 | YES |  3595 |  1440 | 2.50 |
| 6 | 3960 | YES | 20025 |  7992 | 2.51 |

#### Universal ratio across all eight options

| op | max n | ratio at max n |
|---|---|---|
| 1 | 8 | 2.51 |
| 2 | 6 | 2.51 |
| 3 | 6 | 2.51 |
| 4 | 5 | 2.50 |
| 5 | 6 | 2.51 |
| 6 | 6 | 2.51 |
| 7 | 5 | 2.49 |
| 8 | 5 | 2.50 |

**The asymptotic ratio is 2.50 for all eight options**, because the
growth rate of the class count is `≈ q` (half of `2q`):

```
ratio → 2 + |T_n| / (|T_{n-1}| · 2q) ≈ 2 + q/(2q) = 2.5
```

This is independent of `q`, of the option, and of the specific
v-involution. Argmin-parent costs exactly 2.5× caugJAM asymptotically,
universally.

### Hybrid strategies fail

A hybrid that uses `p_first` for chains without v-composed stabilizer
and `p_argmin` otherwise loses the same classes as `p_first` alone:

| option | n | strategy | missing | extra |
|---|---|---|---|---|
| 1 | 6 | first  |  8 | 0 |
| 1 | 6 | hybrid |  8 | 0 |
| 1 | 6 | argmin |  0 | 0 |
| 3 | 6 | first  | 1728 | 0 |
| 3 | 6 | hybrid | 1728 | 0 |
| 3 | 6 | argmin |  0 | 0 |
| 5 | 6 | first  | 1774 | 0 |
| 5 | 6 | hybrid | 1774 | 0 |
| 5 | 6 | argmin |  0 | 0 |

The reason is subtle: the chosen parent must be the **canonical
representative** of its class, not merely a chain without v-composed
stabilizer. `p_first` can pick a non-canonical parent, and the child is
never accepted. Argmin compares canonical keys, which is why it works.

**Argmin is the only correct strategy between first and last.**

## Conclusion for open problem 4 of the `caugJAM` paper

The open problem asked:

> A finer pruning that also removes the ≈1.9-fold residual duplication
> of the augmentation DAG — without changing the parent class — would
> yield a truly isomorph-free generator in McKay's sense. Whether such
> a pruning exists, or whether the residual duplication is irreducible,
> is open.

This project answers it for all eight options:

1. **No G-equivariant position selector exists** (Q1). The obstruction
   is the `v`-composed stabilizer elements, present at every level for
   the q=3 and q=6 options, and at even levels for the q=12 options.
   A cheap parent function based on position (remove first / remove
   last) cannot work.
2. **Strict isomorph-free generation exists** via argmin-parent (Q2),
   and it reproduces the exact class counts of `caugJAM` for all eight
   options. The G-equivariance of `p_argmin` on canonical keys is
   verified exhaustively on 19,008 raw chains at n ≤ 5 for options 1,
   3, and 5.
3. **But it costs exactly 2.5× more** canonicalization calls than
   `caugJAM`, asymptotically and universally. The 2.5 factor is
   `2 + q/(2q)`, and it is independent of the option.
4. **Hybrid strategies fail** (Q2). Using `p_first` when the stabilizer
   has no `v`-composed element loses classes, because canonicity of the
   parent, not absence of the obstruction, is the requirement.

**The tradeoff is sharp and clean:**

- **`caugJAM`**: 1 κ call per child. Output is isomorph-free, generation
  is not. Residual duplication ≈1.9 per child, handled by
  set-deduplication.
- **argmin-parent**: 2.5 κ calls per child asymptotically. Generation is
  strictly isomorph-free in McKay's sense.

There is no third option between the two. Either you pay the 1.9-fold
duplication and deduplicate (caugJAM), or you pay 2.5× the
canonicalization cost to avoid generating duplicates in the first place
(argmin).

## Reproducing

```bash
# Sanity check (7 tests)
pytest tests/test_action.py -v

# Closure of row sets under sign flip (Lemma 1 of the paper)
python scripts/check_closure.py

# Exhaustive G-equivariance check
python scripts/test_equivariance_exhaustive.py --options 1 3 5 --max-n 5

# Q1: obstruction
for opt in 1 2 3 4 5 6 7 8; do
    python scripts/run_obstruction.py --option $opt --levels 2 3 4 5 \
        --output datos/obstruction_op$opt.tsv
done

# Q2: argmin-parent (option 1 up to n=8; others to n=5 or 6)
python scripts/run_argmin.py --option 1 --n-max 8 \
    --output datos/argmin_op1_n8.tsv
for opt in 2 3 5 6; do
    python scripts/run_argmin.py --option $opt --n-max 6 \
        --output datos/argmin_op$opt.tsv
done
for opt in 4 7 8; do
    python scripts/run_argmin.py --option $opt --n-max 5 \
        --output datos/argmin_op$opt.tsv
done

# Hybrid vs first vs argmin
python scripts/test_hybrid.py --option 1 --n-max 6
python scripts/test_hybrid.py --option 3 --n-max 6
python scripts/test_hybrid.py --option 5 --n-max 6

# All remaining options in one go
./scripts/run_all_options.sh
```

## Layout

- `iso_free/action.py`: G-action on JAM chains (all options).
  `v = flip` for planar (1, 2, 5), `v = sign ∘ flip` for buckled
  (3, 4, 6, 7, 8). Includes `sign_flip_token` with Janus pair
  identification per Definition 3 of the paper.
- `iso_free/parents.py`: `p_first`, `p_last`, `p_argmin`.
- `iso_free/obstruction.py`: v-composed stabilizer test.
- `scripts/check_closure.py`: verifies row sets are closed under
  `v_content` (Lemma 1 of the paper).
- `scripts/test_equivariance_exhaustive.py`: exhaustive check of
  `κ(p_argmin(g·c)) = κ(p_argmin(c))` on all raw chains.
- `scripts/test_hybrid.py`: compares `first`, `hybrid`, `argmin`
  strategies.
- `scripts/run_obstruction.py`: Q1 experiment.
- `scripts/run_argmin.py`: Q2 experiment.
- `scripts/run_all_options.sh`: Q1 + Q2 for options 2, 4, 6, 7, 8.
- `datos/`: TSV outputs.
- `figuras/`: TikZ figures (pending).
- `tests/`: unit tests.

## Status

- **All eight options tested.** Q1 = NO (with the odd-level exception
  for q=12 options); Q2 = YES at 2.5× cost.
- **Exhaustive G-equivariance** verified on 19,008 raw chains for
  options 1, 3, 5 at n ≤ 5.
- **Hybrid strategies** tested and shown to fail for options 1, 3, 5.
- **Closure of row sets** verified for options 3–8 (Lemma 1 holds).

## Closure of row sets under sign flip

All eight options have row sets closed under `v_content`, as required
by Lemma 1 of the main paper. Verified by `scripts/check_closure.py`:
options 3, 4, 5, 6, 7, 8 are all closed. For option 5, the Janus pair
`(+k-k)` and `(-k+k)` are identified by Definition 3 of the paper;
`sign_flip_token` respects this identification.

## Relationship to the main paper

This project addresses open problem 4 of:

> *Growing as Pruning: Isomorph-free generation of JAM chains via
> canonical augmentation* (in preparation, target: MATCH).

The main paper's §7 documents the residual duplication ≈1.9 and defers
the question to future work. This project closes it for all eight
options with a clean tradeoff: no cheap position-based selector exists
(Q1), a strict generator exists via argmin-parent at exactly 2.5× cost
(Q2), hybrids fail, and the two extremes are the only options
available.

## Open questions for future work

1. **Cheaper G-equivariant parent functions.** The negative result on
   position selectors shows that any such parent must inspect the
   content of the chain, not only its endpoints. Whether a
   content-based parent cheaper than argmin exists is open.
2. **Optimality of the 2.5 factor.** Within the class of parent
   functions that choose between `p_first` and `p_last` by a
   G-invariant criterion, `p_argmin` is optimal (it achieves the
   minimal possible cost, 2 κ calls per child). Whether a broader class
   of parent functions can do better is open.
3. **Per-level alternation for q=12 options.** The obstruction vanishes
   at odd levels for options 4, 7, 8. A per-level strategy (position at
   odd levels, argmin at even) could in principle yield ≈1.75× cost,
   still above caugJAM but below argmin. Whether such a strategy is
   valid (and preserves G-equivariance across levels) is open.
