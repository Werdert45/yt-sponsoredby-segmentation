# SponsoredBye

Finds the "this video is sponsored by" part of a YouTube video from the transcript alone, so you can skip it. Sponsor reads are baked into the video itself, so ad blockers can't touch them; text can. A team project from our MSc at Bocconi University.

![Logistic baseline against the T5 plus BiLSTM tagger: WindowDiff falls from 99.1% to 15.6%, Pk from 76.0% to 12.1%, macro F1 rises from 56.6% to 86.2%](https://ianronk.nl/projects/sponsoredbye-sponsored-segment-detection/results-baseline-vs-bilstm.svg)

## Result

| Metric | Logistic baseline | SponsoredBye |
|---|---|---|
| Macro F1 | 56.6% | **86.2%** |
| WindowDiff (lower is better) | 99.1% | **15.6%** |
| Pk (lower is better) | 76.0% | **12.1%** |

Trained on 630 MB of labelled transcript text. WindowDiff and Pk score where the sponsor read starts and ends, so a boundary one sentence late counts as a near-miss, not a miss.

## How it works

1. **Data** (`data/`). Crowd-sourced sponsor timestamps say, per video, when the sponsor read starts and ends. A scraper pulls the transcript, punctuation is restored, timings are aligned, and every sentence is labelled sponsor or content.
2. **Model** (`model/`). Each sentence is embedded with sentence-T5, and a bidirectional LSTM reads the whole sequence and gives every sentence a sponsor probability. The baseline is a logistic regression that looks at one sentence at a time.
3. **Demo** (`demo/`). A Gradio app: paste a video URL, get the start and end of the sponsor read.

## Run it

The demo:

```bash
cd demo
pip install -r requirements.txt gradio==4.31.4
python app.py
```

Training uses the notebooks in `model/` and the packages in the top-level `requirements.txt`.

## Data

The full dataset lives in MongoDB and is not public. A sample is in `data/data_sample.json`; for access, contact ian@ronk.org.

## Team

Built by [Werdert45](https://github.com/Werdert45), [eyadrmsh](https://github.com/eyadrmsh), [Gsalocchi](https://github.com/Gsalocchi), [nilanshadargan](https://github.com/nilanshadargan) and [mark-levin](https://github.com/mark-levin).

## Write-up

How the dataset was built and why accuracy is the wrong metric: [SponsoredBye on ianronk.nl](https://ianronk.nl/en/research/sponsoredbye-sponsored-segment-detection).
