# R9 Finite Conformance Catalogue

The machine-readable denominator is `case_catalogue.json` version
`auto-decte-r9-v1`: 35 unique cases spanning P0–P6. Each case declares its
class, exact pytest node, expected public status, and digest expectation.

`tests/conformance/oracle.py` is the independent raw-relational oracle.
`run_catalogue.py` retains one JSON receipt and one pytest temp root per case.
`verify_catalogue_results.py` checks the denominator, catalogue hash, per-case
hashes, outcomes, and database evidence schema. `ACTIVE_CATALOGUE_RUN.txt`
points at the current development run; it is not the R14 evidence freeze.

Claim boundary: the artifact may report “35/35 declared catalogue cases” for
this development gate. It may not claim arbitrary-corruption completeness,
unbounded proof, or final paper evidence until the frozen R14 rerun exists.
