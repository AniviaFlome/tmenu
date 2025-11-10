{
  lib,
  python3Packages,
}:

python3Packages.buildPythonApplication {
  pname = "tmenu";
  version = "0.1.0";

  src = ../.;

  pyproject = false;

  propagatedBuildInputs = with python3Packages; [
    x256
    pyfiglet
  ];

  dontBuild = true;

  installPhase = ''
    runHook preInstall

    mkdir -p $out/bin
    mkdir -p $out/share/tmenu/themes

    # Install executable
    cp src/tmenu.py $out/bin/tmenu
    chmod +x $out/bin/tmenu

    # Install default config
    cp src/config.default.ini $out/share/tmenu/

    # Install themes folder
    cp -r themes/* $out/share/tmenu/themes/

    runHook postInstall
  '';

  nativeCheckInputs = with python3Packages; [
    pytestCheckHook
  ];

  checkPhase = ''
    runHook preCheck
    pytest src/test_tmenu.py
    runHook postCheck
  '';

  meta = with lib; {
    description = "dmenu for terminal";
    homepage = "https://github.com/AniviaFlome/tmenu";
    license = licenses.mit;
    maintainers = [ AniviaFlome ];
    platforms = lib.platforms.all;
    mainProgram = "tmenu";
  };
}
