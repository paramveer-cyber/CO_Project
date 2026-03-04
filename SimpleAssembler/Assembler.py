REGISTERS = {"zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4,"t0": 5, "t1": 6, "t2": 7,"s0": 8, "fp": 8, "s1": 9,"a0": 10, "a1": 11, "a2": 12, "a3": 13,"a4": 14, "a5": 15, "a6": 16, "a7": 17,"s2": 18, "s3": 19, "s4": 20, "s5": 21,"s6": 22, "s7": 23, "s8": 24, "s9": 25,"s10": 26, "s11": 27,"t3": 28, "t4": 29, "t5": 30, "t6": 31}

for i in range(32):
    REGISTERS[f"x{i}"] = i

COMMANDS = ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "or", "and", "lw", "addi", "sltiu", "jalr", "sw","beq","bne","bge","bgeu","blt","bltu"]

R_TYPE = {"add":  ("0000000", "000"),"sub":  ("0100000", "000"),"sll":  ("0000000", "001"),"slt":  ("0000000", "010"),"sltu": ("0000000", "011"),"xor":  ("0000000", "100"),"srl":  ("0000000", "101"),"or": ("0000000", "110"),"and": ("0000000", "111")}

I_TYPE = {"lw": ("010","0000011"), "addi": ("000", "0010011"), "sltiu": ("011","0010011"), "jalr": ("000", "1100111")}

S_TYPE = {"sw": ("010", "0100011")}

def reg_to_bin(reg):
    return format(REGISTERS[reg], "05b")

def assemble(lines):
    outputLines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue


        firstSeparation = line.split(maxsplit=1)
        instr, rest = firstSeparation
        if instr not in COMMANDS:
            print(f"Unsupported instruction: {instr}")
            outputLines.append(f"Unsupported instruction: {instr}")
            continue
        rd, rs1, rs2 = rest.split(",")
        # error support added:
        if rd not in REGISTERS or rs1 not in REGISTERS or rs2 not in REGISTERS:
            print("Unsupported register used!")
            outputLines.append("Unsupported register used!")
            continue

        #R-type done
        if instr in R_TYPE:
            rd, rs1, rs2 = rest.split(",")
            if rd not in REGISTERS or rs1 not in REGISTERS or rs2 not in REGISTERS:
                print("Unsupported register used!")
                outputLines.append("Unsupported register used!")
                continue
            funct7, funct3 = R_TYPE[instr]
            binary = (funct7 + reg_to_bin(rs2) + reg_to_bin(rs1) + funct3 + reg_to_bin(rd) + "0110011")
            outputLines.append(binary)

        #S-type 
        elif instr in S_TYPE:
            funct3, opcode = S_TYPE[instr]
            try:
                rs2, addr_part = rest.split(",")
                imm_str, rs1 = addr_part.strip().replace(")", "").split("(")
                rs1 = rs1.strip()
                imm = int(imm_str)
            except:
                outputLines.append("Invalid S-type format")
                continue

            if rs1 not in REGISTERS or rs2 not in REGISTERS:
                outputLines.append("Unsupported register used!")
                continue

            if imm < -2048 or imm > 2047:
                outputLines.append("Immediate out of 12-bit signed range")
                continue

            imm_bin = format(imm & 0b111111111111, "012b") 
            binary = (
                imm_bin[:7]  +
                reg_to_bin(rs2) +
                reg_to_bin(rs1) +
                funct3 +
                imm_bin[7:]   +
                opcode
            )

            outputLines.append(binary)
        #i type added, try except baad m
        elif instr in I_TYPE:
            funct3, opcode = I_TYPE[instr]

            if instr == "lw":
                rd, addr_part = rest.split(",")
                imm_str, rs1 = addr_part.strip().replace(")", "").split("(")
                rs1 = rs1.strip()
                imm = int(imm_str, 0)

            else:
                rd, rs1, imm_str = rest.split(",")
                imm = int(imm_str.strip(), 0)
            imm_bin = format(imm & 0xFFF, "012b")
            binary = (
                imm_bin +
                reg_to_bin(rs1) +
                funct3 +
                reg_to_bin(rd) +
                opcode
            )

            outputLines.append(binary)

    return outputLines

