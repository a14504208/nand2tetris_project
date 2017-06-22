// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

// initialize
@R2
M = 0
@i
M = 0

(Loop)
@i
D = M
@R1
D = M - D // compare if i == R1
@End
D;JEQ // jump to end of loop if i == R1

// add R0 to result
@R0
D = M
@R2
M = D + M

// add 1 to i
@i
M = M + 1

// jump back to beginning
@Loop
0;JEQ

(End)
@End
0;JEQ // infinite loop to end program