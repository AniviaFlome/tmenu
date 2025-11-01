{
  lib,
  python3Packages,
  fetchFromGitHub,
}:

python3Packages.buildPythonApplication {
  pname = "tmenu";
  version = "0.1.0";

  src = ./..;

  format = "other";

  installPhase = ''
    mkdir -p $out/bin

    # Copy tmenu.py and config.default.ini to bin directory
    cp src/tmenu.py $out/bin/tmenu
    cp src/config.default.ini $out/bin/config.default.ini
    chmod +x $out/bin/tmenu

    # Copy themes to share
    mkdir -p $out/share/tmenu/themes
    cp themes/*.ini $out/share/tmenu/themes/
  '';

  meta = with lib; {
    description = "A dmenu-like command executor for the terminal";
    homepage = "https://github.com/AniviaFlome/tmenu";
    license = licenses.mit0;
    maintainers = [ AniviaFlome ];
    platforms = platforms.unix;
    mainProgram = "tmenu";
  };
}
