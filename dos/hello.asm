;==============================================================================
; HELLO.ASM - Hello, World! Program for MS-DOS
;==============================================================================
; Description:  A simple 'Hello, World!' program written in x86 Assembly
;               for MS-DOS systems. This program demonstrates basic DOS
;               interrupt calls for console output.
;
; Author:       DOS Programming Example
; Version:      1.0
; Target:       MS-DOS 2.0+ / PC-DOS / FreeDOS / DOSBox
; Assembler:    MASM, TASM, NASM, or compatible x86 assembler
;
; Compatibility Notes:
;   - Works with MS-DOS 2.0 and later versions
;   - Compatible with PC-DOS, DR-DOS, FreeDOS, and DOSBox
;   - Requires 8086/8088 or later processor (uses 16-bit real mode)
;   - Minimal memory requirements: < 1KB
;
; DOS Interrupts Used:
;   INT 21h, AH=09h - Display string (terminated with '$')
;   INT 21h, AH=4Ch - Terminate program with return code
;==============================================================================

; Memory model and processor directive
.MODEL SMALL                ; Small memory model (code < 64KB, data < 64KB)
.STACK 100h                 ; Reserve 256 bytes for stack

;------------------------------------------------------------------------------
; DATA SEGMENT - Contains program data
;------------------------------------------------------------------------------
.DATA
    ; Message string - must end with '$' for DOS function 09h
    msg     DB  'Hello, World!', 0Dh, 0Ah, '$'
    ; 0Dh = Carriage Return (CR)
    ; 0Ah = Line Feed (LF)
    ; '$'  = String terminator for INT 21h/AH=09h

;------------------------------------------------------------------------------
; CODE SEGMENT - Contains executable code
;------------------------------------------------------------------------------
.CODE
main PROC
    ; Initialize data segment register
    MOV     AX, @DATA       ; Get address of data segment
    MOV     DS, AX          ; Load into DS register

    ; Display the message using DOS interrupt
    MOV     AH, 09h         ; DOS function: Display string
    LEA     DX, msg         ; Load effective address of message into DX
    INT     21h             ; Call DOS interrupt

    ; Terminate program and return to DOS
    MOV     AH, 4Ch         ; DOS function: Terminate with return code
    MOV     AL, 00h         ; Return code 0 (success)
    INT     21h             ; Call DOS interrupt

main ENDP
END main
