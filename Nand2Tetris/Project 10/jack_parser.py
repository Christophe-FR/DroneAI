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

class parser():
    tokens = []
    types = []
    content = ''
    indent = 0
    def __init__(self,filename, tokens, types):
        self.file = open(filename,'w')
        self.tokens = tokens
        self.types = types
        self.landmarks = []

    def eatToken(self, tokentype):
#        print(self.tokens[0:3])
        if self.types[0] == tokentype:
            self.isEaten = True
            self.tokens.pop(0)
            self.types.pop(0)
            return True
        else:
            return False
         
    def parse(self):
        while self.compileClass():
            continue
    def putHead(self, name):
        self.landmarks.append(len(self.content))
        self.writeContent(xmlTag(name,'open', self.indent))
        self.indent +=1
    def putTail(self,name, cplret):
        self.indent -=1
        self.writeContent(xmlTag(name,'close', self.indent))
        stop = self.landmarks.pop()
        if cplret == False:
            self.content = self.content[0:stop]
        print('compile' + name + ' = '+ str(cplret))
    def compileClass(self):
        self.putHead('class')
        
        cplret = \
        self.compileKeyword('class') and \
        self.compileClassName() and \
        self.compileSymbol('{')
        if cplret:
            while self.compileClassVarDec():
                continue
            while self.compileSubroutineDec():
                continue
        cplret = cplret and self.compileSymbol('}') 

        self.putTail('class',cplret)
        return cplret
    
    def compileClassName(self):
        cplret = self.compileIdentifier()
        print('compileClassName = '+ str(cplret))
        return cplret
    
    def compileVarName(self):
        cplret = self.compileIdentifier()
        print('compileVarName = '+ str(cplret))
        return cplret
    
    def compileSubroutineName(self):
        cplret = self.compileIdentifier()
        print('compileSubroutineName = '+ str(cplret))
        return cplret
    
    def compileClassVarDec(self):
        self.putHead('classVarDec')
        
        cplret = self.compileKeyword('static') or self.compileKeyword('field')
        cplret = cplret and self.compileType() 
        cplret = cplret and self.compileVarName() 
        if cplret:
            while self.compileSymbol(',') and self.compileVarName():
                continue
        cplret = cplret and self.compileSymbol(';')
        
        self.putTail('classVarDec',cplret)
        return cplret
    
    def compileSubroutineDec(self):
        self.putHead('subroutineDec')
        
        cplret = self.compileKeyword('constructor') or self.compileKeyword('function') or self.compileKeyword('method') 
        cplret = cplret and (self.compileKeyword('void') or self.compileType())
        cplret = cplret and self.compileSubroutineName() 
        cplret = cplret and self.compileSymbol('(') 
        cplret = cplret and self.compileParameterList()
        cplret = cplret and self.compileSymbol(')')
        cplret = cplret and self.compileSubroutineBody() 
        
        self.putTail('subroutineDec',cplret)
        return cplret
    
    def compileParameterList(self):
        self.putHead('parameterList')
        
        if self.compileType() and self.compileVarName():
            while self.compileSymbol(',') and self.compileType() and self.compileVarName():
                continue
        cplret = True
        
        self.putTail('parameterList',cplret)
        return cplret
    
    def compileSubroutineBody(self):
        self.putHead('subroutineBody')
        
        cplret = self.compileSymbol('{')
        if cplret:
            while self.compileVarDec():
                continue
        cplret = cplret and self.compileStatements() 
        cplret = cplret and self.compileSymbol('}') 

        self.putTail('subroutineBody',cplret)
        return cplret
    
    def compileVarDec(self):
        self.putHead('varDec')
        
        cplret = self.compileKeyword('var')
        cplret = cplret and self.compileType() 
        cplret = cplret and self.compileVarName()
        if cplret:
            while self.compileSymbol(',') and self.compileVarName():
                continue
        cplret = cplret and self.compileSymbol(';')
        
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
        
        cplret = self.compileKeyword('let')
        cplret = cplret and self.compileVarName() 
        if cplret:
            self.compileSymbol('[')
            self.compileExpression()
            self.compileSymbol(']')
        cplret = cplret and self.compileSymbol('=')
        cplret = cplret and self.compileExpression()
        cplret = cplret and self.compileSymbol(';')
        
        self.putTail('letStatement',cplret)
        return cplret
    
    def compileIfStatement(self):
        self.putHead('ifStatement')
        
        cplret = self.compileKeyword('if')

        cplret = cplret and self.compileSymbol('(')
        cplret = cplret and self.compileExpression()
        cplret = cplret and self.compileSymbol(')') 
        cplret = cplret and self.compileSymbol('{')
        cplret = cplret and self.compileStatements() 
        cplret = cplret and self.compileSymbol('}')

        if self.compileKeyword('else'):
            self.compileSymbol('{')
            self.compileStatements()
            self.compileSymbol('}')
            
        self.putTail('ifStatement',cplret)
        return cplret
    
    def compileWhileStatement(self):
        self.putHead('whileStatement')
        
        cplret = self.compileKeyword('while')
        cplret = cplret and self.compileSymbol('(') 
        cplret = cplret and self.compileExpression()
        cplret = cplret and self.compileSymbol(')') 
        cplret = cplret and self.compileSymbol('{')
        cplret = cplret and self.compileStatements()
        cplret = cplret and self.compileSymbol('}')
        
        self.putTail('whileStatement',cplret)
        return cplret
    
    def compileDoStatement(self):
        self.putHead('doStatement')
        
        cplret = self.compileKeyword('do')
        cplret = cplret and self.compileSubroutineCall()
        cplret = cplret and self.compileSymbol(';')
        
        self.putTail('doStatement',cplret)
        return cplret
    
    def compileReturnStatement(self):
        self.putHead('returnStatement')
        
        cplret = self.compileKeyword('return')
        if cplret:
            self.compileExpression()
        cplret = cplret and self.compileSymbol(';')
        
        self.putTail('returnStatement',cplret)
        return cplret
    
    def compileExpression(self):
        self.putHead('expression')
        
        cplret = self.compileTerm()
        if cplret:
            while self.compileOp() and self.compileTerm():
                continue
        
        self.putTail('expression',cplret)
        return cplret
    
    def compileTerm(self):
        self.putHead('term')
        
        cplret = self.compileIntegerConstant() or\
        self.compileStringConstant() or \
        self.compileKeywordConstant() or \
        (self.compileSymbol('(') and self.compileExpression() and self.compileSymbol(')')) or \
        (self.compileUnaryOp() and self.compileTerm())
        
        if len(self.tokens)>=2 and self.tokens[1] == '[':
            cplret = cplret or (self.compileVarName() and self.compileSymbol('[') and self.compileExpression() and self.compileSymbol(']'))
        elif len(self.tokens)>=2 and (self.tokens[1] == '(' or self.tokens[1] == '.'):
            cplret = cplret or self.compileSubroutineCall()
        else:
            cplret = cplret or self.compileVarName()
        
        self.putTail('term',cplret)
        return cplret
    
    def compileSubroutineCall(self):
        if (len(self.tokens)>=2 and self.tokens[1]=='.'):
            cplret = ( \
                  (self.compileClassName() or self.compileVarName()) and \
                  self.compileSymbol('.') and \
                  self.compileSubroutineName() and \
                  self.compileSymbol('(') and \
                  self.compileExpressionList() and \
                  self.compileSymbol(')') \
                  )
        else :
            cplret = ( \
                  self.compileSubroutineName() and \
                  self.compileSymbol('(') and \
                  self.compileExpressionList() and \
                  self.compileSymbol(')') \
                  )
        return cplret
    
    def compileExpressionList(self):
        self.putHead('expressionList')
        
        if self.compileExpression():
            while self.compileSymbol(',') and self.compileExpression():
                continue
        cplret = True
        
        self.putTail('expressionList',cplret)
        return cplret
    
    def compileOp(self):
        cplret = self.compileSymbol('+') or \
        self.compileSymbol('-') or \
        self.compileSymbol('*') or \
        self.compileSymbol('/') or \
        self.compileSymbol('&') or \
        self.compileSymbol('|') or \
        self.compileSymbol('<') or \
        self.compileSymbol('>') or \
        self.compileSymbol('=')
        return cplret
    
    def compileUnaryOp(self):
