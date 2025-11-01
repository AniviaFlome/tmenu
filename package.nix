{
  lib,
  python3Packages,
}:

python3Packages.buildPythonApplication {
  pname = "tmenu";
  version = "0.1.0";

  src = ./.;

  pyproject = false;

  propagatedBuildInputs = with python3Packages; [
    x256
    pyfiglet
  ];

  # Don't build, just copy files
  dontBuild = true;

  # Install the application
  installPhase = ''
    runHook preInstall

    mkdir -p $out/bin
    mkdir -p $out/themes

    # Install the main script
    cp src/tmenu.py $out/bin/tmenu
    chmod +x $out/bin/tmenu

    # Install default config in same directory as script (script expects it there)
    cp src/config.default.ini $out/bin/

    # Install themes in parent directory of bin/ (script looks in ../themes/)
    cp -r themes/* $out/themes/

    runHook postInstall
  '';

  # Run tests
  nativeCheckInputs = with python3Packages; [
    pytestCheckHook
  ];

  checkPhase = ''
    runHook preCheck
    pytest src/test_tmenu.py
    runHook postCheck
  '';

  meta = with lib; {
    description = "A dmenu-like command executor for the terminal";
    homepage = "https://github.com/yourusername/tmenu";
    license = licenses.mit;
    maintainers = [ ];
    mainProgram = "tmenu";
  };
}
