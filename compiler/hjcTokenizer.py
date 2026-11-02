"""
hvmParser.py -- Tokenizer class for Hack Jack compiler
Solution provided by Nand2Tetris authors, licensed for educational purposes
Commented, refactored, and skeleton-ized by Janet Davis, April 18, 2016
Refactored by John Stratton and Janet Davis, April 2019
"""

import string
from hjcTokens import *
from hjcError import *

symbols = '{}()[].,;+-*/&|<>=~'
numberChars = string.digits
numberStart = numberChars
identStart = string.ascii_letters + '_'
identChars = identStart + numberChars    
keywords = {
    'boolean' : KW_BOOLEAN,
    'char' : KW_CHAR,
    'class' : KW_CLASS,
    'constructor' : KW_CONSTRUCTOR,
    'do' : KW_DO,
    'else' : KW_ELSE,
    'false' : KW_FALSE,
    'field' : KW_FIELD,
    'function' : KW_FUNCTION,
    'if' : KW_IF,
    'int' : KW_INT,
    'let' : KW_LET,
    'method' : KW_METHOD,
    'null' : KW_NULL,
    'return' : KW_RETURN,
    'static' : KW_STATIC,
    'this' : KW_THIS,
    'true' : KW_TRUE,
    'var' : KW_VAR,
    'void' : KW_VOID,
    'while' : KW_WHILE
    }


