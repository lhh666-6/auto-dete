"""Read-only counterexample for the frozen observation checker.

Loads a Git blob in memory and never modifies the checkout or archived source.
"""
import hashlib
import subprocess
import sys
import types
from dataclasses import replace

REF = "c6d512843c905cab6d8521dd8c914f7fb26d85ae:latest/code/formal-fixed/observation_witnesses.py"
raw = subprocess.check_output(["git", "show", REF])
module = types.ModuleType("frozen_observation_checker")
sys.modules[module.__name__] = module
exec(raw.decode("utf-8"), module.__dict__)
module.verify()
print("Frozen source:", REF)
print("SHA-256:", hashlib.sha256(raw).hexdigest())
print("Existing verification: PASS")

history = module.paired_histories()["D_V"][0]
before = (module.FieldValue("score", 90),)
after = (module.FieldValue("score", 1),)
authorization = replace(history.authorizations[0], authorized_value=1)
good = replace(
    history,
    authorizations=(authorization,),
    successor_values=after,
    commits=(module.CommitStep("successor-1", before, after),),
    source_transitions=(
        module.SourceTransition("prior-score", "score", 90),
        module.SourceTransition("transition-score", "score", 1),
    ),
)
bad = replace(good, authorizations=(replace(authorization, authorized_value=True),))
print("Domain errors:", module.validate_history_domain(good), module.validate_history_domain(bad))
print("All projections equal:", module.project(good, module.CLASSES) == module.project(bad, module.CLASSES))
print("Good outcome:", module.normative_outcome(good))
print("Bad outcome:", module.normative_outcome(bad))
print("Good D_V:", module.observe(good, "D_V"))
print("Bad D_V:", module.observe(bad, "D_V"))
assert not module.validate_history_domain(good)
assert not module.validate_history_domain(bad)
assert module.project(good, module.CLASSES) == module.project(bad, module.CLASSES)
assert module.normative_outcome(good) != module.normative_outcome(bad)

# The declared domain requires the commit sequence to reach the endpoint.
# Its dictionary comparisons likewise collapse JSON number/Boolean types.
disconnected = replace(
    bad,
    successor_values=(module.FieldValue("score", True),),
    source_transitions=(
        module.SourceTransition("prior-score", "score", 90),
        module.SourceTransition("transition-score", "score", True),
    ),
)
print("Disconnected canonical endpoint, domain errors:", module.validate_history_domain(disconnected))
print("Disconnected canonical endpoint, outcome:", module.normative_outcome(disconnected))
print("Commit ends at integer 1; declared endpoint is Boolean true.")
assert not module.validate_history_domain(disconnected)
assert module.normative_outcome(disconnected)[0] == "admissible"
