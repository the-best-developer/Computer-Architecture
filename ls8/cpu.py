"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ir = 0
        self.mar = 0
        self.mdr = 0
        self.fl = 0
        self.sp = 0xF4
        self.fl = 0b00000000

        self.ram = [0] * 256
        self.regs = [0] * 8
        
        self.HLT = 0b00000001
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.MUL = 0b10100010
        self.PUSH = 0b01000101
        self.RET = 0b00010001
        self.POP = 0b01000110
        self.CALL = 0b01010000
        self.ADD = 0b10100000
        self.CMP = 0b10100111
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110


    def load(self, file):
        """Load a program into memory."""

        address = 0

        try:
            with open(file) as file:
                for line in file:
                    comment_split = line.split("#")
                    number_string = comment_split[0].strip()

                    if number_string == '':
                        continue

                    num = int(number_string, 2)
                    # print("{:08b} is {:d}".format(num, num))
                    self.ram[address] = num
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: could not find {sys.argv[1]}")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.regs[reg_a] += self.regs[reg_b]
        
        elif op == "SUB":
            self.regs[reg_a] -= self.regs[reg_b]

        elif op == "MUL":
            self.regs[reg_a] *= self.regs[reg_b]


        else:
            raise Exception("Unsupported ALU operation")
            

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def run(self):
        """Run the CPU."""

        pc = self.pc
        ir = self.ir
        mar = self.mar
        mdr = self.mdr
        fl = self.fl
        sp = self.sp
        fl = self.fl

        ram = self.ram
        regs = self.regs

        HLT = self.HLT
        LDI = self.LDI
        PRN = self.PRN
        MUL = self.MUL
        PUSH = self.PUSH
        POP = self.POP
        CALL = self.CALL
        RET = self.RET
        ADD = self.ADD
        CMP = self.CMP
        JMP = self.JMP
        JEQ = self.JEQ
        JNE = self.JNE

        operand_a = None
        operand_a = None

        while True:
            ir = self.ram_read(pc)
            # print(ir)

            if ir == HLT:
                break
            
            operand_a = self.ram_read(pc + 1)
            operand_b = self.ram_read(pc + 2)

            if ir == LDI:
                regs[operand_a] = operand_b
                pc += 3
                continue

            if ir == PRN:
                print(regs[operand_a])
                pc += 2
                continue

            if ir == MUL:
                self.alu('MUL', operand_a, operand_b)
                pc += 3
                continue

            if ir == ADD:
                self.alu('ADD', operand_a, operand_b)
                pc += 3
                continue

            if ir == PUSH:
                register_to_read = self.ram_read(pc + 1)
                value = regs[register_to_read]

                sp -= 1
                self.ram_write(value, sp)

                pc += 2
                continue
    
            if ir == POP:
                data = self.ram_read(sp)

                register_to_read = self.ram_read(pc + 1)
                regs[register_to_read] = data
        
                sp += 1
        
                pc += 2
                continue

            if ir == CALL:
                # Address two steps ahead because our register is called one step ahead
                return_address = pc + 2
                # push return address to stack
                sp -= 1
                self.ram_write(return_address, sp)
        
                register_to_look_at = self.ram_read(pc + 1)
                address_to_jump_to = regs[register_to_look_at]
                pc = address_to_jump_to
                continue

            if ir == RET:
                # Read return value, should be the at the current position in the stack
                return_value = self.ram_read(sp)
                # Set jump back from subroutine 
                pc = return_value
                # Pop return value from stack(move up in stack, value will be considered free space)
                sp += 1
                continue

            if ir == CMP:

                reg_a = self.ram_read(pc + 1)
                reg_b = self.ram_read(pc + 2)

                if regs[reg_a] < regs[reg_b]:
                    fl = 0b00000100

                elif regs[reg_a] > regs[reg_b]:
                    fl = 0b00000010

                elif regs[reg_a] == regs[reg_b]:
                    fl = 0b00000001

                else:
                    fl = 0b00000000
                
                pc += 3
                continue

            if ir == JMP:

                reg = self.ram_read(pc + 1)
                jump_to = regs[reg]
                
                pc = jump_to
                continue

            if ir == JEQ:
                # Checking if equal, grab only the last bit
                masked_byte = 0b0000001
                # Grab register to jump to
                reg = self.ram_read(pc + 1)
                # Apply mask over flag to get only the last bit
                masked_value = fl & masked_byte
                # Shift over x spaces, based on where the LGE flag is set
                # Equal is the last bit, so we don't need to shift
                shifted_flag = masked_value >> 0

                if shifted_flag == 1:
                    # If true: jump
                    pc = regs[reg]
                    continue

                pc += 1
                continue

            if ir == JNE:
                # Checking if equal, grab only the last bit
                masked_byte = 0b0000001
                # Grab register to jump to
                reg = self.ram_read(pc + 1)
                # Apply mask over flag to get only the last bit
                masked_value = fl & masked_byte
                # Shift over x spaces, based on where the LGE flag is set
                # Equal is the last bit, so we don't need to shift
                shifted_flag = masked_value >> 0

                if shifted_flag == 0:
                    # If true: jump
                    pc = regs[reg]
                    continue

                pc += 1
                continue

                
                
            pc += 1

new_CPU = CPU()

if len(sys.argv) > 1:
        new_CPU.load(sys.argv[1])
        new_CPU.run()
else:
    print(f"{sys.argv[0]}: please input file")
            
