# Nand2Tetris Computer Systems — CS 210

A collection of computer systems coursework exploring the Hack platform, from assembly language and an assembler through VM translation and Jack compilation. The archive covers projects 4 and 6–11.

## Repository layout

| Directory | Coursework |
|---|---|
| `assembly-programs/` | Project 4: Hack assembly programs |
| `assembler/` | Project 6: Python Hack assembler |
| `vm-translator/project-07/` | Project 7: stack arithmetic and memory access |
| `vm-translator/project-08/` | Project 8: program flow and function calls |
| `jack-programs/` | Project 9: Jack programs |
| `syntax-analyzer/` | Project 10: Jack syntax analysis |
| `compiler/` | Project 11: Jack compiler and code generation |

## Running the tools

Python source is preserved in its original project layout, including the course-provided entry points. Example assembler usage (from the original source):

```bash
cd assembler
python3 hasm.py path/to/Program.asm
```

The VM translator entry points are `hvm.py` inside each project directory; the compiler entry point is `hjc.py` inside `compiler/`. **Note:** The provided VM entry points contain hardcoded `sys.argv` assignments for class tests. Adjust those to accept your input path before running on new files. The compiler starter code may also depend on course-provided modules; check imports before use.


Nand2Tetris is based on *The Elements of Computing Systems* by Noam Nisan and Shimon Schocken. This repository is an independent student coursework archive, not an official course distribution.
