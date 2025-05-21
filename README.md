# FOL Pretrain Dataset Generation
Code for generating FOL-Pretrain dataset

## Data Generation Instructions
- To generate FOL rule sets generation with SymPy, run
```python src/fol_generator.py``` 
Some post processing might be required, as detailed in `scripts/process_generated_rules.py` for organizing the resulting data into post processing format for the next steps.

- Then, with GPT-4 or GPT-3.5, generate predicates like `Exists(x)` or `Relates(x,y)`. Some results from example runs with predicates are shown in `data/batches` and `data/predicate_prompted`.
  
First, to generate predicate prompts and batch prompt the models, run

```python scripts/batch_prompt_predicates.py```

Then, retrieve the batches

```python scripts/retrieve_gpt_batches.py```

Finally, process the resulting files

```python scripts/process_prompted_predicates.py```

- To generate certain FOL datasets with rules and predicates, run
  
```python src/generate_data.py```
