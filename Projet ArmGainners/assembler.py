#!/usr/bin/env python3
import re
import sys

class PARMAssembler:
    def __init__(self):
        self.registers = {f'r{i}': i for i in range(8)}
        self.registers['sp'] = 13
        
    def clean_line(self, line):
        line = re.sub(r'[@].*$', '', line)
        if line.strip().startswith('.'):
            return ''
        if re.match(r'\s*(push|add\s+r7\s*,\s*sp)', line, re.IGNORECASE):
            return ''
        return line.strip()
    
    def parse_register(self, reg_str):
        reg_str = reg_str.lower().strip()
        if reg_str in self.registers:
            return self.registers[reg_str]
        raise ValueError(f"Invalid register: {reg_str}")
    
    def parse_immediate(self, imm_str):
        imm_str = imm_str.strip().lstrip('#')
        if imm_str.startswith('0x'):
            return int(imm_str, 16)
        return int(imm_str)
    
    def encode_shift_add_sub_mov(self, mnemonic, operands):
        mnemonic = mnemonic.upper()
        
        if mnemonic == 'LSLS' and len(operands) == 3:
            rd = self.parse_register(operands[0])
            rn = self.parse_register(operands[1])
            imm5 = self.parse_immediate(operands[2])
            return (0b00000 << 11) | (imm5 << 6) | (rn << 3) | rd
        
        if mnemonic == 'LSRS' and len(operands) == 3:
            rd = self.parse_register(operands[0])
            rn = self.parse_register(operands[1])
            imm5 = self.parse_immediate(operands[2])
            return (0b00001 << 11) | (imm5 << 6) | (rn << 3) | rd
        
        if mnemonic == 'ASRS' and len(operands) == 3:
            rd = self.parse_register(operands[0])
            rn = self.parse_register(operands[1])
            imm5 = self.parse_immediate(operands[2])
            return (0b00010 << 11) | (imm5 << 6) | (rn << 3) | rd
        
        if mnemonic == 'ADDS' and len(operands) == 3 and not operands[2].startswith('#'):
            rd = self.parse_register(operands[0])
            rn = self.parse_register(operands[1])
            rm = self.parse_register(operands[2])
            return (0b0001100 << 9) | (rm << 6) | (rn << 3) | rd
        
        if mnemonic == 'SUBS' and len(operands) == 3 and not operands[2].startswith('#'):
            rd = self.parse_register(operands[0])
            rn = self.parse_register(operands[1])
            rm = self.parse_register(operands[2])
            return (0b0001101 << 9) | (rm << 6) | (rn << 3) | rd
        
        if mnemonic == 'ADDS' and len(operands) == 3 and operands[2].startswith('#'):
            rd = self.parse_register(operands[0])
            rn = self.parse_register(operands[1])
            imm3 = self.parse_immediate(operands[2])
            return (0b0001110 << 9) | (imm3 << 6) | (rn << 3) | rd
        
        if mnemonic == 'SUBS' and len(operands) == 3 and operands[2].startswith('#'):
            rd = self.parse_register(operands[0])
            rn = self.parse_register(operands[1])
            imm3 = self.parse_immediate(operands[2])
            return (0b0001111 << 9) | (imm3 << 6) | (rn << 3) | rd
        
        if mnemonic == 'MOVS':
            rd = self.parse_register(operands[0])
            imm8 = self.parse_immediate(operands[1])
            return (0b00100 << 11) | (rd << 8) | imm8
        
        if mnemonic == 'CMP' and operands[1].startswith('#'):
            rn = self.parse_register(operands[0])
            imm8 = self.parse_immediate(operands[1])
            return (0b00101 << 11) | (rn << 8) | imm8
        
        if mnemonic == 'ADDS' and len(operands) == 2:
            rdn = self.parse_register(operands[0])
            imm8 = self.parse_immediate(operands[1])
            return (0b00110 << 11) | (rdn << 8) | imm8
        
        if mnemonic == 'SUBS' and len(operands) == 2:
            rdn = self.parse_register(operands[0])
            imm8 = self.parse_immediate(operands[1])
            return (0b00111 << 11) | (rdn << 8) | imm8
        
        raise ValueError(f"Unknown instruction: {mnemonic} {operands}")
    
    def encode_data_processing(self, mnemonic, operands):
        opcodes = {
            'ANDS': 0b0000, 'EORS': 0b0001, 'LSLS': 0b0010, 'LSRS': 0b0011,
            'ASRS': 0b0100, 'ADCS': 0b0101, 'SBCS': 0b0110, 'RORS': 0b0111,
            'TST': 0b1000, 'RSBS': 0b1001, 'CMP': 0b1010, 'CMN': 0b1011,
            'ORRS': 0b1100, 'MULS': 0b1101, 'BICS': 0b1110, 'MVNS': 0b1111
        }
        
        mnemonic = mnemonic.upper()
        if mnemonic not in opcodes:
            raise ValueError(f"Unknown data processing: {mnemonic}")
        
        opcode = opcodes[mnemonic]
        
        if mnemonic == 'RSBS':
            rd = self.parse_register(operands[0])
            rn = self.parse_register(operands[1])
            return (0b010000 << 10) | (opcode << 6) | (rn << 3) | rd
        
        if mnemonic == 'MULS':
            rdm = self.parse_register(operands[0])
            rn = self.parse_register(operands[1])
            return (0b010000 << 10) | (opcode << 6) | (rn << 3) | rdm
        
        rdn = self.parse_register(operands[0])
        rm = self.parse_register(operands[1])
        return (0b010000 << 10) | (opcode << 6) | (rm << 3) | rdn
    
    def encode_load_store(self, mnemonic, operands):
        match = re.match(r'(\w+)\s*,\s*\[\s*sp\s*(?:,\s*#(\d+))?\s*\]', 
                        ','.join(operands), re.IGNORECASE)
        if not match:
            raise ValueError(f"Invalid load/store format: {operands}")
        
        rt = self.parse_register(match.group(1))
        offset = int(match.group(2)) if match.group(2) else 0
        imm8 = offset // 4
        
        if mnemonic.upper() == 'STR':
            return (0b10010 << 11) | (rt << 8) | imm8
        elif mnemonic.upper() == 'LDR':
            return (0b10011 << 11) | (rt << 8) | imm8
        
        raise ValueError(f"Unknown load/store: {mnemonic}")
    
    def encode_sp_address(self, mnemonic, operands):
        offset_str = operands[-1]
        offset = self.parse_immediate(offset_str)
        imm7 = offset // 4
        
        if mnemonic.upper() == 'ADD':
            return (0b10110000 << 8) | (0 << 7) | imm7
        elif mnemonic.upper() == 'SUB':
            return (0b10110000 << 8) | (1 << 7) | imm7
        
        raise ValueError(f"Unknown SP instruction: {mnemonic}")
    
    def encode_branch(self, mnemonic, operands, labels, current_addr):
        label = operands[0]
        
        if label not in labels:
            raise ValueError(f"Undefined label: {label}")
        
        target = labels[label]
        offset = target - current_addr - 3
        
        if len(mnemonic) > 1:
            cond_map = {
                'EQ': 0b0000, 'NE': 0b0001, 'CS': 0b0010, 'CC': 0b0011, 'HS': 0b0010, 'LO': 0b0011,
                'MI': 0b0100, 'PL': 0b0101, 'VS': 0b0110, 'VC': 0b0111,
                'HI': 0b1000, 'LS': 0b1001, 'GE': 0b1010, 'LT': 0b1011,
                'GT': 0b1100, 'LE': 0b1101, 'AL': 0b1110
            }
            cond = mnemonic[1:].upper()
            if cond not in cond_map:
                raise ValueError(f"Unknown condition: {cond}")
            
            imm8 = offset & 0xFF
            return (0b1101 << 12) | (cond_map[cond] << 8) | imm8
        
        imm11 = offset & 0x7FF
        return (0b11100 << 11) | imm11
    
    def assemble(self, asm_code):
        lines = asm_code.split('\n')
        instructions = []
        labels = {}
        
        addr = 0
        for line in lines:
            clean = self.clean_line(line)
            if not clean:
                continue
            
            if ':' in clean:
                label_name = clean.split(':')[0].strip()
                labels[label_name] = addr
                clean = clean.split(':', 1)[1].strip()
                if not clean:
                    continue
            
            addr += 1
        
        addr = 0
        for line in lines:
            clean = self.clean_line(line)
            if not clean:
                continue
            
            if ':' in clean:
                clean = clean.split(':', 1)[1].strip()
                if not clean:
                    continue
            
            parts = re.split(r'[\s,]+', clean)
            mnemonic = parts[0].upper()
            operands = [p.strip() for p in parts[1:] if p.strip()]
            
            try:
                if mnemonic.startswith('B'):
                    encoded = self.encode_branch(mnemonic, operands, labels, addr)
                elif mnemonic in ['STR', 'LDR']:
                    encoded = self.encode_load_store(mnemonic, operands)
                elif mnemonic in ['ADD', 'SUB'] and any('sp' in op.lower() for op in [mnemonic] + operands):
                    encoded = self.encode_sp_address(mnemonic, operands)
                elif mnemonic in ['ANDS', 'EORS', 'ADCS', 'SBCS', 'RORS', 
                                 'TST', 'RSBS', 'CMN', 'ORRS', 'MULS', 'BICS', 'MVNS']:
                    encoded = self.encode_data_processing(mnemonic, operands)
                elif mnemonic in ['LSLS', 'LSRS', 'ASRS'] and len(operands) == 2:
                    encoded = self.encode_data_processing(mnemonic, operands)
                elif mnemonic == 'CMP' and not operands[1].startswith('#'):
                    encoded = self.encode_data_processing(mnemonic, operands)
                else:
                    encoded = self.encode_shift_add_sub_mov(mnemonic, operands)
                
                instructions.append(encoded)
                addr += 1
                
            except Exception as e:
                print(f"Error at line {addr}: {line.strip()}", file=sys.stderr)
                print(f"  -> {e}", file=sys.stderr)
                raise
        
        return instructions
    
    def to_logisim_format(self, instructions):
        output = "v2.0 raw\n"
        hex_insts = [f"{inst:04x}" for inst in instructions]
        output += " ".join(hex_insts)
        return output

def main():
    if len(sys.argv) < 2:
        print("Usage: python assembler.py input.s [output.bin]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.s', '.bin')
    
    with open(input_file, 'r') as f:
        asm_code = f.read()
    
    assembler = PARMAssembler()
    instructions = assembler.assemble(asm_code)
    logisim_output = assembler.to_logisim_format(instructions)
    
    with open(output_file, 'w') as f:
        f.write(logisim_output)
    
    print(f"Assembled {len(instructions)} instructions -> {output_file}")

if __name__ == "__main__":
    main()