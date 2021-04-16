#!/usr/bin/env python3

import sys

class Parser:
    def __init__(self,inst):
        self.inst = inst
        self.type = None 
        self.valueV = None
        self.destV = None
        self.compV = None
        self.jumpV = None
        self.cleanUp()
        self.checkType()

    def checkType(self):
        if self.inst == '':
            return 
        elif self.inst.startswith('@'):
            self.type = 'A'
        elif self.inst.startswith('('):
            self.type = 'L'
        else:
            self.type = 'C'

    def value(self):
        if self.type != 'A':
            return None
        self.valueV = self.inst[1:].split(' ')[0]
        return self.valueV

    def cleanUp(self):
        self.inst = self.inst.strip()
        cInd = self.inst.find('//')
        if cInd == -1:
            self.inst = self.inst.strip()
        elif cInd == 0:
            self.inst = ''
        else:
            self.inst = self.inst[0:cInd].strip()
    
    def dest(self):
        eInd = self.inst.find('=')
        if self.type != 'C' or eInd  == -1:
            return None
        self.destV = self.inst[0:eInd].strip() 
        return self.destV    

    def comp(self):
        eInd = self.inst.find('=')
        sInd = self.inst.find(';')
        if self.type != 'C':
            return None
        if eInd != -1 and sInd != -1:
            self.compV = self.inst[eInd+1:sInd].strip()
        elif eInd != -1 and sInd == -1:
            self.compV = self.inst[eInd+1:].strip()
        elif eInd == -1 and sInd != -1:
            self.compV = self.inst[0:sInd].strip()
        elif eInd == -1 and sInd == -1:
            self.compV = self.inst.strip()
        return self.compV 
    
    def jump(self):
        sInd = self.inst.find(';')
        if self.type != 'C' or sInd  == -1:
            return None
        self.jumpV = self.inst[sInd+1:].strip() 
        return self.jumpV

class Code:
    def __init__(self,term):
        self.term = term
        self.valueB = None
        self.destB = None
        self.jumpB = None
        self.compB = None

    def decimalToBinary(self,n):
        return format(n, '016b')
        #return bin(n).replace("0b", "")

    def value(self):
        if self.term == None:
            return None
        self.valueB = self.decimalToBinary(int(self.term))
        return self.valueB
    
    def dest(self):
        if self.term == None:
            self.destB = '000'
        elif self.term == 'M':
            self.destB = '001'
        elif self.term == 'D':
            self.destB = '010'
        elif self.term == 'MD':
            self.destB = '011'
        elif self.term == 'A':
            self.destB = '100'
        elif self.term == 'AM':
            self.destB = '101'
        elif self.term == 'AD':
            self.destB = '110'
        elif self.term == 'AMD':
            self.destB = '111'
        return self.destB
    
    def comp(self):
        a = '0'
        c = ''
        if self.term == None:
            self.compB = None
        elif self.term == '0':
            a = '0'
            c = '101010'
        elif self.term == '1':
            a = '0'
            c = '111111'
        elif self.term == '-1':
            a = '0'
            c = '111010'
        elif self.term == 'D':
            a = '0'
            c = '001100'
        elif self.term == 'A':
            a = '0'
            c = '110000'
        elif self.term == '!D':
            a = '0'
            c = '001101'
        elif self.term == '!A':
            a = '0'
            c = '110001'
        elif self.term == '-D':
            a = '0'
            c = '001111'
        elif self.term == '-A':
            a = '0'
            c = '110011'
        elif self.term == 'D+1':
            a = '0'
            c = '011111'
        elif self.term == 'A+1':
            a = '0'
            c = '110111'
        elif self.term == 'D-1':
            a = '0'
            c = '001110'
        elif self.term == 'A-1':
            a = '0'
            c = '110010'
        elif self.term == 'D+A':
            a = '0'
            c = '000010'
        elif self.term == 'D-A':
            a = '0'
            c = '010011'
        elif self.term == 'A-D':
            a = '0'
            c = '000111'
        elif self.term == 'D&A':
            a = '0'
            c = '000000'
        elif self.term == 'D|A':
            a = '0'
            c = '010101'
        elif self.term == 'M':
            a = '1'
            c = '110000'
        elif self.term == '!M':
            a = '1'
            c = '110001'
        elif self.term == '-M':
            a = '1'
            c = '110011'
        elif self.term == 'M+1':
            a = '1'
            c = '110111'
        elif self.term == 'M-1':
            a = '1'
            c = '110010'
        elif self.term == 'D+M':
            a = '1'
            c = '000010'
        elif self.term == 'D-M':
            a = '1'
            c = '010011'
        elif self.term == 'M-D':
            a = '1'
            c = '000111'
        elif self.term == 'D&M':
            a = '1'
            c = '000000'
        elif self.term == 'D|M':
            a = '1'
            c = '010101'
        self.compB = a + c
        return self.compB

    def jump(self):
        if self.term == None:
            self.jumpB = '000'
        elif self.term == 'JGT':
            self.jumpB = '001'
        elif self.term == 'JEQ':
            self.jumpB = '010'
        elif self.term == 'JGE':
            self.jumpB = '011'
        elif self.term == 'JLT':
            self.jumpB = '100'
        elif self.term == 'JNE':
            self.jumpB = '101'
        elif self.term == 'JLE':
            self.jumpB = '110'
        elif self.term == 'JMP':
            self.jumpB = '111'
        return self.jumpB
    
    
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.addPreDef()

    def addPreDef(self):
        for i in range(16):
            self.symbols["R"+str(i)] = i
        self.symbols["SCREEN"] = 16384
        self.symbols["KBD"] = 24576
        self.symbols["SP"] = 0
        self.symbols["LCL"] = 1
        self.symbols["ARG"] = 2
        self.symbols["THIS"] = 3
        self.symbols["THAT"] = 4
    
    def exists(self, symbol):
        if self.symbols.get(symbol) == None:
            return False
        else: 
            return True 
    
    def addSym(self, symbol, value):
        self.symbols[symbol] = value
    
    def getVal(self, symbol):
        return self.symbols.get(symbol)
    
class Passs:
    def __init__(self, symTab):
        self.symTab = symTab
    
    def firstPass(self):
        with open(sys.argv[1], 'r') as asm:
            lineNo = -1
            for inst in asm:
                p = Parser(inst)
                if p.type == 'A' or p.type == 'C':
                    lineNo += 1
                if p.type == 'L':
                    symbol = p.inst[1:-1]
                    if not self.symTab.exists(symbol):
                       self.symTab.addSym(symbol, lineNo+1) 

    def secPass(self):
        with open(sys.argv[1].split('.')[0]+'.hack','w') as hack:
            with open(sys.argv[1], 'r') as asm:
                n = 16
                for inst in asm:
                    p = Parser(inst)
                    if p.type == 'A':
                        symbol = p.inst[1:]
                        if self.symTab.exists(symbol):
                            c = Code(self.symTab.getVal(symbol))
                            hack.write(c.value()+'\n') 
                        else:
                            try:
                                val = int(symbol)
                                c = Code(val)
                                hack.write(c.value()+'\n') 
                            except ValueError:
                                self.symTab.addSym(symbol, n)
                                c = Code(n)
                                hack.write(c.value()+'\n') 
                                n += 1
                    elif p.type == 'C':
                        d = Code(p.dest())
                        c = Code(p.comp())
                        j = Code(p.jump())
                        hack.write('111'+c.comp()+d.dest()+j.jump()+'\n') 
                        
        
def main():
    st = SymbolTable()
    pas = Passs(st)
    pas.firstPass()
    pas.secPass()

if __name__ == "__main__":
    main()

