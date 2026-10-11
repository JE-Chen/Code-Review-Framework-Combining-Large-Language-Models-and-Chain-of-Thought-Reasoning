"""CLI planning, execution and paired analysis for the 17-mechanism study."""

import json
from pathlib import Path

from prthinker.ablation_study import compare_study, make_plan, run_study
from prthinker.backends import create_backend
from prthinker.cli_io import emit_text


def add_parser(sub, common):
    root = sub.add_parser("ablation-study")
    actions = root.add_subparsers(dest="action", required=True)
    plan = actions.add_parser("plan")
    plan.add_argument("cases", type=Path)
    plan.add_argument("controls", type=Path)
    plan.add_argument("output", type=Path)
    run = actions.add_parser("run", parents=[common])
    run.add_argument("cases", type=Path)
    run.add_argument("plan", type=Path)
    run.add_argument("output_dir", type=Path)
    run.add_argument("--fixtures", type=Path)
    compare = actions.add_parser("compare")
    compare.add_argument("directory", type=Path)
    compare.add_argument("--output", type=Path)
    compare.add_argument("--bootstrap-samples", type=int, default=2000)
    compare.add_argument("--seed", type=int, default=0)


def command(args):
    from prthinker.cli_review import _build_config, _build_retriever

    if args.action == "plan":
        controls = json.loads(args.controls.read_text(encoding="utf-8"))
        payload = make_plan(controls, args.cases)
        if args.output.exists():
            raise FileExistsError(args.output)
        emit_text(json.dumps(payload, indent=2) + "\n", args.output)
        return 0
    if args.action == "compare":
        result = compare_study(args.directory, samples=args.bootstrap_samples, seed=args.seed)
        emit_text(json.dumps(result, indent=2) + "\n", args.output)
        return 0
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    config = _build_config(args)
    if config.max_new_tokens != plan["controls"]["max_new_tokens"] or list(config.steps) != plan["controls"]["steps"]:
        raise ValueError("CLI generation limit and review steps must match the study control")
    fixtures = json.loads(args.fixtures.read_text(encoding="utf-8")) if args.fixtures else {}
    run_study(plan, args.cases, args.output_dir, lambda _control: create_backend(config), fixtures=fixtures,
              retriever_factory=lambda: _build_retriever(args, config))
    return 0
