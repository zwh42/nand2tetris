import os
import argparse
import logging
import re
from pprint import pprint

class HackAssembler:
    variable_address_base = 16 #hard-coded
    variable_address_offset = 0
    lable_offset = 0  
    symbol_table = {}
    src_lines = []
    out_lines = []
    logger = None

    def __init__(self, src_file_path, output_file_path):
        print("Initializing Hack Assembler")
        print("source file: " + src_file_path)
        print("output file: " + output_file_path)

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

      
            
        

    def parse_c_command():
        pass

       

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



            


    
    def decimal_to_binary(self, n):
        return str(bin(n).replace("0b", ""))
    
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

    
    def assemble(self):
        self.extract_label()
        self.logger.debug("source code after label extraction:")
        for i, line in  enumerate(self.src_lines):
            self.logger.debug("{:3} {}".format(i, line))
    




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
    
