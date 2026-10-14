"""Write ``data/naming.json``: real series of the advanced MRI sample, each
judged three ways (its name, dcm2niix's guess, its acquisition parameters),
for the interactive example on How names are decided.

    environments/bids-manager/bin/python bids_manager_documentation/tools/reference/naming_examples.py

Reads the scan table the MRI guide's capture made of the advanced MRI sample
(the parameters BIDS Manager cached from the DICOM headers, and the
classifier's evidence), and asks BIDS Manager's own name patterns what the
series name alone would give. Nothing is invented: every value is read.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from bidsmgr.classifier import sequence_dict

SITE = Path(__file__).resolve().parent.parent.parent
TABLE = Path("/private/tmp/bm_docs/studies/mri_advanced_study/.bidsmgr/project/scans/"
             "0001__MRI_sample_data_neuroimging_unit_oldenburg_1/inventory.tsv")
SERIES = ["ses-pre_T2w", "ses-post_acq-grenm2mm_run-01_T1w", "ses-post_acq-tse_T2w"]


def _ms(v):
    return None if v in (None, "") else _num(float(v) * 1000)


def _num(v) -> str:
    v = round(float(v), 2)
    return str(int(v)) if v == int(v) else str(v)


def main() -> None:
    df = pd.read_csv(TABLE, sep="\t", dtype=str, keep_default_na=False)
    out = []
    for name in SERIES:
        r = df[df["sequence"] == name].iloc[0]
        f = json.loads(r["_features"].replace("'", '"').replace("None", "null").replace("True", "true").replace("False", "false"))
        ev = json.loads(r["classification_evidence"])
        readout = ("spin echo" if f.get("is_se") else "gradient echo" if f.get("is_gre") else "other")
        out.append({
            "series": name,
            "by_name": "anat/" + sequence_dict.guess_sequence_kind(name),
            "by_dcm2niix": ev.get("other") or "",
            "by_parameters": ev.get("ours") or "",
            "chosen": ev.get("chosen"),
            "decided_by": ev.get("decided_by"),
            "confidence": float(r["classification_confidence"]),
            "bids_name": r["bids_name"],
            "parameters": {
                "Sequence": f.get("sequence_name"),
                "Readout": f"{f.get('acquisition_type')} {readout}" + (", inversion recovery" if f.get("is_ir") else ""),
                "Repetition time": f"{_ms(f.get('repetition_time'))} ms",
                "Echo time": f"{_num(f['echo_times'][0])} ms" if f.get("echo_times") else "",
                "Inversion time": f"{_ms(f.get('inversion_time'))} ms" if f.get("inversion_time") else "none",
                "Flip angle": f"{_num(f.get('flip_angle'))}°",
                "Image type": "\\".join(f.get("image_type") or []),
            },
            "evidence": [{"for": e["for"], "source": e["source"], "text": e["text"], "points": e["points"]}
                         for e in ev.get("for", [])],
            "runner_up": [{"for": e["for"], "source": e["source"], "text": e["text"], "points": e["points"]}
                          for e in ev.get("runner_up", [])],
        })
    (SITE / "data" / "naming.json").write_text(json.dumps({"examples": out}, indent=1, ensure_ascii=False) + "\n",
                                               encoding="utf-8")
    print("data/naming.json:", ", ".join(e["series"] for e in out))


if __name__ == "__main__":
    main()
