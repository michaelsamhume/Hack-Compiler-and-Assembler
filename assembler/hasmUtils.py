#!/usr/bin/python3
# Some text copyright (C) 2011 Mark Armbrust.  
# Permission granted for educational use.
# Skeletonized March 2016 by Janet Davis
# Refactored May 19, 2016 by Janet Davis
# Refactored February 2018 by John Stratton
# Edited 2021-22 by Cary Gray

"""
hasmUtils.py
Defines constants and the CodeTranslator class.

See "The Elements of Computing Systems", by Noam Nisan and Shimon Schocken

This parser is slightly different than the parser design in the book.
"""

from hasmError import *

A_INSTRUCTION = 1
C_INSTRUCTION = 2
L_DIRECTIVE = 3

def init_symbol_table():
    """
    Returns a Python dictionary mapping strings (symbol names) to 
    integers (address refered to by that symbol), initialized with 
    all of the Hack assembly predefined symbols.
    """
    predefined_symbols = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            'R0': 0,
            'R1': 1,
            'R2': 2,
            'R3': 3,
            'R4': 4,
            'R5': 5,
            'R6': 6,
            'R7': 7,
            'R8': 8,
            'R9': 9,
            'R10': 10,
            'R11': 11,
            'R12': 12,
            'R13': 13,
            'R14': 14,
            'R15': 15,
            'SCREEN': 0x4000,
            'KBD': 0x6000
            }
    return predefined_symbols

class CodeTranslator(object):
    """
    The CodeTranslator class contains methods to translate 
    comp, dest, and jump mnemonics into binary (represented as a string).
    """

    _comp_dict = {
            '0'  : '0101010',
            '1'  : '0111111',
            '-1' : '0111010',
            'D'  : '0001100',
            'A'  : '0110000',
            '!D' : '0001101',
            '!A' : '0110001',
            '-D' : '0001111',
            '-A' : '0110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'D+A': '0000010',
            'A+D': '0000010',
            'D-A': '0010011',
            'A-D': '0000111',
            'D&A': '0000000',
            'A&D': '0000000',
            'D|A': '0010101',
            'A|D': '0010101',
            'M'  : '1110000',
            '!M' : '1110001',
            '-M' : '1110011',
            'M+1': '1110111',
            'M-1': '1110010',
            'D+M': '1000010',
            'M+D': '1000010',
            'D-M': '1010011',
            'M-D': '1000111',
            'D&M': '1000000',
            'M&D': '1000000',
            'D|M': '1010101',
            'M|D': '1010101'
            }

    _jump_dict = {
            ''   : '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
            }
    
    def __init__(self):
        pass    

    def dest(self, mnemonic):
        """
        Returns the binary code of the dest mnemonic (3 bits as a string).
        Returns '000' if the mnemonic contains none of ADM.
        """
        return ''.join(map(lambda ch: '1' if (ch in mnemonic) else '0', 'ADM'))

    def comp(self, mnemonic):
        """
        Returns the binary code of the comp mnemonic (7 bits as a string).
        Returns None if the mnemonic cannot be decoded.
        """
        return self._comp_dict.get(mnemonic, None)

    def jump(self, mnemonic):
        """
        Returns the binary code of the jump mnemonic (3 bits as a string).
        Returns None if the mnemonic cannot be decoded.
        """
        return self._jump_dict.get(mnemonic, None)

def main():
    # A little test code
    code = CodeTranslator()
    print('DEST    ', code.dest(''))
    print('DEST D  ', code.dest('D'))
    print('DEST AMD', code.dest('AMD'))
    print('COMP D+1', code.comp('D+1'))
    print('JUMP    ', code.jump(''))
    print('JUMP JEQ', code.jump('JEQ'))
    print('JUMP JMP', code.jump('JMP'))

if __name__ == '__main__':
    main()
