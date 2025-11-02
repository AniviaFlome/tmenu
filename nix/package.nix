{
  lib,
  python3Packages,
}:

python3Packages.buildPythonApplication {
  pname = "tmenu";
  version = "0.1.0";

  src = ./..;

  format = "other";

  propagatedBuildInputs = with python3Packages; [
    x256
    pyfiglet
  ];

  installPhase = ''
    mkdir -p $out/bin
    mkdir -p $out/themes

    # Install the main script
    cp src/tmenu.py $out/bin/tmenu
    chmod +x $out/bin/tmenu

    # Install default config in same directory as script (script expects it there)
    cp src/config.default.ini $out/bin/

    # Install themes in parent directory of bin/ (script looks in ../themes/)
    cp themes/*.ini $out/themes/
  '';

  meta = with lib; {
    description = "A dmenu-like command executor for the terminal";
    homepage = "https://github.com/AniviaFlome/tmenu";
    license = licenses.mit0;
    maintainers = [ AniviaFlome ];
    platforms = lib.platforms.all;
    mainProgram = "tmenu";
  };
}
