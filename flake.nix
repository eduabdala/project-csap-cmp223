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
        analysis = with pkgs; [
          snakemake
          (python3.withPackages (ps: with ps; [
            numpy pandas scipy matplotlib pyserial
          ]))
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          name = "cmp223-dev";
          packages = avr ++ bench ++ analysis;

          shellHook = ''
            echo "CMP223 devShell — AVR + analysis"
            echo "  $(avr-gcc --version | head -1)"
            echo "  build:  make -C src/firmware"
            echo "  vendor: src/scripts/vendor-pqc.sh"
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
