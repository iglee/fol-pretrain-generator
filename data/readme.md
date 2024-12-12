# FOL Ruleset Annotation

## Example Data
```json
{
  "data": "((p₀ ∨ p₂ ∨ ¬(p₀ ∧ p₃)) → ¬p₂) ⇔ ((p₀ ∨ p₂ ∨ ¬p₀ ∨ ¬p₃) → ¬p₂) ⇔ (¬p₂)",
  "total_complexity": 55,
  "program_complexity": 41,
  "num_var": 3,
  "num_ops": 4,
  "original_depth": 5,
  "original_complexity": 48,
  "exprs": [
    "(p₀ ∨ p₂ ∨ ¬(p₀ ∧ p₃)) → ¬p₂",
    "(p₀ ∨ p₂ ∨ ¬p₀ ∨ ¬p₃) → ¬p₂",
    "¬p₂"
  ],
  "complexity_by_step": [
    17,
    16,
    4
  ],
  "elimination_complexity": [
    6,
    1
  ]
}
```

## Annotation
- `data`: each example string, which are first-logic rule and equivalent simplifications linked by `⇔` symbol.
- `total_complexity`: `original_complexity` + `sum(elimination complexity)`
- `program_complexity`: program complexity to generate the original expression (i.e. the first rule in `data`)
- `num_var`: number of unique variables
- `num_ops`: number of unique operations, i.e. `∨`, `→` ...
- `original_depth`: maximum depth of original expression. each operator is considered as depth `+1`
- `original_complexity`: complexity of the first rule defined as `program_complexity` + `num_var` + `num_ops`
- `exprs`: list of all expressions. original expression followed by a series of simplified expression in steps. 
- `complexity_by_step`: circuit complexity for each expression in `exprs`
- `elimination_complexity`: program complexity to find a sub expression to be simplified, with `sympy`'s `simplify()`. we assume that `simplify` is relatively constant for each simplification.