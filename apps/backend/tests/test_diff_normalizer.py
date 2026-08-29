from app.github.diff_normalizer import is_noisy_file, normalize_commit_files


def test_noisy_file_filtering() -> None:
    assert is_noisy_file("pnpm-lock.yaml") is True
    assert is_noisy_file("package-lock.json") is True
    assert is_noisy_file("uv.lock") is True
    assert is_noisy_file("node_modules/foo/bar.js") is True
    assert is_noisy_file("dist/bundle.min.js") is True
    assert is_noisy_file(".pytest_cache/v/cache/node") is True
    assert is_noisy_file("src/notifications/poller.ts") is False
    assert is_noisy_file("app/main.py") is False


def test_normalize_commit_files() -> None:
    raw = [
        {"filename": "pnpm-lock.yaml", "additions": 100, "deletions": 50},
        {
            "filename": "src/poller.ts",
            "status": "modified",
            "additions": 20,
            "deletions": 5,
            "patch": "+ const x = 1;",
        },
        {
            "filename": "dist/bundle.min.js",
            "status": "added",
            "additions": 500,
            "deletions": 0,
        },
    ]

    files = normalize_commit_files(raw)
    assert len(files) == 1
    assert files[0].path == "src/poller.ts"
    assert files[0].additions == 20
    assert files[0].patch == "+ const x = 1;"
