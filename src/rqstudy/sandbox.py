"""Run model-written functions with an isolated filesystem and no network.

Bubblewrap namespaces protect the host; a small Python interface also gives the
selector stable seeded randomness, bounded output and documented operations.
https://github.com/containers/bubblewrap
"""
from __future__ import annotations

import functools
import json
import os
import subprocess

DRIVER = """
import ast, json, math, random, resource, sys
resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
resource.setrlimit(resource.RLIMIT_AS, (128*1024**2, 128*1024**2))
resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
p=json.load(sys.stdin)
tree=ast.parse(p['source'])
for n in ast.walk(tree):
    if isinstance(n, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal, ast.ClassDef)):
        raise ValueError('Use the supplied math module and rng object')
    if isinstance(n,ast.Attribute) and n.attr.startswith('_') or isinstance(n,ast.Name) and n.id.startswith('_'):
        raise ValueError('Private attributes are unavailable')
env={'__builtins__':{k: __builtins__.__dict__[k] for k in ('abs','all','any','bool','dict','enumerate','float','int','len','list','max','min','pow','range','reversed','round','set','sorted','str','sum','tuple','zip','isinstance')},'math':math}
exec(compile(tree,'<workspace>','exec'),env)
fn=env[p['function']]
args=[p['context']]
if p['function']=='select_parent': args.append(random.Random(p['seed']))
result=fn(*args)
if not isinstance(result,str) or not 0<len(result)<=8000: raise ValueError('Expected a nonempty bounded string')
print(json.dumps(result,ensure_ascii=True))
"""


class Worker:
    """Expose one JSON-in/string-out invocation to the host orchestrator."""

    def call(self, source: str, function: str, context: dict, seed: int = 0) -> str:
        if len(source) > 16000:
            raise ValueError("Workspace source exceeds the worker limit")
        prefix = ["wsl", "-d", os.getenv("RQGM_WSL_DISTRO", "Ubuntu"), "--exec"] if os.name == "nt" else []
        # Mount runtime binaries alone. The Windows workspace, home and dataset
        # are absent, as are host credentials and network interfaces.
        command = prefix + ["bwrap","--unshare-all","--clearenv","--new-session","--die-with-parent",
                            "--ro-bind","/usr","/usr","--symlink","usr/lib","/lib","--symlink","usr/lib64","/lib64",
                            "--symlink","usr/bin","/bin","--tmpfs","/tmp","--dev","/dev","--proc","/proc","--chdir","/tmp",
                            "--setenv","PYTHONIOENCODING","utf-8","/usr/bin/python3","-I","-S","-c",DRIVER]
        payload = json.dumps(dict(source=source,function=function,context=context,seed=seed),ensure_ascii=True)
        try:
            result = subprocess.run(command, input=payload.encode(), capture_output=True, timeout=12, check=False)
        except subprocess.TimeoutExpired as exc:
            raise ValueError("Worker timed out") from exc
        if result.returncode:
            raise ValueError(result.stderr.decode("utf-8","replace")[-500:] or f"Worker exited {result.returncode}")
        try:
            return json.loads(result.stdout)
        except (ValueError, UnicodeError) as exc:
            raise ValueError("Worker did not return valid JSON") from exc

    @functools.lru_cache(maxsize=1024)
    def instruction(self, source: str, role: str, route: str = "") -> str:
        """Memoize only deterministic instruction calls with identical public context."""
        return self.call(source, "instruct", {"role":role, "route":route})
