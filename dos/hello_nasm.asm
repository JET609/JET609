;==============================================================================
; HELLO_NASM.ASM - Hello, World! Program for MS-DOS (NASM Syntax)
;==============================================================================
; Description:  A simple 'Hello, World!' program written in x86 Assembly
;               using NASM syntax for MS-DOS systems.
;
; Author:       DOS Programming Example
; Version:      1.0
; Target:       MS-DOS 2.0+ / PC-DOS / FreeDOS / DOSBox
; Assembler:    NASM (Netwide Assembler)
;
; Build Instructions:
;   nasm -f bin -o hello.com hello_nasm.asm
;
; Note: This creates a .COM file (tiny model, max 64KB total)
;       which is simpler and more portable than .EXE format.
;
; Compatibility Notes:
;   - Works with MS-DOS 2.0 and later versions
;   - Compatible with PC-DOS, DR-DOS, FreeDOS, and DOSBox
;   - Requires 8086/8088 or later processor
;   - Output file size: approximately 25 bytes
;==============================================================================

; COM files load at offset 100h in the Program Segment Prefix (PSP)
ORG 100h

section .text

start:
    ; Display the message using DOS interrupt
    mov     ah, 09h         ; DOS function: Display string
    mov     dx, message     ; Address of message string
    int     21h             ; Call DOS interrupt

    ; Terminate program and return to DOS
    mov     ah, 4Ch         ; DOS function: Terminate with return code
    xor     al, al          ; Return code 0 (success) - XOR is smaller than MOV
    int     21h             ; Call DOS interrupt

section .data
    ; Message string - must end with '$' for DOS function 09h
    message: db 'Hello, World!', 0Dh, 0Ah, '$'
    ; 0Dh = Carriage Return (CR)
    ; 0Ah = Line Feed (LF)
    ; '$'  = String terminator for INT 21h/AH=09h
