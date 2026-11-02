// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)




// makeing sure R2 is initialized to 0
@R2
M=0

// initialize R0 and check if it's 0
@R0
D=M
@END
D;JEQ  // If R0 == 0, go to END (no multiplication needed)

// initializes R1 and checks if it's 0
@R1
D=M
@END
D;JEQ  // If R1 == 0, go to END

// Starts Loop (Multiplication using Repeated Addition)
(LOOP)
    @R0
    D=M
    @END
    D;JEQ  // Stop when R0 == 0

    // Stores R2's value to a visible RAM location (e.g., SCREEN)
    @R2
    D=M
    @SCREEN   
    M=D

    // Add R1 to R2
    @R2
    D=M
    @R1
    D=D+M
    @R2
    M=D  // Stores new value in R2

    // Decrements R0
    @R0
    M=M-1

    @LOOP
    0;JMP  // Repeat loop

// End of program, stops execution
(END)
    @END
    0;JMP  // Infinite loop to prevent unintended execution
