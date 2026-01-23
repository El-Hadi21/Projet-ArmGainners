#!/bin/bash

echo "================================"
echo "PARM Project Test Runner"
echo "================================"

chmod +x assembler.py
chmod +x test_assembler.py

echo -e "\n[1/2] Execution des tests assembler..."
python3 test_assembler.py

echo -e "\n[2/2] Assemblage de tous les programmes C..."
for c_file in code_c/*.c; do
    s_file="${c_file%.c}.s"
    bin_file="${c_file%.c}.bin"
    
    if [ -f "$s_file" ]; then
        echo "Assembling $s_file..."
        python3 assembler.py "$s_file" "$bin_file"
    fi
done

echo -e "\n================================"
echo "Tous les tests sont effectues"
echo "Verifier Vecteurs_des_tests/coverage_report.txt pour examiner les details"
echo "================================"