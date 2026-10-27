#!/usr/bin/env bash
# ============================================================
# vendor-pqc.sh — Vendoriza as fontes dos algoritmos para pqc/<alg>/<variant>/.
#
# Estrutura alvo (6 binários = 3 algoritmos × 2 variantes):
#   pqc/kyber512/ref     pqc/kyber512/asm
#   pqc/ctru-light/ref   pqc/ctru-light/asm
#   pqc/ecdh/ref         pqc/ecdh/asm
#
# Fontes:
#   - CTRU-Light + Kyber (ref e asm/AVR): artefato CHES 2026 (MIT)
#       https://github.com/whYBeKim/CTRU-Light-and-PQC-on-AVR
#   - ECDH baseline: micro-ecc (uECC). A variante "asm" usa as rotinas
#       assembly AVR embutidas no próprio micro-ecc (uECC_asm_avr).
#
# Uso:
#   scripts/vendor-pqc.sh [kyber512|ctru-light|ecdh|all]
#
# NOTA: os caminhos EXATOS dentro do artefato CHES precisam ser confirmados no
# primeiro clone (a estrutura de crypto_kem/CTRU-Light e crypto_kem/kyber varia
# por versão). Os mapeamentos abaixo estão marcados com TODO onde há incerteza.
# ============================================================
set -euo pipefail

WHAT="${1:-all}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PQC="${ROOT}/firmware/pqc"

CHES_REPO="https://github.com/whYBeKim/CTRU-Light-and-PQC-on-AVR.git"
CHES_REF="${CHES_REF:-main}"
UECC_REPO="https://github.com/kmackay/micro-ecc.git"
UECC_REF="${UECC_REF:-master}"

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

clone_ches() {
    if [ ! -d "${TMP}/ches" ]; then
        echo ">> Clonando artefato CHES (${CHES_REF})..."
        git clone --quiet "${CHES_REPO}" "${TMP}/ches"
        git -C "${TMP}/ches" checkout --quiet "${CHES_REF}"
    fi
}

stamp() {   # $1 = dir destino, $2 = fonte, $3 = repo
    git -C "$4" rev-parse HEAD > /dev/null
    cat > "$1/VENDOR.txt" <<EOF
Fonte : $2
Repo  : $3
Commit: $(git -C "$4" rev-parse HEAD)
Data  : $(date -u +%Y-%m-%dT%H:%M:%SZ)
Gerado por scripts/vendor-pqc.sh. Não editar à mão.
EOF
}

vendor_kyber() {
    clone_ches
    local base="${TMP}/ches/crypto_kem/kyber"
    echo ">> Kyber-512: ref + asm (artefato CHES)"
    # TODO: confirmar subpastas reais (ex.: .../C-ref e .../Montgomery).
    mkdir -p "${PQC}/kyber512/ref" "${PQC}/kyber512/asm"
    # ref = implementação C pura
    cp -f "${base}"/C-ref/*.c "${base}"/C-ref/*.h "${PQC}/kyber512/ref/" 2>/dev/null || \
        echo "!! ajustar caminho ref do Kyber em vendor-pqc.sh"
    # asm = Montgomery com rotinas AVR (.S)
    cp -f "${base}"/Montgomery/*.c "${base}"/Montgomery/*.h "${base}"/Montgomery/*.S \
        "${PQC}/kyber512/asm/" 2>/dev/null || \
        echo "!! ajustar caminho asm do Kyber em vendor-pqc.sh"
    stamp "${PQC}/kyber512/ref" "CHES2026 kyber/C-ref" "${CHES_REPO}" "${TMP}/ches"
    stamp "${PQC}/kyber512/asm" "CHES2026 kyber/Montgomery(asm AVR)" "${CHES_REPO}" "${TMP}/ches"
}

vendor_ctru() {
    clone_ches
    local base="${TMP}/ches/crypto_kem/CTRU-Light"
    echo ">> CTRU-Light: ref + asm (artefato CHES)"
    # TODO: confirmar subpastas reais (ex.: .../C-ref(SHA3) e .../Kred-ascon).
    mkdir -p "${PQC}/ctru-light/ref" "${PQC}/ctru-light/asm"
    cp -f "${base}"/C-ref*/*.c "${base}"/C-ref*/*.h "${PQC}/ctru-light/ref/" 2>/dev/null || \
        echo "!! ajustar caminho ref do CTRU em vendor-pqc.sh"
    cp -f "${base}"/Kred-ascon/*.c "${base}"/Kred-ascon/*.h "${base}"/Kred-ascon/*.S \
        "${PQC}/ctru-light/asm/" 2>/dev/null || \
        echo "!! ajustar caminho asm do CTRU em vendor-pqc.sh"
    stamp "${PQC}/ctru-light/ref" "CHES2026 CTRU-Light/C-ref" "${CHES_REPO}" "${TMP}/ches"
    stamp "${PQC}/ctru-light/asm" "CHES2026 CTRU-Light/Kred-ascon(asm AVR)" "${CHES_REPO}" "${TMP}/ches"
}

vendor_ecdh() {
    echo ">> ECDH: micro-ecc (ref + asm AVR embutido)"
    git clone --quiet "${UECC_REPO}" "${TMP}/uecc"
    git -C "${TMP}/uecc" checkout --quiet "${UECC_REF}"
    for v in ref asm; do
        mkdir -p "${PQC}/ecdh/${v}"
        cp -f "${TMP}/uecc/uECC.c" "${TMP}/uecc/uECC.h" "${PQC}/ecdh/${v}/"
        for f in types.h uECC_vli.h asm_arm.inc asm_avr.inc curve-specific.inc; do
            [ -f "${TMP}/uecc/${f}" ] && cp -f "${TMP}/uecc/${f}" "${PQC}/ecdh/${v}/" || true
        done
        stamp "${PQC}/ecdh/${v}" "micro-ecc (uECC)" "${UECC_REPO}" "${TMP}/uecc"
    done
    # A variante asm ativa o assembly AVR do micro-ecc via define no build.
    echo "   (variante asm: compilar com -DuECC_PLATFORM=uECC_avr -DuECC_OPTIMIZATION_LEVEL=3)"
}

case "${WHAT}" in
    kyber512)   vendor_kyber ;;
    ctru-light) vendor_ctru ;;
    ecdh)       vendor_ecdh ;;
    all)        vendor_kyber; vendor_ctru; vendor_ecdh ;;
    *) echo "Uso: $0 [kyber512|ctru-light|ecdh|all]" >&2; exit 2 ;;
esac

echo ">> OK. Confira os api.h vendorizados e ajuste os adaptadores kem_*.c se o"
echo "   prefixo de símbolo diferir (ver comentários em cada kem_*.c)."
