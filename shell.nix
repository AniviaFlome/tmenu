{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python and dependencies
    python3
    python3Packages.pytest
    python3Packages.pytest-cov

    # Development tools
    pyright
    python3Packages.flake8
    python3Packages.mypy
    python3Packages.pyfiglet
    python3Packages.x256
  ];

  shellHook = ''
    echo "tmenu development environment"
    echo "Python version: $(python3 --version)"
    echo ""
    echo "Available commands:"
    echo "  python -m tmenu          - Run tmenu"
    echo "  nix fmt                  - Format all files"
    echo "  pytest                   - Run tests"
    echo "  pyright tmenu/           - Check errors"
    echo "  flake8 tmenu/            - Lint code"
    echo "  mypy tmenu/              - Type check code"
  '';
}
