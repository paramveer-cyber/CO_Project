import sys

REGISTERS = {"zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4,"t0": 5, "t1": 6, "t2": 7,"s0": 8, "fp": 8, "s1": 9,"a0": 10, "a1": 11, "a2": 12, "a3": 13,"a4": 14, "a5": 15, "a6": 16, "a7": 17,"s2": 18, "s3": 19, "s4": 20, "s5": 21,"s6": 22, "s7": 23,"s8": 24, "s9": 25,"s10": 26, "s11": 27,"t3": 28, "t4": 29, "t5": 30, "t6": 31}

for i in range(32):
    REGISTERS[f"x{i}"] = i

COMMANDS = ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "or", "and", "lw", "addi", "sltiu", "jalr", "sw","beq","bne","bge","bgeu","blt","bltu","jal","lui","auipc"]

R_TYPE = {"add":  ("0000000", "000"),"sub":  ("0100000", "000"),"sll":  ("0000000", "001"),"slt":  ("0000000", "010"),"sltu": ("0000000", "011"),"xor":  ("0000000", "100"),"srl":  ("0000000", "101"), "or": ("0000000", "110"),"and": ("0000000", "111")}

I_TYPE = {"lw": ("010","0000011"), "addi": ("000", "0010011"), "sltiu": ("011","0010011"), "jalr": ("000", "1100111")}

S_TYPE = {"sw": ("010", "0100011")}

B_type={"beq":("000","1100011"),"bne":("001","1100011"),"blt":("100","1100011"),"bge":("101","1100011"),"bltu":("110","1100011"),"bgeu":("111","1100011")}

J_type={"jal": "1101111"}

U_type={"lui":("0110111"),"auipc":("0010111")}  

def reg_to_bin(reg):
    return format(REGISTERS[reg], "05b")

