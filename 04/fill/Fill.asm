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

// calculate number of RAM of screen
@SCREEN
D = A
@KBD
D = A - D
@screen_num
M = D

// declare loop index i
@i
M = 0

// infinite loop
(Loop)
@KBD
D = M

@White_screen
D;JEQ // white-screen if no keyboard input

@Black_screen
0;JEQ // else black-screen

(White_screen)
@i
M = 0 // initialize loop index

(White_screen_loop)
// test if i < screen_num
@screen_num
D = M
@i
D = D - M
@End
D;JEQ

// white the RAM
@SCREEN
D = A
@i
A = D + M
M = 0

// increment loop index
@i
M = M + 1

// jump back to loop start
@White_screen_loop
0;JEQ

(Black_screen)
@i
M = 0 // initialize loop index

(Black_screen_loop)
// test if i < screen_num
@screen_num
D = M
@i
D = D - M
@End
D;JEQ

// black the RAM
@SCREEN
D = A
@i
A = D + M
M = -1

// increment loop index
@i
M = M + 1

// jump back to loop start
@Black_screen_loop
0;JEQ

(End)
@Loop
0;JEQ
