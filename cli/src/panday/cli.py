"""Safe, standard-library Panday command line entry point."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
import re
import shutil
import sys
import statistics
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import tempfile
import time
from pathlib import Path

VERSION = "0.1.0"


def fingerprint(path: Path) -> str:
    if path.is_symlink():
        raise ValueError("skill source cannot be a symbolic link")
    root = path.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("skill source must be a directory")
    digest = hashlib.sha256()
    for item in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
        if item.is_symlink():
            raise ValueError(f"symbolic link not supported: {item.relative_to(root)}")
        if item.is_file():
            rel, data = item.relative_to(root).as_posix().encode(), item.read_bytes()
            digest.update(len(rel).to_bytes(8, "big")); digest.update(rel)
            digest.update(len(data).to_bytes(8, "big")); digest.update(hashlib.sha256(data).digest())
    return digest.hexdigest()


def emit(value: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, sort_keys=True))
    else:
        for key, val in value.items(): print(f"{key}: {val}")


def write_json_artifact(path: Path, value: dict, source_root: Path | None = None, target_root: Path | None = None) -> str:
    resolved=path.expanduser().resolve()
    for root,label in ((source_root,"source"),(target_root,"target")):
        if root is not None and resolved.is_relative_to(root.resolve()):
            raise ValueError(f"report must be outside the {label} package")
    if resolved.exists(): raise ValueError(f"refusing to overwrite report: {resolved}")
    resolved.parent.mkdir(parents=True,exist_ok=True)
    resolved.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return str(resolved)


def read_skill_name(path: Path) -> str:
    import re
    text = (path / "SKILL.md").read_text(encoding="utf-8")
    front = re.search(r"(?ms)^---\s*\n(.*?)\n---\s*\n", text)
    match = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", front.group(1)) if front else None
    if not match: raise ValueError("SKILL.md must have a valid name in frontmatter")
    return match.group(1)


def preview_id(source_digest: str, destination: Path, operation: str) -> str:
    return hashlib.sha256(f"{operation}\0{source_digest}\0{destination.resolve()}".encode()).hexdigest()


def safe_copy(source: Path, destination: Path) -> None:
    fingerprint(source)
    if destination.resolve().is_relative_to(source.resolve()): raise ValueError("destination cannot be inside the source package")
    if destination.exists(): raise ValueError(f"destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, symlinks=False)


def eval_file(path: Path) -> Path:
    return path / "evals" / "evals.json" if path.is_dir() else path


def local_registry() -> list[Path]:
    config = Path.home() / ".panday" / "config.toml"
    if not config.is_file(): return []
    data = tomllib.loads(config.read_text(encoding="utf-8"))
    entries = data.get("registries", [])
    if isinstance(entries, dict): entries = entries.get("paths", [])
    if not isinstance(entries, list): raise ValueError("config registries must be an array of local paths")
    roots=[]
    for value in entries:
        raw=value.get("path") if isinstance(value,dict) else value
        if isinstance(raw,str): roots.append(Path(raw).expanduser().resolve())
    return roots


@contextmanager
def candidate_source(source: str, ref: str | None, subpath: str | None, skill_name: str | None = None):
    """Resolve a local path or explicit GitHub repository into a temporary review tree."""
    local=Path(source).expanduser()
    if local.exists():
        if subpath: raise ValueError("--subpath is only valid for GitHub sources")
        if local.is_symlink(): raise ValueError("candidate source cannot be a symbolic link")
        candidate=local.resolve(strict=True)
        if not (candidate/"SKILL.md").is_file():
            matches=[p.parent for p in candidate.rglob("SKILL.md")]
            if skill_name: matches=[p for p in matches if skill_metadata(p)[0]==skill_name]
            if len(matches)!=1: raise ValueError("source must identify exactly one skill folder; use --skill")
            candidate=matches[0]
        yield candidate; return
    owner=repo=None; parsed=urllib.parse.urlparse(source)
    path_parts=[part for part in parsed.path.strip("/").split("/") if part]
    if parsed.scheme in {"https","http"} and parsed.netloc.lower() in {"github.com","www.github.com"}:
        if len(path_parts)<2: raise ValueError("GitHub source must identify owner/repository")
        owner,repo=path_parts[0],path_parts[1].removesuffix(".git")
        if len(path_parts)>=4 and path_parts[2] in {"tree","blob"}:
            ref=ref or path_parts[3]
            subpath=subpath or "/".join(path_parts[4:])
    elif re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",source):
        owner,repo=source.split("/",1)
    if not owner or not repo: raise ValueError("source must be a local folder or GitHub owner/repository URL")
    token=os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers={"Accept":"application/vnd.github+json","User-Agent":"panday-cli"}
    if token: headers["Authorization"]=f"Bearer {token}"
    api=f"https://api.github.com/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}"
    def get(url: str) -> bytes:
        request=urllib.request.Request(url,headers=headers)
        try:
            with urllib.request.urlopen(request,timeout=30) as response:
                data=response.read(100*1024*1024+1)
        except urllib.error.HTTPError as exc:
            if exc.code in {401,403,404}: raise ValueError(f"GitHub source unavailable or unauthorized (HTTP {exc.code}); existing GH_TOKEN/GITHUB_TOKEN may be required") from exc
            raise ValueError(f"GitHub request failed (HTTP {exc.code})") from exc
        if len(data)>100*1024*1024: raise ValueError("GitHub archive exceeds 100 MiB safety limit")
        return data
    metadata=json.loads(get(api))
    chosen_ref=ref or metadata.get("default_branch")
    if not isinstance(chosen_ref,str) or not chosen_ref: raise ValueError("could not resolve GitHub default branch; pass --ref")
    archive=get(api+"/zipball/"+urllib.parse.quote(chosen_ref,safe=""))
    with tempfile.TemporaryDirectory(prefix="panday-source-") as tmp:
        root=Path(tmp); archive_path=root/"source.zip"; archive_path.write_bytes(archive); extracted=root/"tree"; extracted.mkdir()
        total=0
        with zipfile.ZipFile(archive_path) as zf:
            members=zf.infolist()
            if len(members)>20000: raise ValueError("GitHub archive contains too many entries")
            for member in members:
                name=Path(member.filename)
                if name.is_absolute() or ".." in name.parts: raise ValueError("GitHub archive contains an unsafe path")
                if (member.external_attr >> 16) & 0o170000 == 0o120000: raise ValueError("GitHub archive contains a symbolic link")
                total+=member.file_size
                if total>100*1024*1024: raise ValueError("expanded GitHub archive exceeds 100 MiB safety limit")
            zf.extractall(extracted)
        roots=[p for p in extracted.iterdir() if p.is_dir()]
        if len(roots)!=1: raise ValueError("GitHub archive has an unexpected root layout")
        repo_root=roots[0]
        candidate=(repo_root/subpath).resolve() if subpath else repo_root
        if not candidate.is_relative_to(repo_root.resolve()): raise ValueError("GitHub subpath escapes the repository")
        if not (candidate/"SKILL.md").is_file():
            matches=list(candidate.rglob("SKILL.md"))
            if skill_name: matches=[p for p in matches if skill_metadata(p.parent)[0]==skill_name]
            if len(matches)!=1: raise ValueError("source must identify exactly one skill folder; provide --subpath")
            candidate=matches[0].parent
        yield candidate


def search_skill_catalog(query: str, owner: str | None = None) -> tuple[list[dict], str]:
    """Use the skills CLI-compatible endpoint experimentally, with bounded partial matching/cache."""
    if len(query.strip()) < 2: raise ValueError("search query must contain at least two characters")
    cache_dir=Path.home()/".panday"/"cache"/"skills-search"

    def request_search(term: str) -> tuple[list[dict],bool]:
        params={"q":term,"limit":"25"}
        if owner: params["owner"]=owner
        url="https://skills.sh/api/search?"+urllib.parse.urlencode(params)
        cache=cache_dir/(hashlib.sha256(url.encode()).hexdigest()+".json")
        try:
            request=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":"panday-cli/0.1"})
            with urllib.request.urlopen(request,timeout=8) as response: payload=json.loads(response.read(2*1024*1024+1))
            if not isinstance(payload,dict) or not isinstance(payload.get("skills"),list): raise ValueError("unexpected skills.sh search response")
            rows=[]
            for row in payload["skills"][:25]:
                if not isinstance(row,dict): continue
                fields={"name":row.get("name"),"slug":row.get("slug") or row.get("id"),"source":row.get("source"),"installs":row.get("installs")}
                if not isinstance(fields["name"],str) or not isinstance(fields["slug"],str): continue
                fields["source"]=fields["source"] if isinstance(fields["source"],str) else ""
                fields["installs"]=fields["installs"] if isinstance(fields["installs"],int) else None
                fields["match_type"]="exact"
                fields["url"]="https://skills.sh/"+urllib.parse.quote(fields["slug"],safe="/")
                fields["signal_note"]="Catalog installs measure popularity only; they do not establish quality, safety, or compatibility."
                rows.append(fields)
            try:
                cache_dir.mkdir(parents=True,exist_ok=True)
                cache.write_text(json.dumps({"cached_at":time.time(),"url":url,"rows":rows},indent=2)+"\n",encoding="utf-8")
            except OSError: pass
            return rows,True
        except (OSError,ValueError,json.JSONDecodeError,urllib.error.URLError):
            try:
                saved=json.loads(cache.read_text(encoding="utf-8"))
                if time.time()-saved.get("cached_at",0)<24*3600 and saved.get("url")==url:
                    return saved.get("rows",[]),False
            except (OSError,ValueError,json.JSONDecodeError,AttributeError): pass
            return [],False

    exact,live=request_search(query.strip()); merged=list(exact)
    terms=list(dict.fromkeys(query.strip().split()))
    if len(exact)<10 and 2<=len(terms)<=6:
        seen={x["slug"] for x in merged}
        for index in range(len(terms)):
            partial,_=request_search(" ".join(terms[:index]+terms[index+1:]))
            for item in partial:
                if item["slug"] not in seen and len(merged)<25:
                    item["match_type"]="partial"; merged.append(item); seen.add(item["slug"])
    status="live experimental skills.sh results; endpoint is undocumented and may change" if live else "using recent cached experimental skills.sh results; live search unavailable" if merged else "skills.sh search unavailable; use a configured local registry or explicit GitHub source"
    return merged,status


def skill_metadata(path: Path) -> tuple[str,str]:
    text=(path/"SKILL.md").read_text(encoding="utf-8")
    front=re.search(r"(?ms)^---\s*\n(.*?)\n---\s*\n",text)
    if not front: raise ValueError("SKILL.md frontmatter is missing")
    body=front.group(1)
    name=re.search(r"(?m)^name:\s*([^\n#]+?)\s*$",body)
    desc=re.search(r"(?m)^description:\s*(.*)$",body)
    if not name or not desc: raise ValueError("SKILL.md needs name and description frontmatter")
    skill_name=name.group(1).strip().strip("\"'")
    description=desc.group(1).strip()
    if description.startswith("'") and description.endswith("'"): description=description[1:-1].replace("''","'")
    elif description.startswith('"') and description.endswith('"'): description=description[1:-1]
    if not skill_name or not description.strip(): raise ValueError("SKILL.md name and description must be non-empty")
    return skill_name,description


def local_link_findings(path: Path) -> list[dict]:
    findings=[]
    for markdown in path.rglob("*.md"):
        if markdown.is_symlink(): findings.append({"file":markdown.relative_to(path).as_posix(),"link":"","issue":"symbolic link is not supported"}); continue
        text=markdown.read_text(encoding="utf-8",errors="replace")
        for raw in re.findall(r"\[[^\]]*\]\(([^)]+)\)",text):
            target=raw.strip().split()[0].strip("<>").split("#",1)[0]
            if not target or target.startswith(("https://","http://","mailto:","data:")): continue
            decoded=urllib.parse.unquote(target)
            resolved=(markdown.parent/decoded).resolve()
            if not resolved.is_relative_to(path.resolve()): findings.append({"file":markdown.relative_to(path).as_posix(),"link":raw,"issue":"link escapes package root"})
            elif not resolved.exists(): findings.append({"file":markdown.relative_to(path).as_posix(),"link":raw,"issue":"target does not exist"})
    return findings


def validate_provider_package(path: Path, provider: str) -> list[str]:
    name,description=skill_metadata(path); warnings=[]
    if provider=="claude":
        if len(name)>64 or not re.fullmatch(r"[a-z0-9-]+",name) or any(token in name.lower() for token in ("anthropic","claude")):
            raise ValueError("Claude target name must be <=64 lowercase letters/numbers/hyphens and cannot contain reserved provider names")
        if len(description)>1024 or re.search(r"</?[A-Za-z][^>]*>",description):
            raise ValueError("Claude target description exceeds 1024 characters or contains XML tags")
        if (path/"agents"/"openai.yaml").exists(): warnings.append("agents/openai.yaml is OpenAI-specific metadata and will be preserved as inert source metadata")
    elif provider=="codex":
        if len(name)>64 or not re.fullmatch(r"[a-z0-9-]+",name): raise ValueError("Codex skill name must be <=64 lowercase letters, numbers, and hyphens")
        if len(description)>1024: raise ValueError("description exceeds the supported 1024 character interoperability limit")
    else: raise ValueError("supported target providers are codex and claude")
    return warnings


def aggregate_benchmark(path: Path, eval_path: Path | None = None) -> dict:
    records=[]
    for line_number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        item=json.loads(line)
        if not isinstance(item,dict): raise ValueError(f"benchmark line {line_number} must be an object")
        if not isinstance(item.get("scenario_id"),str) or item.get("variant") not in {"baseline","with_skill"} or not isinstance(item.get("run_id"),str) or not isinstance(item.get("passed"),bool):
            raise ValueError(f"benchmark line {line_number} requires scenario_id, variant, run_id, and passed")
        item["_score_supplied"]="score" in item
        item["_quality_score_supplied"]="quality_score" in item
        item["score"]=item.get("score",1.0 if item["passed"] else 0.0)
        if not isinstance(item["score"],(int,float)) or isinstance(item["score"],bool) or isinstance(item["score"],float) and not math.isfinite(item["score"]) or not 0<=item["score"]<=1: raise ValueError(f"benchmark line {line_number} score must be between zero and one")
        if item["_quality_score_supplied"] and (not isinstance(item["quality_score"],(int,float)) or isinstance(item["quality_score"],bool) or isinstance(item["quality_score"],float) and not math.isfinite(item["quality_score"]) or not 0<=item["quality_score"]<=1): raise ValueError(f"benchmark line {line_number} quality_score must be between zero and one")
        for metric in ("duration_seconds","tokens","cost_usd"):
            value=item.get(metric)
            if value is not None and (not isinstance(value,(int,float)) or isinstance(value,bool) or isinstance(value,float) and not math.isfinite(value) or value<0): raise ValueError(f"benchmark line {line_number} {metric} must be non-negative and finite")
        records.append(item)
    if not records: raise ValueError("benchmark has no result records")
    identities=[(x["scenario_id"],x["variant"],x["run_id"]) for x in records]
    if len(set(identities))!=len(identities): raise ValueError("benchmark contains duplicate run identities")
    definitions=None
    if eval_path:
        evals=json.loads(eval_file(eval_path).read_text(encoding="utf-8"))
        scenarios=evals.get("scenarios") if isinstance(evals,dict) else None
        if not isinstance(scenarios,list): raise ValueError("eval definitions require scenarios")
        definitions={x["id"]:{a["id"]:a.get("kind") for a in x.get("assertions",[])} for x in scenarios}
        for row in records:
            if row["scenario_id"] not in definitions: raise ValueError(f"unknown scenario id: {row['scenario_id']}")
            if not isinstance(row.get("assertions"),list): raise ValueError(f"run {row['scenario_id']}/{row['run_id']} requires assertion evidence")
            expected=definitions[row["scenario_id"]]
            if any(not isinstance(a,dict) or not isinstance(a.get("id"),str) for a in row["assertions"]): raise ValueError(f"invalid assertion evidence for {row['scenario_id']}/{row['run_id']}")
            actual={a["id"] for a in row["assertions"]}
            if len(actual)!=len(row["assertions"]): raise ValueError(f"duplicate assertion ids for {row['scenario_id']}/{row['run_id']}")
            missing=set(expected)-actual
            if actual-set(expected) or any(expected[key]!="process" for key in missing): raise ValueError(f"assertions mismatch for {row['scenario_id']}/{row['run_id']}")
            checked=[]; process=[]
            for assertion in row["assertions"]:
                kind=expected[assertion["id"]]
                if kind=="process" and assertion.get("status")=="unassessed":
                    if "passed" in assertion: raise ValueError(f"unassessed process assertions cannot have passed for {row['scenario_id']}/{row['run_id']}")
                    process.append({"id":assertion["id"],"status":"unassessed"})
                    continue
                if not isinstance(assertion.get("passed"),bool) or not isinstance(assertion.get("evidence"),str) or not assertion["evidence"].strip(): raise ValueError(f"invalid assertion evidence for {row['scenario_id']}/{row['run_id']}")
                checked.append(assertion["passed"])
                if kind=="process": process.append({"id":assertion["id"],"status":"passed" if assertion["passed"] else "failed"})
            process.extend({"id":key,"status":"unassessed"} for key in sorted(missing))
            if row["passed"]!=all(checked): raise ValueError(f"passed must equal assessed assertion conjunction for {row['scenario_id']}/{row['run_id']}")
            quality=[a["passed"] for a in row["assertions"] if expected[a["id"]]!="process" and isinstance(a.get("passed"),bool)]
            row["_quality_passed"]=all(quality) if quality else None
            row["_process_assertions"]=process
            has_process="process" in expected.values()
            if row["_quality_score_supplied"]:
                row["score"]=row["quality_score"]
            elif has_process or not row["_score_supplied"]:
                row["score"]=sum(quality)/len(quality) if quality else None
    groups={variant:[r for r in records if r["variant"]==variant] for variant in ("baseline","with_skill")}
    def summary(rows):
        if not rows: return {"runs":0,"passed":0,"pass_rate":None,"pass_rate_standard_error":None,"score_mean":None,"score_stdev":None,"duration_seconds_mean":None,"duration_seconds_stdev":None,"tokens_mean":None,"tokens_stdev":None,"cost_usd_mean":None,"cost_usd_stdev":None}
        quality=[r.get("_quality_passed",r["passed"]) for r in rows]
        assessed=[value for value in quality if isinstance(value,bool)]
        rate=sum(assessed)/len(assessed) if assessed else None
        out={"runs":len(rows),"passed":sum(assessed),"pass_rate":rate,"pass_rate_standard_error":math.sqrt(rate*(1-rate)/len(assessed)) if rate is not None else None,"quality_assessed_runs":len(assessed)}
        if definitions is not None:
            checks=[check for row in rows for check in row.get("_process_assertions",[])]
            out["process_assertions"]={"total":len(checks),"assessed":sum(x["status"]!="unassessed" for x in checks),"passed":sum(x["status"]=="passed" for x in checks),"failed":sum(x["status"]=="failed" for x in checks),"unassessed":sum(x["status"]=="unassessed" for x in checks)}
        for field in ("score","duration_seconds","tokens","cost_usd"):
            values=[float(r[field]) for r in rows if r.get(field) is not None]
            out[field+"_mean"]=statistics.mean(values) if values else None
            out[field+"_stdev"]=statistics.stdev(values) if len(values)>1 else None
        return out
    by_key={(r["scenario_id"],r["run_id"],r["variant"]):r for r in records}
    pair_keys=sorted({(r["scenario_id"],r["run_id"]) for r in records if (r["scenario_id"],r["run_id"],"baseline") in by_key and (r["scenario_id"],r["run_id"],"with_skill") in by_key})
    paired={}
    for metric in ("passed","score","duration_seconds","tokens","cost_usd"):
        deltas=[]
        for scenario,run_id in pair_keys:
            base=by_key[(scenario,run_id,"baseline")]; treated=by_key[(scenario,run_id,"with_skill")]
            base_value=base.get("_quality_passed",base[metric]) if metric=="passed" else base.get(metric)
            treated_value=treated.get("_quality_passed",treated[metric]) if metric=="passed" else treated.get(metric)
            if base_value is not None and treated_value is not None: deltas.append(float(treated_value)-float(base_value))
        paired[metric]={"pairs":len(deltas),"mean":statistics.mean(deltas) if deltas else None,"stdev":statistics.stdev(deltas) if len(deltas)>1 else None}
    scenario_ids=sorted({r["scenario_id"] for r in records})
    incomplete=[]
    scenarios={}
    repetition_counts={}
    for scenario in scenario_ids:
        by_variant={v:[r for r in records if r["scenario_id"]==scenario and r["variant"]==v] for v in groups}
        baseline_ids={r["run_id"] for r in by_variant["baseline"]}
        treated_ids={r["run_id"] for r in by_variant["with_skill"]}
        if not baseline_ids or baseline_ids!=treated_ids: incomplete.append(scenario)
        repetition_counts[scenario]=min((len(rows) for rows in by_variant.values()),default=0)
        scenarios[scenario]={v:summary(rows) for v,rows in by_variant.items() if rows}
    result={"schema_version":1,"records":len(records),"variants":{v:summary(rows) for v,rows in groups.items()},"paired":{"complete_pairs":len(pair_keys),"deltas_with_skill_minus_baseline":paired},"incomplete_scenarios":incomplete,"minimum_repetitions_per_scenario":min(repetition_counts.values(),default=0),"scenarios":scenarios,"limitations":["Paired score summaries do not establish causality or superiority without calibrated grading, declared scope, and sufficient independent runs."]}
    result["complete"]=bool(pair_keys) and not incomplete and (definitions is None or set(definitions).issubset(set(scenario_ids)))
    if definitions is not None:
        result["safety_failures"]=sum(1 for row in records for assertion in row.get("assertions",[]) if definitions[row["scenario_id"]].get(assertion["id"])=="safety" and not assertion["passed"])
        result["safety_assertions_present"]=any(kind=="safety" for assertions in definitions.values() for kind in assertions.values())
        process_by_variant={}
        for variant,rows in groups.items():
            checks=[check for row in rows for check in row.get("_process_assertions",[])]
            process_by_variant[variant]={"total":len(checks),"assessed":sum(x["status"]!="unassessed" for x in checks),"passed":sum(x["status"]=="passed" for x in checks),"failed":sum(x["status"]=="failed" for x in checks),"unassessed":sum(x["status"]=="unassessed" for x in checks)}
        result["process_assertions"]=dict(process_by_variant["with_skill"])
        result["process_assertions"]["by_variant"]=process_by_variant
        result["process_assessment_complete"]=result["process_assertions"]["unassessed"]==0
    return result


def evaluate_gate(report: dict, policy: dict) -> tuple[dict, int]:
    if not isinstance(report,dict) or not isinstance(policy,dict): raise ValueError("gate report and policy must be JSON objects")
    def hold(reason: str) -> tuple[dict,int]: return {"gate":"HOLD","reasons":[reason]},4
    if "safety_failures" not in report or not isinstance(report.get("safety_failures"),int) or isinstance(report.get("safety_failures"),bool) or report["safety_failures"]<0 or report.get("safety_assertions_present") is not True:
        return hold("report lacks explicit safety assertion coverage and a valid safety_failures count")
    variants=report.get("variants",{})
    quality=report.get("quality",variants.get("with_skill",{}).get("pass_rate")) if isinstance(variants,dict) else report.get("quality")
    complete=report.get("complete")
    if complete is not None and not isinstance(complete,bool): raise ValueError("report complete must be a boolean")
    paired=report.get("paired",{})
    if not isinstance(paired,dict): raise ValueError("report paired summary must be an object")
    if complete is None: complete=not report.get("incomplete_scenarios",[]) and paired.get("complete_pairs",0)>0
    if not complete or quality is None: return hold("report is incomplete or has no quality measure")
    minimum_quality=policy.get("minimum_quality",1.0)
    if not isinstance(minimum_quality,(int,float)) or isinstance(minimum_quality,bool) or isinstance(minimum_quality,float) and not math.isfinite(minimum_quality) or not 0<=minimum_quality<=1: raise ValueError("minimum_quality must be between zero and one")
    max_safety=policy.get("maximum_safety_failures",0)
    if not isinstance(max_safety,int) or isinstance(max_safety,bool) or max_safety<0: raise ValueError("maximum_safety_failures must be a non-negative integer")
    required_pairs=policy.get("required_complete_pairs",1)
    if not isinstance(required_pairs,int) or isinstance(required_pairs,bool) or required_pairs<1: raise ValueError("required_complete_pairs must be a positive integer")
    actual_pairs=report.get("paired",{}).get("complete_pairs",0)
    if not isinstance(actual_pairs,int) or isinstance(actual_pairs,bool) or actual_pairs<required_pairs:
        return hold(f"requires {required_pairs} complete pairs; found {actual_pairs}")
    required_repetitions=policy.get("minimum_repetitions",1)
    if not isinstance(required_repetitions,int) or isinstance(required_repetitions,bool) or required_repetitions<1: raise ValueError("minimum_repetitions must be a positive integer")
    actual_repetitions=report.get("minimum_repetitions_per_scenario",0)
    if not isinstance(actual_repetitions,int) or isinstance(actual_repetitions,bool) or actual_repetitions<required_repetitions:
        return hold(f"requires {required_repetitions} repetitions per scenario; found {actual_repetitions}")
    process_policy={key:policy[key] for key in ("minimum_process_assessment_rate","maximum_process_failures") if key in policy}
    reasons=[]
    if process_policy:
        process=report.get("process_assertions")
        fields=("total","assessed","passed","failed","unassessed")
        if not isinstance(process,dict) or any(not isinstance(process.get(key),int) or isinstance(process.get(key),bool) for key in fields):
            return hold("report lacks process-assessment counts required by policy")
        if any(process[key]<0 for key in fields) or process["assessed"]+process["unassessed"]!=process["total"] or process["passed"]+process["failed"]!=process["assessed"]:
            raise ValueError("report process-assessment counts are inconsistent")
        if "minimum_process_assessment_rate" in process_policy:
            minimum=process_policy["minimum_process_assessment_rate"]
            if not isinstance(minimum,(int,float)) or isinstance(minimum,bool) or isinstance(minimum,float) and not math.isfinite(minimum) or not 0<=minimum<=1: raise ValueError("minimum_process_assessment_rate must be between zero and one")
            rate=process["assessed"]/process["total"] if process["total"] else 0.0
            if rate<minimum: return hold(f"requires process assessment rate {minimum}; found {rate}")
        if "maximum_process_failures" in process_policy:
            maximum=process_policy["maximum_process_failures"]
            if not isinstance(maximum,int) or isinstance(maximum,bool) or maximum<0: raise ValueError("maximum_process_failures must be a non-negative integer")
            if process["total"]==0: return hold("report contains no process assertions required by policy")
            if process["unassessed"]: return hold("process assertions remain unassessed under a process-failure gate")
            if process["failed"]>maximum: reasons.append("process assertion failure threshold exceeded")
    if report["safety_failures"]>max_safety: reasons.append("safety floor failed")
    if not isinstance(quality,(int,float)) or isinstance(quality,bool) or isinstance(quality,float) and not math.isfinite(quality) or not 0<=quality<=1: raise ValueError("report quality must be between zero and one")
    if quality<minimum_quality: reasons.append("quality threshold failed")
    passed=not reasons
    return {"gate":"ALLOW" if passed else "BLOCK","quality":quality,"reasons":reasons},0 if passed else 3


def transform_provider_package(path: Path, provider: str) -> list[dict]:
    name,description=skill_metadata(path); changes=[]
    if provider=="codex":
        metadata=path/"agents"/"openai.yaml"
        if not metadata.exists():
            metadata.parent.mkdir(parents=True,exist_ok=True)
            short=description[:64].rstrip()
            while len(short)<25: short=(short+" Skill workflow")[:64]
            safe_name=name.replace("-"," ").title()
            metadata.write_text(f'interface:\n  display_name: "{safe_name}"\n  short_description: "{short.replace(chr(34), chr(39))}"\n  default_prompt: "Use ${name} to follow the skill instructions."\n',encoding="utf-8")
            changes.append({"path":"agents/openai.yaml","status":"created","reason":"Codex skill interface metadata was absent"})
    warnings=validate_provider_package(path,provider)
    for warning in warnings: changes.append({"path":"agents/openai.yaml","status":"preserved_inert","reason":warning})
    for finding in local_link_findings(path): changes.append({"path":finding["file"],"status":"manual_review","reason":f"{finding['issue']}: {finding['link']}"})
    return changes


def discover_local(query: str | None) -> list[dict]:
    found=[]
    for root in local_registry():
        if not root.exists(): continue
        candidates=[root] if (root/"SKILL.md").is_file() else [p.parent for p in root.rglob("SKILL.md")]
        for path in candidates:
            try:
                name=read_skill_name(path)
                description=""
                for line in (path/"SKILL.md").read_text(encoding="utf-8").splitlines()[:8]:
                    if line.startswith("description:"): description=line.partition(":")[2].strip(); break
                if query and query.casefold() not in f"{name} {description}".casefold(): continue
                found.append({"name":name,"path":str(path),"description":description,"source":"configured-local-registry"})
            except (OSError,ValueError): continue
    return found


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="panday", description="Standalone skill discovery and lifecycle tools")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    sub = parser.add_subparsers(dest="area")
    sub.add_parser("init", help="initialize a Panday project config")
    skills = sub.add_parser("skills", help="discover and manage skills").add_subparsers(dest="command")
    for name in ("search", "list", "show", "inspect", "install", "migrate"):
        command = skills.add_parser(name); command.add_argument("source_or_query", nargs="?")
        command.add_argument("--source"); command.add_argument("--to"); command.add_argument("--target", type=Path)
        command.add_argument("--ref"); command.add_argument("--subpath")
        command.add_argument("--skill")
        command.add_argument("--owner")
        command.add_argument("--from-provider",choices=("codex","claude"))
        command.add_argument("--project", type=Path); command.add_argument("--report-dir", type=Path)
        command.add_argument("--report",type=Path)
        command.add_argument("--preview", action="store_true"); command.add_argument("--apply", action="store_true")
        command.add_argument("--fingerprint"); command.add_argument("--scan-only", action="store_true")
        command.add_argument("--plan", action="store_true"); command.add_argument("--doctor", action="store_true")
        command.add_argument("--validate-target", action="store_true")
    ev = sub.add_parser("eval", help="validate evaluation assets and reports").add_subparsers(dest="command")
    for name in ("validate", "init", "gate", "report", "workspace", "benchmark"):
        command=ev.add_parser(name); command.add_argument("path",type=Path); command.add_argument("--policy",type=Path); command.add_argument("--output",type=Path); command.add_argument("--evals",type=Path)
    life = sub.add_parser("lifecycle", help="inspect lifecycle records").add_subparsers(dest="command")
    for name in ("fingerprint", "validate-record", "validate-chain"):
        command=life.add_parser(name); command.add_argument("paths",type=Path,nargs="+")
    sub.add_parser("doctor",help="show local setup readiness")
    return parser


def main(argv: list[str] | None = None) -> int:
    args=build_parser().parse_args(argv); as_json=bool(args.json)
    try:
        if args.area=="doctor":
            cfg=Path.home()/".panday"/"config.toml"
            registry_count=len(local_registry())
            emit({"ok":True,"version":VERSION,"python":sys.version.split()[0],"config":str(cfg),"configured":cfg.exists(),"registry_paths":registry_count,"github_auth":"environment-token" if (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")) else "not-detected; public repositories remain available","auth_values_printed":False},as_json); return 0
        if args.area=="init":
            cfg=Path.home()/".panday"/"config.toml"; cfg.parent.mkdir(parents=True,exist_ok=True)
            if not cfg.exists(): cfg.write_text('version = 1\n\n[registries]\n',encoding="utf-8")
            emit({"ok":True,"config":str(cfg)},as_json); return 0
        if args.area=="lifecycle":
            if args.command=="fingerprint":
                emit({"ok":True,"items":[{"path":str(p),"sha256_tree":fingerprint(p)} for p in args.paths]},as_json); return 0
            records=[json.loads(p.read_text(encoding="utf-8")) for p in args.paths]
            for record in records:
                if isinstance(record,dict) and record.get("schema_version")=="panday-skill-lifecycle/v2":
                    from importlib.util import module_from_spec, spec_from_file_location
                    validator=Path(__file__).parents[3]/"panday-lifecycle"/"validate_v2.py"
                    if not validator.exists(): raise ValueError("v2 validator package is unavailable")
                    spec=spec_from_file_location("panday_lifecycle_v2",validator); module=module_from_spec(spec); spec.loader.exec_module(module); module.validate(record)
                else:
                    validator=Path(__file__).parents[3]/"panday-lifecycle"/"lifecycle.py"
                    spec=spec_from_file_location("panday_lifecycle_v1",validator); module=module_from_spec(spec); spec.loader.exec_module(module); module.validate_record(record)
            if args.command=="validate-chain":
                versions={r.get("schema_version") or r.get("schema") for r in records}
                if len(versions)>1: raise ValueError("mixed lifecycle schema versions cannot be chained together")
                if versions=={"panday-skill-lifecycle/v2"}:
                    validator=Path(__file__).parents[3]/"panday-lifecycle"/"validate_v2.py"
                    spec=spec_from_file_location("panday_lifecycle_v2_chain",validator); module=module_from_spec(spec); spec.loader.exec_module(module); module.validate_chain(records)
                else:
                    validator=Path(__file__).parents[3]/"panday-lifecycle"/"lifecycle.py"
                    spec=spec_from_file_location("panday_lifecycle_chain",validator); module=module_from_spec(spec); spec.loader.exec_module(module); module.validate_chain(args.paths)
            emit({"ok":True,"validated":len(records),"note":"structural validation only; not approval"},as_json); return 0
        if args.area=="skills" and args.command=="inspect":
            source=args.source_or_query or args.source or ""
            with candidate_source(source,args.ref,args.subpath,args.skill) as src:
                digest=fingerprint(src); name=read_skill_name(src)
                inventory=[{"path":item.relative_to(src).as_posix(),"bytes":item.stat().st_size} for item in sorted(src.rglob("*")) if item.is_file()]
                findings=local_link_findings(src)
                report={"ok":True,"source":source,"resolved_skill":name,"fingerprint":digest,"files":inventory,"local_link_findings":findings,"executed_candidate_code":False}
                if args.report_dir:
                    report["report_path"]=write_json_artifact(args.report_dir/"inspection.json",report,src)
                    report["report_written"]=True
                emit(report,as_json); return 0
        if args.area=="skills" and args.command in {"install","migrate"}:
            if not args.source_or_query: raise ValueError("an exact local folder or GitHub owner/repository source is required")
            with candidate_source(args.source_or_query,args.ref,args.subpath,args.skill) as src:
                digest=fingerprint(src); name=read_skill_name(src)
                if args.command=="install":
                    if not args.project: raise ValueError("install requires --project")
                    destination=args.project.resolve()/".agents"/"skills"/name
                else:
                    if args.to not in {"codex","claude"}: raise ValueError("migrate requires --to codex or --to claude")
                    if not args.target: raise ValueError("migrate requires --target destination folder")
                    destination=args.target.resolve()
                if args.command=="install":
                    preview=preview_id(digest,destination,"install")
                    if not args.apply:
                        emit({"ok":True,"mode":"preview","operation":"install","source":args.source_or_query,"resolved_skill":name,"source_fingerprint":digest,"destination":str(destination),"preview_fingerprint":preview,"writes":False},as_json); return 0
                    if not args.fingerprint or args.fingerprint!=preview: raise ValueError("apply requires the current preview_fingerprint; no write was performed")
                    safe_copy(src,destination); installed=fingerprint(destination)
                    if installed!=digest: raise ValueError("copied bytes differ from previewed source; inspect destination before retry")
                    emit({"ok":True,"mode":"applied","operation":"install","destination":str(destination),"source_fingerprint":digest,"installed_fingerprint":installed,"verified":True},as_json); return 0
                source_provider=args.from_provider
                if source_provider is None:
                    source_text=str(src).replace("\\","/").lower()
                    if "/.claude/skills/" in source_text: source_provider="claude"
                    elif "/.agents/skills/" in source_text or (src/"agents"/"openai.yaml").is_file(): source_provider="codex"
                with tempfile.TemporaryDirectory(prefix="panday-migration-") as temp:
                    staged=Path(temp)/name; shutil.copytree(src,staged,symlinks=False)
                    changes=transform_provider_package(staged,args.to)
                    warnings=validate_provider_package(staged,args.to)
                    if source_provider is None: warnings.append("source provider is unknown; pass --from-provider for a complete compatibility map")
                    elif source_provider==args.to: warnings.append("source and target providers match; this validates packaging but does not convert between formats")
                    output_digest=fingerprint(staged)
                    preview=preview_id(hashlib.sha256((digest+output_digest).encode()).hexdigest(),destination,"migrate")
                    if args.doctor:
                        emit({"ok":True,"mode":"doctor","target_provider":args.to,"target_parent_exists":destination.parent.exists(),"target_exists":destination.exists(),"source_provider":source_provider,"target_validation":"pass","writes":False},as_json); return 0
                    if args.validate_target:
                        emit({"ok":True,"mode":"validate-target","target_provider":args.to,"target_fingerprint":output_digest,"warnings":warnings,"writes":False},as_json); return 0
                    mode="scan-only" if args.scan_only else "plan" if args.plan else "preview"
                    if not args.apply:
                        report={"ok":True,"mode":mode,"operation":"migrate","source_provider":source_provider,"target_provider":args.to,"source":args.source_or_query,"skill":name,"source_fingerprint":digest,"target_fingerprint":output_digest,"destination":str(destination),"preview_fingerprint":preview,"changes":changes,"warnings":warnings,"writes":False}
                        if args.report:
                            report["report_path"]=write_json_artifact(args.report,report,src,destination)
                            report["report_written"]=True
                        emit(report,as_json); return 0
                    if not args.fingerprint or args.fingerprint!=preview: raise ValueError("apply requires the current preview_fingerprint; no write was performed")
                    if args.report:
                        report_path=args.report.expanduser().resolve()
                        if report_path.exists(): raise ValueError(f"refusing to overwrite report: {report_path}")
                        if report_path.is_relative_to(src.resolve()) or report_path.is_relative_to(destination): raise ValueError("report must be outside the source and target packages")
                    safe_copy(staged,destination); installed=fingerprint(destination)
                    if installed!=output_digest: raise ValueError("migrated target bytes differ from the preview; inspect destination before retry")
                    report={"ok":True,"mode":"applied","operation":"migrate","source_fingerprint":digest,"target_fingerprint":installed,"destination":str(destination),"changes":changes,"warnings":warnings,"verified":True}
                    if args.report:
                        report["report_path"]=write_json_artifact(args.report,report,src,destination)
                        report["report_written"]=True
                    emit(report,as_json); return 0
        if args.area=="eval":
            if args.command=="validate":
                source=eval_file(args.path); data=json.loads(source.read_text(encoding="utf-8"))
                if not isinstance(data,dict) or data.get("version")!=1 or not isinstance(data.get("skill"),str) or not isinstance(data.get("scenarios"),list) or not data["scenarios"]: raise ValueError("evals need version 1, skill, and non-empty scenarios")
                seen=set()
                for case in data["scenarios"]:
                    if not isinstance(case,dict) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",str(case.get("id",""))) or case["id"] in seen or not isinstance(case.get("prompt"),str) or not case["prompt"].strip() or not isinstance(case.get("should_trigger"),bool) or case.get("risk") not in {"low","medium","high"} or not isinstance(case.get("holdout"),bool) or not isinstance(case.get("assertions"),list) or not case["assertions"]: raise ValueError("scenario requires a unique path-safe id, prompt, trigger, risk, holdout, and assertions")
                    seen.add(case["id"]); assertion_ids=set()
                    for assertion in case["assertions"]:
                        if not isinstance(assertion,dict) or not isinstance(assertion.get("id"),str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",assertion["id"]) or assertion["id"] in assertion_ids or assertion.get("kind") not in {"outcome","process","safety","trigger"} or not isinstance(assertion.get("description"),str) or not assertion["description"].strip(): raise ValueError(f"scenario {case['id']} has invalid assertion metadata")
                        assertion_ids.add(assertion["id"])
                emit({"ok":True,"skill":data["skill"],"source":str(source),"scenarios":len(data["scenarios"])},as_json); return 0
            if args.command=="init":
                output=args.output or (args.path/"evals"/"evals.json" if args.path.is_dir() else args.path)
                if output.exists(): raise ValueError(f"refusing to overwrite {output}")
                template={"version":1,"skill":args.path.name,"scenarios":[{"id":"replace-this","prompt":"Replace with a representative task.","should_trigger":True,"risk":"low","holdout":False,"tags":["normal"],"assertions":[{"id":"expected-outcome","kind":"outcome","description":"Replace with an observable success criterion."}]}]}
                output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(template,indent=2)+"\n",encoding="utf-8")
                emit({"ok":True,"created":str(output)},as_json); return 0
            if args.command=="workspace":
                source=eval_file(args.path); data=json.loads(source.read_text(encoding="utf-8")); output=args.output or source.with_name(source.stem+"-workspace.json")
                if output.exists(): raise ValueError(f"refusing to overwrite {output}")
                rows={"schema":"panday-eval-workspace/v1","skill":data.get("skill"),"source":str(args.path.resolve()),"scenarios":[{"id":x["id"],"runs":[]} for x in data.get("scenarios",[])]}
                output.write_text(json.dumps(rows,indent=2)+"\n",encoding="utf-8"); emit({"ok":True,"workspace":str(output),"scenarios":len(rows["scenarios"])},as_json); return 0
            if args.command in {"report","benchmark"}:
                if args.command=="benchmark" or args.path.suffix==".jsonl":
                    data=aggregate_benchmark(args.path,args.evals)
                    result={"ok":True,"input":str(args.path.resolve()),"report":data}
                    exit_code=0
                    if args.policy:
                        policy=json.loads(args.policy.read_text(encoding="utf-8"))
                        decision,exit_code=evaluate_gate(data,policy)
                        data["gate"]=decision
                        result["ok"]=decision["gate"]=="ALLOW"
                        result["gate"]=decision
                    if args.output: result["output_path"]=write_json_artifact(args.output,data)
                    emit(result,as_json); return exit_code
                data=json.loads(args.path.read_text(encoding="utf-8"))
                if not isinstance(data,dict): raise ValueError("report must be a JSON object")
                emit({"ok":True,"input":str(args.path.resolve()),"report":data},as_json); return 0
            if args.command=="gate":
                if not args.policy: raise ValueError("gate requires --policy")
                report=json.loads(args.path.read_text(encoding="utf-8")); policy=json.loads(args.policy.read_text(encoding="utf-8"))
                decision,exit_code=evaluate_gate(report,policy)
                emit({"ok":decision["gate"]=="ALLOW",**decision,"policy":str(args.policy)},as_json); return exit_code
        if args.area=="skills" and args.command in {"search","list","show"}:
            if args.command=="show":
                target=Path(args.source_or_query or args.source or "")
                if target.exists(): rows=[{"name":read_skill_name(target),"path":str(target.resolve()),"fingerprint":fingerprint(target)}]
                else: rows=[x for x in discover_local(None) if x["name"]==args.source_or_query]
            elif args.command=="search" or args.command=="list" and args.source=="skills.sh":
                query=args.source_or_query or ""
                if args.owner and not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})",args.owner): raise ValueError("--owner must be a valid GitHub owner name")
                if args.command=="list" and len(query.strip())<2: raise ValueError("skills.sh currently exposes search only; provide a query or use a configured local registry for list")
                online=[]; search_note="remote search not requested"
                if args.source in {None,"skills.sh"}: online,search_note=search_skill_catalog(query,args.owner)
                local=discover_local(query)
                seen={item.get("slug") or item.get("name") for item in online}
                rows=online+[item for item in local if item["name"] not in seen]
                if args.source not in {None,"skills.sh","local"}: raise ValueError("supported search sources are skills.sh and local")
                if args.source=="local": rows=local; search_note="configured local registries only"
                exact_count=sum(1 for row in rows if row.get("match_type")!="partial")
                emit({"ok":bool(rows) or args.source=="local","items":rows,"count":len(rows),"exact_count":exact_count,"source_status":search_note,"quality_note":"Catalog popularity is discovery evidence only, not quality or safety evidence."},as_json)
                return 0 if rows else 4
            else: rows=discover_local(None)
            if not rows: raise ValueError("no matching skills; configure local paths in ~/.panday/config.toml or search skills.sh")
            emit({"ok":True,"items":rows,"count":len(rows)},as_json); return 0
        emit({"ok":True,"version":VERSION,"message":"Use --help for commands"},as_json); return 0
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        emit({"ok":False,"error":str(exc),"code":"operation_failed"},as_json); return 2


if __name__=="__main__": raise SystemExit(main())
