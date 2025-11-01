{ pkgs, treefmt }:

pkgs.mkShell {
  nativeBuildInputs = [
    treefmt.build.wrapper
  ];

  buildInputs = with pkgs; [
    # Python and dependencies
    python3
    python3Packages.pytest
    python3Packages.pytest-cov

    # Development tools
    python3Packages.flake8
    python3Packages.mypy
    python3Packages.pyfiglet
    python3Packages.x256

    # Optional utilities
    ncurses
  ];

  shellHook = ''
    echo "tmenu development environment"
    echo "Python version: $(python3 --version)"
    echo ""
    echo "Available commands:"
    echo "  python src/tmenu.py      - Run tmenu"
    echo "  pytest                   - Run tests"
    echo "  treefmt                  - Format all files"
    echo "  flake8 src/              - Lint code"
    echo "  mypy src/                - Type check code"
  '';
}
