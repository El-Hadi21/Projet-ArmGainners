#!/bin/bash

echo "================================================================"
echo "         PARM C Compilation Pipeline                           "
echo "================================================================"

if ! command -v clang &> /dev/null; then
    echo "ERREUR: clang n'est pas installe"
    echo "   Installation: brew install llvm@8"
    exit 1
fi

CLANG_VERSION=$(clang --version | head -n1 | grep -oE '[0-9]+' | head -1)
echo "Compilateur: clang version $CLANG_VERSION"

if [ "$CLANG_VERSION" -ge 9 ]; then
    echo ""
    echo "================================================================"
    echo "AVERTISSEMENT: Clang version $CLANG_VERSION detectee"
    echo "================================================================"
    echo "Le projet PARM necessite Clang 4-8 pour la compatibilite ARM."
    echo "Clang 9+ genere des instructions incompatibles."
    echo ""
    echo "Les fichiers .s existants seront assembles directement."
    echo "Pour recompiler depuis C, installez: brew install llvm@8"
    echo "================================================================"
    echo ""
    USE_EXISTING=1
else
    USE_EXISTING=0
fi

cd code_c || exit 1

SUCCESS=0
FAILED=0

for c_file in *.c; do
    if [ -f "$c_file" ]; then
        base="${c_file%.c}"
        s_file="${base}.s"
        bin_file="${base}.bin"
        
        echo "----------------------------------------------------------------"
        echo "Fichier: $c_file"
        
        if [ $USE_EXISTING -eq 1 ]; then
            if [ -f "$s_file" ]; then
                echo "  [INFO] Utilisation du fichier .s existant"
            else
                echo "  [IGNORE] Pas de fichier .s disponible"
                FAILED=$((FAILED + 1))
                continue
            fi
        else
            echo "  [1/2] Compilation C -> Assembleur..."
            clang -S -target arm-none-eabi -mcpu=cortex-m0 -O0 -mthumb -nostdlib \
                -I./include "$c_file" -o "$s_file" 2>&1 | grep -v "warning"
            
            if [ $? -ne 0 ] || [ ! -f "$s_file" ]; then
                echo "  [ECHEC] Echec compilation C"
                FAILED=$((FAILED + 1))
                continue
            fi
            echo "  [OK] Genere: $s_file"
        fi
        
        echo "  [2/2] Assemblage -> Binaire Logisim..."
        cd ..
        python3 assembler.py "code_c/$s_file" "code_c/$bin_file" 2>&1
        
        if [ $? -eq 0 ]; then
            echo "  [OK] Genere: $bin_file"
            SUCCESS=$((SUCCESS + 1))
        else
            echo "  [ECHEC] Echec assemblage"
            FAILED=$((FAILED + 1))
        fi
        cd code_c
    fi
done

cd ..

echo ""
echo "================================================================"
echo "                    RESUME                                      "
echo "================================================================"
echo " Succes:  $SUCCESS fichiers"
echo " Echec:   $FAILED fichiers"
echo "================================================================"

if [ $SUCCESS -gt 0 ]; then
    echo ""
    echo "Fichiers .bin generes dans code_c/"
    echo "Utilisables dans Logisim (charger dans ROM)"
fi