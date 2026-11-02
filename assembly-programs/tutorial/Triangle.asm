// Gets N from Mem[0]. Computes sum=1+2+...+N and stores in Mem[1].
// Similar to the example in Figure 4.2, p. 65.
    @i    
    M=1      // i=1
    @R1
    M=0      / sum=0
(LOOP)
    @i
    D=M      // D=i
    @R0
    D=D-M    // D=i-N
    @END
    D;JGT    // If (i-N)>0 goto END
    @i
    D=M      // D=i
    @R1
    M=D+M    // sum=sum+i
    @Loop
    0;JMP
(END)
    @END
    0;JMP    // Infinite loop
