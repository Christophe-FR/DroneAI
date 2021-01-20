# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 19:55:59 2020

@author: lutzc
"""
import os 

class Parser:
    file = ''
    hasMoreCommands = True
    currentCommand = ''
    cmd = ''
    arg1 = ''
    arg2 = ''
    def __init__(self,filename):
        self.file = open(filename)
    def advance(self):
        self.cmd = ''
        self.arg1 = ''
        self.arg2 = ''
        self.readCommand()
        print(self.currentCommand)
        self.analyzeCommand()
    def readCommand(self):   
        string = ''
        while self.hasMoreCommands :
            string = self.file.readline()
            #print(string)
            if not string: 
                self.hasMoreCommands = False
                break
            else:
                string = string.split('//')[0].strip()
                if not(string==''):
                   break
        self.currentCommand = string
    def analyzeCommand(self):
        string_splitted = self.currentCommand.split(' ') 
        self.cmd =string_splitted[0]
        if len(string_splitted)>=2:
            self.arg1 =string_splitted[1]
        if len(string_splitted)>=3:
            self.arg2 =string_splitted[2]

class CodeWritter:
    file = ''
    label_idx = 0
    def __init__(self,filename):
        self.file = open(filename,'w+')
    def writeText(self, text):
        self.file.write(text + '\r')
    def writeAssembly(self, cmd, arg1, arg2, vmfile):
        #print('VM CODE : CMD = ' + cmd + ' ARG1 = ' + arg1 + ' ARG2 = ' + arg2)
        asm = '//' + cmd + ' ' + arg1 + ' ' + arg2
        asm = newLine(asm)
        filename = vmfile.split('/')[-1:][0].split('.')[0]
        if cmd == 'push':
            if arg1 == 'constant': # push constant
                asm = pushConstantSeg(asm, arg2)
            elif arg1 == 'local': # push local
                asm = pushMemSeg(asm, 'LCL', arg2)
            elif arg1 == 'argument':
                asm = pushMemSeg(asm, 'ARG', arg2)
            elif arg1 == 'this':
                asm = pushMemSeg(asm, 'THIS', arg2)
            elif arg1 == 'that':
                asm = pushMemSeg(asm, 'THAT', arg2)
            elif arg1 == 'static':
                # D = filename.arg2
                asm = asm + newLine('@' + filename + '.' + str(arg2))
                asm = asm + newLine('D = M')
                # *SP = D
                asm = asm + newLine('@SP')
                asm = asm + newLine('A = M')
                asm = asm + newLine('M = D')
                # SP ++
                asm = asm + newLine('@SP')
                asm = asm + newLine('M = M + 1')
            elif arg1 == 'temp':
                # D = *(addr)
                asm = asm + newLine('@' + str(arg2))
                asm = asm + newLine('D = A')
                asm = asm + newLine('@5')
                asm = asm + newLine('A = A + D')
                asm = asm + newLine('D = M')
                # *SP = D
                asm = asm + newLine('@SP')
                asm = asm + newLine('A = M')
                asm = asm + newLine('M = D')
                # SP ++
                asm = asm + newLine('@SP')
                asm = asm + newLine('M = M + 1')
            elif arg1 == 'pointer':
                if arg2 == '0':
                    th = 'THIS'
                elif arg2 == '1':
                    th = 'THAT'
                else:
                    print('ERROR PUSH POINTER')
                asm = asm + newLine('@' + th)
                asm = asm + newLine('D = M')
                asm = asm + newLine('@SP')
                asm = asm + newLine('A = M')
                asm = asm + newLine('M = D')
                # SP ++
                asm = asm + newLine('@SP')
                asm = asm + newLine('M = M + 1')
            else:
                 print('ERROR PUSH')
        elif cmd == 'pop':
             if arg1 == 'local':
                 asm = popMemSeg(asm, 'LCL', arg2)
             elif arg1 == 'argument':
                 asm = popMemSeg(asm, 'ARG', arg2)
             elif arg1 == 'this':
                 asm = popMemSeg(asm, 'THIS', arg2)
             elif arg1 == 'that':
                 asm = popMemSeg(asm, 'THAT', arg2)
             elif arg1 == 'static':
                 # SP --
                 asm = asm + newLine('@SP')
                 asm = asm + newLine('M = M - 1')
                 # D = *SP
                 asm = asm + newLine('A = M')
                 asm = asm + newLine('D = M')
                 asm = asm + newLine('@' + filename + '.' + str(arg2))
                 # M = D
                 asm = asm + newLine('M = D')
             elif arg1 == 'temp':
                 # R13 = addr = 5 + arg2
                 asm = asm + newLine('@' + str(arg2))
                 asm = asm + newLine('D = A')
                 asm = asm + newLine('@5')
                 asm = asm + newLine('D = A + D')
                 asm = asm + newLine('@R13')
                 asm = asm + newLine('M = D')
                 # SP --
                 asm = asm + newLine('@SP')
                 asm = asm + newLine('M = M - 1')
                 # *R13 = *SP
                 asm = asm + newLine('A = M')
                 asm = asm + newLine('D = M')
                 asm = asm + newLine('@R13')
                 asm = asm + newLine('A = M')
                 asm = asm + newLine('M = D')
             elif arg1 == 'pointer':
                 if arg2 == '0':
                    th = 'THIS'
                 elif arg2 == '1':
                    th = 'THAT'
                 else:
                    print('ERROR POP POINTER')
                 # SP --
                 asm = asm + newLine('@SP')
                 asm = asm + newLine('M = M - 1')
                 #
                 asm = asm + newLine('A = M')
                 asm = asm + newLine('D = M')
                 asm = asm + newLine('@' + th)
                 asm = asm + newLine('M = D')
             else:
                 print('ERROR POP')
        elif cmd == 'add':
            asm = arithAndBooleanOp(asm, '+')
        elif cmd == 'sub':
            asm = arithAndBooleanOp(asm, '-')
        elif cmd == 'neg':
            # SP --
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M - 1')
            # *SP = -*SP
            asm = asm + newLine('A = M')
            asm = asm + newLine('M = -M')
            # SP ++
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M + 1')
        elif cmd == 'eq':
            asm = logicOp(asm, 'JEQ', self.label_idx)
        elif cmd == 'gt': # x > y
            asm = logicOp(asm, 'JGT', self.label_idx)
        elif cmd == 'lt': # x > y
            asm = logicOp(asm, 'JLT', self.label_idx)
        elif cmd == 'and':
            asm = arithAndBooleanOp(asm,'&')
        elif cmd == 'or':
            asm = arithAndBooleanOp(asm,'|')
        elif cmd == 'not':
            # SP --
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M - 1')
            # *SP = -*SP
            asm = asm + newLine('A = M')
            asm = asm + newLine('M = !M')
            # SP ++
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M + 1')
        elif cmd == 'label':
            asm = asm + newLine('(' + filename + '$' + arg1 + ')')
        elif cmd == 'if-goto':
            # SP --
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M - 1')
            # D = *SP
            asm = asm + newLine('@SP')
            asm = asm + newLine('A = M')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@' + filename + '$' + arg1)
            asm = asm + newLine('D; JNE')
        elif cmd == 'goto':
            asm = asm + newLine('@' + filename + '$' + arg1)
            asm = asm + newLine('D; JMP') # D is not needed here as jump is unconditional
        elif cmd == 'function':
            asm = asm + newLine('(' + arg1 + ')')
            for _ in range(int(arg2)):
                asm = pushConstantSeg(asm, '0')
        elif cmd == 'call':
            label = arg1 + '$' + 'ret' + str(self.label_idx)
            # push return address
            asm = asm + newLine('@' + label)
            asm = asm + newLine('D = A')
            asm = asm + newLine('@SP')
            asm = asm + newLine('A = M')
            asm = asm + newLine('M = D')
            # SP ++
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M + 1')
            # push LCL
            asm = asm + newLine('@LCL')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@SP')
            asm = asm + newLine('A = M')
            asm = asm + newLine('M = D')
            # SP ++
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M + 1')
            # push ARG
            asm = asm + newLine('@ARG')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@SP')
            asm = asm + newLine('A = M')
            asm = asm + newLine('M = D')
            # SP ++
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M + 1')
            # push THIS
            asm = asm + newLine('@THIS')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@SP')
            asm = asm + newLine('A = M')
            asm = asm + newLine('M = D')
            # SP ++
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M + 1')
            # push THAT
            asm = asm + newLine('@THAT')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@SP')
            asm = asm + newLine('A = M')
            asm = asm + newLine('M = D')
            # SP ++
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M + 1')
            # set arg segment of callee
            asm = asm + newLine('@SP')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@' + str(int(arg2) + 5))
            asm = asm + newLine('D = D - A')
            asm = asm + newLine('@ARG')
            asm = asm + newLine('M = D')
            # set the local segment to the tip of the stack
            asm = asm + newLine('@SP')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@LCL')
            asm = asm + newLine('M = D')
            # jump to function
            asm = asm + newLine('@' + arg1)
            asm = asm + newLine('D; JMP')
            # place return label
            asm = asm + newLine('(' + label + ')')
        elif cmd == 'return':
            # FRAME = R13 = LCL
            asm = asm + newLine('@LCL')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@R13')
            asm = asm + newLine('M = D')
            # RET = R14 = *(FRAME - 5)
            asm = asm + newLine('@R13')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@5')
            asm = asm + newLine('A = D - A')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@R14')
            asm = asm + newLine('M = D')
            # copy return value to top of caller stack (= callee arg 0)
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = M - 1')
            asm = asm + newLine('A = M')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@ARG')
            asm = asm + newLine('A = M')
            asm = asm + newLine('M = D')
            # reposition the stack pointer after the return value
            asm = asm + newLine('@ARG')
            asm = asm + newLine('D = M')
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = D + 1')          
            # restore THAT memory segment
            asm = asm + newLine('@R13')
            asm = asm + newLine('D = M') # D = R13 = FRAME
            asm = asm + newLine('@1')
            asm = asm + newLine('A = D - A') # A = FRAME - 1
            asm = asm + newLine('D = M') # D = *A = *(FRAME - 1)
            asm = asm + newLine('@THAT')
            asm = asm + newLine('M = D')
            # restore THAT memory segment
            asm = asm + newLine('@R13')
            asm = asm + newLine('D = M') # D = R13 = FRAME
            asm = asm + newLine('@1')
            asm = asm + newLine('A = D - A') # A = FRAME - 1
            asm = asm + newLine('D = M') # D = *A = *(FRAME - 1)
            asm = asm + newLine('@THAT')
            asm = asm + newLine('M = D')
            # restore THIS memory segment
            asm = asm + newLine('@R13')
            asm = asm + newLine('D = M') # D = R13 = FRAME
            asm = asm + newLine('@2')
            asm = asm + newLine('A = D - A') # A = FRAME - 2
            asm = asm + newLine('D = M') # D = *A = *(FRAME - 2)
            asm = asm + newLine('@THIS')
            asm = asm + newLine('M = D')
            # restore ARG memory segment
            asm = asm + newLine('@R13')
            asm = asm + newLine('D = M') # D = R13 = FRAME
            asm = asm + newLine('@3')
            asm = asm + newLine('A = D - A') # A = FRAME - 3
            asm = asm + newLine('D = M') # D = *A = *(FRAME - 3)
            asm = asm + newLine('@ARG')
            asm = asm + newLine('M = D')
            # restore LCL memory segment
            asm = asm + newLine('@R13')
            asm = asm + newLine('D = M') # D = R13 = FRAME
            asm = asm + newLine('@4')
            asm = asm + newLine('A = D - A') # A = FRAME - 4
            asm = asm + newLine('D = M') # D = *A = *(FRAME - 4)
            asm = asm + newLine('@LCL')
            asm = asm + newLine('M = D')
            # goto return value, stored in RET = R14
            asm = asm + newLine('@R14')
            asm = asm + newLine('A = M')
            asm = asm + newLine('D; JMP')
        elif cmd == 'bootstrap':
            asm = asm + newLine('@256')
            asm = asm + newLine('D = A')
            asm = asm + newLine('@SP')
            asm = asm + newLine('M = D')
        else:
            print('ERROR COMMAND')
        self.label_idx = self.label_idx + 1
        self.file.write(asm+'\r')
    def close(self):
        self.file.close()

def newLine(string):
    return string + '\r'

def arithAndBooleanOp(asm, operation):
    # SP --
    asm = asm + newLine('@SP')
    asm = asm + newLine('M = M - 1')
    # D = *SP
    asm = asm + newLine('A = M')
    asm = asm + newLine('D = M')
    # SP --
    asm = asm + newLine('@SP')
    asm = asm + newLine('M = M - 1')
    asm = asm + newLine('A = M')
    # *SP = *SP + D
    asm = asm + newLine('M = M '+ operation + 'D')
    # SP ++
    asm = asm + newLine('@SP')
    asm = asm + newLine('M = M + 1')
    return asm

def logicOp(asm, operation, label_idx): # y - x (operation) 0 ?
    # SP --
    asm = asm + newLine('@SP')
    asm = asm + newLine('M = M - 1')
    # D = *SP
    asm = asm + newLine('A = M')
    asm = asm + newLine('D = M')
    # SP --
    asm = asm + newLine('@SP')
    asm = asm + newLine('M = M - 1')
    # D = *SP - D
    asm = asm + newLine('A = M')
    asm = asm + newLine('D = M - D') # D = a - b
    # if D = a - b (operation) 0 return -1
    asm = asm + newLine('M = -1')
    asm = asm + newLine('@label_' + str(label_idx))
    asm = asm + newLine('D; ' + operation)
    # else 0
    asm = asm + newLine('@SP')
    asm = asm + newLine('A = M')
    asm = asm + newLine('M = 0')
    asm = asm + newLine('(label_' + str(label_idx) + ')')
    # SP ++
    asm = asm + newLine('@SP')
    asm = asm + newLine('M = M + 1')
    return asm

def popMemSeg(asm, segment, i):
    # R13 = addr = LCL + arg1
    asm = asm + newLine('@' + str(i))
    asm = asm + newLine('D = A') # D = i
    asm = asm + newLine('@' + segment)
    asm = asm + newLine('A = M') # A = segment (not a deferencing)
    asm = asm + newLine('D = A + D') # D = A + D = segment + i
    asm = asm + newLine('@R13')
    asm = asm + newLine('M = D') # R13 = D
    # SP --
    asm = asm + newLine('@SP')
    asm = asm + newLine('M = M - 1')
    # *R13 = *SP
    asm = asm + newLine('A = M')
    asm = asm + newLine('D = M') # D = *SP
    asm = asm + newLine('@R13') 
    asm = asm + newLine('A = M')
    asm = asm + newLine('M = D')
    return asm
    
def pushMemSeg(asm, segment, i): 
    # D = *(addr)
    asm = asm + newLine('@' + str(i))
    asm = asm + newLine('D = A')  # D = i
    asm = asm + newLine('@' + segment)
    asm = asm + newLine('A = M') # M = segment
    asm = asm + newLine('A = A + D') # A = segment + i
    asm = asm + newLine('D = M') # D = *(*segment + i)
    # *SP = D
    asm = asm + newLine('@SP')
    asm = asm + newLine('A = M')
    asm = asm + newLine('M = D')
    # SP ++
    asm = asm + newLine('@SP')
    asm = asm + newLine('M = M + 1')
    return asm
    
def pushConstantSeg(asm, value): 
    # *SP = arg2
    asm = asm + newLine('@' + value)
    asm = asm + newLine('D = A')
    asm = asm + newLine('@SP')
    asm = asm + newLine('A = M')
    asm = asm + newLine('M = D')
    # SP ++
    asm = asm + newLine('@SP')
    asm = asm + newLine('M = M + 1')
    return asm


path = '/Users/lutzc/Desktop/nand2tetris/projects/08/FunctionCalls/FibonacciElement'

# Code to support handling of directory and file.
# Output: filenameIn/filenameOut full paths
if os.path.isdir(path):
    filename = os.listdir(path)
    for idx in range(len(filename)):
        filename[idx] = path + '/' + filename[idx]
    filenameOut = path + '/' + path.split('/')[-1] + '.asm'
elif os.path.isfile(path):
    filename = path
    filenameOut = filename[:-3] + '.asm'
else:
    print('Path not valid')
filenameIn = []
for file in filename:
    if file[-3:] == '.vm':
        filenameIn.append(file)

cw = CodeWritter(filenameOut)
cw.writeAssembly('bootstrap', '', '', 'bootstrap')
cw.writeAssembly('call', 'Sys.init', '0', 'bootstrap')
for fileIn in filenameIn:
    cw.writeText('// ------------ FILE : ' + fileIn + ' ------------ ')
    p = Parser(fileIn)
    while True:
        p.advance()
        if p.hasMoreCommands == False:
            break
        cw.writeAssembly(p.cmd, p.arg1, p.arg2, p.file.name)
cw.close()