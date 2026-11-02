"""
hvmCodeWriter.py -- Emits assembly language code for the Hack VM translator.
Skeletonized by Janet Davis March 2016
Refactored by John Stratton April 2017
Refactored by Janet Davis March 2019
"""

import os
from hvmCommands import *

# If debug is True, 
# then the VM commands will be written as comments into the output ASM file.
debug = True

class CodeWriter(object):
    
    def __init__(self, outputName):
        """
        Opens 'outputName' and gets ready to write it.
        """
        self.file = open(outputName, 'w')
        self.fileName = self.setFileName(outputName)

        # used to generate unique labels
        self.labelNumber = 0
        self.functionName = ""


    def close(self):
        """
        Writes the terminal loop and closes the output file.
        """
        label = self._uniqueLabel()
        self._writeComment("Infinite loop")
        self._writeCode('(%s), @%s, 0;JMP' % (label, label))
        self.file.close()


    def setFileName(self, fileName):
        """
        Sets the current file name to 'fileName'.
        Restarts the local label counter.

        Strips the path and extension.  The resulting name must be a
        legal Hack Assembler identifier.
        """
        self.fileName = os.path.basename(fileName)
        self.fileName = os.path.splitext(self.fileName)[0]
        self.functionName = ""
        return self.fileName
    
    def _uniqueLabel(self, prefix="label"):
        self.labelNumber += 1
        return f"{self.functionName}${prefix}.{self.labelNumber}"


    def write(self, text):
        """ 
        Write directly to the file.
        """
        self.file.write(text)

    def _writeCode(self, code):
        """
        Writes Hack assembly code to the output file.
        code should be a string containing ASM commands separated by commas,
        e.g., "@10, D=D+A, @0, M=D"
        """
        code = code.replace(',', '\n').replace(' ', '')
        self.file.write(code + '\n')

    def _writeComment(self, comment):
        """
        Writes a comment to the output ASM file.
        """
        if (debug):
            self.file.write('    // %s\n' % comment)

    def _pushD(self):
        """
        Writes Hack assembly code to push the value from the D register 
        onto the stack.
        """
        self._writeCode("@SP, A=M, M=D, @SP, M=M+1")

    def _popD(self):
        """
        Writes Hack assembly code to pop a value from the stack 
        into the D register.
        """
        self._writeCode("@SP, AM=M-1, D=M")

    def writeArithmetic(self, command):
        self._writeComment(command)

        if command == T_ADD:
            self._popD()
            self._writeCode("@SP, AM=M-1, M=M+D, @SP, M=M+1")
    
        elif command == T_SUB:
            self._popD()
            self._writeCode("@SP, AM=M-1, M=M-D, @SP, M=M+1")
    
        elif command == T_NEG:
            self._writeCode("@SP, AM=M-1, M=-M, @SP, M=M+1")
    
        elif command in (T_EQ, T_GT, T_LT):
            jump = {
                T_EQ: "JEQ",
                T_GT: "JGT",
                T_LT: "JLT"
            }[command]
            label_true = self._uniqueLabel()
            label_end = self._uniqueLabel()
    
            self._popD()
            self._writeCode("@SP, AM=M-1, D=M-D")
            self._writeCode(f"@{label_true}, D;{jump}")
            self._writeCode("@SP, A=M, M=0")
            self._writeCode(f"@{label_end}, 0;JMP")
            self._writeCode(f"({label_true}), @SP, A=M, M=-1")
            self._writeCode(f"({label_end}), @SP, M=M+1")
    
        elif command == T_AND:
            self._popD()
            self._writeCode("@SP, AM=M-1, M=D&M, @SP, M=M+1")
    
        elif command == T_OR:
            self._popD()
            self._writeCode("@SP, AM=M-1, M=D|M, @SP, M=M+1")
    
        elif command == T_NOT:
            self._writeCode("@SP, AM=M-1, M=!M, @SP, M=M+1")
    
        else:
            raise(ValueError("Bad arithmetic command"))

    def _translateSegment(self, segment):
        return { T_ARGUMENT: "ARG",
                 T_LOCAL: "LCL",
                 T_THIS: "THIS",
                 T_THAT: "THAT" }[segment]

    def writePushPop(self, commandType, segment, index):
        self._writeComment(f"{'push' if commandType == C_PUSH else 'pop'} {segment} {index}")

        if commandType == C_PUSH:
            if segment == T_CONSTANT:
                self._writeCode(f"@{index}, D=A")
                self._pushD()
            elif segment in (T_LOCAL, T_ARGUMENT, T_THIS, T_THAT):
                self._writeCode(f"@{self._translateSegment(segment)}, D=M, @{index}, A=D+A, D=M")
                self._pushD()
            elif segment == T_TEMP:
                self._writeCode(f"@{5+index}, D=M")
                self._pushD()
            elif segment == T_POINTER:
                self._writeCode(f"@{3+index}, D=M")
                self._pushD()
            elif segment == T_STATIC:
                self._writeCode(f"@{self.fileName}.{index}, D=M")
                self._pushD()
            else:
                raise(ValueError("Bad push segment"))

        elif commandType == C_POP:
            if segment in (T_LOCAL, T_ARGUMENT, T_THIS, T_THAT):
                self._writeCode(f"@{self._translateSegment(segment)}, D=M, @{index}, D=D+A, @R13, M=D")
                self._popD()
                self._writeCode("@R13, A=M, M=D")
            elif segment == T_TEMP:
                self._popD()
                self._writeCode(f"@{5+index}, M=D")
            elif segment == T_POINTER:
                self._popD()
                self._writeCode(f"@{3+index}, M=D")
            elif segment == T_STATIC:
                self._popD()
                self._writeCode(f"@{self.fileName}.{index}, M=D")
            else:
                raise(ValueError("Bad pop segment"))

        else:
            raise(ValueError("Bad push/pop command"))

    # Functions below this comment are for Project 08. Ignore for Project 07.

    def writeLabel(self, label):
        self._writeComment(f'label {label}')
        self._writeCode(f'({self.functionName}${label})')

    def writeGoto(self, label):
        self._writeComment(f'goto {label}')
        self._writeCode(f'@{self.functionName}${label}, 0;JMP')

    def writeIf(self, label):
        self._writeComment(f'if-goto {label}')
        self._popD()
        self._writeCode(f'@{self.functionName}${label}, D;JNE')

    def writeFunction(self, functionName, numLocals):
        self._writeComment(f'function {functionName} {numLocals}')
        self.functionName = functionName
        self._writeCode(f'({functionName})')
        for _ in range(numLocals):
            self._writeCode('@0, D=A')
            self._pushD()

    def writeReturn(self):
        self._writeComment('return')
        self._writeCode('@LCL, D=M, @R13, M=D')  # FRAME = LCL
        self._writeCode('@5, A=D-A, D=M, @R14, M=D')  # RET = *(FRAME-5)
        self._popD()  # pop return value into D
        self._writeCode('@ARG, A=M, M=D')  # *ARG = pop()
        self._writeCode('@ARG, D=M+1, @SP, M=D')  # SP = ARG+1
        self._writeCode('@R13, AM=M-1, D=M, @THAT, M=D')
        self._writeCode('@R13, AM=M-1, D=M, @THIS, M=D')
        self._writeCode('@R13, AM=M-1, D=M, @ARG, M=D')
        self._writeCode('@R13, AM=M-1, D=M, @LCL, M=D')
        self._writeCode('@R14, A=M, 0;JMP')  # goto RET

    def writeCall(self, functionName, numArgs):
        returnLabel = f"{functionName}$ret.{self.labelNumber}"
        self.labelNumber += 1
        self._writeComment(f'call {functionName} {numArgs}')
        self._writeCode(f'@{returnLabel}, D=A')
        self._pushD()
        for seg in ['LCL', 'ARG', 'THIS', 'THAT']:
            self._writeCode(f'@{seg}, D=M')
            self._pushD()
        self._writeCode(f'@SP, D=M, @{numArgs + 5}, D=D-A, @ARG, M=D')
        self._writeCode('@SP, D=M, @LCL, M=D')
        self._writeCode(f'@{functionName}, 0;JMP')
        self._writeCode(f'({returnLabel})')


    def writeInit(self):
        self._writeComment('bootstrap code')
        self._writeCode('@256, D=A, @SP, M=D')
        self.writeCall('Sys.init', 0)


