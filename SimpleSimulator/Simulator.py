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

