#!/usr/bin/env python3
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).parents[1]


class WrapperTests(unittest.TestCase):
    def make_git_repo(self, repo, branch="feature/test"):
        repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", branch, str(repo)], check=True)
        (repo / "tracked.txt").write_text("bundle regression\n")
        subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture"], check=True)

    def test_git_push_wrapper_streams_a_real_bundle_without_stdout_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            self.make_git_repo(repo)
            bindir = root / "bin"
            bindir.mkdir()
            hc = bindir / "hc"
            hc.write_text('#!/bin/sh\ncat > "$BUNDLE_CAPTURE"\ngit bundle verify "$BUNDLE_CAPTURE" > "$VERIFY_CAPTURE" 2>&1\n')
            hc.chmod(0o755)
            capture, verify = root / "received.bundle", root / "verify.log"
            env = os.environ.copy()
            env.update({"PATH": f"{bindir}:/usr/bin:/bin", "BUNDLE_CAPTURE": str(capture), "VERIFY_CAPTURE": str(verify), "WID_GH_REMOTE_SCRIPT": "/remote/gh-app-remote.py"})
            result = subprocess.run([str(ROOT / "scripts/git-app-push.sh"), "developer", "pro-max-ultra/tmc-infrastructure", str(repo), "feature/test"], capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            verify_result = subprocess.run(["git", "bundle", "list-heads", str(capture)], capture_output=True, text=True, check=True)
            self.assertIn("refs/heads/feature/test", verify_result.stdout)
            self.assertIn("The bundle records a complete history", verify.read_text())

    def test_remote_hc_receives_arguments_and_stdin_without_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bindir = root / "bin"
            bindir.mkdir()
            hc = bindir / "hc"
            hc.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$ARGS_FILE"\ncat > "$INPUT_FILE"\n')
            hc.chmod(0o755)
            args_file, input_file = root / "args", root / "input"
            env = os.environ.copy()
            env.update({"PATH": f"{bindir}:/usr/bin:/bin", "ARGS_FILE": str(args_file), "INPUT_FILE": str(input_file), "WID_GH_REMOTE_SCRIPT": "/remote/gh-app-remote.py"})
            result = subprocess.run([str(ROOT / "scripts/gh-app.sh"), "developer", "pro-max-ultra/tmc-infrastructure", "--", "gh", "pr", "create", "--title", "spaces allowed"], input="body from stdin", text=True, capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            args = args_file.read_text().splitlines()
            self.assertEqual(args[:3], ["exec", "--stdin", "--on"])
            self.assertIn("/remote/gh-app-remote.py", args)
            self.assertEqual(args[-4:], ["pr", "create", "--title", "spaces allowed"])
            self.assertEqual(input_file.read_text(), "body from stdin")
            self.assertNotIn("token", args_file.read_text().lower())

    def test_m2_mini_runs_local_broker_without_hc_self_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bindir = root / "bin"
            bindir.mkdir()
            uname = bindir / "uname"
            uname.write_text('#!/bin/sh\necho Darwin\n')
            uname.chmod(0o755)
            python = bindir / "python3"
            python.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$ARGS_FILE"\ncat > "$INPUT_FILE"\n')
            python.chmod(0o755)
            apps = root / "apps.toml"
            apps.write_text("")
            args_file, input_file = root / "args", root / "input"
            env = os.environ.copy()
            env.update({"PATH": f"{bindir}:/usr/bin:/bin", "HOME": str(root), "WID_APPS_TOML": str(apps), "ARGS_FILE": str(args_file), "INPUT_FILE": str(input_file)})
            result = subprocess.run([str(ROOT / "scripts/gh-app.sh"), "tech-lead", "pro-max-ultra/tmc-infrastructure", "--", "gh", "pr", "view"], input="", text=True, capture_output=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            args = args_file.read_text().splitlines()
            self.assertTrue(args[0].endswith("gh-app-remote.py"))
            self.assertEqual(args[1:4], ["tech-lead", "pro-max-ultra/tmc-infrastructure", "--"])
            self.assertEqual(args[4:], ["pr", "view"])


if __name__ == "__main__":
    unittest.main()
