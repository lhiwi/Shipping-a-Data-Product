import sys, pathlib, nbformat as nbf
from nbformat.validator import validate, ValidationError

root = pathlib.Path(".")
bad = []

for ipynb in root.rglob("*.ipynb"):
    try:
        nb = nbf.read(ipynb, as_version=4)   # upgrade to v4 structure if needed
        validate(nb)                          # will raise if invalid
        # Optionally clear outputs to keep diffs clean:
        for c in nb.cells:
            if c.cell_type == "code":
                c.outputs = []
                c.execution_count = None
        nbf.write(nb, ipynb)                 # re-write canonical JSON
        print(f"OK  {ipynb}")
    except (ValidationError, Exception) as e:
        print(f"BAD {ipynb}: {e}")
        bad.append(ipynb)

if bad:
    print("\nFix tips:")
    print("- Open these in VS Code: Right‑click → Open With → JSON Editor.")
    print("- Remove any merge markers like <<<<<<< HEAD / ======= / >>>>>>>.")
    print("- Ensure 'cells' is a list of objects, no stray nulls/commas.")
    sys.exit(1)
