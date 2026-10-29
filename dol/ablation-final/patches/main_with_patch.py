"""Run main.py with $ABLATION_PATCH (a directory holding a sitecustomize.py) on the stage subprocesses' PYTHONPATH.
main.py sets PYTHONPATH to src/ for every stage, which would drop the patch; main.py itself is not modified."""
import os
MAIN = '/mnt/d/tez/practical/protocol_re/main.py'
code = open(MAIN, encoding='utf-8').read()
old = 'env["PYTHONPATH"] = str(SRC_PATH)'
assert code.count(old) >= 1
code = code.replace(old, 'env["PYTHONPATH"] = os.pathsep.join(filter(None, [os.environ.get("ABLATION_PATCH", ""), str(SRC_PATH)]))')
# $ABLATION_STAGE07_ARGS: extra arguments for stage 07 (switches main.py does not expose, e.g. --no-opcode-isolation)
old07 = 'step_args.extend(["--max-fields", str(args.boundary_max_fields)])'
assert code.count(old07) == 1
code = code.replace(old07, old07 + '; step_args.extend(os.environ.get("ABLATION_STAGE07_ARGS", "").split())')
exec(compile(code, MAIN, 'exec'), {'__name__': '__main__', '__file__': MAIN})
