# Build Documentation

## Package Structure

The `package.nix` file defines how tmenu is built and installed using Nix.

### Key Features

- **Python Application**: Uses `buildPythonApplication` from nixpkgs
- **Dependencies**: Automatically includes `x256` and `pyfiglet` Python packages
- **Simple Installation**: Copies the Python script directly without compilation
- **Test Support**: Includes pytest configuration for running tests

### Build Configuration

```nix
{
  lib,
  python3Packages,
}:

python3Packages.buildPythonApplication {
  pname = "tmenu";
  version = "0.1.0";

  src = ./.;
  pyproject = false;           # Not using pyproject.toml
  dontBuild = true;            # No build step needed

  propagatedBuildInputs = [    # Runtime dependencies
    x256
    pyfiglet
  ];
}
```

## Installation Layout

After building, files are installed to:

```
$out/
├── bin/
│   └── tmenu                           # Main executable
└── share/tmenu/
    ├── config/
    │   └── config.default.ini          # Default configuration
    ├── themes/
    │   └── *.ini                       # Theme files
    └── config.example.ini              # Example configuration
```

## Building

### Using Nix Flakes

```bash
# Build the package
nix build

# Run directly
nix run

# Enter development shell
nix develop
```

### Using nix-build

```bash
# Build the package
nix-build -A packages.x86_64-linux.default

# Run the built package
./result/bin/tmenu
```

## Testing

The package includes pytest-based tests:

```bash
# In nix develop shell
pytest src/test_tmenu.py

# Or during build (tests run automatically)
nix build --rebuild
```

## Dependencies

### Runtime Dependencies

- **x256**: Terminal color support library
- **pyfiglet**: ASCII art text generation (optional)

### Build Dependencies

- Python 3
- pytest (for testing)

All dependencies are automatically managed by Nix.

## Troubleshooting

### Build Fails

If `nix build` fails, check:

1. Nix is properly installed: `nix --version`
2. Flakes are enabled in your Nix configuration
3. All source files exist in the correct locations

### Missing Dependencies

The package automatically includes all required Python dependencies through `propagatedBuildInputs`. If you need to add more:

```nix
propagatedBuildInputs = with python3Packages; [
  x256
  pyfiglet
  # Add more packages here
];
```

### Testing Issues

If tests fail during build, you can skip them temporarily:

```bash
nix build --no-check
```

## Integration with Home Manager

See the main README.md for Home Manager integration examples.
