# Studio

Studio is a deterministic brand engine for generating launch packages for fictional technology companies. One versioned token file drives the copy, colors, typography, and generated visual assets. Structured reasoning records explain key creative choices, and a consistency checker verifies that the package follows its source tokens.

Every generated company and every example in this repository is fictional. All visuals are generated as SVG or HTML from the token file. Studio uses no stock images, diffusion models, or opaque bitmap assets. Runtime generation uses the Python standard library and runs on CPU.

## Quickstart

Requires Python 3.10 or newer. Install the pinned development requirements and the local command:

```powershell
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m studio new-brand --seed 42 --out brands/acme/
python -m studio build --brand brands/acme/
python -m studio check --brand brands/acme/
python -m studio export --format zip --brand brands/acme/
```

The example brand is fictional, despite the `acme` directory name. The `new-brand` command writes `tokens.json` and `reasoning.json`. The `build` command writes the full package to `brands/acme/launch/`, checks it, and writes `brands/acme/launch.zip`. The `export` command can recreate that archive on demand.

The package also installs a `studio` console command. Use `python -m studio --help` for CLI options when the Python scripts directory is not on `PATH`. Use `python -m pytest` to run the test suite.

## Architecture

```text
seed
  |
  v
new-brand ---> tokens.json + reasoning.json
                    |
                    v
                  build ---> SVG, HTML, and Markdown artifacts
                    |                         |
                    v                         v
                  manifest <--- consistency checker
                    |
                    v
                  export ---> deterministic ZIP archive
```

Artifact generators read the token file and attach its version and relevant reasoning IDs to each output. Before rendering, `build` validates the structured reasoning log. The checker verifies trace labels, palette colors, type families, and copy constraints. Rebuilding after a token change replaces the generated package so stale colors do not remain.

## Example fictional brand excerpt

```json
{
  "fictional": true,
  "company": {
    "name": "Northstar Works",
    "tagline": "Make room for better work",
    "positioning": "Northstar Works helps small product teams turn scattered feedback into clear next steps."
  },
  "palette": {
    "primary": "#2457A7",
    "ink": "#172033",
    "paper": "#F5F2EA"
  }
}
```

This excerpt is illustrative and fictional. Generated palette values and copy are examples, not claims about a real company or market.

## Reasoning and traceability

`reasoning.json` stores each key decision, the options considered, the chosen option, a rationale, and whether the rationale rests on evidence or assumption. The generator labels synthetic creative judgments as assumptions. Each package artifact carries a fictional-company label, the exact company name and tagline, the token version, and the reasoning IDs that informed it.

The package includes visual identity, a responsive landing page, three product UI screens, two diagrams, a launch article, a ten-slide HTML deck, three social templates, three tagged ad concepts, a video storyboard, a campaign plan, and a brand guide.

## Development

Studio has no runtime package dependencies. Pytest is pinned in `requirements-dev.txt`. Tests use temporary directories and the standard library. No GPU or model runtime is used.
