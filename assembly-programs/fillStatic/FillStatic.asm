// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/FillStatic.asm

// Blackens the screen, i.e. writes "black" in every pixel. 
// Key presses are ignored.
// This is an intermediate step added by Prof. Davis.

@SCREEN
D=A
@current  // Points to current screen address
M=D       // Initializes current to SCREEN

@24575    // Last screen address
D=A
@last
M=D       // Stores last address in 'last'

(LOOP)
@current
A=M       // Loads current screen address into A
M=-1      // Set all 16 bits to 1 (black)

@current
M=M+1     // Moves to next screen address

@last
D=M       // Loads last address
@current
D=D-M     // D = last - current

@LOOP
D;JGE     // If last >= current, repeat loop

(END)
@END
0;JMP     // Infinite loop to halt execution