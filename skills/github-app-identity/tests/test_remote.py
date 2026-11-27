#!/usr/bin/env python3
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).parents[1] / "scripts" / "gh-app-remote.py"
spec = importlib.util.spec_from_file_location("gh_app_remote", SCRIPT)
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)


class Response(io.BytesIO):
    pass


class RemoteTests(unittest.TestCase):
    def test_cache_is_scoped_by_role_and_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            apps = root / "apps.toml"
            apps.write_text("""[tmc-developer]\napp_id=1\ninstallation_id=2\npem='/tmp/key.pem'\n[wid-developer]\napp_id=11\ninstallation_id=12\npem='/tmp/legacy-key.pem'\n[wid-tech-lead]\napp_id=3\ninstallation_id=4\npem='/tmp/key2.pem'\n""")
            api_calls = []

            def open_url(request, timeout):
                api_calls.append(request)
                if request.data is None:
                    return Response(json.dumps({"account": {"login": "pro-max-ultra"}}).encode())
                return Response(json.dumps({"token": f"token-{len(api_calls)}", "expires_at": "2099-01-01T00:00:00Z"}).encode())

            signed = mock.Mock(returncode=0, stdout=b"signature")
            with mock.patch.dict(os.environ, {"WID_APPS_TOML": str(apps), "WID_CACHE_DIR": str(root / "cache"), "WID_GH_API": "https://api.test"}), \
                 mock.patch.object(remote.subprocess, "run", return_value=signed), \
                 mock.patch.object(remote, "urlopen", side_effect=open_url):
                first = remote.mint("developer", "pro-max-ultra/tmc-infrastructure")
                self.assertEqual(first, remote.mint("developer", "pro-max-ultra/tmc-infrastructure"))
                remote.mint("developer", "pro-max-ultra/star-jar")
                remote.mint("tech-lead", "pro-max-ultra/tmc-infrastructure")

            self.assertEqual(len(api_calls), 6)
            token_requests = [request for request in api_calls if request.data is not None]
            payload = json.loads(token_requests[0].data)
            self.assertEqual(payload["repositories"], ["tmc-infrastructure"])
            self.assertEqual(payload["permissions"]["contents"], "write")

            def issuer(request):
                claims = request.get_header("Authorization").split()[1].split(".")[1]
                claims += "=" * (-len(claims) % 4)
                return json.loads(remote.base64.urlsafe_b64decode(claims))["iss"]

            self.assertEqual(issuer(token_requests[0]), "1")
            self.assertEqual(issuer(token_requests[-1]), "3")
            cache_files = list((root / "cache").glob("gh-token-*.json"))
            self.assertEqual(len(cache_files), 3)
            self.assertTrue(all((path.stat().st_mode & 0o777) == 0o600 for path in cache_files))

    def test_gh_receives_scoped_token_and_isolated_config(self):
        seen = {}

        def run(argv, env, check):
            seen.update(argv=argv, env=env)
            return mock.Mock(returncode=0)

        with mock.patch.dict(os.environ, {"GITHUB_TOKEN": "personal-token", "GH_TOKEN": "caller-token"}), \
             mock.patch.object(remote, "mint", return_value="app-token"), \
             mock.patch.object(remote.subprocess, "run", side_effect=run):
            self.assertEqual(remote.main(["developer", "pro-max-ultra/tmc-infrastructure", "--", "pr", "list"]), 0)

        self.assertEqual(seen["argv"], ["gh", "pr", "list"])
        self.assertEqual(seen["env"]["GH_TOKEN"], "app-token")
        self.assertNotIn("GITHUB_TOKEN", seen["env"])
        self.assertNotIn("GH_ENTERPRISE_TOKEN", seen["env"])
        self.assertEqual(seen["env"]["GH_REPO"], "pro-max-ultra/tmc-infrastructure")
        self.assertEqual(seen["env"]["GH_HOST"], "github.com")
        self.assertTrue(seen["env"]["GH_CONFIG_DIR"].startswith(tempfile.gettempdir()))

    def test_rejects_auth_and_implicit_repository(self):
        with self.assertRaises(SystemExit) as auth:
            remote.main(["developer", "pro-max-ultra/tmc-infrastructure", "--", "auth", "token"])
        self.assertEqual(auth.exception.code, 2)
        with self.assertRaises(SystemExit) as invalid:
            remote.main(["developer", "tmc-infrastructure", "--", "pr", "list"])
        self.assertEqual(invalid.exception.code, 2)

    def test_rejects_installation_for_different_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            apps = root / "apps.toml"
            apps.write_text("[wid-developer]\napp_id=1\ninstallation_id=2\npem='/tmp/key.pem'\n")
            with mock.patch.dict(os.environ, {"WID_APPS_TOML": str(apps), "WID_CACHE_DIR": str(root / "cache"), "WID_GH_API": "https://api.test"}), \
                 mock.patch.object(remote.subprocess, "run", return_value=mock.Mock(returncode=0, stdout=b"sig")), \
                 mock.patch.object(remote, "urlopen", return_value=Response(b'{"account":{"login":"someone-else"}}')):
                with self.assertRaises(SystemExit) as rejected:
                    remote.mint("developer", "pro-max-ultra/tmc-infrastructure")
            self.assertEqual(rejected.exception.code, 1)

    def test_git_push_uses_only_host_local_ephemeral_credential(self):
        calls = []
        askpass_contents = []

        def run(argv, **kwargs):
            calls.append((argv, kwargs))
            if "push" in argv:
                askpass_contents.append(Path(kwargs["env"]["GIT_ASKPASS"]).read_text())
            return mock.Mock(returncode=0)

        class Input:
            buffer = io.BytesIO(b"test bundle bytes")

        with mock.patch.object(remote, "mint", return_value="host-only-token"), \
             mock.patch.object(remote.subprocess, "run", side_effect=run), \
             mock.patch.object(remote.sys, "stdin", Input()):
            self.assertEqual(remote.git_push("developer", "pro-max-ultra/tmc-infrastructure", "feature/test"), 0)

        self.assertEqual(len(calls), 3)
        command, options = calls[-1]
        self.assertIn("https://github.com/pro-max-ultra/tmc-infrastructure.git", command)
        self.assertEqual(command[-1], "refs/heads/feature/test:refs/heads/feature/test")
        self.assertNotIn("host-only-token", " ".join(command))
        env = options["env"]
        self.assertEqual(env["WID_GH_TOKEN"], "host-only-token")
        self.assertEqual(env["GIT_CONFIG_GLOBAL"], "/dev/null")
        self.assertEqual(env["GIT_CONFIG_VALUE_0"], "")
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")
        self.assertIn('printf \'%s\' "$WID_GH_TOKEN"', askpass_contents[0])

    def test_git_push_clones_real_bundle_and_pushes_only_requested_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            subprocess.run(["git", "init", "-q", "-b", "feature/test", str(source)], check=True)
            (source / "change.txt").write_text("real bundle\n")
            subprocess.run(["git", "-C", str(source), "add", "change.txt"], check=True)
            subprocess.run(["git", "-C", str(source), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture"], check=True)
            bundle = subprocess.run(["git", "-C", str(source), "bundle", "create", "-", "refs/heads/feature/test"], capture_output=True, check=True).stdout

            class Input:
                buffer = io.BytesIO(bundle)

            actual_run = subprocess.run
            calls = []

            def run(argv, **kwargs):
                if argv[:3] == ["git", "check-ref-format", "--branch"] or (len(argv) > 2 and argv[1:3] == ["clone", "--bare"]):
                    return actual_run(argv, **kwargs)
                if "push" in argv:
                    calls.append((argv, kwargs))
                    checkout = argv[argv.index("-C") + 1]
                    ref = actual_run(["git", "--git-dir", checkout, "show-ref", "--verify", "refs/heads/feature/test"], capture_output=True)
                    self.assertEqual(ref.returncode, 0)
                    return mock.Mock(returncode=0)
                return actual_run(argv, **kwargs)

            with mock.patch.object(remote, "mint", return_value="remote-token"), \
                 mock.patch.object(remote.subprocess, "run", side_effect=run), \
                 mock.patch.object(remote.sys, "stdin", Input()):
                self.assertEqual(remote.git_push("developer", "pro-max-ultra/tmc-infrastructure", "feature/test"), 0)

            self.assertEqual(len(calls), 1)
            push, options = calls[0]
            self.assertEqual(push[-2:], ["https://github.com/pro-max-ultra/tmc-infrastructure.git", "refs/heads/feature/test:refs/heads/feature/test"])
            self.assertNotIn("--force", push)
            self.assertNotIn("remote-token", " ".join(push))
            self.assertEqual(options["env"]["WID_GH_TOKEN"], "remote-token")


if __name__ == "__main__":
    unittest.main()
