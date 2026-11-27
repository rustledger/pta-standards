import json

from conftest import require_beancount

from ptadiff.cli import main


def test_cli_generate(tmp_path):
    out = tmp_path / "g.jsonl"
    assert main(["generate", "--format", "beancount", "--generator", "g1", "--seed", "1",
                 "--n", "5", "-o", str(out)]) == 0  # fmt: skip
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(rows) == 5 and all(set(r) == {"id", "text"} for r in rows)


def test_cli_run_and_minimize(tmp_path, fake_impl_argv, capsys):
    require_beancount()
    corpus = tmp_path / "c"
    corpus.mkdir()
    (corpus / "a.beancount").write_text(
        "2024-01-01 open Assets:A\n; BAD2\n2024-01-02 close Assets:A\n"
    )
    (corpus / "b.beancount").write_text("2024-01-01 open Assets:A\n")
    impl = " ".join(fake_impl_argv)
    rep = tmp_path / "r.json"
    assert main(["run", "--format", "beancount", "--impl", impl, "--input", str(corpus),
                 "--json", str(rep), "--minimize", "5", "--jobs", "2"]) == 0  # fmt: skip
    data = json.loads(rep.read_text())
    assert data["totals"] == {"inputs": 2, "match": 1, "mismatch": 1}
    [cat] = data["categories"]
    assert cat["key"] == "impl-more|impl:X2|top|-"
    # Not `BAD2`: without the `;` beancount reports that line too, which is
    # another category; the minimizer keeps the key.
    assert cat["minimized"] == ";BAD2"
    capsys.readouterr()
    assert main(["minimize", "--format", "beancount", "--impl", impl,
                 str(corpus / "a.beancount")]) == 0  # fmt: skip
    out = json.loads(capsys.readouterr().out)
    assert out["text"] == ";BAD2" and out["complete"]
