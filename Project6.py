#!/usr/bin/env python3

import os

symbolTable = { }



def main():
    
   #FileName: "iterate,asm"
    #Opening the file and reading it simultaneously line by line
    
    code = [] # create an empty list which will contain pure code.
    
    for i in range(16):
        symbolTable["R"+str(i)] = i
    symbolTable["SCREEN"] = 16384
    symbolTable["KBD"] = 24576
    symbolTable["SP"] = 0
    symbolTable["LCL"] = 1
    symbolTable["ARG"] = 2
    symbolTable["THIS"] = 3
    symbolTable["THAT"] = 4
    fileName = "../rect/RectL.asm"
    fileName2, _ = os.path.splitext(fileName) 
    outFileName = fileName2 +'_ns' + ".hack"
    
    try:
        inFile = open(fileName, "r")#inFile has the object of while and we are opening the file with permissions of read only
        print("File opened.")
        
    except:
        print("Error opening the file: " + fileName)
        return
    
# Open the output file in write mode.
    try:
        outFile = open(outFileName, "w") # outFile has the object of file
        print("File opened.")
            
    except:
        print("Error openeing the file: " + outFileName)
        return
        
    line = inFile.readline() # reading the file line by line
    
    while line != "":
        line = getPureCode(line)
        if line !="":
            code.append(line)
            
        line = inFile.readline() # Keep printing and raeding the next line until line is equal to null
        
    inFile.close()
   # print(code)
    firstPass(code)
    printSymbolTable(symbolTable)
    #print(code)
    secondPass(code, outFile)
    outFile.close()


def printSymbolTable(symbolTable):
    for x,y in symbolTable.items():
        print(x, ":", y)

    
def getPureCode(line):
    # find and remove comments and spaces. 
    try : 
        pos= line.index("//") #Getting rid of the comments 
        line = line[0:pos] #Extracting the line of code from 0 till position (pos)
    except:
        pass
    line = line.strip() #Removes leading and trailing spaces within the instruction.
    
    line = line.replace(" ", "")# Getting rid of spaces in between pure code
    line = line.replace("\t", "")# Getting rid of tabs
    return line

def firstPass(code):
    global symbolTable
    i = 0
    while i < len(code):
        # Lets check if this list item is a lable symbol.
        if (code[i][0] == "("):  # code[0][0] = @  and code[0][1] = i
            label = parseLabel(code[i]) #(LOOP) ---> LOOP
            if label != "":
                symbolTable[label] = i
            code.pop(i)
            continue   # ignore incrementing i since we have deleted current insturction from the list, i is now pointing to next instruction.
        
        i = i+1
                   
def parseLabel(lblstatement):
    if (lblstatement[-1] ==")"):
        return (lblstatement[1:len(lblstatement)-1])
    return ""


def secondPass(code, outFile):
    n = 16
    i = 0
    global symbolTable
    while i < len(code):
        #Lets check if this the ith element from the list "code" is a variable symbol. Add it in the symbol table.
  
    # check if this is an A instruction
       
        if (code[i][0] == "@"):
            # check if the symbol is already present in symbol table, tranlsate the instruction, otherwise add the symbol in the table and translate the instruction.
            # complete this to add symbol in symbolTable
            bcode, inc = translateA(code[i],n)
            if inc:
                n += 1
        else:
            bcode = translateC(code[i])
        
        i = i+1
        outFile.write(bcode+"\n")
        
    
 
def translateA(inst,n):
    #@16 ---->  00000000000010000 
    # convert the value after @ to bianry, make it 16 bits long and return
    symbol = inst[1:]
    if symbolTable.get(symbol) != None:
        c = Code(symbolTable[symbol])
        return c.value(), False
    else:
        try:
            val = int(symbol)
            c = Code(val)
            return c.value(), False
        except ValueError:
            symbolTable[symbol] = n
            c = Code(n)
            return c.value(), True
    

def translateC(inst):
    d = Code(dest(inst))
    c = Code(comp(inst))
    j = Code(jump(inst))
    # do the translation of C as per the specification of HACK langauge.
    return '111'+c.comp()+d.dest()+j.jump()

def dest(inst):
    eInd = inst.find('=')
    if eInd  == -1:
        return  None
    destV = inst[0:eInd].strip() 
    return destV    

def comp(inst):
    eInd = inst.find('=')
    sInd = inst.find(';')
    if eInd != -1 and sInd != -1:
        compV = inst[eInd+1:sInd].strip()
    elif eInd != -1 and sInd == -1:
        compV = inst[eInd+1:].strip()
    elif eInd == -1 and sInd != -1:
        compV = inst[0:sInd].strip()
    elif eInd == -1 and sInd == -1:
        compV = inst.strip()
    return compV 

def jump(inst):
    sInd = inst.find(';')
    if sInd  == -1:
        return None
    jumpV = inst[sInd+1:].strip() 
    return jumpV

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

main()
