# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 12:52:15 2017

@author: Louis
"""
import os.path

class SymbolTable:
    def __init__(self):
        """
        Set default entries, and keep record of the first unoccupied address
        """
        self.table = dict()
        self.empty_address = 16
        
        # Set default for the predefined valuable
        self.init_virtual_register()
        self.init_pointer()
        self.init_io()

    def addEntry(self, entry, address):
        """
        Relate the entry to the address, and save in table
        """
        self.table[entry] = address
    
    def hasEntry(self, entry):
        """
        Return True if the entry is in the table
        """
        return entry in self.table.keys()
    
    def getAddress(self, entry):
        """
        Return the address of the entry, only called when the entry exists
        """
        return self.table[entry]
    
    def allocate(self, entry):
        """
        Allocate empty address for valuable. Relate entry to the allocated 
        address, and return allocated address
        """
        self.addEntry(entry, self.empty_address)
        self.empty_address += 1
        return self.empty_address - 1
    
    def init_virtual_register(self):
        for i in range(16):
            self.addEntry('R' + str(i), i)
    
    def init_pointer(self):
        self.addEntry('SP', 0)
        self.addEntry('LCL', 1)
        self.addEntry('ARG', 2)
        self.addEntry('THIS', 3)
        self.addEntry('THAT', 4)
    
    def init_io(self):
        self.addEntry('SCREEN', 16384)
        self.addEntry('KBD', 24576)
    
class Parser:
    def __init__(self, file):
        """
        Open file for assembling, and initialize program counter
        """
        self.fp = open(file)
        self.prog_cnt = 0
        self.parsed_cmd = []
        self.advance()
    
    def firstPass(self, symbol_table):
        """
        Run through the whole file and record all pseudo instruction in the 
        symbol table
        """
        while self.hasCmd():
            cmd = self.parseCmd()
            if cmd.form == 'P':
                symbol_table.addEntry(cmd.tag, self.prog_cnt)
            else:
                self.parsed_cmd.append(cmd)
                self.prog_cnt += 1
            
            self.advance()
    
    def advance(self):
        """
        Advance to the next line which is not comment or empty line, and save 
        it in curr_line
        """
        while True:
            curr_line = self.fp.readline()
            
            if curr_line.startswith('/'):
                continue
            elif len(curr_line) > 0 and curr_line.strip() == '':
                continue
            else:
                self.curr_line = curr_line
                break
    
    def hasCmd(self):
        """
        Return True if the file has more command to be parse, else otherwise.
        """        
        if self.curr_line == '':
            return False
        else:
            return True
    
    def parseCmd(self):
        """
        Parse curr_line of Hack assembly language, and return in the form of 
        Instruction class
        """
        # Strip comment
        comment = self.curr_line.find('/')
        if comment != -1:
            self.curr_line = self.curr_line[:comment]
            
        # Strip white space
        self.curr_line = self.curr_line.strip()
        
        if self.curr_line.startswith('@'):
            return Instruction('A', self.curr_line[1:])
        elif self.curr_line.startswith('('):
            open_b = self.curr_line.find('(')
            close_b = self.curr_line.find(')')
            tag = self.curr_line[open_b + 1:close_b]
            return Instruction('P', tag)
        else:                
            dest_i = self.curr_line.find('=')
            jump_i = self.curr_line.find(';')
            
            if dest_i != -1:
                dest, self.curr_line = self.curr_line.split('=')
            else:
                dest = 'null'
            
            if jump_i != -1:
                comp, jump = self.curr_line.split(';')
            else:
                comp = self.curr_line
                jump = 'null'
            
            return Instruction('C', comp, dest, jump)
    
class Instruction:
    def __init__(self, form, *contents):
        """
        Receive form to indicate which instruction it is, and list of contents
        which are incorporated according to the form
        """
        self.form = form
        
        if form == 'A':
            self.value = contents[0]
        elif form == 'P':
            self.tag = contents[0]
        elif form == 'C':
            self.comp = contents[0]
            self.dest = contents[1]
            self.jump = contents[2]

class Decoder:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.init_c_dict()
    
    C_DICT = dict()

    def init_c_dict(self):
        comp_inst = [('0', '0101010'),
                     ('1', '0111111'),
                     ('-1', '0111010'),
                     ('D', '0001100'),
                     ('A', '0110000'),
                     ('!D', '0001101'),
                     ('!A', '0110001'),
                     ('-D', '0001111'),
                     ('-A', '0110011'),
                     ('D+1', '0011111'),
                     ('A+1', '0110111'),
                     ('D-1', '0001110'),
                     ('A-1', '0110010'),
                     ('D+A', '0000010'),
                     ('D-A', '0010011'),
                     ('A-D', '0000111'),
                     ('D&A', '0000000'),
                     ('D|A', '0010101'),
                     ('M', '1110000'),
                     ('!M', '1110001'),
                     ('-M', '1110011'),
                     ('M+1', '1110111'),
                     ('M-1', '1110010'),
                     ('D+M', '1000010'),
                     ('D-M', '1010011'),
                     ('M-D', '1000111'),
                     ('D&M', '1000000'),
                     ('D|M', '1010101'),]
        
        dest_inst = [('null', '000'),
                     ('M', '001'),
                     ('D', '010'),
                     ('MD', '011'),
                     ('A', '100'),
                     ('AM', '101'),
                     ('AD', '110'),
                     ('AMD', '111')]
    
        jump_inst = [('null', '000'),
                     ('JGT', '001'),
                     ('JEQ', '010'),
                     ('JGE', '011'),
                     ('JLT', '100'),
                     ('JNE', '101'),
                     ('JLE', '110'),
                     ('JMP', '111')]
    
        self.C_DICT['comp'] = dict(comp_inst)
        self.C_DICT['dest'] = dict(dest_inst)
        self.C_DICT['jump'] = dict(jump_inst)    

    def decode(self, inst):
        """
        Take an Instruction class, translate to and output according binary code in
        the form of the string
        """
        if inst.form == 'A':
            if inst.value.isdigit():
                bin_code = '0{:0>15}'.format(bin(int(inst.value))[2:])
            elif self.symbol_table.hasEntry(inst.value):
                value = self.symbol_table.getAddress(inst.value)
                bin_code = '0{:0>15}'.format(bin(value)[2:])
            else:
                value = self.symbol_table.allocate(inst.value)
                bin_code = '0{:0>15}'.format(bin(value)[2:])
                
        elif inst.form == 'C':
            bin_code = '111'
            bin_code += self.C_DICT['comp'][inst.comp]
            bin_code += self.C_DICT['dest'][inst.dest]
            bin_code += self.C_DICT['jump'][inst.jump]
        
        return bin_code
    
    def __call__(self, inst):
        return self.decode(inst)
    
def main():
    while True:
        file = input('Please enter path to file for assembling, q to quit:')
        
        if file == 'q':
            break
        
        symbol_table = SymbolTable()
        parse = Parser(file)
        parse.firstPass(symbol_table)
        decode = Decoder(symbol_table)
        output_f = open(os.path.splitext(file)[0] + '.hack', 'w')
        
        for cmd in parse.parsed_cmd:
            bin_code = decode(cmd)
            output_f.write(bin_code + '\n')
        
        output_f.close()
        print('Assembly complete')

if __name__ == '__main__':
    main()