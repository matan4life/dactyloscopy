# workflow/

Rules for derived data: how each derived artifact is produced from raw inputs, and which manifest, rule and code revision it depends on, so that it can be regenerated rather than trusted.
Derived data itself is never committed. It lives under `$LABDATA/derived`, outside the tree. No rule is written here yet: `REF-015` adopts this contract and leaves the form of the first rule open, and until one exists derived data is rebuilt by the command form under `scripts/` that the record made from it names. Nothing described here writes into a raw location.
Not here: the derived artifacts, input data, or results.