def assemble(lines):
    outputLines = []
    label={}
    address=0
    pcCounter=0

    processed_lines=[]

    for i in range(len(lines)):
        line = lines[i].strip()

        if not line:
            continue

        firstSep=line.split(maxsplit=1)

        if firstSep[0].endswith(":"):
            label_name=firstSep[0][:-1]

            if not label_name[0].isalpha():
                print(f"Error at line {i+1}: Invalid label name")
                outputLines.append(f"Error at line {i+1}: Invalid label name")
                continue

            label[label_name]=address

            if len(firstSep)==1:
                continue

            line=firstSep[-1].strip()

        processed_lines.append((line,i+1))
        address+=4

    halt_found = False
    for line,_ in processed_lines:
        if line.replace(" ","") == "beqzero,zero,0":
            halt_found = True
            break

    if not halt_found:
        print("Error: Missing Virtual Halt instruction")
        return ["Error: Missing Virtual Halt instruction"]

    for line,lineno in processed_lines:

        finalSeparation = line.split(maxsplit=1)
        if len(finalSeparation) != 2:
            print(f"Error at line {lineno}: Invalid Input Format!")
            outputLines.append(f"Error at line {lineno}: Invalid Input Format!")
            continue
        instr, rest = finalSeparation
        
        if instr not in COMMANDS:
            print(f"Error at line {lineno}: Unsupported instruction")
            outputLines.append(f"Error at line {lineno}: Unsupported instruction")
            continue

        if instr in R_TYPE:
            rd, rs1, rs2 = rest.split(",")

            rd=rd.strip()
            rs1=rs1.strip()
            rs2=rs2.strip()
            
            if rd not in REGISTERS or rs1 not in REGISTERS or rs2 not in REGISTERS:
                print(f"Error at line {lineno}: Unsupported register used")
                outputLines.append(f"Error at line {lineno}: Unsupported register used")
                continue

            funct7, funct3 = R_TYPE[instr]
            binary = (funct7 + reg_to_bin(rs2) + reg_to_bin(rs1) + funct3 + reg_to_bin(rd) + "0110011")
            outputLines.append(binary)
        
        elif instr in S_TYPE:
            funct3, opcode = S_TYPE[instr]
            try:
                rs2, addr_part = rest.split(",")
                imm_str, rs1 = addr_part.strip().replace(")", "").split("(")
                rs1 = rs1.strip()
                imm = int(imm_str, 0)
            except:
                print(f"Error at line {lineno}: Invalid S-type format")
                outputLines.append(f"Error at line {lineno}: Invalid S-type format")
                continue

            rs1=rs1.strip()
            rs2=rs2.strip()

            if rs1 not in REGISTERS or rs2 not in REGISTERS:
                print(f"Error at line {lineno}: Unsupported register used")
                outputLines.append(f"Error at line {lineno}: Unsupported register used")
                continue

            if imm < -2048 or imm > 2047:
                print(f"Error at line {lineno}: Immediate out of 12-bit signed range")
                outputLines.append(f"Error at line {lineno}: Immediate out of 12-bit signed range")
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

        elif instr in I_TYPE:
            funct3, opcode = I_TYPE[instr]

            try:
                if instr == "lw":
                    rd, addr_part = rest.split(",")
                    imm_str, rs1 = addr_part.strip().replace(")", "").split("(")
                    rs1 = rs1.strip()
                    imm = int(imm_str, 0)
                else:
                    rd, rs1, imm_str = rest.split(",")
                    imm = int(imm_str.strip(), 0)
            except:
                print(f"Error at line {lineno}: Invalid I-type format")
                outputLines.append(f"Error at line {lineno}: Invalid I-type format")
                continue
            
            rd=rd.strip()
            rs1=rs1.strip()

            if rd not in REGISTERS or rs1 not in REGISTERS:
                print(f"Error at line {lineno}: Unsupported register used")
                outputLines.append(f"Error at line {lineno}: Unsupported register used")
                continue

            if imm < -2048 or imm > 2047:
                print(f"Error at line {lineno}: Immediate out of 12-bit signed range")
                outputLines.append(f"Error at line {lineno}: Immediate out of 12-bit signed range")
                continue

            imm_bin = format(imm & 0xFFF, "012b")
            binary = (
                imm_bin +
                reg_to_bin(rs1) +
                funct3 +
                reg_to_bin(rd) +
                opcode
            )

            outputLines.append(binary)

        elif instr in B_type:
            funct3,opcode=B_type[instr]

            try:
                rs1,rs2,imm_str=rest.split(",")
                imm=int(imm_str, 0)
            except ValueError:
                try:
                    imm=label[imm_str.strip()]-pcCounter
                except KeyError:
                    print(f"Error at line {lineno}: Invalid label")
                    outputLines.append(f"Error at line {lineno}: Invalid label")
                    continue
            except:
                print(f"Error at line {lineno}: Invalid B-type format")
                outputLines.append(f"Error at line {lineno}: Invalid B-type format")
                continue

            rs1=rs1.strip()
            rs2=rs2.strip()

            if rs1 not in REGISTERS or rs2 not in REGISTERS:
                print(f"Error at line {lineno}: Unsupported register used")
                outputLines.append(f"Error at line {lineno}: Unsupported register used")
                continue

            if imm < -4096 or imm > 4094 or imm % 2 != 0:
                print(f"Error at line {lineno}: Immediate out of B-type range")
                outputLines.append(f"Error at line {lineno}: Immediate out of B-type range")
                continue

            imm_bin = format(imm & 0x1FFF, "013b")
            binary = ( 
                imm_bin[0] + 
                imm_bin[2:8]+
                reg_to_bin(rs2.strip()) +
                reg_to_bin(rs1.strip()) +
                funct3 +
                imm_bin[8:12]+
                imm_bin[1]+
                opcode
            )
            outputLines.append(binary)

        elif instr in J_type:
            opcode=J_type[instr]

            try:
                rd,imm_str=rest.split(",")
                imm=int(imm_str, 0)
            except ValueError:
                try:
                    imm=label[imm_str.strip()]-pcCounter
                except KeyError:
                    print(f"Error at line {lineno}: Invalid label")
                    outputLines.append(f"Error at line {lineno}: Invalid label")
                    continue
            except:
                print(f"Error at line {lineno}: Invalid J-type format")
                outputLines.append(f"Error at line {lineno}: Invalid J-type format")
                continue

            rd=rd.strip()

            if rd not in REGISTERS:
                print(f"Error at line {lineno}: Unsupported register used")
                outputLines.append(f"Error at line {lineno}: Unsupported register used")
                continue
            
            if imm<-1048576 or imm>1048574:
                print(f"Error at line {lineno}: Immediate out of J-type range")
                outputLines.append(f"Error at line {lineno}: Immediate out of J-type range")
                continue

            imm_bin = format(imm & 0x1FFFFF, "021b")
            binary = ( 
                imm_bin[0] + 
                imm_bin[10:20]+
                imm_bin[9]+
                imm_bin[1:9]+
                reg_to_bin(rd.strip()) +
                opcode
            )
            outputLines.append(binary)

        elif instr in U_type:
            opcode=U_type[instr]

            try:
                rd,imm_str=rest.split(",")
                imm=int(imm_str,0)
            except:
                print(f"Error at line {lineno}: Invalid U-type format")
                outputLines.append(f"Error at line {lineno}: Invalid U-type format")
                continue

            rd=rd.strip()

            if rd not in REGISTERS:
                print(f"Error at line {lineno}: Unsupported register used")
                outputLines.append(f"Error at line {lineno}: Unsupported register used")
                continue
            
            if imm<0 or imm>1048575:
                print(f"Error at line {lineno}: Immediate out of U-type range")
                outputLines.append(f"Error at line {lineno}: Immediate out of U-type range")
                continue
            
            imm_bin = format(imm & 0xFFFFF, "020b")
            binary = ( 
                imm_bin + 
                reg_to_bin(rd.strip()) +
                opcode
            )
            outputLines.append(binary)

        pcCounter+=4

    return outputLines


if __name__ == "__main__":
    input_file=sys.argv[1]
    output_file=sys.argv[2]

    with open(input_file,"r") as f:
        lines=f.readlines()

    result=assemble(lines)

    with open(output_file,"w") as f:
        for line in result:
            f.write(line+"\n")