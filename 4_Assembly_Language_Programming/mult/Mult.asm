// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.
// Put your code here.
// Idea: R2=R1+R1+...+R1 for R0 times.
// Everytime we increase R2 by R1, we decrease R0 by 1.
// When R0 is decreased to 0, the loop ends and R2 is the result.
    @R2     // R2 refers to the multiplication result
    M=0     // R2=0 initially
(LOOP)
    @R0
    D=M     // D=R0
    @END
    D;JEQ   // if R0 == 0 goto END
    @R1
    D=M     // D=R1
    @R2
    M=D+M   // R2=R1+R2
    @R0
    M=M-1   // R0=R0-1
    @LOOP
    0;JMP   // Goto LOOP
(END)
    @END
    0;JMP   // Infinite loop