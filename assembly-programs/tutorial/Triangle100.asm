// Adds 1+...+100.  
// Source: Figure 4.2, p. 65.
    @i       // i refers to some memory location.
    M=1      // i=1
    @sum     // sum refers to some memory location.
    M=0      // sum=0
(LOOP)
    @i
    D=M      // D=i
    @100
    D=D-A    // D=i-100
    @END
    D;JGT    // If (i-N)>0 goto END
    @i
    D=M      // D=i
    @sum
    M=D+M    // sum=sum+i
    @i
    M=M+1    // i=i+1
    @LOOP
    0;JMP
(END)
    @END
    0;JMP    // Infinite loop
             // (Hack does not have a HALT instruction.)
