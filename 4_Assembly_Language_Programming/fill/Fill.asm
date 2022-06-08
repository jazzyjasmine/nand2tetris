// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
// Let x.addr denotes the memory location (address) of x
    @SCREEN 
    D=A     // D=SCREEN.addr
    @pointer
    M=D     // pointer=SCREEN.addr
(LOOP)
    @KBD
    D=M     // D=KBD
    @CLEAN
    D;JEQ   // if KBD==0 (keyboard is unpressed), jump to CLEAN
    @pointer
    A=M     // A=pointer
    M=-1    // RAM[pointer]=-1, i.e. blaken the pixels
    @pointer
    D=M+1   // D=pointer+1  
    @KBD
    D=D-A   // D=pointer+1-KBD.addr
    @LOOP 
    D;JGE   // if pointer+1>=KBD.addr, jump to LOOP instead of increasing pointer by 1
    @pointer
    M=M+1   // pointer=pointer+1, i.e. increase pointer by 1
    @LOOP
    0;JMP   // jump to LOOP
(CLEAN)
    @pointer
    A=M     // A=pointer
    M=0     // RAM[pointer]=0, i.e. whiten the pixels
    @pointer
    D=M-1   // D=pointer-1
    @SCREEN
    D=D-A   // D=pointer-1-SCREEN
    @LOOP
    D;JLT   // if pointer-1<SCREEN, jump to LOOP instead of decreasing pointer by 1
    @pointer
    M=M-1   // pointer=pointer-1, i.e. decrease pointer by 1
    @LOOP
    0;JMP   // jump to LOOP
