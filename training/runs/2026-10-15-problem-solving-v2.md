# Problem-solving v2: evidence-led engineering scenarios

## Dataset and training

The generated dataset has 175 training rows, 59 validation rows, and 81 held-out rubric cases. This iteration contributes twelve worked scenarios, six validation examples, and twelve fresh held-out prompts. Topics include container DNS, idempotent processing, rolling database migrations, memory growth, hydration mismatches, dependency advisories, Kubernetes readiness, query plans, Kafka/SQL commit ordering, concurrent test isolation, API retries, and canary rollouts. The builder checks unique IDs and exact prompt separation across splits.

Trained `Qwen2.5-Coder-3B-Instruct-4bit` on Apple M3 with 24 GiB unified memory using MLX LoRA: 150 iterations, batch size 1, one trainable layer (0.013%), 1,024-token sequence limit, and two validation batches. Validation loss changed from 5.137 to 2.479; final training loss was 1.835. These loss values do not establish useful generalization.

## Fresh held-out comparison

| Twelve new problem-solving prompts | Base | Candidate |
|---|---:|---:|
| Deterministic lexical rubric | 1/12 | 0/12 |

The rubric requires multiple scenario-specific elements and forbids selected unsafe claims. The base usually produced longer, more actionable answers but still missed most requirements. The candidate was shorter and regressed on this screen: for example, it proposed a flag/lock for duplicate payments without a durable idempotency guarantee, suggested scaling down old pods during a readiness failure, and recommended removing an advisory rather than updating the vulnerable dependency. It also omitted the commit ordering needed to avoid losing Kafka-to-SQL updates.

Do not promote `training/adapters/cenere-problem-solving-v2-candidate`; keep the base checkpoint as default. The result says this small fine-tune did not improve the measured behavior. The lexical rubric is only a deterministic screen, not a semantic reasoning benchmark, and neither result is a broad measure of engineering competence.

## Next iteration

Do not reuse these twelve prompts as unseen evaluation after changing the training set. Review the candidate failures, add independently authored scenarios and stronger action-level checks, and evaluate the next candidate on a fresh holdout. For tasks that produce code or repository changes, prefer compilation, tests, and resulting-state assertions over keyword matching.
