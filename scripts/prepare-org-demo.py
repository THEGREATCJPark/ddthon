"""Explicit operator setup. No approval or publication is synthesized."""
import argparse
import json
from pathlib import Path
from org_demo import bootstrap, connect_work
from tests.prepare_p0_work import prepare_work

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['bootstrap', 'p0', 'connect'])
parser.add_argument('destination')
parser.add_argument('--remote', required=True)
parser.add_argument('--branch', required=True)
parser.add_argument('--reviewer', default='박찬준')
args = parser.parse_args()
if args.mode == 'bootstrap':
    result = bootstrap(args.destination, args.remote, args.branch)
else:
    if args.mode == 'p0':
        prepare_work(Path(args.destination), seed_local=False)
    result = connect_work(args.destination, args.remote, args.branch, args.reviewer)
print(json.dumps(result, ensure_ascii=False, indent=2))
