# runs/

Run records and the observations that support claims: a `results.json` per run, with the pair list and score vector it was computed from. Every record names the dataset, manifests, protocol, metric definition, seed and code revision it used; a result that does not is not a result. Metrics are stored as fractions.
A commit that records a run uses the `run:` prefix and carries the headline metric in its subject.
Not here: images, minutiae, or any observation from which either could be reconstructed.
