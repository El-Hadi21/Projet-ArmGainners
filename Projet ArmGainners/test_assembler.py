#!/usr/bin/env python3
import os
import sys
from assembler import PARMAssembler

def compare_files(generated, expected):
    with open(generated, 'r') as f:
        gen_content = f.read().strip()
    with open(expected, 'r') as f:
        exp_content = f.read().strip()
    
    gen_lines = gen_content.split('\n')
    exp_lines = exp_content.split('\n')
    
    if gen_lines[0] != exp_lines[0]:
        return False, "Header mismatch"
    
    gen_insts = ' '.join(gen_lines[1:]).split()
    exp_insts = ' '.join(exp_lines[1:]).split()
    
    if len(gen_insts) != len(exp_insts):
        return False, f"Length mismatch: {len(gen_insts)} vs {len(exp_insts)}"
    
    for i, (g, e) in enumerate(zip(gen_insts, exp_insts)):
        if g != e:
            return False, f"Instruction {i}: {g} != {e}"
    
    return True, "OK"

def test_integration_files():
    test_dirs = [
        'code_asm/test_integration/conditional',
        'code_asm/test_integration/data_processing',
        'code_asm/test_integration/load_store',
        'code_asm/test_integration/miscellaneous',
        'code_asm/test_integration/shift_add_sub_mov'
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    assembler = PARMAssembler()
    
    print("="*60)
    print("TESTS D'INTEGRATION DU PARSEUR")
    print("="*60)
    print("")
    
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            print(f"Avertissement: {test_dir} introuvable")
            continue
        
        for filename in os.listdir(test_dir):
            if filename.endswith('.s'):
                total_tests += 1
                s_file = os.path.join(test_dir, filename)
                bin_file = os.path.join(test_dir, filename.replace('.s', '.bin'))
                temp_bin = s_file.replace('.s', '_temp.bin')
                
                if not os.path.exists(bin_file):
                    print(f"Avertissement: {bin_file} attendu introuvable")
                    continue
                
                try:
                    with open(s_file, 'r') as f:
                        asm_code = f.read()
                    
                    instructions = assembler.assemble(asm_code)
                    logisim_output = assembler.to_logisim_format(instructions)
                    
                    with open(temp_bin, 'w') as f:
                        f.write(logisim_output)
                    
                    success, msg = compare_files(temp_bin, bin_file)
                    
                    if success:
                        passed_tests += 1
                        print(f"[OK] {s_file}")
                    else:
                        failed_tests.append((s_file, msg))
                        print(f"[ECHEC] {s_file}: {msg}")
                    
                    os.remove(temp_bin)
                    
                except Exception as e:
                    failed_tests.append((s_file, str(e)))
                    print(f"[ECHEC] {s_file}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Tests d'integration parseur: {passed_tests}/{total_tests} reussis")
    print(f"Taux de couverture: {100*passed_tests/total_tests if total_tests > 0 else 0:.1f}%")
    print(f"{'='*60}")
    
    if failed_tests:
        print(f"\nTests echoues:")
        for test, reason in failed_tests:
            print(f"  - {test}: {reason}")
    
    return passed_tests, total_tests

def main():
    integ_p, integ_t = test_integration_files()
    
    os.makedirs('Vecteurs_des_tests', exist_ok=True)
    with open('Vecteurs_des_tests/coverage_report.txt', 'w') as f:
        f.write(f"RAPPORT DE COUVERTURE DES TESTS - PROJET PARM\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"TESTS D'INTEGRATION DU PARSEUR (assembleur)\n")
        f.write(f"{'-'*60}\n")
        f.write(f"Tests reussis: {integ_p}/{integ_t}\n")
        f.write(f"Taux de couverture: {100*integ_p/integ_t if integ_t > 0 else 0:.1f}%\n\n")
        f.write(f"TESTS D'INTEGRATION DU CPU (Logisim)\n")
        f.write(f"{'-'*60}\n")
        f.write(f"A completer manuellement apres tests dans Logisim\n")
        f.write(f"Instructions testees: [ ] / [ ]\n")
        f.write(f"Taux de couverture: [ ]%\n\n")
        f.write(f"{'='*60}\n")
        f.write(f"Note: Les tests CPU doivent etre realises dans Logisim\n")
        f.write(f"en chargeant les fichiers .bin dans la ROM.\n")
    
    print(f"\nRapport sauvegarde: Vecteurs_des_tests/coverage_report.txt")
    
    sys.exit(0 if integ_p == integ_t else 1)

if __name__ == "__main__":
    main()