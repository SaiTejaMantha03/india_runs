# Redrob Hackathon — Intelligent Candidate Discovery & Ranking

This is our submission for the "Senior AI Engineer (Founding Team)" ranking
challenge. It's a rule-based ranker — no embeddings, no calls to an LLM, no
training step. We built it this way on purpose: every score it produces can
be traced back to a specific line of code and a specific reason, which
matters a lot once you're trying to explain your own system in an interview.

## Getting it running

```bash
python3 rank.py
```
or 

```bash
python3 rank.py
```

That's really all you need to type. Just make sure `candidates.jsonl` (or
the gzipped version) is sitting in this same folder first — we don't ship
it in the repo since it's ~487MB and GitHub won't take a file that big
anyway (see `.gitignore`). Once it's there, the script finds it
automatically and writes the ranked output to `outputs/submission.csv`,
creating that folder if it doesn't already exist.

If your data lives somewhere else, you can point at it directly:
```bash
python3 rank.py --candidates /path/to/candidates.jsonl --out /path/to/submission.csv
```

or 

```bash
python rank.py --candidates /path/to/candidates.jsonl --out /path/to/submission.csv
```

No pre-computation, no model downloads, no internet connection required
either way. On the full 100,000-candidate pool it takes about **45–65
seconds** and uses roughly **1.7GB of RAM** — comfortably inside the
5-minute / 16GB / CPU-only / no-network limits the hackathon sets.

Once it's done, it's worth double-checking the output is actually valid
before you submit it anywhere:

```bash
python3 validate_submission.py outputs/submission.csv
```

or

```bash
python validate_submission.py outputs/submission.csv
```

## Why we went rule-based instead of using embeddings or an LLM

The brief is explicit that there's no fixed architecture expected — "unleash
your innovation" — so this was a real choice, not a default. We landed on a
transparent, rule-based scorer for three reasons, and all three came out of
actually looking at the data rather than just assuming:

1. **The dataset is built to fool similarity-based approaches.** The
   candidates who look the *most* like a perfect match by keywords or title
   turned out, when we checked, to be almost entirely fabricated honeypots
   (more on this below). A similarity-based ranker would rank exactly the
   wrong people at the top.
2. **You can defend every decision.** Each part of the score breaks down
   into something specific and checkable. If someone asks "why did this
   candidate rank #12," there's an actual answer, not a black box.
3. **It's the only thing that fits the compute budget.** Running an LLM
   call per candidate across 100,000 people, in under 5 minutes, with no
   network access, isn't really on the table — and the spec itself points
   this out.

## What we found before we wrote a single scoring weight

We didn't start by guessing what a "good" scorer should reward. We started
by opening the actual `candidates.jsonl` and poking at it until the data
told us where the real signal was and where the traps were. Three things we
found along the way ended up shaping almost every decision in this repo.

### Finding #1: the titles that look like a perfect match are, almost entirely, fake

Our first instinct was the obvious one — titles like *"Senior AI Engineer,"
"Staff Machine Learning Engineer,"* or *"Recommendation Systems Engineer"*
read as the closest possible match to the job description, so surely
that's where the best candidates would be hiding.

That instinct turned out to be completely wrong, and checking it directly
against the data is what proved it:

- Those 13 "perfect" titles add up to exactly **179 candidates** in the
  whole pool.
- **Every single one of them** — 100% — carries 2 or more skills listed at
  "expert" proficiency at the same time. Everywhere else in the dataset,
  that rate is basically 0%.
- Even the most modest case in that group (`CAND_0037000`, with just 2
  expert skills) doesn't add up: 2.7 years of claimed experience, but 75
  months — over 6 years — of career history listed, and a skill supposedly
  used for 87 months, more than double their total claimed experience.
- We opened several of these profiles by hand (`CAND_0002025`,
  `CAND_0008425`, `CAND_0068351`, and others) and every one had the same
  kind of contradiction — skills used longer than the person's entire
  career, or overlapping degrees that don't make sense together.