#        self.writeContent(xmlTag('unaryOp','open', self.indent))
        cplret = self.compileSymbol('-') or self.compileSymbol('~')
#        self.writeContent(xmlTag('unaryOp','close', self.indent))
        print('compileUnaryOp = '+ str(cplret))
        return cplret
    
    def compileKeywordConstant(self):
#        self.writeContent(xmlTag('keywordConstant','open', self.indent))
        cplret = self.compileKeyword('true') or \
        self.compileKeyword('false') or \
        self.compileKeyword('null') or \
        self.compileKeyword('this')
#        self.writeContent(xmlTag('keywordConstant','close', self.indent))
        print('compileKeywordConstant = '+ str(cplret))
        return cplret
    
    def compileType(self):
#        self.writeContent(xmlTag('type','open', self.indent))
        cplret = self.compileKeyword('int') or \
        self.compileKeyword('char') or \
        self.compileKeyword('boolean') or \
        self.compileClassName()
#        self.writeContent(xmlTag('type','close', self.indent))
        print('compileType = '+ str(cplret))
        return cplret
    
    def compileAtomic(self, tag):
        token = self.tokens[0]
        if token == '<':
            token = '&lt;'
        elif token == '&':
            token = '&amp;'
        elif token == '>':
            token = '&gt;'
        self.writeContent(xmlTag(tag, 'open', self.indent, True) + ' ' + token + ' ' + xmlTag(tag, 'close', self.indent, True))
        return self.eatToken(tag)
    
    def compileSymbol(self, symbol):
        cplret = False
        if len(self.tokens)!=0 and self.tokens[0] == symbol:
            cplret = self.compileAtomic('symbol')
        print('compileSymbol(' + symbol + ') = '+ str(cplret))
        return cplret
    
    def compileKeyword(self, keyword):
        cplret = False
        if len(self.tokens)!=0 and self.tokens[0] == keyword:
            cplret = self.compileAtomic('keyword')
        print('compileKeyword(' + keyword + ') = '+ str(cplret))
        return cplret
    def compileIntegerConstant(self):
        cplret = False
        if len(self.tokens)!=0 and self.types[0] == 'integerConstant':
            cplret = self.compileAtomic('integerConstant')
        print('compileIntegerConstant = '+ str(cplret))
        return cplret
    def compileStringConstant(self):
        cplret = False
        if len(self.tokens)!=0 and self.types[0] == 'stringConstant':
            cplret = self.compileAtomic('stringConstant')
        print('compileStringConstant = '+ str(cplret))
        return cplret
    def compileIdentifier(self):
        cplret = False
        if len(self.tokens)!=0 and self.types[0] == 'identifier':
            cplret = self.compileAtomic('identifier')
        print('compileIdentifier = '+ str(cplret))
        return cplret
    def close(self):
        self.file.close()
    def writeContent(self, string):
        self.content = self.content + string
    def writeFile(self):
        self.file.write(self.content)
        

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

path ='/Users/lutzc/Desktop/nand2tetris/projects/11/Seven'

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
#    tzr.printTokens()
    tzr.close()
    fileOut = fileIn[:-5] +'.xml'
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
