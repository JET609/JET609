/*============================================================================
 * HELLO.C - Hello, World! Program for MS-DOS
 *============================================================================
 * Description:  A simple 'Hello, World!' program written in ANSI C
 *               for MS-DOS systems. Compatible with Turbo C, Borland C,
 *               Microsoft C, and DJGPP compilers.
 *
 * Author:       DOS Programming Example
 * Version:      1.0
 * Target:       MS-DOS 2.0+ / PC-DOS / FreeDOS / DOSBox
 *
 * Compiler Compatibility:
 *   - Turbo C / Turbo C++ (Borland)
 *   - Borland C++ 3.x - 5.x
 *   - Microsoft C 5.x - 7.x
 *   - Microsoft Visual C++ 1.x (16-bit)
 *   - DJGPP (DOS port of GCC)
 *   - Watcom C/C++
 *   - Pacific C
 *
 * Build Instructions (see README.md for details):
 *   Turbo C:  tcc hello.c
 *   DJGPP:    gcc -o hello.exe hello.c
 *   Watcom:   wcl hello.c
 *
 * Compatibility Notes:
 *   - Uses standard ANSI C library functions only
 *   - No DOS-specific extensions required
 *   - Memory model: Small (suitable for most compilers)
 *   - Works with MS-DOS 2.0 and later
 *============================================================================*/

#include <stdio.h>      /* Standard I/O functions */

/*
 * main - Program entry point
 *
 * Returns: 0 on success (EXIT_SUCCESS)
 */
int main(void)
{
    /* Display greeting message to standard output */
    printf("Hello, World!\n");

    /* Return success code to DOS */
    return 0;
}
