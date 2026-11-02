#!/usr/bin/python3
# Some text copyright (C) 2011 Mark Armbrust.  
# Permission granted for educational use.
# Skeletonized March 2016 by Janet Davis
# Refactored May 2016 by Janet Davis
# Refactored February 2018 by John Stratton
# Refactored and debugged January 2019 by Janet Davis
# Edited 2021-22 by Cary Gray

"""
hasm.py -- Hack computer assembler

Translates a Hack assembly program into the corresponding Hack machine language program.
See "The Elements of Computing Systems", by Noam Nisan and Shimon Schocken

Usage: python3 hasm.py PROGRAM.asm
"""


from hasmUtils import *
from sys import argv
import re

next_variable_address = 16  # Global RAM pointer for new variables

def read_asm_file(input_filename):
    try:
        inFile = open(input_filename, 'r')
    except:
        FatalError('Could not open source file "' + input_filename + '"')

    rawline = inFile.readline()
    list_of_lines = []

    while rawline != '':
        line = rawline.strip()
        comment_start = line.find("//")
        if comment_start >= 0:
            line = line[:comment_start].strip()
        if line != '':
            list_of_lines.append(line)
        rawline = inFile.readline()

    inFile.close()
    return list_of_lines

def statement_type(statement):
    if statement.startswith('@'):
        return A_INSTRUCTION
    elif statement.startswith('(') and statement.endswith(')'):
        return L_DIRECTIVE
    else:
        return C_INSTRUCTION


def emit_C_instruction(statement, output_file):
    codeTranslator = CodeTranslator()

    if '=' in statement:
        dest_mnemonic, remainder = statement.split('=')
    else:
        dest_mnemonic, remainder = 'null', statement

    if ';' in remainder:
        comp_mnemonic, jump_mnemonic = remainder.split(';')
    else:
        comp_mnemonic, jump_mnemonic = remainder, 'null'

    dest_mnemonic = dest_mnemonic.strip()
    comp_mnemonic = comp_mnemonic.strip()
    jump_mnemonic = jump_mnemonic.strip()
    if jump_mnemonic == 'null':
        jump_mnemonic = ''

    comp_bits = codeTranslator.comp(comp_mnemonic)
    dest_bits = codeTranslator.dest(dest_mnemonic)
    jump_bits = codeTranslator.jump(jump_mnemonic)

    if comp_bits is None or dest_bits is None or jump_bits is None:
        print(f"ERROR: Invalid C-instruction: {statement}")
        import sys
        sys.exit(-1)

    # Writes the instruction to the output file
    instruction = '111' + comp_bits + dest_bits + jump_bits
    output_file.write(instruction + '\n')



def emit_A_instruction(statement, symbol_table, output_file):
    global next_variable_address
    symbol = statement[1:]

    if symbol.isdigit():
        address = int(symbol)
    else:
        if symbol not in symbol_table:
            symbol_table[symbol] = next_variable_address
            next_variable_address += 1
        address = symbol_table[symbol]

    instruction = format(address, '016b')
    output_file.write(instruction + '\n')

def first_pass(statement_list, symbol_table):
    rom_address = 0
    for statement in statement_list:
        if statement_type(statement) == L_DIRECTIVE:
            label = statement[1:-1]
            symbol_table[label] = rom_address
        else:
            rom_address += 1

def second_pass(statement_list, symbol_table, output_filename):
    output_file = open(output_filename, "w")
    if not output_file:
        FatalError("Cannot open output file " + output_filename)

    for statement in statement_list:
        stype = statement_type(statement)
        if stype == A_INSTRUCTION:
            emit_A_instruction(statement, symbol_table, output_file)
        elif stype == C_INSTRUCTION:
            emit_C_instruction(statement, output_file)
        # L_DIRECTIVE (labels) are ignored

    output_file.close()


def main():
    # For Spyder or IDE use, set this manually
    input_filename = "pong/Pong.asm"
    output_filename = "pong/Pong.hack"

    print("Running assembler...")
    symbol_table = init_symbol_table()
    list_of_statements = read_asm_file(input_filename)
    print("Read", len(list_of_statements), "statements")

    first_pass(list_of_statements, symbol_table)
    print("First pass done.")

    second_pass(list_of_statements, symbol_table, output_filename)
    print("Assembly complete! Check", output_filename)

if __name__ == '__main__':
    main()