class Tokenizer(object):
    def __init__(self, sourceName, outputFile=None, source=False):
        """
        Opens 'sourceFile' and gets ready to parse it.
        """
        self.file = open(sourceName, 'r');
        self.lineNumber = 0
        self.line = ''
        self.rawline = ''
        self.inComment = False
        self.printSource = source
        self.outputFile = outputFile

    def Advance(self):
        """
        Reads the next command from the input and makes it the current
        command.
        Returns True if a command was found, False at end of file.
        """
        
        while True: 
            if len(self.line) == 0:
                if not self.file:
                    
                    return False

                else:
                    # Read next line
                    self.rawline = self.file.readline()
                    if len(self.rawline) == 0:
                        return False # End of file
                    self.lineNumber = self.lineNumber + 1

                    # Remove ending line break, preserving other white space
                    self.rawline = self.rawline.replace('\n', '')
                    self.line = self.rawline

                    # Print source line as a comment in the output file
                    if (self.printSource):
                        self.outputFile.WriteXml('source',
                                '/// %d: %s' %(self.lineNumber,self.rawline))

                    # Skip over comments in the source file
                    self._SkipComments()

                    # Replace tabs with spaces and strip leading/trailing white space
                    self.line = self.line.replace('\t', ' ').strip()

                    # If nothing is left, read another line
                    if len(self.line) == 0:
                        continue
                    
            # Attempt to parse a token from the current line
            self._Parse()

            # If no token was found, read the next line and try again
            if self.token == (None, None):
                continue

            # When a token is finally found, return true!
            return True


    def LineNumber(self):
        return self.lineNumber
    

    def LineStr(self):
        return self.rawline
    

    def TokenType(self):
        return self.token[0]
    

    def TokenTypeStr(self):
        """
        Returns a string representing the token type.
        """
        if self.token[0] == TK_SYMBOL or self.token[0] == TK_KEYWORD:
            return '"'+self.token[1]+'"'
        return tokenTypes[self.token[0]]
    

    def Keyword(self):
        """
        Returns the current token if it is a keyword.
        Otherwise, raises an error.
        """
        if (self.token[0] == TK_KEYWORD):
            return keywords[self.token[1]]
        raise HjcError('Request for keyword when current token is ' + tokenTypes[token[0]] )
    

    def KeywordStr(self, keywordId=None):
        """
        Returns a string representation of the given numeric token ID,
        or the current token if it is a keyword.
        """
        if (keywordId != None):
            for k in keywords:
                if keywords[k] == keywordId:
                    return k
            raise ValueError
        if (self.token[0] == TK_KEYWORD):
            return self.token[1]

    

    def Symbol(self):
        """
        Returns the current token if it is a symbol.
        Otherwise, raises an error.
        """
        if (self.token[0] == TK_SYMBOL):
            return self.token[1]
        raise HjcError('Request for symbol when current token is ' + tokenTypes[token[0]] )
    

    def Identifier(self):
        """
        Returns the current token if it is an identifier.
        Otherwise, raises an error.
        """
        if (self.token[0] == TK_IDENTIFIER):
            return self.token[1]
        raise HjcError('Request for identifier when current token is ' + tokenTypes[token[0]] )
    

    def IntVal(self):
        """
        Returns the integer value of the current token, if it is an integer constant.
        Otherwise, raises an error.
        """
        if (self.token[0] == TK_INT_CONST):
            return int(self.token[1])
        raise HjcError('Request for integer constant when current token is ' + tokenTypes[token[0]] )
    

    def StringVal(self):
        """
        Returns the current token if it is a string constant.
        Otherwise, raises an error.
        """
        if (self.token[0] == TK_STRING_CONST):
            return self.token[1]
        raise HjcError('Request for string literal when current token is ' + tokenTypes[token[0]] )

    def _SkipComments(self):
         """
         If there are comments next in the input stream, skips over them 
         to the next token.
         """
         # Look for // comments and remove them
         i = self.line.find('//')
         if i != -1:
             self.line = self.line[:i]

         # If in a multiline comment, see if we have reached the end
         if self.inComment:
             i = self.line.find('*/')
             if i == -1:
                 
                 self.line = ''
             else:
                 
                 self.line = self.line[i+2:]
                 self.inComment = False

         # Look for the start of a /* */ comment
         i = self.line.find('/*')
         while i != -1:
            j = self.line.find('*/')
            if j != -1:
                
                self.line = self.line[:i] + ' ' + self.line[j+2:]
            else:
                # start of multiline comment
                self.line = self.line[:i]
                self.inComment = True
                break
            
            i = self.line.find('/*')


    def _Parse(self):
        """
        Parses the next token, storing it in self.token.
        """
        self.token = (None, None)
        

        while len(self.line):     # Characters remain
            ch = self.line[0]     # Get the next charater
            if ch == ' ':         # Skip spaces; they are not represented in the parse tree
                self.line = self.line[1:]
                continue
            if ch in symbols:     # Parse a symbol
                self.line = self.line[1:]
                self.token = (TK_SYMBOL, ch)
                return
            if ch in numberStart:
                self.token = (TK_INT_CONST, self._ParseInt())
                return
            elif ch == '"':
                self.token = (TK_STRING_CONST, self._ParseString())
                return
            elif ch in identStart:
                self._ParseIdent()
                return


            
            raise HjcError('Syntax error in line '+str(self.lineNumber)+': illegal character "' + ch + '"')

    def _ParseIdent(self):
        """
        Parse and return a string representing an identifier or keyword.
        """
        ident = ''
        while len(self.line) > 0 and self.line[0] in identChars:
            ident += self.line[0]
            self.line = self.line[1:]
    
        if ident in keywords:
            self.token = (TK_KEYWORD, ident)
        else:
            self.token = (TK_IDENTIFIER, ident)
        return ident




    def _ParseInt(self):
        """
        Parses and returns a non-negative integer (converted to int type)
        """
        number = ''
        while len(self.line) > 0 and self.line[0] in numberChars:
            number += self.line[0]
            self.line = self.line[1:]
        return int(number)



    def _ParseString(self):
        """
        Parses and returns a string constant, NOT INCLUDING the quotes.
        Throws an error if the line ends without a closing quotation mark.
        """
        self.line = self.line[1:]  
        stringConst = ''
        while len(self.line) > 0:
            if self.line[0] == '"':
                self.line = self.line[1:]  
                return stringConst
            stringConst += self.line[0]
            self.line = self.line[1:]
        raise HjcError('Syntax error in line ' + str(self.lineNumber) + ': open string constant')


