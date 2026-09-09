# Composite Final resource-gate precheck

This create-only precheck consumes the immutable Pilot-3 manifest, the complete D2b manifest, the
manifest-bound composite eligibility receipt, and the frozen resource policy. The mechanically
selected roster is G1/G2/D1; D2 and D2b remain excluded.

Successful recent provider calls are evidence of connectivity, not an independent attestation that
the complete 1,260-execution Final can finish within available provider credits. Accordingly, all
three credit fields remain false and this gate must block Final freeze. No Final provider call was
made.
