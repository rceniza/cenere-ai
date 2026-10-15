# Cenere problem-solving v1

This extension adds explicit practice in debugging, test design, performance diagnosis, concurrency, versioned research, safe tool use, planning, uncertainty, review, algorithm selection, and incident response.

It is generated from the v4 curriculum plus 12 training examples, six validation examples, and ten held-out rubric cases. Rebuild it with:

```sh
python3 curriculum/datasets/build_problem_solving_v1.py
python3 curriculum/datasets/build_problem_solving_v1.py --check
```

Train an adapter against it with:

```sh
cd training
python train.py --model models/Qwen2.5-Coder-3B-Instruct-4bit \
  --data ../curriculum/datasets/cenere-problem-solving-v1 \
  --output adapters/cenere-problem-solving-v1-candidate \
  --iters 150 --batch-size 1 --num-layers 1 --max-seq-length 1024
```

The ten evaluation prompts are diagnostic and use a lexical rubric. They are not proof of general reasoning. Evaluate any coding changes with compilation and behavior tests, and evaluate agent tasks by checking the resulting repository state and required tests. Do not train on these evaluation prompts and continue calling them held out.
