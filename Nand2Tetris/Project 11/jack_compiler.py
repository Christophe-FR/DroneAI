# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 14:36:51 2020

@author: lutzc
"""
import os 

class tokenizer:
    file =''
    content =''
    tokens = []
    types = []
    def __init__(self,filename):
        self.file = open(filename)
        self.content = self.file.read()
    def readToken(self):
        print(self.content[0:15])
        token = None
        tokenType = None
        if self.content == '':
            None
        elif self.content[0] in ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']:
            token = self.content[0]
            tokenType ='symbol'
            self.content = eat(self.content, token)
        elif self.content[0].isnumeric():
            n = 1
            while self.content[n].isnumeric() :
                n += 1
            token = self.content[0:n]
            tokenType ='integerConstant'
            self.content = eat(self.content, token)
        elif self.content[0].isalpha() or self.content[0] =='_':
            n = 1
            while self.content[n].isalpha() or self.content[n].isnumeric() or self.content[n] =='_':
                n += 1
            token = self.content[0:n]
            if  token in ['class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']: 
                tokenType ='keyword'
            else:
                tokenType ='identifier'
            self.content = eat(self.content, token)
        elif self.content[0] =='"':
            n = 1
            while self.content[n] !='"':
                n += 1
            token = self.content[1:n]
            tokenType ='stringConstant'
            self.content = eat(self.content, '"' + token + '"')
        else :
            print('ERROR: Unrecognized token = ', self.content)
        
        return token, tokenType
    def collectTokens(self):
        while True:
            if self.content =='':
                break
            else:
                self.content = eatNoCode(self.content)
                token, tokentype = self.readToken()
                if token != None:
                    self.tokens.append(token)
                    self.types.append(tokentype)
    def printTokens(self):
        for idx in range(len(self.tokens)):
            print(self.types[idx] + '\t' + self.tokens[idx])
    def close(self):
        self.file.close()

def eat(body, string):
    if body[0:len(string)] == string:
        body = body[len(string):]
    else:
        print('ERROR : Could not eat string')
    return body

def eatNoCode(body):
    while True :
        if body == '':
            break
        elif body[0] ==' ':
            body = eat(body,' ')
        elif body[0:3] =='/**':
            while body[0:2] !='*/':
                body = eat(body, body[0])
            body = eat(body,'*/')
        elif body[0:2] =='//':
            while body[0:1] !='\n' :
                body = eat(body, body[0])
            body = eat(body,'\n')
        elif body[0:1] =='\n':
            body = eat(body,'\n')
        elif body[0:1] =='\t':   
            body = eat(body,'\t')
        elif body[0:1] =='\r':   
            body = eat(body,'\r')
        else:
            break
    return body

class symbolTable:
    name = ''
    table = []
    def __init__(self):
        self.flush()
    def define(self, name, typ, kind):
        self.table.append([name, typ, kind, str(self.VarCount(kind))])
    def flush(self):
        self.table = []
    def VarCount(self, kind):
        count = 0
        for symbol in self.table:
            if symbol[2] == kind:
                count = count + 1
        return count
    def TypeOf(self, name):
        for symbol in self.table:
            if symbol[0] == name:
                return symbol[1]
        return None
    def KindOf(self, name):
        for symbol in self.table:
            if symbol[0] == name:
                return symbol[2]
        return None
    def IndexOf(self, name):
        for symbol in self.table:
            if symbol[0] == name:
                return symbol[3]
        return None
    def IsDefined(self, name):
        for symbol in self.table:
            if symbol[0] == name:
#                print(symbol)
                return True
        return False
    def printTable(self):
        if self.table == []:
            print('Table is empty.')
        else:
            for symbol in self.table:
                print(symbol)


class parser():
    tokens = []
    types = []
    XMLcontent = ''
    VMcontent = ''
    indent = 0
    ClassSymbolTable = symbolTable()
    SubroutineSymbolTable = symbolTable()
    label = 0
    
    def __init__(self,filename, tokens, types):
        self.XMLfile = open(filename + '.xml','w')
        self.VMfile = open(filename + '.vm','w')
        self.tokens = tokens
        self.types = types
        self.landmarks = []

    def eatToken(self, tokentype):
#        print(self.tokens[0:3])
        if self.types[0] == tokentype:
            self.isEaten = True
            lunch = self.tokens.pop(0)
            self.types.pop(0)
            return True, lunch
        else:
            return False, None
         
    def parse(self):
        while self.compileClass():
            continue
    def putHead(self, name):
        self.landmarks.append(len(self.XMLcontent))
        self.writeXML(xmlTag(name,'open', self.indent))
        self.indent +=1
    def putTail(self,name, cplret):
        self.indent -=1
        self.writeXML(xmlTag(name,'close', self.indent))
        stop = self.landmarks.pop()
        if cplret == False:
            self.XMLcontent = self.XMLcontent[0:stop]
        print('compile' + name + ' = '+ str(cplret))
    def compileClass(self):
        self.putHead('class')
        
        cplret = self.compileKeyword('class')[0]
        if cplret:
            cplret, classname = self.compileClassName()
            self.ClassSymbolTable.name = classname
            cplret = cplret and self.compileSymbol('{')[0]
        if cplret:
            while self.compileClassVarDec():
                continue
            while self.compileSubroutineDec():
                continue
        cplret = cplret and self.compileSymbol('}')[0]

        self.ClassSymbolTable.flush()
        self.putTail('class',cplret)
        return cplret
    
    def compileClassName(self):
        cplret, classname = self.compileIdentifier()
        print('compileClassName = '+ str(cplret))
        return cplret, classname
    
    def compileVarName(self):
        cplret, varname = self.compileIdentifier()
        print('compileVarName = '+ str(cplret))
        return cplret, varname
    
    def compileSubroutineName(self):
        cplret, subroutinename = self.compileIdentifier()
        print('compileSubroutineName = '+ str(cplret))
        return cplret, subroutinename
    
    def compileClassVarDec(self):
        self.putHead('classVarDec')
        
        cplret, kind = self.compileKeyword('static')
        if cplret:
            print('static')
        if not cplret:
            cplret, kind = self.compileKeyword('field')
        if cplret:
            cplret, typ = self.compileType()
        if cplret:
            cplret, varname = self.compileVarName()
        if cplret:
            self.ClassSymbolTable.define(varname, typ, kind)
            while True:
                cplret_optional = self.compileSymbol(',')[0]
                if cplret_optional:
                    cplret_optional, varname = self.compileVarName()
                    if cplret_optional:
                        self.ClassSymbolTable.define(varname, typ, kind)
                    else:
                        break
                else:
                    break
        cplret = cplret and self.compileSymbol(';')[0]
        
        self.putTail('classVarDec',cplret)
        return cplret
    
    def compileSubroutineDec(self):
        self.putHead('subroutineDec')
        
        cplret, subroutine = self.compileKeyword('constructor')
        if not cplret:
            cplret, subroutine = self.compileKeyword('function')
        if not cplret:
            cplret, subroutine = self.compileKeyword('method')
            if cplret:
                self.SubroutineSymbolTable.define('this','pointer','argument')
        cplret = cplret and (self.compileKeyword('void')[0] or self.compileType()[0])
        if cplret:
            cplret, subroutinename = self.compileSubroutineName() 
        cplret = cplret and self.compileSymbol('(')[0]
        cplret = cplret and self.compileParameterList()
        cplret = cplret and self.compileSymbol(')')[0]
        
        if cplret:
            self.writeVM('\r' + 'function ' + self.ClassSymbolTable.name + '.' + subroutinename + ' ')
            landmark = len(self.VMcontent)
            if subroutine == 'method':
                self.writeVM('push argument 0')
                self.writeVM('pop pointer 0')
            elif subroutine == 'constructor':
                self.writeVM('push constant ' + str(self.ClassSymbolTable.VarCount('field')))
                self.writeVM('call Memory.alloc 1')
                self.writeVM('pop pointer 0')
            elif subroutine == 'function':
                None
            else:
                raise Exception('Unrecognized subroutine')
            cplret = cplret and self.compileSubroutineBody()
            if cplret:
                self.VMcontent = self.VMcontent[0:landmark-1] + str(self.SubroutineSymbolTable.VarCount('local')) + '\r' + self.VMcontent[landmark:-1]
        
        self.SubroutineSymbolTable.flush()
        
        self.putTail('subroutineDec',cplret)
        return cplret
    
    def compileParameterList(self):
        self.putHead('parameterList')
        
        cplret_optional, typ = self.compileType()
        if cplret_optional:
            cplret_optional, varname = self.compileVarName()
            if cplret_optional:
                self.SubroutineSymbolTable.define(varname, typ, 'argument')
                while True:
                    cplret_optional = self.compileSymbol(',')[0]
                    if cplret_optional:
                        cplret_optional, typ = self.compileType()
                        if cplret_optional:
                            cplret_optional, varname = self.compileVarName()
                            if cplret_optional:
                                self.SubroutineSymbolTable.define(varname, typ, 'argument')
                            else:
                                break
                        else:
                            break
                    else:
                        break
        cplret = True
        
        self.putTail('parameterList',cplret)
        return cplret
    
    def compileSubroutineBody(self):
        self.putHead('subroutineBody')
        
        cplret = self.compileSymbol('{')[0]
        if cplret:
            while self.compileVarDec():
                continue
        cplret = cplret and self.compileStatements() 
        cplret = cplret and self.compileSymbol('}')[0]
        
        self.putTail('subroutineBody',cplret)
        return cplret
    
    def compileVarDec(self):
        self.putHead('varDec')
        
        cplret, kind = self.compileKeyword('var')
        if cplret:
            cplret, typ = self.compileType()
            if cplret:
                cplret, varname = self.compileVarName()
                if cplret:
                    self.SubroutineSymbolTable.define(varname, typ, 'local')
                    while True:
                        cplret_optional = self.compileSymbol(',')[0]
                        if cplret_optional:
                            cplret_optional, varname = self.compileVarName()
                            self.SubroutineSymbolTable.define(varname, typ, 'local')
                        else:
                            break
                cplret = cplret and self.compileSymbol(';')[0]
        
        self.putTail('varDec',cplret)
        return cplret
    
    def compileStatements(self):
        self.putHead('statements')
        
        while self.compileStatement():
            continue
        cplret = True
        
        self.putTail('statements',cplret)
        return cplret
    
    def compileStatement(self):        
        cplret = self.compileLetStatement() or \
        self.compileIfStatement() or \
        self.compileWhileStatement() or \
        self.compileDoStatement() or \
        self.compileReturnStatement()
        return cplret
    
    def compileLetStatement(self):
        self.putHead('letStatement')
        
        cplret = self.compileKeyword('let')[0]
        if cplret:
            cplret, varname = self.compileVarName()
            cplretarr = cplret and self.compileSymbol('[')[0]
            if cplretarr:
                if self.SubroutineSymbolTable.IsDefined(varname):
                    self.writeVM('push ' + self.SubroutineSymbolTable.KindOf(varname)\
                         + ' ' + self.SubroutineSymbolTable.IndexOf(varname))
                elif self.ClassSymbolTable.IsDefined(varname):
                    if self.ClassSymbolTable.KindOf(varname) == 'field':
                        self.writeVM('push this ' + self.ClassSymbolTable.IndexOf(varname))
                    elif self.ClassSymbolTable.KindOf(varname) == 'static':
                        self.writeVM('push static ' + self.ClassSymbolTable.IndexOf(varname))
                    else:
                        raise Exception('Class variable shall be of kind field or static')
                else:
                    raise Exception('Variable assigned is not declared')
                self.compileExpression()
                self.writeVM('add')
                self.compileSymbol(']')[0]
            cplret = cplret and self.compileSymbol('=')[0]
            cplret = cplret and self.compileExpression()
            cplret = cplret and self.compileSymbol(';')[0]
            if cplretarr:
                self.writeVM('pop temp 0')
                self.writeVM('pop pointer 1')
                self.writeVM('push temp 0')
                self.writeVM('pop that 0')
            else:
                if self.SubroutineSymbolTable.IsDefined(varname):
                    self.writeVM('pop ' + self.SubroutineSymbolTable.KindOf(varname)\
                             + ' ' + self.SubroutineSymbolTable.IndexOf(varname))
                elif self.ClassSymbolTable.IsDefined(varname):
                    if self.ClassSymbolTable.KindOf(varname) == 'field':
                        self.writeVM('pop this ' + self.ClassSymbolTable.IndexOf(varname))
                    elif self.ClassSymbolTable.KindOf(varname) == 'static':
                        self.writeVM('pop static ' + self.ClassSymbolTable.IndexOf(varname))
                    else:
                        raise Exception('Class variable shall be of kind field or static')
                else:
                    raise Exception('Variable assigned is not declared')
            
        self.putTail('letStatement',cplret)
        return cplret
    
    def compileIfStatement(self):
        self.putHead('ifStatement')
        
        cplret = self.compileKeyword('if')[0]

        cplret = cplret and self.compileSymbol('(')[0]
        cplret = cplret and self.compileExpression()
        cplret = cplret and self.compileSymbol(')')[0]
        if cplret:
            self.writeVM('not')
            L1 = 'IF_TRUE_' + self.getLabel()
            self.writeVM('if-goto ' + L1)
        
        cplret = cplret and self.compileSymbol('{')[0]
        cplret = cplret and self.compileStatements()
        cplret = cplret and self.compileSymbol('}')[0]

        if cplret:
            if self.compileKeyword('else')[0]:
                L2 = 'IF_FALSE_' + self.getLabel()
                self.writeVM('goto ' + L2)
                self.writeVM('label ' + L1)
                self.compileSymbol('{')[0]
                self.compileStatements()
                self.compileSymbol('}')[0]
                self.writeVM('label ' + L2)
            else:
                self.writeVM('label ' + L1)
        self.putTail('ifStatement',cplret)
        return cplret
    
    def compileWhileStatement(self):
        self.putHead('whileStatement')
        
        cplret = self.compileKeyword('while')[0]
        cplret = cplret and self.compileSymbol('(')[0]
        if cplret:
            L1 = 'WHILE_' + self.getLabel()
            self.writeVM('label ' + L1)
        cplret = cplret and self.compileExpression()
        cplret = cplret and self.compileSymbol(')')[0]
        cplret = cplret and self.compileSymbol('{')[0]
        if cplret:
            self.writeVM('not')
            L2 = 'WHILE_' + self.getLabel()
            self.writeVM('if-goto ' + L2)
        cplret = cplret and self.compileStatements()
        cplret = cplret and self.compileSymbol('}')[0]
        if cplret:
            self.writeVM('goto ' + L1)
            self.writeVM('label ' + L2)
        
        self.putTail('whileStatement',cplret)
        return cplret
    
    def compileDoStatement(self):
        self.putHead('doStatement')
        
        cplret = self.compileKeyword('do')[0]
        cplret = cplret and self.compileSubroutineCall()
        cplret = cplret and self.compileSymbol(';')[0]
        
        if cplret:
            self.writeVM('pop temp 0 ')
        self.putTail('doStatement',cplret)
        return cplret
    
    def compileReturnStatement(self):
        self.putHead('returnStatement')
        
        cplret = self.compileKeyword('return')[0]
        if cplret:
            if not self.compileExpression():
                self.writeVM('push constant 0')
            self.writeVM('return')
            cplret = cplret and self.compileSymbol(';')[0]
        
        self.putTail('returnStatement',cplret)
        return cplret
    
    def compileExpression(self):
        self.putHead('expression')
        
        cplret = self.compileTerm()
        if cplret:
            while True:
                cplret_optional, op = self.compileOp()
                cplret_optional = cplret_optional and self.compileTerm()
                if cplret_optional:
                    if op == '+':
                        self.writeVM('add')
                    elif op == '-':
                        self.writeVM('sub')
                    elif op == '*':
                        self.writeVM('call Math.multiply 2')
                    elif op == '/':
                        self.writeVM('call Math.divide 2')
                    elif op == '&':
                        self.writeVM('and')
                    elif op =='|':
                        self.writeVM('or')
                    elif op =='<':
                        self.writeVM('lt')
                    elif op =='>':
                        self.writeVM('gt')
                    elif op == '=':
                        self.writeVM('eq')
                    else:
                        raise Exception('Unrecognized operation')
                else:
                    break
#            while self.compileOp()[0] and self.compileTerm():
#                continue
        
        self.putTail('expression',cplret)
        return cplret
    
    def compileTerm(self):
        self.putHead('term')
        
        cplret = self.compileIntegerConstant()[0] or\
        self.compileStringConstant()[0] or \
        self.compileKeywordConstant()[0] or \
        (self.compileSymbol('(')[0] and self.compileExpression() and self.compileSymbol(')')[0]) or \
        self.compileUnaryOpTerm()
        
        if len(self.tokens)>=2 and self.tokens[1] == '[':
            cplret = cplret or self.compileArrayIndexing()
        elif len(self.tokens)>=2 and (self.tokens[1] == '(' or self.tokens[1] == '.'):
            cplret = cplret or self.compileSubroutineCall()
        else:
            if not cplret:
                cplret, varname = self.compileVarName()
                if cplret:
                    if self.SubroutineSymbolTable.IsDefined(varname):
                        self.writeVM('push ' + self.SubroutineSymbolTable.KindOf(varname)\
                             + ' ' + self.SubroutineSymbolTable.IndexOf(varname))
                    elif self.ClassSymbolTable.IsDefined(varname):
                        if self.ClassSymbolTable.KindOf(varname) == 'field':
                            self.writeVM('push this ' + self.ClassSymbolTable.IndexOf(varname))
                        elif self.ClassSymbolTable.KindOf(varname) == 'static':
                            self.writeVM('push static ' + self.ClassSymbolTable.IndexOf(varname))
                        else:
                            raise Exception('Class variable shall be of kind field or static')
                    else:
                        raise Exception('Variable is not defined')
                        
        self.putTail('term',cplret)
        return cplret
    
    def compileArrayIndexing(self):
        cplret, arrayname = self.compileVarName()
        cplret = cplret and self.compileSymbol('[')[0]
        cplret = cplret and self.compileExpression()
        cplret = cplret and self.compileSymbol(']')[0]
        if cplret == True:
            if self.SubroutineSymbolTable.IsDefined(arrayname):
                self.writeVM('push ' + self.SubroutineSymbolTable.KindOf(arrayname)\
                             + ' ' + self.SubroutineSymbolTable.IndexOf(arrayname))
                self.writeVM('add')
                self.writeVM('pop pointer 1')
                self.writeVM('push that 0')
        return cplret
    def compileUnaryOpTerm(self):
        cplret, op = self.compileUnaryOp()
        cplret = cplret and self.compileTerm()
        if cplret:
            if op == '-':
                self.writeVM('neg')
            elif op == '~':
                self.writeVM('not')
            else:
                raise Exception('Unreconized unary operation')
        return cplret            
        
    def compileSubroutineCall(self):
        if (len(self.tokens)>=2 and self.tokens[1]=='.'):
            cplret = self.compileMethodCall()
        else :
            cplret, subroutinename = self.compileSubroutineName()
            cplret = cplret and self.compileSymbol('(')[0]
            if cplret:
                self.writeVM('push pointer 0')
                cplret, argcount = self.compileExpressionList() 
            cplret = cplret and self.compileSymbol(')')[0]
            if cplret:
                self.writeVM('call ' + self.ClassSymbolTable.name + '.' + subroutinename + ' ' + str( int(argcount) + 1 ) )
            
        return cplret
    
    def compileMethodCall(self):
#        cplret, classname = self.compileClassName()
#        if not cplret:
        cplret, varname = self.compileVarName()
        if cplret:
            if self.SubroutineSymbolTable.IsDefined(varname):
                self.writeVM('push ' + self.SubroutineSymbolTable.KindOf(varname)\
                         + ' ' + self.SubroutineSymbolTable.IndexOf(varname))
                classname = self.SubroutineSymbolTable.TypeOf(varname)
                incr = 1
            elif self.ClassSymbolTable.IsDefined(varname):
                self.writeVM('push this ' + self.ClassSymbolTable.IndexOf(varname))
                classname = self.ClassSymbolTable.TypeOf(varname)
                incr = 1
            else:
                classname = varname
                incr = 0
        cplret = cplret and self.compileSymbol('.')[0]
        if cplret:
            cplret, subroutinename =  self.compileSubroutineName()
            cplret =  cplret and self.compileSymbol('(')[0]
            if cplret:
                cplret, argcount = self.compileExpressionList()
                cplret = cplret and self.compileSymbol(')')[0]
        
        if cplret:
            argcount = str(int(argcount) + incr)
            self.writeVM('call ' + classname + '.' + subroutinename + ' ' + argcount)
#        cplret = (self.compileClassName()[0] or self.compileVarName()[0]) and \
#              self.compileSymbol('.')[0] and \
#              self.compileSubroutineName()[0] and \
#              self.compileSymbol('(')[0] and \
#              self.compileExpressionList() and \
#              self.compileSymbol(')')[0]
        return cplret
    
    def compileExpressionList(self):
        self.putHead('expressionList')
        argcount = 0
        if self.compileExpression():
            argcount +=1
            while self.compileSymbol(',')[0] and self.compileExpression():
                argcount +=1
                continue
        cplret = True
        
        self.putTail('expressionList',cplret)
        return cplret, str(argcount)
    
    def compileOp(self):
        for smbl in ['+','-','*','/','&','|','<','>','=']:
            cplret, op = self.compileSymbol(smbl)
            if cplret:
                break
        return cplret, op
    
    def compileUnaryOp(self):
#        self.writeXML(xmlTag('unaryOp','open', self.indent))
        for smbl in ['-','~']:
            cplret, op = self.compileSymbol(smbl)
            if cplret:
                break
#        self.writeXML(xmlTag('unaryOp','close', self.indent))
        print('compileUnaryOp = '+ str(cplret))
        return cplret, op
    
    def compileKeywordConstant(self):
#        self.writeXML(xmlTag('keywordConstant','open', self.indent))
        for kwrd in ['true', 'false', 'null', 'this']:
            cplret, keyword = self.compileKeyword(kwrd)
            if cplret:
                if keyword == 'true':
                    self.writeVM('push constant 1')
                    self.writeVM('neg')
                elif keyword == 'false' or keyword == 'null':
                    self.writeVM('push constant 0')
                elif keyword == 'this':
                    self.writeVM('push pointer 0')
                else:
                    raise Exception('Unrecognzed keyword constant')
                break
#        self.writeXML(xmlTag('keywordConstant','close', self.indent))
        print('compileKeywordConstant = '+ str(cplret))
        return cplret, keyword
    
    def compileType(self):
#        self.writeXML(xmlTag('type','open', self.indent))
        cplret, typ = self.compileKeyword('int')
        if not cplret:
            cplret, typ = self.compileKeyword('char')
            if not cplret:
                cplret, typ = self.compileKeyword('boolean')
                if not cplret:
                    cplret, typ = self.compileClassName()
#        self.writeXML(xmlTag('type','close', self.indent))
        print('compileType = '+ str(cplret))
        return cplret, typ
    
    def compileAtomic(self, tag):
        token = self.tokens[0]
        if token == '<':
            token = '&lt;'
        elif token == '&':
            token = '&amp;'
        elif token == '>':
            token = '&gt;'
        self.writeXML(xmlTag(tag, 'open', self.indent, True) + ' ' + token + ' ' + xmlTag(tag, 'close', self.indent, True))
        return self.eatToken(tag)
    
    def compileSymbol(self, symbol):
        cplret = False
        smbl = None
        if len(self.tokens)!=0 and self.tokens[0] == symbol:
            cplret, smbl = self.compileAtomic('symbol')
        print('compileSymbol(' + symbol + ') = '+ str(cplret))
        return cplret, smbl
    
    def compileKeyword(self, keyword):
        cplret = False
        kwrd = None
        if len(self.tokens)!=0 and self.tokens[0] == keyword:
            cplret, kwrd = self.compileAtomic('keyword')
        print('compileKeyword(' + keyword + ') = '+ str(cplret))
        return cplret, kwrd
    def compileIntegerConstant(self):
        cplret = False
        integer = None
        if len(self.tokens)!=0 and self.types[0] == 'integerConstant':
            cplret, integer = self.compileAtomic('integerConstant')
        print('compileIntegerConstant = '+ str(cplret))
        if cplret:
            self.writeVM('push constant ' + integer)
        return cplret, integer
    def compileStringConstant(self):
        cplret = False
        string = None
        if len(self.tokens)!=0 and self.types[0] == 'stringConstant':
            cplret, string = self.compileAtomic('stringConstant')
            if cplret == True:
                stringlen = len(string)
                self.writeVM('push constant ' + str(stringlen) )
                self.writeVM('call String.new 1')
                for i in range(stringlen):
                    self.writeVM('push constant ' +  str(ord(string[i])))
                    self.writeVM('call String.appendChar 2')
                
        print('compileStringConstant = '+ str(cplret))
        return cplret, string
    def compileIdentifier(self):
        cplret = False
        identifier = None
        if len(self.tokens)!=0 and self.types[0] == 'identifier':
            cplret, identifier = self.compileAtomic('identifier')
        print('compileIdentifier = '+ str(cplret))
        return cplret, identifier
    def getLabel(self):
        self.label += 1
        return self.useLabel()
    def useLabel(self):
        return 'L' + str(self.label)
    def close(self):
        self.XMLfile.close()
        self.VMfile.close()
    def writeXML(self, string):
        self.XMLcontent = self.XMLcontent + string
    def writeVM(self, string):
        self.VMcontent = self.VMcontent + string + '\r'
    def writeFile(self):
        self.XMLfile.write(self.XMLcontent)
        self.VMfile.write(self.VMcontent)
        

def xmlTag(taged_string, select, n_indentation = 0, same_line = False):
    if select == 'open':
        string = '<' + taged_string + '>'
        if not same_line:
             string = string + '\r'
        string = n_indentation * '  ' + string
        return  string
    elif select == 'close':
        string = '<' + '/' + taged_string + '>\r'
        string = (not same_line) * n_indentation * '  ' + string
#        if not same_line:
#            string = '\r' + string
        return  string
    else:
        print('ERROR : Unrecognized XML tag selection')
        return  ''

path ='/Users/lutzc/Desktop/nand2tetris/projects/11/ComplexArrays'

# Code to support handling of directory and file.
# Output: filenameIn/fileOut full paths
if os.path.isdir(path):
    filename = os.listdir(path)
    for idx in range(len(filename)):
        filename[idx] = path +'/'+ filename[idx]
    filenameOut = path +'/'+ path.split('/')[-1] +'.jack'
elif os.path.isfile(path):
    filename = []
    filename.append(path)
else:
    print('Path not valid')
filenameIn = []
for file in filename:
    print(file[-5:])
    if file[-5:] =='.jack':
        filenameIn.append(file)


for fileIn in filenameIn:
    tzr = tokenizer(fileIn)
    tzr.collectTokens()
    tzr.printTokens()
    tzr.close()
    fileOut = fileIn[:-5]
    print('Parsing ' + fileIn.split('/')[-1] + '...')
    psr = parser(fileOut, tzr.tokens, tzr.types)
    psr.parse()
    if len(psr.tokens)==0:
        print('All tokens have been consumed')
    else:
         raise Exception('Error during parsing')
    psr.writeFile()
    psr.close()
    print('Parsing done')
    psr.ClassSymbolTable.printTable()
    psr.SubroutineSymbolTable.printTable()
