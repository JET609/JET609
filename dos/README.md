# DOS Hello World Program

A simple, well-documented "Hello, World!" application designed for classic **MS-DOS** systems. This project demonstrates DOS programming fundamentals using both **x86 Assembly** and **C** languages.

---

## 📁 Project Structure

```
dos/
├── README.md          # This documentation file
├── hello.asm          # Assembly version (MASM/TASM syntax)
├── hello_nasm.asm     # Assembly version (NASM syntax)
└── hello.c            # C version (ANSI C)
```

---

## 🎯 Program Overview

The program performs the simplest possible operation: displaying "Hello, World!" on the screen and terminating. Despite its simplicity, it demonstrates:

- **DOS Interrupt Calls** (INT 21h) for console output
- **Proper Program Termination** with return codes
- **Memory Models** for 16-bit real mode programming
- **Cross-compiler Compatibility**

---

## 🔧 System Requirements

### Hardware
- IBM PC/XT/AT compatible computer, or emulator
- 8086/8088 processor or later
- Minimum 64KB RAM
- DOS-compatible display adapter

### Software
- MS-DOS 2.0 or later (MS-DOS, PC-DOS, DR-DOS, FreeDOS)
- Appropriate assembler or C compiler (see below)

---

## 📦 Compilation Instructions

### Assembly Version (MASM/TASM)

#### Using Microsoft Macro Assembler (MASM)
```dos
masm hello.asm;
link hello.obj;
```

#### Using Turbo Assembler (TASM)
```dos
tasm hello.asm
tlink hello.obj
```

### Assembly Version (NASM)

#### Using NASM (Netwide Assembler)
```dos
nasm -f bin -o hello.com hello_nasm.asm
```

This creates a compact `.COM` file that can be executed directly.

### C Version

#### Using Turbo C / Turbo C++
```dos
tcc hello.c
```

#### Using Borland C++
```dos
bcc hello.c
```

#### Using Microsoft C
```dos
cl hello.c
```

#### Using DJGPP (GCC for DOS)
```dos
gcc -o hello.exe hello.c
```

#### Using Watcom C/C++
```dos
wcl hello.c
```

---

## 🚀 Running the Program

After successful compilation, run the program from the DOS command prompt:

### For .EXE files:
```dos
hello.exe
```

### For .COM files:
```dos
hello.com
```

### Expected Output:
```
Hello, World!
```

---

## 🖥️ Testing with DOSBox (Modern Systems)

If you don't have access to a physical DOS machine, you can use [DOSBox](https://www.dosbox.com/) emulator:

1. **Install DOSBox** on your modern operating system

2. **Mount a folder** containing your source files:
   ```
   mount c: /path/to/dos/folder
   c:
   ```

3. **Compile and run** using the instructions above

### Quick DOSBox Commands:
```
dosbox -c "mount c: /path/to/folder" -c "c:" -c "hello.exe"
```

---

## 📚 Technical Details

### DOS Interrupts Used

| Interrupt | Function | Description |
|-----------|----------|-------------|
| INT 21h, AH=09h | Display String | Outputs a '$'-terminated string to STDOUT |
| INT 21h, AH=4Ch | Terminate | Ends program execution with return code |

### Memory Models (Assembly)

The MASM version uses the **SMALL** memory model:
- Code segment: up to 64KB
- Data segment: up to 64KB
- Suitable for most small DOS programs

The NASM version produces a **.COM** file (TINY model):
- Combined code and data: up to 64KB
- Loads at offset 100h (PSP)
- Simplest and most portable format

### Return Codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 1+   | Error   |

Check return code in DOS with:
```dos
echo %ERRORLEVEL%
```

---

## 📝 Legacy Compatibility Notes

### MS-DOS Version Compatibility
| DOS Version | Compatibility |
|-------------|---------------|
| MS-DOS 1.x  | ⚠️ Limited (no INT 21h/4Ch) |
| MS-DOS 2.0+ | ✅ Full support |
| PC-DOS      | ✅ Full support |
| DR-DOS      | ✅ Full support |
| FreeDOS     | ✅ Full support |
| DOSBox      | ✅ Full support |

### Processor Compatibility
- **8086/8088**: ✅ Fully compatible
- **80286+**: ✅ Fully compatible (real mode)
- **x64 (64-bit)**: ❌ Requires emulator (DOSBox, Virtual Machine)

### Compiler-Specific Notes

#### Turbo C 2.0
- Default memory model: Small
- Include files in standard location
- No special options needed

#### DJGPP
- Produces 32-bit protected mode executables
- Requires CWSDPMI.EXE or similar DPMI server
- Larger executable size

#### NASM
- Use `-f bin` for raw binary output (.COM)
- Use `-f obj` for linkable object files

---

## 🔍 Code Explanation

### Assembly Version (Simplified)

```asm
mov ah, 09h      ; DOS function: print string
mov dx, msg      ; Address of the message
int 21h          ; Call DOS

mov ah, 4Ch      ; DOS function: terminate
mov al, 0        ; Return code 0
int 21h          ; Call DOS
```

### C Version

```c
#include <stdio.h>

int main(void) {
    printf("Hello, World!\n");
    return 0;
}
```

---

## 📖 Resources

- [Ralf Brown's Interrupt List](http://www.ctyme.com/rbrown.htm) - Comprehensive DOS interrupt reference
- [DOSBox Documentation](https://www.dosbox.com/wiki/Main_Page) - DOSBox emulator guide
- [FreeDOS Project](https://www.freedos.org/) - Modern open-source DOS
- [NASM Documentation](https://www.nasm.us/doc/) - NASM assembler manual

---

## 📜 License

This code is provided as an educational example and is released into the public domain. Use it freely for learning, modification, and distribution.

---

## ✨ Author

Created as a DOS programming example demonstrating classic system programming techniques.

---

<div align="center">
  <sub>Built with ❤️ for retro computing enthusiasts</sub>
</div>
