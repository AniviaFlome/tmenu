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

  dontBuild = true;

  installPhase = ''
    runHook preInstall

    mkdir -p $out/bin
    mkdir -p $out/themes

    cp src/tmenu.py $out/bin/tmenu
    chmod +x $out/bin/tmenu
    cp src/config.default.ini $out/bin/
    cp -r themes/* $out/themes/

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
    mainProgram = "tmenu";
  };
}
