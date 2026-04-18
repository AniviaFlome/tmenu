{
  pkgs ? import <nixpkgs> { },
}:

let
  python = pkgs.python3.withPackages (ps: [
    ps.pytest
    ps.pytest-cov
    ps.pyfiglet
    ps.x256
  ]);
in
pkgs.mkShell {
  packages = [
    python
    pkgs.pyright
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
  '';
}
