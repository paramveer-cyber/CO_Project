REGISTERS = {"zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4,"t0": 5, "t1": 6, "t2": 7,"s0": 8, "fp": 8, "s1": 9,"a0": 10, "a1": 11, "a2": 12, "a3": 13,"a4": 14, "a5": 15, "a6": 16, "a7": 17,"s2": 18, "s3": 19, "s4": 20, "s5": 21,"s6": 22, "s7": 23, "s8": 24, "s9": 25,"s10": 26, "s11": 27,"t3": 28, "t4": 29, "t5": 30, "t6": 31}

for i in range(32):
    REGISTERS[f"x{i}"] = i

COMMANDS = ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "or", "and"]

R_TYPE = {"add":  ("0000000", "000"),"sub":  ("0100000", "000"),"sll":  ("0000000", "001"),"slt":  ("0000000", "010"),"sltu": ("0000000", "011"),"xor":  ("0000000", "100"),"srl":  ("0000000", "101"),"or": ("0000000", "110"),"and": ("0000000", "111")}

def reg_to_bin(reg):
    return format(REGISTERS[reg], "05b")

def assemble(lines):
    outputLines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        
    return outputLines

