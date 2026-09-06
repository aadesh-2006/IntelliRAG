import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import argparse
import json
from evaluation.runner import EvaluationRunner

def main():
    parser = argparse.ArgumentParser(description="IntelliRAG AI Evaluation Runner")
    parser.add_argument("--extraction", action="store_true", help="Run extraction evaluation")
    parser.add_argument("--retrieval", action="store_true", help="Run retrieval evaluation")
    parser.add_argument("--groundedness", action="store_true", help="Run groundedness evaluation")
    parser.add_argument("--citations", action="store_true", help="Run citation evaluation")
    parser.add_argument("--all", action="store_true", help="Run all evaluation suites")
    parser.add_argument("--json", action="store_true", help="Print JSON results to stdout")

    args = parser.parse_args()

    run_all = args.all or (not args.extraction and not args.retrieval and not args.groundedness and not args.citations)
    run_ext = run_all or args.extraction
    run_ret = run_all or args.retrieval
    run_gnd = run_all or args.groundedness
    run_cit = run_all or args.citations

    runner = EvaluationRunner()
    results = runner.run(
        run_extraction=run_ext,
        run_retrieval=run_ret,
        run_groundedness=run_gnd,
        run_citations=run_cit
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(runner.generate_markdown_report(results))

if __name__ == "__main__":
    main()
