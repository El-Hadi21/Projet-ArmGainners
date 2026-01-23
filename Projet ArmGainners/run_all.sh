#!/bin/bash

echo "================================================================"
echo "         PARM PROJECT - SUITE COMPLETE DE TESTS                "
echo "================================================================"
echo ""

chmod +x assembler.py 2>/dev/null
chmod +x test_assembler.py 2>/dev/null
chmod +x compile_c.sh 2>/dev/null

echo "----------------------------------------------------------------"
echo " ETAPE 1/2 : Tests d'integration du parseur                    "
echo "----------------------------------------------------------------"

if [ -f "test_assembler.py" ]; then
    python3 test_assembler.py
    TEST_RESULT=$?
else
    echo "[ERREUR] test_assembler.py introuvable"
    TEST_RESULT=1
fi

echo ""
echo "----------------------------------------------------------------"
echo " ETAPE 2/2 : Assemblage des programmes C                       "
echo "----------------------------------------------------------------"

if [ -f "compile_c.sh" ]; then
    bash compile_c.sh
else
    echo "[ERREUR] compile_c.sh introuvable"
fi

echo ""
echo "================================================================"
echo "                    RESUME FINAL                                "
echo "================================================================"

if [ $TEST_RESULT -eq 0 ]; then
    echo " [OK] Tests d'integration parseur:  REUSSIS"
else
    echo " [ECHEC] Tests d'integration parseur:  ECHOUES"
fi

C_COUNT=$(ls code_c/*.bin 2>/dev/null | wc -l)
echo " [INFO] Programmes C assembles:  $C_COUNT fichiers .bin"

echo "================================================================"
echo " Rapport:   Vecteurs_des_tests/coverage_report.txt"
echo " Binaires:  code_c/*.bin (pour tests CPU dans Logisim)"
echo "================================================================"