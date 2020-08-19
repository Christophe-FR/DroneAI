# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 22:10:58 2020

@author: lutzc

Assembler : Converts assembly (.asm) to hack binary (.hack)
"""


class Parser:
    file = ''
    eof = False
    ncmd = 0
    def __init__(self,filename):
        self.file = open(filename)
        self.resetFields()
    def readCommand(self):
        command = ''
        while not(self.eof) :
            command = self.file.readline()
            
            if not command: 
                self.eof = True
                break
            else:
                command = command.split('//')[0].strip()
                if not(command==''):
                   break
        print('RAW = ', command) 
        self.command = command
        
        
    def parseCommand(self):
        string = self.command
        if string[0] == '(':
            self.commandType = 'PSEUDO'
            string = string.strip('(')
            string = string.strip(')')
            self.symbol = string
        elif string[0] == '@':
            self.ncmd = self.ncmd + 1
            self.commandType = 'A'
            if string[1:].isnumeric():
                self.symbol = int(string[1:])
            else:
                self.symbol = string[1:]
        else:
            self.commandType = 'C'
            self.ncmd = self.ncmd + 1
            if '=' in string:
                string = string.split('=')
                self.dest = string[0]
                string = string[1:]
            if ';' in string:
                string = string.split(';')
                self.comp = string[0]
                self.jump = string[1]
            else:
                self.comp = string[0]
    def resetFields(self):
        self.command = ''
        self.commandType = ''
        self.commandCount = 0
        self.symbol = ''
        self.dest = ''
        self.comp = ''
        self.jump = ''
    def show(self):
        print('///// COMMAND ', self.ncmd, ' /////')
        print('cmd : \t', self.command)
        print('typ : \t', self.commandType)
        print('sbl : \t', self.symbol)
        print('dest : \t', self.dest)
        print('comp : \t', self.comp)
        print('jump : \t', self.jump)
        
    def advance(self):
        self.resetFields()
        self.readCommand()
        if not(self.eof):
            self.parseCommand()
            #self.show()
                
def assemble(commandtype, symbol, dest, comp, jump):
    binary = ''
    if commandtype == 'A':
        binary = binary + '0'
        symbol = bin(symbol)[2:]
        for _ in range(15-len(symbol)):
            symbol = '0' + symbol
        binary = binary + symbol
    elif commandtype == 'C':
        binary = binary + '111'
        if 'M' in comp:
            binary = binary + '1'
            comp = comp.replace('M','A')
        else:
            binary = binary + '0'
        if comp == '0':
            binary = binary + '101010'
        elif comp == '1':
            binary = binary + '111111'
        elif comp == '-1':
            binary = binary + '111010'
        elif comp == 'D':
            binary = binary + '001100'
        elif comp == 'A':
            binary = binary + '110000'
        elif comp == '!D':
            binary = binary + '001101'
        elif comp == '!A':
            binary = binary + '110001'
        elif comp == '-D':
            binary = binary + '001111'
        elif comp == '-A':
            binary = binary + '110011'
        elif comp == 'D+1':
            binary = binary + '011111'
        elif comp == 'A+1':
            binary = binary + '110111'
        elif comp == 'D-1':
            binary = binary + '001110'
        elif comp == 'A-1':
            binary = binary + '110010'
        elif comp == 'D+A':
            binary = binary + '000010'
        elif comp == 'D-A':
            binary = binary + '010011'
        elif comp == 'A-D':
            binary = binary + '000111'
        elif comp == 'D&A':
            binary = binary + '000000'
        elif comp == 'D|A':
            binary = binary + '010101'
        else:
            print('unknown command')
            
        if dest == '':
            binary = binary + '000'
        elif dest == 'M':
            binary = binary + '001'
        elif dest == 'D':
            binary = binary + '010'
        elif dest == 'MD':
            binary = binary + '011'
        elif dest == 'A':
            binary = binary + '100'
        elif dest == 'AM':
            binary = binary + '101'
        elif dest == 'AD':
            binary = binary + '110'
        elif dest == 'AMD':
            binary = binary + '111'
        else:
            print('unknown destination')
            
        if jump == '':
            binary = binary + '000'
        elif jump == 'JGT':
            binary = binary + '001'
        elif jump == 'JEQ':
            binary = binary + '010'
        elif jump == 'JGE':
            binary = binary + '011'
        elif jump == 'JLT':
            binary = binary + '100'
        elif jump == 'JNE':
            binary = binary + '101'
        elif jump == 'JLE':
            binary = binary + '110'
        elif jump == 'JMP':
            binary = binary + '111'
        else:
            print('unknown jump')
    else:
        print('NOT C OR A COMMAND')
    return binary
    
    
    
filename = '/Users/lutzc/Desktop/Rect0.asm'
hackfile = open(filename[:-4] + '.hack','w+')

p=Parser(filename);
SymbolTable = dict()
SymbolTable['R0'] = 0
SymbolTable['R1'] = 1
SymbolTable['R2'] = 2
SymbolTable['R3'] = 3
SymbolTable['R4'] = 4
SymbolTable['R5'] = 5
SymbolTable['R6'] = 6
SymbolTable['R7'] = 7
SymbolTable['R8'] = 8
SymbolTable['R9'] = 0
SymbolTable['R10'] = 10
SymbolTable['R11'] = 11
SymbolTable['R12'] = 12
SymbolTable['R13'] = 13
SymbolTable['R14'] = 14
SymbolTable['R15'] = 15
SymbolTable['SCREEN'] = 16384
SymbolTable['KBD'] = 24576
SymbolTable['SP'] = 0
SymbolTable['LCL'] = 1
SymbolTable['ARG'] = 2
SymbolTable['THIS'] = 3
SymbolTable['THAT'] = 4


p=Parser(filename);
nvar = 16

print('PASS 1')
while True:
    p.advance()
    if p.commandType == 'PSEUDO':
        if p.symbol not in SymbolTable.keys():
            SymbolTable[p.symbol] = p.ncmd
        else:
            print('label defined twice!')
    if p.eof:
        break

p=Parser(filename);
print('PASS 2')
while True:
    p.advance()
    if not p.commandType == 'PSEUDO':
        if isinstance(p.symbol, str) and not p.symbol == '':
            if p.symbol not in SymbolTable.keys():
                SymbolTable[p.symbol] = nvar
                nvar = nvar +1;
            p.symbol = SymbolTable[p.symbol]
            print(p.symbol)
    binary = assemble(p.commandType, p.symbol, p.dest, p.comp, p.jump)
    print(binary)
    if not binary == '':
        hackfile.write(binary+'\r')
    if p.eof:
        break
hackfile.close()


    
