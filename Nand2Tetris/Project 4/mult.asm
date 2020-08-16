
@R0
D=M
@R3
M=D

(MULT)
@R3
D= M
@END
D;JLE
@R3
D = D - 1
M = D

@R1
D = M
@R2
D = D + M
M = D
@ MULT
0; JMP
(END)

@END
0;JMP