So this isn't a "maybe be a little careful here" situation — **this whole
group of titles is the honeypot trap**, full stop. It looks like whoever
built this dataset deliberately put the fabricated profiles behind exactly
the titles a lazy keyword search would rank first. Which, honestly, lines
up perfectly with what the job description itself warns: *"the 'right
answer' is not 'find candidates whose skills section contains the most AI
keywords.'"*

The real candidates were hiding somewhere quieter — a much bigger group of
**3,195 candidates** with titles like Data Scientist, ML Engineer, AI
Specialist, Senior Software Engineer (ML), and a few others. None of these
ring the same alarm bells: 0% of them have inflated expert-skill counts,
and their profiles hold together logically.

### Finding #2: the "obvious" honeypot checks were way too aggressive

Before we landed on the expert-skill-count signal, we tried some more
intuitive checks first — does years of experience roughly match the total
time listed in career history, do education dates overlap suspiciously,
are role descriptions copy-pasted across jobs. Every one of these flagged
tens of thousands of candidates, which is nowhere close to the roughly 80
honeypots the spec describes.

That told us these checks were mostly just picking up ordinary noise from
how the dataset was generated, not actual fabrication. If we'd used them as
hard filters, we'd have wrongly thrown out a huge number of perfectly
legitimate people. So instead, they stayed in as small, gentle penalties
rather than outright disqualifiers (see `src/anomaly.py`).

### Finding #3: career history text doesn't really back up the skills list

The job description specifically asks for this kind of judgment: a
candidate might not have "RAG" or "Pinecone" written anywhere in their
skills, but if their career history shows they actually built a
recommendation system, that should count. We built a mechanism for exactly
this — scanning career history text for real evidence of that kind of work.

In practice, it barely ever fires. The career history descriptions in this
dataset seem to come from a fairly generic, templated pool of text that
doesn't reliably mention the specific skills listed elsewhere on the same
profile. We kept the mechanism in (it's the right idea, and it does no
harm sitting there), but we want to be upfront that most of the real signal
in this dataset comes from the skills list itself — checked for internal
consistency — rather than from free-text evidence. That's just what the
data actually supported, not what we'd hoped for going in.

## How it's put together

```
rank.py                  Entry point: load -> score -> rank -> write CSV
src/
  title_taxonomy.py      Title -> relevance prior (encodes Finding #1)
  skill_taxonomy.py      Skill name -> relevance weight, by empirical
                          frequency tier (core / buzzword / adjacent /
                          data-infra / honeypot-bait / noise)
  experience.py          5-9y band scoring (soft, per JD's own framing)
  coherence.py           Career-history evidence bonus (Tier-5 rescue)
                          + skill-without-evidence discount (anti
                          keyword-stuffing)
  disqualifiers.py       JD's explicit "things we do NOT want": title-
                          chasers, consulting-only careers, CV/speech-
                          only, architecture-only, recent-LangChain-only
  anomaly.py              Honeypot defenses (Findings #1 and #2)
  behavioral.py          redrob_signals -> availability multiplier
                          (recency, responsiveness, notice period,
                          location/visa constraints)
  scorer.py               Combines all of the above into final_score
  reasoning.py            Per-candidate reasoning text generation
```

### How the score is actually calculated

```
base_score = 0.40 * title_relevance
           + 0.30 * skill_match (discounted if uncorroborated)
           + 0.15 * experience_fit
           + 0.15 * career_evidence_bonus

adjusted_score = base_score
               * disqualifier_multiplier   (culture/role-fit issues)
               * anomaly_multiplier         (honeypot defenses)
               * availability_multiplier    (behavioral signals + location)

final_score = adjusted_score * 100
```

We kept the three multiplier stages deliberately separate from the base
score above them, rather than folding everything into one big formula.
The reasoning: those three things — role/culture fit, data-integrity
red flags, and whether someone's actually reachable right now — are
genuinely different kinds of problems. Keeping them as separate
multipliers means a serious issue in just one of them can drag down an
otherwise strong candidate, without us having to hand-write a special
case for every possible combination of problems.

### How we actually catch the honeypots

1. **A title from the fabricated bucket plus 2+ expert skills gets hit
   hardest** (the score gets multiplied by 0.15). This is the strongest
   single check we have, and it's justified directly by Finding #1 above.
