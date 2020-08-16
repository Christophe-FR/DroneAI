
(start)
@i
M=0 // i = 0

@KBD
D=M
@whiten
D; JEQ



// BLACK SCREEN
(blacken)
@8192
D=A
@i
D = M-D // i-8192
@start
D; JEQ
@i
D = M
@SCREEN
A=A+D
M=-1 // blacken
@i
M = M + 1 // i++
@blacken
0; JMP

// WHITE SCREEN
(whiten)
@8192
D=A
@i
D = M-D // i-8192
@start
D; JEQ
@i
D = M
@SCREEN
A=A+D
M=0 // whiten
@i
M = M + 1 // i++
@whiten
0; JMP

@start
D; JEQ