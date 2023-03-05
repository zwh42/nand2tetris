import os
import argparse
import logging
import re
from pprint import pprint

class HackAssembler:
    output_file_path = ""
    variable_address_base = 16 #hard-coded
    variable_address_offset = 0
    lable_offset = 0  
    symbol_table = {
        "R0": 0,
        "R1": 1,
        "R2": 2,
        "R3": 3,
        "R4": 4,
        "R5": 5,
        "R6": 6,
        "R7": 7,
        "R8": 8,
        "R9": 9,
        "R10": 10,
        "R11": 11,
        "R12": 12,
        "R13": 13,
        "R14": 14,
        "R15": 15,
        "SCREEN": 16384,
        "KBD": 24576,
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,        
    }

    comp_table = {
        # a = 0
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001111",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",

        #a = 1
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101",        
    }

    dest_table = {
        "null": "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111",
    }

    jump_table = {
        "null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }

    src_lines = []
    out_lines = []
    logger = None

    def __init__(self, src_file_path, output_file_path):
        print("Initializing Hack Assembler")
        print("source file: " + src_file_path)
        print("output file: " + output_file_path)

        self.output_file_path = output_file_path

        # print("symbol table:")
        # print(self.symbol_table)

        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)


        
        with open(src_file_path, "r") as f:
            self.src_lines = [line.strip().split("//")[0] for line in f.readlines() if ((not line.strip().startswith(r"//")) and line.strip())]

        self.logger.debug("cleaned source:")
        line_number = 0
        for line in self.src_lines:
            self.logger.debug("{:3}\t{}".format(line_number, line))
            line_number += 1

      
    def extract_symbol(self):
        self.logger.debug("constrcut symbol table...")
        line_number = 0
        updated_lines = []
        for line in self.src_lines:
            if not self.parse_label(line):
                self.parse_variable(line)
        
            line_number += 1
          
            

    def parse_variable(self, line):
        variable_pattern = re.compile("@([\S]+)")
        m = re.match(variable_pattern, line)
        
        if m is None:
            return False
        
        variable = m.group(1)
        assert (not variable[0].isdigit())
        if variable not in self.symbol_table:
            v_addr = self.variable_address_base + self.variable_address_offset 
            self.logger.debug('found new variable: "{}", add to symbol tabel with address: {}'
                              .format(variable, v_addr))
            self.variable_address_offset += 1

        return True


    
    def extract_label(self):
        temp_lines = []
        line_number = 0
        for line in self.src_lines:
            m = re.match("\((.+)\)", line)
            if m is not None:
                label = m.group(1)
                if label not in self.symbol_table:
                    self.symbol_table[label]  = line_number
                    self.logger.debug('new label "{}" added to symbol table with value {}'
                                      .format(label, line_number))
            else:
                line_number += 1
                temp_lines.append(line)
        
        self.src_lines = temp_lines
        print("updated symbol table:")
        print(self.symbol_table)
        

    def handle_lines(self):
        temp_lines = []
        for line in self.src_lines:
            if line.startswith("@"):
                line  = self.handle_A_instruction(line)
            else:
                line = self.handle_C_instruction(line)

            temp_lines.append(line)
        
        self.out_lines = temp_lines
        for src, out in zip(self.src_lines, self.out_lines):
            print("src: {}, assemble: {}".format(src, out))
        


    
    def add_variable_to_symbol_table(self, var):
        var_addr = self.variable_address_base + self.variable_address_offset
        self.symbol_table[var] = var_addr
        self.variable_address_offset += 1


    def handle_A_instruction(self, line):
        result = ""
        line = line.strip()
        var = line[1:]
        if not var.isdigit():
            if var not in self.symbol_table:
                self.add_variable_to_symbol_table(var)
            
            result = self.decimal_to_binary(self.symbol_table[var], 15)
        else:
            result = self.decimal_to_binary(var, 15)
        
        result = "0" + result
        print("A instruction: {}, result = {}, length = {}".format(line, result, len(result)))
        return result

    
    def handle_C_instruction(self, line):
        result = "111"
        dest = "null"
        comp = None
        jump = "null"
        
        assert ("=" in line) or (";" in line)
        temp = re.split("=|;", line)
        if len(temp) == 3:
            dest = temp[0].strip()
            comp = temp[1].strip()
            jump = temp[2].strip()
        elif len(temp) == 2:
            #print(temp)
            if "=" in line:
                dest = temp[0].strip()
                comp = temp[1].strip()
            else:
                comp = temp[0].strip()
                jump = temp[1].strip()
        else:
            comp = temp[0].strip()
        
        #print("line: {}, dest: {}, comp: {}, jump: {}".format(line, dest, comp, jump))
        result = result + self.comp_table[comp] + self.dest_table[dest] + self.jump_table[jump]
        print("C-line: {}, result: {}".format(line, result))
        assert len(result) == 16
        return result

      
    def decimal_to_binary(self, value, width):
        #return str(bin(n).replace("0b", ""))
        value = int(value)
        format_str = "{0:0" + str(width) + "b}"
        return format_str.format(value)

    
    def parse_label(self, line):
        print("parse_label line number: " , line_number)
        m = re.compile("\((.+)\)").search(line)
        if m is not None:
            label = m.group(1)
            if label not in self.symbol_table:
                label_value = line_number - self.lable_offset
                self.symbol_table[label] = label_value
                self.logger.debug('add new label "{}" to symbol tabel with value {}, label offset  = {}'
                                  .format(label, label_value, self.lable_offset))
                self.lable_offset -= 1
            else:
                self.logger.debug('label "{}" is aleady inside symbol table'.format(label))
            return True
        else:
            return False

    
    def output_file(self):
        with open(self.output_file_path, "w") as f:
            for line in self.out_lines:
                f.write(line + "\n")
    
    def assemble(self):
        self.extract_label()
        self.logger.debug("source code after label extraction:")
        for i, line in  enumerate(self.src_lines):
            self.logger.debug("{:3} {}".format(i, line))
        
        self.handle_lines()
        self.output_file()

    




def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, required=True)
    parser.add_argument('--out', type=str, required=True)
    args = parser.parse_args()
    return args



if __name__ == "__main__":
    args = parse_args()
    print(args)
    assembler = HackAssembler(args.src, args.out)
    assembler.assemble()
    
