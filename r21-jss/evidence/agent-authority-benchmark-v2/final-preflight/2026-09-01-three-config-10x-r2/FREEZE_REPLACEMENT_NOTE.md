# Final freeze replacement note

The first freeze copy was never used for a provider call. Its network-free dry run generated Python
bytecode cache files inside the immutable tree, and the post-run verifier correctly rejected the
extra files. That copy is preserved unchanged. This R2 preflight retains the same source commit,
Final configuration, matrix, and output target while disabling Python bytecode writes for every
dry and live invocation.
