{
  description = "PTA Standards - Plain Text Accounting specification and conformance tests";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Python environment for test harness
        pythonEnv = pkgs.python312.withPackages (ps: with ps; [
          pytest
          pyyaml
        ]);

      in
      {
        packages.default = pkgs.buildEnv {
          name = "pta-tools";
          paths = with pkgs; [ beancount hledger ledger ];
        };

        devShells.default = pkgs.mkShell {
          name = "pta-standards";

          buildInputs = with pkgs; [
            # PTA tools
            beancount
            hledger
            ledger

            # Python for test harness
            pythonEnv

            # Node.js for tree-sitter
            nodejs_20

            # Tree-sitter
            tree-sitter

            # Documentation
            mdbook
            pandoc

            # JSON/YAML tools
            jq
            yq-go

            # Development
            git
            gh
            pre-commit

            # Shell utilities
            ripgrep
            fd
          ];

          shellHook = ''
            echo "PTA Standards Development Environment"
            echo ""
            echo "Tools:"
            echo "  beancount:   $(bean-check --version 2>&1 | head -1 || echo 'v3')"
            echo "  hledger:     $(hledger --version | head -1)"
            echo "  ledger:      $(ledger --version | head -1)"
            echo "  tree-sitter: $(tree-sitter --version)"
            echo ""
            echo "Run tests:"
            echo "  python tests/harness/runners/python/runner.py --manifest tests/beancount/v3/manifest.json"
            echo ""
          '';
        };

        checks = {
          test-harness = pkgs.runCommand "check-test-harness" {
            buildInputs = [ pythonEnv pkgs.beancount ];
          } ''
            cd ${self}
            python -c "import json, yaml; print('OK')"
            touch $out
          '';
        };
      }
    );
}
