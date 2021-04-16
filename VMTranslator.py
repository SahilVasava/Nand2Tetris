#!/usr/bin/env python3

import sys
import os

class Parser:
    def __init__(self,inst):
        self.inst = inst
        self.type = None 
        self.arg1V = None
        self.arg2V = None
        self.cleanUp()
        self.checkType()

    def checkType(self):
        arith = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        if self.inst == '':
            return 
        elif self.inst.startswith('push'):
            self.type = 'C_PUSH'
        elif self.inst.startswith('pop'):
            self.type = 'C_POP'
        elif self.inst.startswith('label'):
            self.type = 'C_LABEL'
        elif self.inst.startswith('if-goto'):
            self.type = 'C_IF'
        elif self.inst.startswith('goto'):
            self.type = 'C_GOTO'
        elif self.inst.startswith('function'):
            self.type = 'C_FUNCTION'
        elif self.inst.startswith('return'):
            self.type = 'C_RETURN'
        elif self.inst.startswith('call'):
            self.type = 'C_CALL'
        elif any(map(self.inst.__contains__, arith)):
            self.type = 'C_ARITHMETIC'

    def arg1(self):
        if self.type == 'C_ARITHMETIC':
            self.arg1V = self.inst
            return self.arg1V
        elif self.type == 'C_PUSH' or self.type == 'C_POP' or self.type == 'C_LABEL' or self.type == 'C_IF' or self.type == 'C_GOTO' or self.type == 'C_CALL' or self.type == 'C_FUNCTION':
            self.arg1V = self.inst.split(' ')[1]
            return self.arg1V
        else:
            return None 

    def arg2(self):
        if self.type == 'C_PUSH' or self.type == 'C_POP' or self.type == 'C_CALL' or self.type == 'C_FUNCTION':
            self.arg2V = self.inst.split(' ')[2]
            return self.arg2V
        else:
            return None 

    def cleanUp(self):
        self.inst = self.inst.strip()
        cInd = self.inst.find('//')
        if cInd == -1:
            self.inst = self.inst.strip()
        elif cInd == 0:
            self.inst = ''
        else:
            self.inst = self.inst[0:cInd].strip()
    

