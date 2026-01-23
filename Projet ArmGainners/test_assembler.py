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
    
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            print(f"Warning: {test_dir} not found")
            continue
        
        for filename in os.listdir(test_dir):
            if filename.endswith('.s'):
                total_tests += 1
                s_file = os.path.join(test_dir, filename)
                bin_file = os.path.join(test_dir, filename.replace('.s', '.bin'))
                temp_bin = s_file.replace('.s', '_temp.bin')
                
                if not os.path.exists(bin_file):
                    print(f"Warning: Expected {bin_file} not found")
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
                        print(f"✓ {s_file}")
                    else:
                        failed_tests.append((s_file, msg))
                        print(f"✗ {s_file}: {msg}")
                    
                    os.remove(temp_bin)
                    
                except Exception as e:
                    failed_tests.append((s_file, str(e)))
                    print(f"✗ {s_file}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Integration Tests: {passed_tests}/{total_tests} passed")
    print(f"Coverage: {100*passed_tests/total_tests if total_tests > 0 else 0:.1f}%")
    
    if failed_tests:
        print(f"\nFailed tests:")
        for test, reason in failed_tests:
            print(f"  - {test}: {reason}")
    
    return passed_tests, total_tests

def test_unit_examples():
    assembler = PARMAssembler()
    unit_tests = 0
    unit_passed = 0
    
    tests = [
        ("sub sp, #12", "b083"),
        ("movs r0, #0", "2000"),
        ("str r0, [sp, #8]", "9002"),
        ("movs r1, #1", "2101"),
        ("adds r1, r1, r2", "1889"),
        ("lsls r0, r1, #5", "0148"),
        ("lsrs r2, r3, #10", "0a9a"),
        ("asrs r4, r5, #3", "10ec"),
        ("ands r0, r1", "4008"),
        ("eors r2, r3", "405a"),
    ]
    
    print("\nUnit Tests:")
    for asm, expected in tests:
        unit_tests += 1
        try:
            result = assembler.assemble(asm)
            hex_result = f"{result[0]:04x}"
            if hex_result == expected:
                unit_passed += 1
                print(f"✓ {asm:20s} -> {hex_result}")
            else:
                print(f"✗ {asm:20s} -> {hex_result} (expected {expected})")
        except Exception as e:
            print(f"✗ {asm:20s} -> ERROR: {e}")
    
    print(f"\nUnit Tests: {unit_passed}/{unit_tests} passed")
    print(f"Coverage: {100*unit_passed/unit_tests:.1f}%")
    
    return unit_passed, unit_tests

def main():
    print("="*60)
    print("PARM Assembler Test Suite")
    print("="*60)
    
    unit_p, unit_t = test_unit_examples()
    integ_p, integ_t = test_integration_files()
    
    total_passed = unit_p + integ_p
    total_tests = unit_t + integ_t
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")
    print(f"Couverture globale: {100*total_passed/total_tests if total_tests > 0 else 0:.1f}%")
    print(f"{'='*60}")
    
    with open('Vecteurs_des_tests/coverage_report.txt', 'w') as f:
        f.write(f"Rapport couverture des tests PARM Assembler Test Coverage Report\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Tests unitaires: {unit_p}/{unit_t} ({100*unit_p/unit_t:.1f}%)\n")
        f.write(f"Tests d'integrations: {integ_p}/{integ_t} ({100*integ_p/integ_t:.1f}%)\n")
        f.write(f"Couverture totale: {total_passed}/{total_tests} ({100*total_passed/total_tests:.1f}%)\n")
    
    sys.exit(0 if total_passed == total_tests else 1)

if __name__ == "__main__":
    main()