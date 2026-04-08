import sys

registers = [0]*32
memory = {} 
registers[2] = 0b00000000000000000000000101111100

def instructionFetch(linesToRead, PC):
    if PC >= 0x00000100 or PC < 0x00000000:
        print(f"Error Occured on line no. {PC//4+1} : Program Memory overflow!")
        exit(1)
    if PC//4 >= len(linesToRead):
        print("Invalid instruction memory access")
        exit(1)
    if PC % 4 != 0:
        print("Invalid PC alignment")
        exit(1)

    instruction = linesToRead[PC//4]

    return instruction

def decode(instruction):    
    instruction = instruction.strip()
    if len(instruction) != 32:
        print("Invalid instruction length")
        exit(1)

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
            print("Invalid R-type instruction")
            exit(1)

    elif opcode == "0100011":
        decoded["type"] = "S"
        imm = instruction[0:7] + instruction[20:25]
        decoded["imm"] = int(imm, 2)
        decoded["rs2"] = int(instruction[7:12], 2)
        decoded["rs1"] = int(instruction[12:17], 2)
        decoded["funct3"] = instruction[17:20]

        decoded["working"] = "sw"
    
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

        elif opcode == "0000011":
            decoded["working"] = "lw"

        elif opcode == "1100111":
            decoded["working"] = "jalr"

    elif opcode in ["0110111", "0010111"]:
        decoded["type"] = "U"
        decoded["imm"] = int(instruction[0:20], 2)
        decoded["rd"] = int(instruction[20:25], 2)

        if opcode == "0110111":
            decoded["working"] = "lui"
        else:
            decoded["working"] = "auipc"

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

    elif opcode == "1101111":
        decoded["type"] = "J"
        imm = instruction[0] + instruction[12:20] + instruction[11] + instruction[1:11] + "0"
        decoded["imm"] = int(imm, 2)
        decoded["rd"] = int(instruction[20:25], 2)

        decoded["working"] = "jal"

    else:
        print("Unknown opcode")
        exit(1)
    
    return decoded

        
def simulate(linesToExecute, outputFilename):
    PC = 0

    # with open(outputFilename, "w") as f:
        # while True:
            # instruction = instructionFetch(linesToExecute, PC)

            
            # decodedInstruction = decode(instruction)
            # executedValues = execute(decodedInstruction, registers, PC)

            # memoryAccess(executedValues)
            # writeBack(executedValues, registers)





if __name__ == "__main__":
    input_file=sys.argv[1]
    output_file=sys.argv[2]
    with open(input_file,"r") as f:
        lines=f.readlines()
    lines = [line.strip() for line in lines]
    simulate(lines, output_file)