class CodeWriter:
    def __init__(self):
        path = os.path.abspath(sys.argv[1])
        if os.path.isdir(path):
            dirName = os.path.basename(os.path.normpath(path))
            path = os.path.join(path, dirName+'.asm')
        else:
            path, _ = os.path.splitext(path) 
            path = path + '.asm'
        self.asm = open(path,'w') 
        self.ltCount = 0
        self.gtCount = 0
        self.eqCount = 0
        self.ltECount = 0
        self.gtECount = 0
        self.eqECount = 0
        self.funcECount = 0
        self.callECount = 0
        self.lineCount = 0
        self.writeInit()
    
    def finish(self):
        self.asm.close()

    def writeInit(self):
        '''
            
            @256
            D=A
            @SP
            M=D
    
            call Sys.init      
            
        '''
        initC = f'@256,D=A,@SP,M=D'
        self.asm.write(f'// Init code\n')
        self.asm.write(initC.replace(',','\n'))
        self.asm.write('\n\n')
        p = Parser('call Sys.init 0')
        self.writeCall(p)

    def writeArithmetic(self, parser):
        if parser.type != 'C_ARITHMETIC':
            return
        addC = '@SP,M=M-1,A=M,D=M,@SP,M=M-1,A=M,M=M+D,@SP,M=M+1'
        subC = '@SP,M=M-1,A=M,D=M,@SP,M=M-1,A=M,M=M-D,@SP,M=M+1'
        negC = '@SP,M=M-1,A=M,M=-M,@SP,M=M+1'
        ltC = f'@SP,M=M-1,A=M,D=M,@y,M=D,@SP,M=M-1,A=M,D=M,@x,M=D,@y,D=D-M,@LT{self.ltCount},D;JLT,@SP,A=M,M=0,@LT_END{self.ltECount},0;JMP,(LT{self.ltCount}),@SP,A=M,M=-1,(LT_END{self.ltECount}),@SP,M=M+1'
        gtC = f'@SP,M=M-1,A=M,D=M,@y,M=D,@SP,M=M-1,A=M,D=M,@x,M=D,@y,D=D-M,@GT{self.gtCount},D;JGT,@SP,A=M,M=0,@GT_END{self.gtECount},0;JMP,(GT{self.gtCount}),@SP,A=M,M=-1,(GT_END{self.gtECount}),@SP,M=M+1'
        eqC = f'@SP,M=M-1,A=M,D=M,@y,M=D,@SP,M=M-1,A=M,D=M,@x,M=D,@y,D=D-M,@EQ{self.eqCount},D;JEQ,@SP,A=M,M=0,@EQ_END{self.eqECount},0;JMP,(EQ{self.eqCount}),@SP,A=M,M=-1,(EQ_END{self.eqECount}),@SP,M=M+1'
        andC = '@SP,M=M-1,A=M,D=M,@SP,M=M-1,A=M,M=M&D,@SP,M=M+1'
        orC = '@SP,M=M-1,A=M,D=M,@SP,M=M-1,A=M,M=M|D,@SP,M=M+1'
        notC = '@SP,M=M-1,A=M,M=!M,@SP,M=M+1'

        self.lineCount += 1
        if parser.arg1() == 'add':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(addC.replace(',','\n'))
            self.asm.write('\n\n')
        elif parser.arg1() == 'sub':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(subC.replace(',','\n'))
            self.asm.write('\n\n')
        elif parser.arg1() == 'neg':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(negC.replace(',','\n'))
            self.asm.write('\n\n')
        elif parser.arg1() == 'lt':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(ltC.replace(',','\n'))
            self.asm.write('\n\n')
            self.ltCount += 1
            self.ltECount += 1
        elif parser.arg1() == 'gt':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(gtC.replace(',','\n'))
            self.asm.write('\n\n')
            self.gtCount += 1
            self.gtECount += 1
        elif parser.arg1() == 'eq':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(eqC.replace(',','\n'))
            self.asm.write('\n\n')
            self.eqCount += 1
            self.eqECount += 1
        elif parser.arg1() == 'and':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(andC.replace(',','\n'))
            self.asm.write('\n\n')
        elif parser.arg1() == 'or':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(orC.replace(',','\n'))
            self.asm.write('\n\n')
        elif parser.arg1() == 'not':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(notC.replace(',','\n'))
            self.asm.write('\n\n')
            
    def writePushPop(self, parser, fileN):
        print('1 pushpop called', parser.inst, parser.type)
        if parser.type != 'C_PUSH' and parser.type != 'C_POP':
            return
        print('pushpop called')
        arg1 = parser.arg1()
        arg2 = parser.arg2()
        pushLcl = f'@{arg2},D=A,@addr,M=D,@LCL,D=M,@addr,M=M+D,A=M,D=M,@SP,A=M,M=D,@SP,M=M+1'
        pushArg = f'@{arg2},D=A,@addr,M=D,@ARG,D=M,@addr,M=M+D,A=M,D=M,@SP,A=M,M=D,@SP,M=M+1'
        pushThis = f'@{arg2},D=A,@addr,M=D,@THIS,D=M,@addr,M=M+D,A=M,D=M,@SP,A=M,M=D,@SP,M=M+1'
        pushThat = f'@{arg2},D=A,@addr,M=D,@THAT,D=M,@addr,M=M+D,A=M,D=M,@SP,A=M,M=D,@SP,M=M+1'

        popLcl = f'@{arg2},D=A,@addr,M=D,@LCL,D=M,@addr,M=M+D,@SP,M=M-1,A=M,D=M,@addr,A=M,M=D'
        popArg = f'@{arg2},D=A,@addr,M=D,@ARG,D=M,@addr,M=M+D,@SP,M=M-1,A=M,D=M,@addr,A=M,M=D'
        popThis = f'@{arg2},D=A,@addr,M=D,@THIS,D=M,@addr,M=M+D,@SP,M=M-1,A=M,D=M,@addr,A=M,M=D'
        popThat = f'@{arg2},D=A,@addr,M=D,@THAT,D=M,@addr,M=M+D,@SP,M=M-1,A=M,D=M,@addr,A=M,M=D'

        pushConst = f'@{arg2},D=A ,@SP,A=M,M=D,@SP,M=M+1'

        pushStatic = f'@{fileN}.{arg2},D=M,@SP,A=M,M=D,@SP,M=M+1'
        popStatic = f'@SP,M=M-1,A=M,D=M,@{fileN}.{arg2},M=D'

        pushTemp = f'@{arg2},D=A,@addr,M=D,@5,D=A,@addr,M=M+D,A=M,D=M,@SP,A=M,M=D,@SP,M=M+1'
        popTemp = f'@{arg2},D=A,@addr,M=D,@5,D=A,@addr,M=M+D,@SP,M=M-1,A=M,D=M,@addr,A=M,M=D'

        pushPoint0 = f'@THIS,D=M,@SP,A=M,M=D,@SP,M=M+1'
        pushPoint1 = f'@THAT,D=M,@SP,A=M,M=D,@SP,M=M+1'
        popPoint0 = f'@SP,M=M-1,A=M,D=M,@THIS,M=D'
        popPoint1 = f'@SP,M=M-1,A=M,D=M,@THAT,M=D'
        print(f'arg1: {arg1} arg2: {arg2}')
        self.lineCount += 1
        if arg1 == 'local' and parser.type == 'C_PUSH':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(pushLcl.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'local' and parser.type == 'C_POP':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(popLcl.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'argument' and parser.type == 'C_PUSH':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(pushArg.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'argument' and parser.type == 'C_POP':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(popArg.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'this' and parser.type == 'C_PUSH':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(pushThis.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'this' and parser.type == 'C_POP':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(popThis.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'that' and parser.type == 'C_PUSH':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(pushThat.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'that' and parser.type == 'C_POP':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(popThat.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'constant' and parser.type == 'C_PUSH':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(pushConst.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'static' and parser.type == 'C_PUSH':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(pushStatic.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'static' and parser.type == 'C_POP':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(popStatic.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'temp' and parser.type == 'C_PUSH':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(pushTemp.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'temp' and parser.type == 'C_POP':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(popTemp.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'pointer' and parser.type == 'C_PUSH' and arg2 == '0':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(pushPoint0.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'pointer' and parser.type == 'C_PUSH' and arg2 == '1':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(pushPoint1.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'pointer' and parser.type == 'C_POP' and arg2 == '0':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(popPoint0.replace(',','\n'))
            self.asm.write('\n\n')
        elif arg1 == 'pointer' and parser.type == 'C_POP' and arg2 == '1':
            self.asm.write(f'// {parser.inst}\n')
            self.asm.write(popPoint1.replace(',','\n'))
            self.asm.write('\n\n')

    def writeLabel(self, parser):
        '''
            label loop

            (loop)
        '''
        if parser.type != 'C_LABEL':
            return
        arg1 = parser.arg1()
        labelC = f'({arg1})'

        self.asm.write(f'// {parser.inst}\n')
        self.asm.write(labelC)
        self.asm.write('\n\n')
    
    def writeGoto(self, parser):
        '''
            goto label

            @label
            0;JMP
        '''
        if parser.type != 'C_GOTO':
            return
        arg1 = parser.arg1()
        gotoC = f'@{arg1},0;JMP'

        self.lineCount += 1
        self.asm.write(f'// {parser.inst}\n')
        self.asm.write(gotoC.replace(',','\n'))
        self.asm.write('\n\n')
            
    def writeIf(self, parser):
        '''
            logicalInst
            if-goto label 

            @SP
            M=M-1
            A=M
            D=M 
            @label
            D;JNE
        '''
        if parser.type != 'C_IF':
            return
        arg1 = parser.arg1()
        ifC = f'@SP,M=M-1,A=M,D=M,@{arg1},D;JNE'

        self.lineCount += 1
        self.asm.write(f'// {parser.inst}\n')
        self.asm.write(ifC.replace(',','\n'))
        self.asm.write('\n\n')

    def writeFunction(self, parser):
        '''
            function functionName nVars

            Pseudo code:
            (arg1)
            i = nVars
            while i>0:
                *SP = 0
                SP = SP + 1
                i-=1

            (arg1)
            @arg2
            D=A
            @i
            M=D
            (FUNC.LOOP{funcECount}) 
            @i
            D=M
            @FUNC.STOP{funcECount}
            D;JEQ
            @SP
            A=M
            M=0
            @SP
            M=M+1 
            @i
            M=M-1
            @FUNC.LOOP{funcECount}
            0;JMP
            (FUNC.STOP{funcECount})
        '''
        if parser.type != 'C_FUNCTION':
            return
        arg1 = parser.arg1()
        arg2 = parser.arg2()
        funcC = f'({arg1}),@{arg2},D=A,@i,M=D,(FUNC.LOOP{self.funcECount}),@i,D=M,@FUNC.STOP{self.funcECount},D;JEQ,@SP,A=M,M=0,@SP,M=M+1,@i,M=M-1,@FUNC.LOOP{self.funcECount},0;JMP,(FUNC.STOP{self.funcECount})'

        self.asm.write(f'// {parser.inst}\n')
        self.asm.write(funcC.replace(',','\n'))
        self.asm.write('\n\n')
        self.funcECount += 1

    def writeReturn(self, parser):
        '''
            return
            

            @LCL
            D=M
            @endFrame
            M=D

            @5
            D=A
            @addr
            M=D 
            @endFrame
            D=M
            @addr
            M=D-M
            A=M
            D=M
            @retAddr
            M=D

            @SP
            M=M-1
            A=M
            D=M
            @ARG
            A=M
            M=D 

            D=A+1
            @SP
            M=D

            @endFrame
            D=M
            @addr
            M=D-1
            A=M
            D=M
            @THAT
            M=D

            @2
            D=A
            @addr
            M=D 
            @endFrame
            D=M
            @addr
            M=D-M
            A=M
            D=M
            @THIS
            M=D

            @3
            D=A
            @addr
            M=D 
            @endFrame
            D=M
            @addr
            M=D-M
            A=M
            D=M
            @ARG
            M=D

            @4
            D=A
            @addr
            M=D 
            @endFrame
            D=M
            @addr
            M=D-M
            A=M
            D=M
            @LCL
            M=D

            @retAddr
            A=M
            0;JMP
        ''' 
        if parser.type != 'C_RETURN':
            return
        returnC = f'@LCL,D=M,@endFrame,M=D,@5,D=A,@addr,M=D ,@endFrame,D=M,@addr,M=D-M,A=M,D=M,@retAddr,M=D,@SP,M=M-1,A=M,D=M,@ARG,A=M,M=D,D=A+1,@SP,M=D,@endFrame,D=M,@addr,M=D-1,A=M,D=M,@THAT,M=D,@2,D=A,@addr,M=D ,@endFrame,D=M,@addr,M=D-M,A=M,D=M,@THIS,M=D,@3,D=A,@addr,M=D ,@endFrame,D=M,@addr,M=D-M,A=M,D=M,@ARG,M=D,@4,D=A,@addr,M=D ,@endFrame,D=M,@addr,M=D-M,A=M,D=M,@LCL,M=D,@retAddr,A=M,0;JMP'

        self.asm.write(f'// {parser.inst}\n')
        self.asm.write(returnC.replace(',','\n'))
        self.asm.write('\n\n')

    def writeCall(self, parser):
        '''
            call functionName numArgs 
            
            @retAddrLabel{callECount}
            D=A
            @SP
            A=M
            M=D
            @SP
            M=M+1

            @LCL
            D=M
            @SP
            A=M
            M=D
            @SP
            M=M+1

            @ARG
            D=M
            @SP
            A=M
            M=D
            @SP
            M=M+1

            @THIS
            D=M
            @SP
            A=M
            M=D
            @SP
            M=M+1

            @THAT
            D=M
            @SP
            A=M
            M=D
            @SP
            M=M+1

            @5
            D=A
            @addr
            M=D
            @SP
            D=M
            @addr
            M=D-M
            @{arg2}
            D=A
            @addr
            M=M-D
            D=M 
            @ARG
            M=D

            @SP
            D=M
            @LCL
            M=D

            @{arg1}
            0;JMP

            (retAddrLabel{callECount})
        '''
        if parser.type != 'C_CALL':
            return
        arg1 = parser.arg1()
        if parser.arg2() != None:
            arg2 = parser.arg2()
        else:
            arg2 = '0'

        callC = f'@retAddrLabel{self.callECount},D=A,@SP,A=M,M=D,@SP,M=M+1,@LCL,D=M,@SP,A=M,M=D,@SP,M=M+1,@ARG,D=M,@SP,A=M,M=D,@SP,M=M+1,@THIS,D=M,@SP,A=M,M=D,@SP,M=M+1,@THAT,D=M,@SP,A=M,M=D,@SP,M=M+1,@5,D=A,@addr,M=D,@SP,D=M,@addr,M=D-M,@{arg2},D=A,@addr,M=M-D,D=M,@ARG,M=D,@SP,D=M,@LCL,M=D,@{arg1},0;JMP,(retAddrLabel{self.callECount})'

        self.asm.write(f'// {parser.inst}\n')
        self.asm.write(callC.replace(',','\n'))
        self.asm.write('\n\n')
        self.callECount += 1
        


def main():
    path = os.path.abspath(sys.argv[1])
    code = CodeWriter()
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            print(f'Files {files}')
            if 'Sys.vm' in files:
                setup(os.path.join(root,'Sys.vm'),code)
            for filee in files:
                fileN, ext = os.path.splitext(filee)
                if filee != 'Sys.vm' and  ext == '.vm':
                    print(f'fileeeee {filee}')
                    setup(os.path.join(root, filee),code, fileN)
    else:
        setup(path,code) 
    code.finish()
        
                    
def setup(path,code, fileN = None):
    with open(path, 'r') as vm:
        for inst in vm:
            p = Parser(inst)
            print(p.inst,p.type)    
            if p.type == 'C_ARITHMETIC':
                code.writeArithmetic(p)
            elif p.type == 'C_PUSH' or p.type == 'C_POP':
                code.writePushPop(p, fileN)
            elif p.type == 'C_IF':
                code.writeIf(p)
            elif p.type == 'C_LABEL':
                code.writeLabel(p)
            elif p.type == 'C_GOTO':
                code.writeGoto(p)
            elif p.type == 'C_FUNCTION':
                code.writeFunction(p)
            elif p.type == 'C_RETURN':
                code.writeReturn(p)
            elif p.type == 'C_CALL':
                code.writeCall(p)
    

if __name__ == "__main__":
    main()
