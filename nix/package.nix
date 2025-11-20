{
  lib,
  python3Packages,
}:

python3Packages.buildPythonApplication {
  pname = "tmenu";
  version = "0.1.0";

  src = ../.;

  pyproject = true;

  build-system = with python3Packages; [
    setuptools
    wheel
  ];

  propagatedBuildInputs = with python3Packages; [
    x256
    pyfiglet
    tomli
  ];

  nativeCheckInputs = with python3Packages; [
    pytestCheckHook
  ];

  pythonImportsCheck = [ "tmenu" ];

  meta = with lib; {
    description = "dmenu for terminal";
    homepage = "https://github.com/AniviaFlome/tmenu";
    license = licenses.mit;
    maintainers = [ AniviaFlome ];
    platforms = lib.platforms.all;
    mainProgram = "tmenu";
  };
}
