import sys

registers = [0]*32
memory = {} 
registers[2] = 0b00000000000000000000000101111100

def error(msg, PC):
    print(f"Error Occured on line no. {PC//4 + 1} : {msg}")
    exit(1)

def sign_extend(value, bits):
    if (value >> (bits - 1)) & 1:
        return value - (1 << bits)
    return value

def instructionFetch(linesToRead, PC):
    if PC >= 0x00000100 or PC < 0x00000000:
        error("Program Memory overflow!", PC)
    if PC//4 >= len(linesToRead):
        error("Invalid instruction memory access", PC)
    if PC % 4 != 0:
        error("Invalid PC alignment", PC)

    return linesToRead[PC//4]

def decode(instruction, PC):
    instruction = instruction.strip()
    if len(instruction) != 32:
        error("Invalid instruction length", PC)

    opcode = instruction[25:32]
    decoded = {"opcode": opcode}

    if opcode == "0110011":
        decoded["type"] = "R"
        decoded["funct7"] = instruction[0:7]
        decoded["rs2"] = int(instruction[7:12], 2)
        decoded["rs1"] = int(instruction[12:17], 2)
        decoded["funct3"] = instruction[17:20]
        decoded["rd"] = int(instruction[20:25], 2)

        funct3 = decoded["funct3"]
        funct7 = decoded["funct7"]

        if funct3 == "000" and funct7 == "0000000":
            decoded["working"] = "add"
        elif funct3 == "000" and funct7 == "0100000":
            decoded["working"] = "sub"
        elif funct3 == "001":
            decoded["working"] = "sll"
        elif funct3 == "010":
            decoded["working"] = "slt"
        elif funct3 == "011":
            decoded["working"] = "sltu"
        elif funct3 == "100":
            decoded["working"] = "xor"
        elif funct3 == "101":
            decoded["working"] = "srl"
        elif funct3 == "110":
            decoded["working"] = "or"
        elif funct3 == "111":
            decoded["working"] = "and"
        else:
            error("Invalid R-type instruction", PC)

    elif opcode in ["0010011", "0000011", "1100111"]:
        decoded["type"] = "I"
        decoded["imm"] = int(instruction[0:12], 2)
        decoded["rs1"] = int(instruction[12:17], 2)
        decoded["funct3"] = instruction[17:20]
        decoded["rd"] = int(instruction[20:25], 2)

        funct3 = decoded["funct3"]

        if opcode == "0010011":
            if funct3 == "000":
                decoded["working"] = "addi"
            elif funct3 == "011":
                decoded["working"] = "sltiu"
            else:
                error("Invalid I-type instruction", PC)

        elif opcode == "0000011":
            decoded["working"] = "lw"

        elif opcode == "1100111":
            decoded["working"] = "jalr"

    elif opcode == "0100011":
        decoded["type"] = "S"
        imm = instruction[0:7] + instruction[20:25]
        decoded["imm"] = int(imm, 2)
        decoded["rs2"] = int(instruction[7:12], 2)
        decoded["rs1"] = int(instruction[12:17], 2)
        decoded["funct3"] = instruction[17:20]
        decoded["working"] = "sw"

    elif opcode == "1100011":
        decoded["type"] = "B"
        imm = instruction[0] + instruction[24] + instruction[1:7] + instruction[20:24] + "0"
        decoded["imm"] = int(imm, 2)
        decoded["rs2"] = int(instruction[7:12], 2)
        decoded["rs1"] = int(instruction[12:17], 2)
        decoded["funct3"] = instruction[17:20]

        funct3 = decoded["funct3"]

        if funct3 == "000":
            decoded["working"] = "beq"
        elif funct3 == "001":
            decoded["working"] = "bne"
        elif funct3 == "100":
            decoded["working"] = "blt"
        elif funct3 == "101":
            decoded["working"] = "bge"
        elif funct3 == "110":
            decoded["working"] = "bltu"
        elif funct3 == "111":
            decoded["working"] = "bgeu"
        else:
            error("Invalid B-type instruction", PC)

    elif opcode in ["0110111", "0010111"]:
        decoded["type"] = "U"
        decoded["imm"] = int(instruction[0:20], 2)
        decoded["rd"] = int(instruction[20:25], 2)

        if opcode == "0110111":
            decoded["working"] = "lui"
        else:
            decoded["working"] = "auipc"

    elif opcode == "1101111":
        decoded["type"] = "J"
        imm = instruction[0] + instruction[12:20] + instruction[11] + instruction[1:11] + "0"
        decoded["imm"] = int(imm, 2)
        decoded["rd"] = int(instruction[20:25], 2)
        decoded["working"] = "jal"

    else:
        error("Unknown opcode", PC)

    return decoded

def execute(decoded, registers, PC):
    nextPC = PC+4
    result = {
        "rd": None,
        "value": None,
        "mem_write": False,
        "mem_read": False,
        "mem_address": None,
        "mem_value": None,
        "nextPC": nextPC
    }

    typ = decoded["type"]
    op = decoded["working"]

    if typ == "R":
        rs1 = registers[decoded["rs1"]]
        rs2 = registers[decoded["rs2"]]

        if op == "add":
            val = rs1 + rs2
        elif op == "sub":
            val = rs1 - rs2
        elif op == "sll":
            val = rs1 << (rs2 & 0x1F)
        elif op == "slt":
            val = int(rs1 < rs2)
        elif op == "sltu":
            val = int((rs1 & 0xFFFFFFFF) < (rs2 & 0xFFFFFFFF))
        elif op == "xor":
            val = rs1 ^ rs2
        elif op == "srl":
            val = (rs1 & 0xFFFFFFFF) >> (rs2 & 0x1F)
        elif op == "or":
            val = rs1 | rs2
        elif op == "and":
            val = rs1 & rs2

        result["rd"] = decoded["rd"]
        result["value"] = val & 0xFFFFFFFF

    elif typ == "I":
        rs1 = registers[decoded["rs1"]]
        imm = sign_extend(decoded["imm"], 12)

        if op == "addi":
            result["rd"] = decoded["rd"]
            result["value"] = (rs1 + imm) & 0xFFFFFFFF

        elif op == "sltiu":
            result["rd"] = decoded["rd"]
            result["value"] = int((rs1 & 0xFFFFFFFF) < (imm & 0xFFFFFFFF))

        elif op == "lw":
            result["mem_read"] = True
            result["mem_address"] = rs1 + imm
            result["rd"] = decoded["rd"]

        elif op == "jalr":
            result["rd"] = decoded["rd"]
            result["value"] = PC + 4
            result["nextPC"] = (rs1 + imm) & ~1

    elif typ == "S":
        rs1 = registers[decoded["rs1"]]
        rs2 = registers[decoded["rs2"]]
        imm = sign_extend(decoded["imm"], 12)

        result["mem_write"] = True
        result["mem_address"] = rs1 + imm
        result["mem_value"] = rs2

    elif typ == "B":
        rs1 = registers[decoded["rs1"]]
        rs2 = registers[decoded["rs2"]]
        imm = sign_extend(decoded["imm"], 13)

        take = False

        if op == "beq":
            take = (rs1 == rs2)
        elif op == "bne":
            take = (rs1 != rs2)
        elif op == "blt":
            take = (rs1 < rs2)
        elif op == "bge":
            take = (rs1 >= rs2)
        elif op == "bltu":
            take = ((rs1 & 0xFFFFFFFF) < (rs2 & 0xFFFFFFFF))
        elif op == "bgeu":
            take = ((rs1 & 0xFFFFFFFF) >= (rs2 & 0xFFFFFFFF))

        if take:
            result["nextPC"] = PC + imm

    elif typ == "U":
        imm = decoded["imm"] << 12

        if op == "lui":
            result["rd"] = decoded["rd"]
            result["value"] = imm
        elif op == "auipc":
            result["rd"] = decoded["rd"]
            result["value"] = PC + imm

    elif typ == "J":
        imm = sign_extend(decoded["imm"], 21)
        result["rd"] = decoded["rd"]
        result["value"] = PC + 4
        result["nextPC"] = PC + imm

    return result

def memoryAccess(res, PC):
    if res["mem_read"] or res["mem_write"]:
        addr = res["mem_address"]

        if not (((0x100 <= addr <= 0x17F) or (0x10000 <= addr <= 0x1007F)) and addr % 4 == 0):
            error(f"Invalid memory access at address {addr}", PC)

    if res["mem_read"]:
        res["value"] = memory.get(addr, 0) & 0xFFFFFFFF
    elif res["mem_write"]:
        memory[addr] = res["mem_value"]

def writeBack(res, registers):
    if res["rd"] is not None and res["rd"] != 0:
        registers[res["rd"]] = res["value"]
    registers[0] = 0  

def simulate(linesToExecute, outputFilename):
    PC = 0

    with open(outputFilename, "w") as f:
        while True:
            instruction = instructionFetch(linesToExecute, PC)

            if instruction == "00000000000000000000000001100011":
                line = f"0b{format(PC, '032b')}"
                for reg in registers:
                    line += " 0b" + format(reg & 0xFFFFFFFF, '032b')
                f.write(line + "\n")
                break

            decodedInstruction = decode(instruction, PC)
            executedValues = execute(decodedInstruction, registers, PC)

            memoryAccess(executedValues, PC)
            writeBack(executedValues, registers)

            PC = executedValues["nextPC"]
            line = f"0b{format(PC, '032b')}"
            for reg in registers:
                line += " 0b" + format(reg & 0xFFFFFFFF, '032b')
            f.write(line + "\n")


        base_addr = 0x00010000

        for i in range(32):
            addr = base_addr + i*4
            val = memory.get(addr, 0)

            f.write(f"0x{addr:08X}:0b{format(val & 0xFFFFFFFF, '032b')}\n")

if __name__ == "__main__":
    input_file=sys.argv[1]
    output_file=sys.argv[2]
    with open(input_file,"r") as f:
        lines=f.readlines()
    lines = [line.strip() for line in lines]
    simulate(lines, output_file)