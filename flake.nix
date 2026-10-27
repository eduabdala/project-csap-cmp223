{
  description = "CMP223 — toolchain AVR (ATmega4809) + análise PQC reprodutível";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Cross-toolchain AVR. O conjunto pkgsCross.avr já traz o gcc com
        # avr-libc para o target; não dá para compilar avr-libc no host.
        avr = with pkgs.pkgsCross.avr.buildPackages; [
          gcc        # avr-gcc
          binutils   # avr-ld, avr-objcopy, avr-size, ...
        ];

        # Ferramentas de bancada e gravação.
        bench = with pkgs; [
          avrdude      # gravação via UPDI
          sigrok-cli   # analisador lógico
          pulseview    # visualização (opcional, GUI)
          picocom       # terminal serial
        ];

        # Stack de análise (Snakemake + Python científico).
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
            echo "CMP223 devShell — AVR + análise"
            echo "  $(avr-gcc --version | head -1)"
            echo "  build:  make -C src/firmware"
            echo "  vendor: src/scripts/vendor-kyber.sh"
          '';
        };

        # Build do firmware como pacote derivável/reprodutível.
        # Requer que pqc/kyber512/ já esteja vendorizado (vendor-kyber.sh).
        packages.firmware = pkgs.stdenv.mkDerivation {
          pname = "cmp223-firmware-kyber512";
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
