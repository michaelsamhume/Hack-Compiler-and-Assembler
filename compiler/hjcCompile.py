"""
hjcCompile.py -- CompileEngine class for Hack computer Jack compiler
Solution provided by Nand2Tetris authors, licensed for educational purposes
Refactored and skeleton-ized by Janet Davis, April 18, 2016
Refactored by John Stratton, April 2019
"""

from hjcTokens import *
from hjcTokenizer import *
from hjcOutputFile import *
from hjcSymbolTable import *
from hjcVmWriter import *


xml = True  


class CompileEngine(object):
    def __init__(self, inputFileName, outputFileName, xmlOutputFileName, source=True):
        """
        Initializes the compilation of 'inputFileName' to 'outputFileName'.
        If 'source' is True, source code will be included as comments in the
            output.
        """
        self.className = None
        self.inputFileName = inputFileName
        self.source = source
        self.xmlIndent = 0
        self.labelCounters = {}
        self.xmlOutputFile = OutputFile(xmlOutputFileName)
        self.vmWriter = VmWriter(outputFileName)
        self.symbolTable = SymbolTable()
        self.tokenizer = Tokenizer(inputFileName, self.xmlOutputFile, source)
        if not self.tokenizer.Advance():
            self._RaiseError('Premature EOF')


    def Close(self):
        """
        Finalize the compilation and close the output file.
        """
        self.xmlOutputFile.Close()
        
    def _GetNextLabel(self, label_prefix):
        """
        Gets a label that is unique within this subroutine.
        """

        if label_prefix not in self.labelCounters:
            self.labelCounters[label_prefix] = -1
        self.labelCounters[label_prefix] += 1
        return label_prefix + str(self.labelCounters[label_prefix])


    def CompileClass(self):
        """
        Compiles <class> :=
            'class' <class-name> '{' <class-var-dec>* <subroutine-dec>* '}'

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after final '}'
        """
        self._WriteXmlTag('<class>\n')
        self._ExpectKeyword(KW_CLASS)
        self._NextToken()

        self.className = self._ExpectIdentifier()
        self._NextToken()

        self._ExpectSymbol('{')
        self._NextToken()

        while True:
            if not self._MatchKeyword((KW_STATIC, KW_FIELD)):
                break
            self._CompileClassVarDec();

        while True:
            if not self._MatchKeyword((KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD)):
                break
            self._CompileSubroutine();

        self._ExpectSymbol('}')
        self._WriteTokenXML()
        self._WriteXmlTag('</class>\n')
        if self.tokenizer.Advance():
            self._RaiseError('Junk after end of class definition')

    def _CompileClassVarDec(self):
        """
        Compiles <class-var-dec> :=
            ('static' | 'field') <type> <var-name> (',' <var-name>)* ';'

        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<classVarDec>\n')

        storageClass = self._ExpectKeyword((KW_STATIC, KW_FIELD))
        self._NextToken()

        if self.tokenizer.TokenType() == TK_KEYWORD:
            variableType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
        else:
            variableType = self._ExpectIdentifier()
        self._NextToken()

        while True:
            variableName = self._ExpectIdentifier()
            self._NextToken()
            if storageClass == KW_STATIC:
                self._DefineSymbol(variableName, variableType, SYMK_STATIC)
            else:
                self._DefineSymbol(variableName, variableType, SYMK_FIELD)


            if not self._MatchSymbol(','):
                break
            self._NextToken()

        self._ExpectSymbol(';')
        self._NextToken()
        self._WriteXmlTag('</classVarDec>\n')

    def _CompileSubroutine(self):
        """
        Compiles <subroutine-dec> :=
            ('constructor' | 'function' | 'method') ('void' | <type>)
            <subroutine-name> '(' <parameter-list> ')' <subroutine-body>
            
        ENTRY: Tokenizer positioned on the initial keyword.
        EXIT:  Tokenizer positioned after <subroutine-body>.
        """
        self._WriteXmlTag('<subroutineDec>\n')

        self.symbolTable.StartSubroutine()
        self.labelCounters = {}

        subroutineType = self._ExpectKeyword((KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD))
        self._NextToken()
        #TODO-11C: For a method in particular, we need to declare an implicit 
        #          first argument in the symbol table before we add the others.
        if subroutineType == KW_METHOD:
            self.symbolTable.Define("this", self.className, SYMK_ARG)

        if self.tokenizer.TokenType() == TK_KEYWORD:
            returnType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN, KW_VOID))
        else:
            returnType = self._ExpectIdentifier()
        self._NextToken()

        subroutineName = self._ExpectIdentifier()
        self._NextToken()


        self._ExpectSymbol('(')
        self._NextToken()

        self._CompileParameterList()
        
        self._ExpectSymbol(')')
        self._NextToken()
        
        self._CompileSubroutineBody(subroutineType, subroutineName)

        self._WriteXmlTag('</subroutineDec>\n')


    def _CompileParameterList(self):
        """
        Compiles <parameterList> :=
            ((<type> <varName>) (',' <type> <varName>)*)?
    
        ENTRY: Tokenizer is positioned at the first parameter (or ')')
        EXIT:  Tokenizer is positioned at the symbol after the list
        """
        self._WriteXmlTag('<parameterList>\n')
    
        if not self._MatchSymbol(')'):
            while True:
                # Get type
                if self.tokenizer.TokenType() == TK_KEYWORD:
                    varType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
                else:
                    varType = self._ExpectIdentifier()  # class name
    
                self._NextToken()
    
                # Get name
                varName = self._ExpectIdentifier()
                self._DefineSymbol(varName, varType, SYMK_ARG)
                self._NextToken()
    
                if not self._MatchSymbol(','):
                    break
                self._NextToken()
    
        self._WriteXmlTag('</parameterList>\n')

                

    def _CompileSubroutineBody(self, subroutineType, subroutineName):
        """
        Compiles <subroutine-body> :=
            '{' <var-dec>* <statements> '}'

        The tokenizer is expected to be positioned before the {
        ENTRY: Tokenizer positioned on the initial '{'.
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<subroutineBody>\n')
        
        self._ExpectSymbol('{')
        self._NextToken()

        while self._MatchKeyword(KW_VAR):
            self._CompileVarDec()

        #TODO-11A: Write the VM function command below.
        #          The function name is given as a parameter above; 
        #          you will also need self.className.
        funcName = self.className + "." + subroutineName
        nLocals = self.symbolTable.VarCount(SYMK_VAR)
        self.vmWriter.WriteFunction(funcName, nLocals)
        if subroutineType == KW_CONSTRUCTOR:
            #In a constructor, the first operations must allocate memory for 
            # the current object.
            self.vmWriter.WritePush(SEG_CONST, self.symbolTable.VarCount(SYMK_FIELD))
            self.vmWriter.WriteCall("Memory.alloc", 1)
            self.vmWriter.WritePop(SEG_POINTER, 0)
        elif subroutineType == KW_METHOD:
            #TODO-11C: Replace "pass" with code to move the current object pointer
            #          from its spot as the first argument to the THIS pointer location
            self.vmWriter.WritePush(SEG_ARG, 0)
            self.vmWriter.WritePop(SEG_POINTER, 0)

        self._CompileStatements()

        self._ExpectSymbol('}')
        self._NextToken()
        
        self._WriteXmlTag('</subroutineBody>\n')


    def _CompileVarDec(self):
        """
        Compiles <var-dec> :=
            'var' <type> <var-name> (',' <var-name>)* ';'
    
        ENTRY: Tokenizer positioned on the initial 'var'.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<varDec>\n')
        
        storageClass = self._ExpectKeyword(KW_VAR)
        self._NextToken()
        
        if self.tokenizer.TokenType() == TK_KEYWORD:
            variableType = self._ExpectKeyword((KW_INT, KW_CHAR, KW_BOOLEAN))
        else:
            variableType = self._ExpectIdentifier()
        self._NextToken()
    
        while True:
            variableName = self._ExpectIdentifier()
            self._NextToken()
            self._DefineSymbol(variableName, variableType, SYMK_VAR)
    
            if not self._MatchSymbol(','):
                break
            self._NextToken()
    
        self._ExpectSymbol(';')
        self._NextToken()
        
        self._WriteXmlTag('</varDec>\n')

        




    def _CompileStatements(self):
        """
        Compiles <statements> := (<let-statement> | <if-statement> |
            <while-statement> | <do-statement> | <return-statement>)*

        The tokenizer is expected to be positioned on the first statement
        ENTRY: Tokenizer positioned on the first statement.
        EXIT:  Tokenizer positioned after final statement.
        """
        self._WriteXmlTag('<statements>\n')

        kw = self._MatchKeyword((KW_DO, KW_IF, KW_LET, KW_RETURN, KW_WHILE))

        while kw:
            if kw == KW_DO:
                self._CompileDo()
            elif kw == KW_IF:
                self._CompileIf()
            elif kw == KW_LET:
                self._CompileLet()
            elif kw == KW_RETURN:
                self._CompileReturn()
            elif kw == KW_WHILE:
                self._CompileWhile()
            kw = self._MatchKeyword((KW_DO, KW_IF, KW_LET, KW_RETURN, KW_WHILE))
            
        self._WriteXmlTag('</statements>\n')


    def _CompileLet(self):
        self._WriteXmlTag('<letStatement>\n')
    
        self._ExpectKeyword(KW_LET)
        self._NextToken()
    
        varName = self._ExpectIdentifier()
        kind = self.symbolTable.KindOf(varName)
        index = self.symbolTable.IndexOf(varName)
        self._NextToken()
    
        isArray = False
        if self._MatchSymbol('['):
            self._ExpectSymbol('[')
            self._NextToken()
            self._CompileExpression()
            self._ExpectSymbol(']')
            self._NextToken()
            isArray = True
    
            # compute address: base + offset
            self.vmWriter.WritePush(self._KindToSegment(kind), index)
            self.vmWriter.WriteArithmetic(OP_ADD)
    
        self._ExpectSymbol('=')
        self._NextToken()
        self._CompileExpression()
        self._ExpectSymbol(';')
        self._NextToken()
    
        if isArray:
            self.vmWriter.WritePop(SEG_TEMP, 0)
            self.vmWriter.WritePop(SEG_POINTER, 1)
            self.vmWriter.WritePush(SEG_TEMP, 0)
            self.vmWriter.WritePop(SEG_THAT, 0)
        else:
            self.vmWriter.WritePop(self._KindToSegment(kind), index)
    
        self._WriteXmlTag('</letStatement>\n')




    def _CompileDo(self):
        """
        Compiles <do-statement> := 'do' <subroutine-call> ';'
        
        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final ';'.
        """
        self._WriteXmlTag('<doStatement>\n')

        self._ExpectKeyword(KW_DO)
        self._NextToken()

        self._CompileCall()

        #TODO-11A: Discard the return value from a void function 
        #          by popping it into temp 0.
        self.vmWriter.WritePop(SEG_TEMP, 0)

        self._ExpectSymbol(';')
        self._NextToken()

        self._WriteXmlTag('</doStatement>\n')


    def _CompileCall(self, firstIdentifier=None):
        """
        <subroutine-call> := (<subroutine-name> '(' <expression-list> ')') |
            ((<class-name> | <var-name>) '.' <subroutine-name> '('
            <expression-list> ')')

        <*-name> := <identifier>

        ENTRY: Tokenizer positioned on the first identifier.
            If 'firstIdentifier' is supplied, tokenizer is on the '.'
        EXIT:  Tokenizer positioned after final ';'.
        """
        scopeName = None
        if firstIdentifier == None:
            firstIdentifier = self._ExpectIdentifier()
            self._NextToken()
        
        sym = self._ExpectSymbol('.(')
        self._NextToken()

        if sym == '.':
            scopeName = firstIdentifier
            subroutineName = self._ExpectIdentifier()
            self._NextToken()
            
            sym = self._ExpectSymbol('(')
            self._NextToken()
        else:
            subroutineName = firstIdentifier

        argcount = 0
        callClass = scopeName
        if scopeName != None:
            # Determine if scopeName is an object (local, arg, field, or static) or a class.
            kind = self.symbolTable.KindOf(scopeName)
            if kind is not None:
                # It's a variable referring to an object instance.
                # Push the object onto the stack as the first (implicit) argument.
                self.vmWriter.WritePush(self._KindToSegment(kind), self.symbolTable.IndexOf(scopeName))
                callClass = self.symbolTable.TypeOf(scopeName)  # the variable's type is the class of the object
                argcount += 1
            else:
                # It's a class name; no implicit 'this' argument needed.
                callClass = scopeName
        else:
            self.vmWriter.WritePush(SEG_POINTER, 0)
            callClass = self.className
            argcount += 1

        argcount += self._CompileExpressionList()

        #TODO-11A: Write the call to the function using scopeName and functionName.
        functionName = f"{callClass}.{subroutineName}"
        self.vmWriter.WriteCall(functionName, argcount)
        self._NextToken()
        

    def _CompileReturn(self):
        """
        Compiles <return-statement> := 'return' <expression>? ';'
        """
        self._WriteXmlTag('<returnStatement>\n')
    
        self._ExpectKeyword(KW_RETURN)
        self._NextToken()
    
        
        if not self._MatchSymbol(';'):
            self._CompileExpression()  
            self.vmWriter.WriteReturn()
        else:
            
            self.vmWriter.WritePush(SEG_CONST, 0)
            self.vmWriter.WriteReturn()
    
        self._ExpectSymbol(';')
        self._NextToken()
    
        self._WriteXmlTag('</returnStatement>\n')



    def _CompileIf(self):
        """
        Compiles <if-statement> :=
            'if' '(' <expression> ')' '{' <statements> '}' ( 'else'
            '{' <statements> '}' )?

        ENTRY: Tokenizer positioned on the first keyword.
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<ifStatement>\n')

        self._ExpectKeyword(KW_IF)
        self._NextToken()

        self._ExpectSymbol('(')
        self._NextToken()

        self._CompileExpression()

        truecase = self._GetNextLabel("IF_TRUE")
        falsecase = self._GetNextLabel("IF_FALSE")
        endif = self._GetNextLabel("IF_END")

        self.vmWriter.WriteIf(truecase)
        self.vmWriter.WriteGoto(falsecase)
        self.vmWriter.WriteLabel(truecase)

        self._ExpectSymbol(')')
        self._NextToken()

        self._ExpectSymbol('{')
        self._NextToken()

        self._CompileStatements()

        self._ExpectSymbol('}')
        self._NextToken()


        if self._MatchKeyword(KW_ELSE):
            self.vmWriter.WriteGoto(endif)
            self.vmWriter.WriteLabel(falsecase)
            self._NextToken()

            self._ExpectSymbol('{')
            self._NextToken()

            self._CompileStatements()

            self._ExpectSymbol('}')
            self._NextToken()
            self.vmWriter.WriteLabel(endif)
        else:
            self.vmWriter.WriteLabel(falsecase)
        
        self._WriteXmlTag('</ifStatement>\n')


    def _CompileWhile(self):
        """
        Compiles <while-statement> :=
            'while' '(' <expression> ')' '{' <statements> '}'
    
        ENTRY: Tokenizer positioned on the first keyword
        EXIT:  Tokenizer positioned after final '}'.
        """
        self._WriteXmlTag('<whileStatement>\n')
    
        self._ExpectKeyword(KW_WHILE)
        self._NextToken()
    
        conditionLabel = self._GetNextLabel("WHILE_EXP")
        endLabel = self._GetNextLabel("WHILE_END")
    
        self.vmWriter.WriteLabel(conditionLabel)
    
        self._ExpectSymbol('(')
        self._NextToken()
        self._CompileExpression()
        self._ExpectSymbol(')')
        self._NextToken()
    
        self.vmWriter.WriteArithmetic(OP_NOT)
        self.vmWriter.WriteIf(endLabel)
    
        self._ExpectSymbol('{')
        self._NextToken()
        self._CompileStatements()
        self._ExpectSymbol('}')
        self._NextToken()
    
        self.vmWriter.WriteGoto(conditionLabel)
        self.vmWriter.WriteLabel(endLabel)
    
        self._WriteXmlTag('</whileStatement>\n')


    def _CompileExpression(self):
        """
        Compiles <expression> := <term> (op <term>)*
        """
        self._WriteXmlTag('<expression>\n')
    
        self._CompileTerm()
    
        while self._MatchSymbol('+-*/&|<>='):
            op = self._ExpectSymbol('+-*/&|<>=')  #
            self._NextToken()                    
            self._CompileTerm()
    
            # Write VM code for the operator
            if op == '*':
                self.vmWriter.WriteCall("Math.multiply", 2)
            elif op == '/':
                self.vmWriter.WriteCall("Math.divide", 2)
            else:
                vm_ops = {'+': OP_ADD, '-': OP_SUB, '&': OP_AND, '|': OP_OR, '<': OP_LT, '>': OP_GT, '=': OP_EQ}
                self.vmWriter.WriteArithmetic(vm_ops[op])
    
        self._WriteXmlTag('</expression>\n')


    def _EmitStringConstantVMCode(self, stringConstant):
        """Emits VM code for the given string constant"""
        self.vmWriter.WritePush(SEG_CONST, len(stringConstant))
        self.vmWriter.WriteCall("String.new", 1)
        for char in stringConstant:
            self.vmWriter.WritePush(SEG_CONST, ord(char))
            self.vmWriter.WriteCall("String.appendChar", 2)
        return

    def _CompileTerm(self):
        """
        Compiles <term> := integerConstant | stringConstant | keywordConstant
                           | varName | varName '[' expression ']'
                           | subroutineCall | '(' expression ')'
                           | unaryOp term
        """
        self._WriteXmlTag('<term>\n')
        tokenType = self.tokenizer.TokenType()
    
        # Integer constant
        if tokenType == TK_INT_CONST:
            value = self.tokenizer.IntVal()
            self.vmWriter.WritePush(SEG_CONST, value)
            self._NextToken()
    
        # String constant
        elif tokenType == TK_STRING_CONST:
            string = self.tokenizer.StringVal()
            self.vmWriter.WritePush(SEG_CONST, len(string))
            self.vmWriter.WriteCall("String.new", 1)
            for ch in string:
                self.vmWriter.WritePush(SEG_CONST, ord(ch))
                self.vmWriter.WriteCall("String.appendChar", 2)
            self._NextToken()
    
        # Keyword constant: true, false, null, this
        elif tokenType == TK_KEYWORD:
            kw = self.tokenizer.Keyword()
            if kw == KW_TRUE:
                self.vmWriter.WritePush(SEG_CONST, 0)
                self.vmWriter.WriteArithmetic(OP_NOT)
            elif kw in (KW_FALSE, KW_NULL):
                self.vmWriter.WritePush(SEG_CONST, 0)
            elif kw == KW_THIS:
                self.vmWriter.WritePush(SEG_POINTER, 0)
            self._NextToken()
    
        # Unary operation
        elif self._MatchSymbol('-~'):
            op = self._ExpectSymbol('-~')
            self._NextToken()
            self._CompileTerm()
            if op == '-':
                self.vmWriter.WriteArithmetic(OP_NEG)
            elif op == '~':
                self.vmWriter.WriteArithmetic(OP_NOT)
    
        # expression with paratheses
        elif self._MatchSymbol('('):
            self._ExpectSymbol('(')
            self._NextToken()
            self._CompileExpression()
            self._ExpectSymbol(')')
            self._NextToken()
    
        # Identifier: variable, array access, or subroutine call
        elif tokenType == TK_IDENTIFIER:
            name = self.tokenizer.Identifier()
            self._NextToken()
    
            # Array access: varName[expression]
            if self._MatchSymbol('['):
                self._ExpectSymbol('[')
                self._NextToken()
                self._CompileExpression()
                self._ExpectSymbol(']')
                self._NextToken()
                self.vmWriter.WritePush(
                    self._KindToSegment(self.symbolTable.KindOf(name)),
                    self.symbolTable.IndexOf(name)
                )
                self.vmWriter.WriteArithmetic(OP_ADD)
                self.vmWriter.WritePop(SEG_POINTER, 1)
                self.vmWriter.WritePush(SEG_THAT, 0)
    
            # Method call: varName.subroutineName(expressionList)
            elif self._MatchSymbol('.'):
                isObject = self.symbolTable.KindOf(name) is not None
                if isObject:
                    segment = self._KindToSegment(self.symbolTable.KindOf(name))
                    index = self.symbolTable.IndexOf(name)
                    self.vmWriter.WritePush(segment, index)
                    objectType = self.symbolTable.TypeOf(name)
                else:
                    objectType = name
    
                self._ExpectSymbol('.')
                self._NextToken()
                subroutineName = self._ExpectIdentifier()
                self._NextToken()
    
                self._ExpectSymbol('(')
                self._NextToken()
                argCount = self._CompileExpressionList()
                if isObject:
                    argCount += 1
                self._ExpectSymbol(')')
                self._NextToken()
    
                self.vmWriter.WriteCall(objectType + "." + subroutineName, argCount)
    
            # subroutine call: subroutineName(expressionList)
            elif self._MatchSymbol('('):
                self._ExpectSymbol('(')
                self._NextToken()
                argCount = self._CompileExpressionList()
                self._ExpectSymbol(')')
                self._NextToken()
                self.vmWriter.WriteCall(name, argCount)
    
            # Simple variable: varName
            else:
                self.vmWriter.WritePush(
                    self._KindToSegment(self.symbolTable.KindOf(name)),
                    self.symbolTable.IndexOf(name)
                )
    
        else:
            self._RaiseError("Unexpected token in term")
    
        self._WriteXmlTag('</term>\n')




    def _CompileExpressionList(self):
        """
        Compiles <expression-list> :=
            (<expression> (',' <expression>)* )?

        Returns number of expressions compiled.

        ENTRY: Tokenizer positioned on the first expression.
        EXIT:  Tokenizer positioned after the last expression.
        """
        self._WriteXmlTag('<expressionList>\n')

        count = 0
        while True:
            if self._MatchSymbol(')'):
                break
            self._CompileExpression()
            count += 1

            if not self._MatchSymbol(','):
                break
            self._NextToken()
        
        self._WriteXmlTag('</expressionList>\n')
        return count

    def _MatchKeyword(self, keywords):
        """
        Check whether the next token matches one of 'keywords'.
        'keywords' may be a keywordID or a list or tuple of keywordIDs.
        If one of the keywords is matched, returns the matched keyword.
        If next token is not a keyword matching one of the requested keywords, returns None.
        """
        if type(keywords) == list:
            keywords = tuple(keywords)
        elif type(keywords) != tuple:
            keywords = (keywords,)
        if not self.tokenizer.TokenType() == TK_KEYWORD:
            return None
        if self.tokenizer.Keyword() in keywords:
            return self.tokenizer.Keyword()
        return None


    def _ExpectKeyword(self, keywords):
        """
        Parse the next token.  It is expected to be one of 'keywords'.
        'keywords' may be a keywordID or a list or tuple of keywordIDs.

        If an expected keyword is parsed, returns the keyword.
        Otherwise raises an error.
        """
        match = self._MatchKeyword(keywords)
        if not match:
            self._RaiseError('Expected '+self._KeywordStr(keywords)+', got '+
                             self.tokenizer.TokenTypeStr())
        else:
            return match

    def _ExpectIdentifier(self):
        """
        Parse the next token.  It is expected to be an identifier.

        Returns the identifier parsed or raises an error.
        """
        if not self.tokenizer.TokenType() == TK_IDENTIFIER:
            self._RaiseError('Expected <identifier>, got '+
                             self.tokenizer.TokenTypeStr())
        return self.tokenizer.Identifier()
        
    def _MatchSymbol(self, symbols):
        """
        Parse the next token.  It is expected to be one of 'symbols'.
        'symbols' is a string of one or more legal symbols.

        If an expected symbol is parsed, returns the symbol.
        If no such symbol is parsed, returns None.
        """
        if not self.tokenizer.TokenType() == TK_SYMBOL or self.tokenizer.Symbol() not in symbols:
            return None
        else:
            return self.tokenizer.Symbol()

    def _ExpectSymbol(self, symbols):
        """
        Parse the next token.  It is expected to be one of 'symbols'.
        'symbols' is a string of one or more legal symbols.

        If an expected symbol is parsed, returns the symbol.
        Otherwise raises an error.
        """
        sym = self._MatchSymbol(symbols)
        if not sym:
            if not self.tokenizer.TokenType() == TK_SYMBOL:
                self._RaiseError('Expected '+self._SymbolStr(symbols)+', got '+
                                 self.tokenizer.TokenTypeStr())
            else:
                self._RaiseError('Expected '+self._SymbolStr(symbols)+', got '+
                                 self._SymbolStr(self.tokenizer.Symbol()))
        return sym

    def _MatchIntConstant(self):
        """
        Parse the next token.  It is expected to be of type TK_INT_CONST

        If an expected token is matched, returns the integer constant.
        If no such token is parsed, returns None.
        """
        if self.tokenizer.TokenType() == TK_INT_CONST:
            return self.tokenizer.IntVal()
        return None

    def _MatchStringConstant(self):
        """
        Parse the next token.  It is expected to be TK_STRING_CONST.

        If the string constant if present, or None.
        """
        if self.tokenizer.TokenType() == TK_STRING_CONST:
            return self.tokenizer.StringVal()
        return None

    def _RaiseError(self, error):
        message = '%s line %d:\n  %s\n  %s' % (
                  self.inputFileName, self.tokenizer.LineNumber(),
                  self.tokenizer.LineStr(), error)
        raise HjcError(message)
        

    def _KeywordStr(self, keywords):
        if type(keywords) != tuple:
            return '"' + self.tokenizer.KeywordStr(keywords) + '"'
        ret = ''
        for kw in keywords:
            if len(ret):
                ret += ', '
            ret += '"' + self.tokenizer.KeywordStr(kw) + '"'
        if len(keywords) > 1:
            ret = 'one of (' + ret + ')'
        return ret
        
        
    def _SymbolStr(self, symbols):
        if type(symbols) != tuple:
            return '"' + symbols + '"'
        ret = ''
        for symbol in symbols:
            if len(ret):
                ret += ', '
            ret += '"' + symbol + '"'
        if len(symbols) > 1:
            ret = 'one of (' + ret + ')'
        return ret
        
        
    def _NextToken(self, emitXML=True):
        if emitXML:
            self._WriteTokenXML()
        if not self.tokenizer.Advance():
            self._RaiseError('Premature EOF')

    def _ConsumeToken(self):
        if not self.tokenizer.Advance():
            self._RaiseError('Premature EOF')

    def _WriteXmlTag(self, tag):
        if xml:
            if tag[1] == '/':
                self.xmlIndent -= 1
            self.xmlOutputFile.Write('  ' * self.xmlIndent)
            self.xmlOutputFile.Write(tag)
            if '/' not in tag:
                self.xmlIndent += 1
    
    def _WriteXml(self, tag, value):
        if xml:
            self.xmlOutputFile.Write('  ' * self.xmlIndent)
            self.xmlOutputFile.WriteXml(tag, value)

    def _SkipStatement(self, end_symbol):
         """
         Consumes tokens unparsed until the specified end symbol is seen.
         Used as a placeholder for actually parsing the statements.
         """
         while not self._ExpectSymbol(end_symbol):
             self._NextToken();
         self._NextToken();

    def _WriteTokenXML(self):
         """
         Writes out whatever the next token is to the output file, regardless of type or content.
         """
         tokenType = self.tokenizer.TokenType()
         if tokenType == TK_SYMBOL:
             self._WriteXml('symbol', self.tokenizer.Symbol())
         elif tokenType == TK_KEYWORD:
             self._WriteXml('keyword', self.tokenizer.KeywordStr())
         elif tokenType == TK_IDENTIFIER:
             self._WriteXml('identifier', self.tokenizer.Identifier())
         elif tokenType == TK_INT_CONST:
             self._WriteXml('integerConstant', str(self.tokenizer.IntVal()))
         elif tokenType == TK_STRING_CONST:
             self._WriteXml('stringConstant', self.tokenizer.StringVal())

    def _DefineSymbol(self, name, type, kind):
        """
        Adds a new symbol to the symbol table.
        """
        self.symbolTable.Define(name, type, kind)

    def _KindToSegment(self, kind):
        """
        Converts symbol table "kinds" to segment numbers for the VmWriter.
        Includes a safety check for undeclared variables.
        """
        if kind is None:
            self._RaiseError("Variable used before declaration or not in symbol table")
        return (SEG_STATIC, SEG_THIS, SEG_ARG, SEG_LOCAL)[kind]


    def _WriteSymbolTableEntry(self, name, assign=False):
        """
        Writes an XML tag for a symbol table entry.
        """
        type = self.symbolTable.TypeOf(name)
        kind = self.symbolTable.KindOfStr(name)
        index = self.symbolTable.IndexOf(name)
        self._WriteXmlTag('<tableEntry type="%s" kind="%s" index="%s" assign="%s">\n' % (type, kind, index, assign))
