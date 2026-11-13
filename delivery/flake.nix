{
  description = "CMP223 — AVR toolchain (ATmega4809) + reproducible PQC analysis";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # AVR cross-toolchain. The pkgsCross.avr set already ships gcc with
        # avr-libc for the target; avr-libc cannot be built on the host.
        avr = with pkgs.pkgsCross.avr.buildPackages; [
          gcc        # avr-gcc
          binutils   # avr-ld, avr-objcopy, avr-size, ...
        ];

        # Bench and programming tools.
        bench = with pkgs; [
          avrdude      # programming via UPDI
          sigrok-cli   # logic analyzer
          pulseview    # visualization (optional, GUI)
          picocom      # serial terminal
        ];

        # Analysis stack (Snakemake + scientific Python).
        #
        # pyDOE3 is not (yet) in nixpkgs (see NixOS/nixpkgs#309784), so we build
        # it inline from PyPI, pinned by hash for reproducibility.
        pyDOE3 = pkgs.python3Packages.buildPythonPackage rec {
          pname = "pyDOE3";
          version = "1.0.3";
          pyproject = true;
          src = pkgs.python3Packages.fetchPypi {
            pname = "pydoe3";
            inherit version;
            hash = "sha256-4FR9e5GdzSWavZa5HqVvjRpB9j79bzk+rNvAZpfWA04=";
          };
          nativeBuildInputs = with pkgs.python3Packages; [ hatchling hatch-vcs ];
          propagatedBuildInputs = with pkgs.python3Packages; [ numpy scipy ];
          doCheck = false;
        };

        # R + Quarto + TeX Live (Linux Libertine / acmart + TikZ) for analise.qmd.
        rPkgs = with pkgs.rPackages; [
          tidyverse
          patchwork
          ggdist
          emmeans
          car
          tikzDevice
          ragg
          systemfonts
          jpeg
          knitr
          rmarkdown
        ];

        rEnv = pkgs.rWrapper.override { packages = rPkgs; };
        quartoEnv = pkgs.quarto.override { extraRPackages = rPkgs; };

        tex = pkgs.texlive.combine {
          inherit (pkgs.texlive)
            scheme-medium
            acmart
            babel-portuges
            comment
            environ
            fontaxes
            hyperxmp
            ifmtarg
            inconsolata
            kastrup
            libertine
            mweights
            ncctools
            newtx
            preprint
            preview
            totpages
            trimspaces
            upquote
            xstring;
        };

        analysis = with pkgs; [
          snakemake
          nodejs
          rEnv
          quartoEnv
          tex
          (python3.withPackages (ps: with ps; [
            numpy
            pandas
            scipy
            statsmodels
            matplotlib
            seaborn
            plotnine
            pillow
            jupyter
            nbconvert
            ipykernel
            pyserial
            pyyaml
          ] ++ [ pyDOE3 ]))
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          name = "cmp223-dev";
          packages = avr ++ bench ++ analysis ++ [ pkgs.glibcLocales ];
          LOCALE_ARCHIVE = "${pkgs.glibcLocales}/lib/locale/locale-archive";
          LC_ALL = "C.UTF-8";
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
          ];

          shellHook = ''
            echo "CMP223 devShell — AVR + analysis"
            echo "  $(avr-gcc --version | head -1)"
            echo "  build:  make -C src/firmware"
            echo "  vendor: src/scripts/vendor-pqc.sh"
          '';
        };

        # Lightweight shell only for building and flashing the firmware (no Python/Snakemake).
        devShells.firmware = pkgs.mkShell {
          name = "cmp223-firmware";
          packages = avr ++ [ pkgs.avrdude pkgs.picocom ];

          shellHook = ''
            echo "CMP223 firmware shell — AVR toolchain + avrdude"
            echo "  $(avr-gcc --version | head -1)"
            echo "  build:  make -C src/firmware ALG=kyber512 VARIANT=asm OPT=-O3"
            echo "  flash:  make -C src/firmware ALG=kyber512 VARIANT=asm flash PORT=/dev/ttyACM0"
          '';
        };

        # Firmware build as a derivable/reproducible package.
        # Requires pqc/<alg>/<variant>/ to be vendored first (vendor-pqc.sh).
        packages.firmware = pkgs.stdenv.mkDerivation {
          pname = "cmp223-firmware";
          version = "0.1.0";
          src = ./src/firmware;
          nativeBuildInputs = with pkgs.pkgsCross.avr.buildPackages; [ gcc binutils ];
          buildPhase = "make";
          installPhase = ''
            mkdir -p $out
            cp build/*.hex build/*.elf build/*.map $out/ 2>/dev/null || true
          '';
        };
      });
}
