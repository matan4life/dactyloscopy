# workflow/

Rules for derived data: how each derived artifact is produced from raw inputs, and which manifest, rule and code revision it depends on, so that it can be regenerated rather than trusted.
Derived data itself is never committed. It lives under `LAB_DERIVED`, outside the tree, and is rebuilt from these rules. Nothing described here writes into a raw location.
Not here: the derived artifacts, input data, or results.