2. **A general expert-skill-count curve** for everyone outside that
   bucket — gentle, not a cliff edge, so a genuinely senior engineer with
   2-3 real expert-level skills doesn't get unfairly punished.
3. **Skills "used" longer than the person's entire career** — a flat-out
   impossibility once it goes past a small noise allowance.
4. **"Expert" in something used for 0 months** — this is the literal
   example given in the submission spec itself, and it's about as
   unambiguous a red flag as you can get.
5. **A small set of suspiciously polished-sounding skill names**
   ("Information Retrieval Systems," "Search Backend," "Ranking
   Systems," and similar) that we noticed show up almost exclusively on
   the same fabricated, expert-stacked profiles. We treat this as
   supporting evidence, not the main signal.

The result on the real `candidates.jsonl`: **0% of our top 100 are
honeypots**, compared to 48–76% on three other reference rankings we
checked before settling on this approach (full comparison in
`docs/honeypot_audit.md`).

## What changed after we first Validation 

After our first Validation, We reviewed it and pointed out a real
problem: the reasoning text we generated for skill-matched candidates
always ended with the same line — *"...overlapping the JD's core
retrieval/vector-search requirements"* — no matter whether that candidate
actually had anything related to retrieval in their skills list. We
checked this directly against `candidates.jsonl` ourselves (all three
examples the review pointed to checked out as genuine problems), and it
turned out to affect every single row in some form, with 55 out of 100
sharing the exact same ending. That's a real bug, not a misunderstanding —
the spec calls this out specifically as something Stage 4 review checks for.

**We fixed it** in `src/reasoning.py` — the closing line is now built by
actually looking at which vector-database or search skills the candidate
has, and only mentioning what's genuinely there. Full details, including
why we also checked and rejected an alternative "fixed" submission
(`submission_v2.csv`, which scored an 83% honeypot rate when we checked it
against the same fabrication pattern from Finding #1 — that's an automatic
disqualification under the spec's rules, regardless of any other score),
are in `docs/bugfix_hallucination.md`.

Everything in this repo reflects the fixed version. The bug only affected
how reasoning text was written — the actual scoring and ranking logic
never changed.

## What we know this doesn't do perfectly

We'd rather say this upfront than have it discovered later:

- **The career-history evidence check rarely actually triggers** (this is
  Finding #3 above). The mechanism is built correctly and would do its job
  on data where it applies, but in this specific dataset, most of our
  actual ranking signal comes from the skills list and title rather than
  from free-text evidence.
- **The list of "fabricated" titles is specific to this dataset.** We
  found it by checking this exact released pool — if a different, hidden
  evaluation set placed its honeypots differently, that specific list in
  `title_taxonomy.py` would need to be re-derived. What does generalize is
  the *method*: check whether suspicious signals cluster by title before
  trusting a title as a good sign.
- **We don't do any deep NLP on the free-text fields.** `profile.summary`
  and the career history descriptions are barely used beyond the narrow
  evidence check. A more sophisticated language model could probably pull
  more out of them — we chose not to, to stay auditable and inside the
  compute budget.

## Reproducing this from scratch

```bash
git clone <this-repo>
cd <this-repo>
cp /path/to/candidates.jsonl .
python3 rank.py
python3 validate_submission.py outputs/submission.csv
```

(Or skip the copy step entirely and run
`python3 rank.py --candidates /path/to/candidates.jsonl` instead.)

Nothing to install — it only uses Python's standard library (Python 3.9+).

## How we used AI tools while building this

We used Claude quite a bit throughout — for exploring the dataset and
forming hypotheses, drafting and refining the heuristics and regex logic,
and writing most of the code itself, with a person reviewing and steering
at every step. But none of the specific numbers in this README were just
taken on faith: the 179-candidate honeypot bucket, the 100%-vs-0%
expert-skill split, the 3,195-candidate clean pool, the 0% honeypot rate
in our final top 100 — every one of these was checked by actually running
a script against the real `candidates.jsonl` and looking at the output.
The scripts we used for that are in `docs/`. See `submission_metadata.yaml`
for the full, formal declaration.
