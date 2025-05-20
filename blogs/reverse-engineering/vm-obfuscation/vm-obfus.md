Great. I’ll analyze the VM-obfuscation project on GitHub to deeply understand how it transforms original JavaScript code into an AST, generates bytecode from the AST, and how the VM in `vm.js` interprets that bytecode to replicate the original logic.

I’ll also examine related JS virtualizer projects if helpful for comparison or clarity. I’ll get back to you with a detailed breakdown of the entire pipeline from source to obfuscated execution.

# Virtual Machine Obfuscation Pipeline for JavaScript

**Virtualization-based obfuscation** works by converting the original code into a custom **bytecode** that runs on a bundled virtual machine. The VM executes instruction-by-instruction, never revealing the original source directly ([The Secret Guide To Virtualization Obfuscation In JavaScript | Johannes Willbold](https://jwillbold.com/posts/obfuscation/2019-06-16-The-Secret-Guide-To-Virtualization-Obfuscation-In-JavaScript/#:~:text=What%20is%20virtualization%20obfuscation%3F)). The `VM-obfuscation` project follows this approach in three main stages: 

1. **Parsing the code into an AST (Abstract Syntax Tree)**  
2. **Translating the AST into a custom bytecode (instruction sequence)**  
3. **Executing the bytecode on a JavaScript VM (`vm.js`/`machine.js`) to reproduce original logic**  

We’ll break down each stage, referencing code from the repository and comparing to similar tools. 

## 1. AST Generation and Transformation

**Parsing to AST:** The obfuscator first parses the original JavaScript source into an AST. This is typically done with a parser like **Babel** or **Esprima**, which can produce a tree of nodes representing syntax (e.g., Program, FunctionDeclaration, BinaryExpression, etc.). In this project, the code for parsing isn’t explicitly shown (likely handled by a library), but similar projects use Babel’s AST parsing and traversal facilities ([VitalyTartynov/jsvm alternatives and similar packages](https://relatedrepos.com/gh/VitalyTartynov/jsvm#:~:text=)) (“用babel ast解析js代码并翻译” – “use Babel AST to parse JS code and translate”). We can reasonably assume `VM-obfuscation` uses a standard JS parser to obtain the AST of the input code.

**AST traversal:** Once the AST is obtained, the obfuscator likely walks through it to build an intermediate representation. The repository includes a `lib/codemodify.js` and `lib/jsinterpret.js`, suggesting multiple AST processing passes. For example, *codemodify* might perform preparatory transformations on the AST (renaming variables, simplifying constructs), and *jsinterpret* might then recursively “interpret” the AST nodes to generate VM instructions. The code hints at a function `generateVar()` and usage of random values for identifiers ([Update · ajsdev/VM-obfuscation@8f492e3 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/8f492e3afe02e420d8feb2bbb99daa119820994d#:~:text=var%20MEMORY%20%3D%20generateVar)), which suggests that during AST processing, new random variable names are generated for use in the VM (to replace clear names like `MEMORY` or `CODE`). Each original variable or literal might be assigned a slot in a virtual **memory array**.  

**Example transformation:** Consider a simple snippet: 

```js
var a = 10;
var b = 20;
console.log(a/b);
``` 

During AST traversal, the tool would identify: 
- Two variable declarations (`a` and `b`) with numeric literals,
- A binary expression (`a/b`),
- A call expression (`console.log`). 

These would be mapped to a sequence of VM operations. In comments, the project illustrates how a similar code is **first broken into VM operations** (allocate values, perform operation, convert to string, log result) and then into numeric bytecode ([Update · ajsdev/VM-obfuscation@9ff05ab · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/9ff05ab0d9c37416b62f816568f824eb07ad4c58#:~:text=1234%200%2010%20%2F%2F%20allocate,0%20as%2010)) ([Update · ajsdev/VM-obfuscation@9ff05ab · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/9ff05ab0d9c37416b62f816568f824eb07ad4c58#:~:text=1244%202%202%20%2F%2F%20inttostring,2%20store%20in%202)):

```text
// Pseudocode operations:
allocate 1 = 10  
allocate 2 = 20  
divide 1 by 2 -> store in 3  
inttostring 3 -> store in 3  
log 3  
end

// Bytecode representation (numeric opcodes and operands):
1234 0 10    // allocate memory[0] = 10  
1234 1 20    // allocate memory[1] = 20  
1240 2 0 1   // divide memory[0] by memory[1], store in memory[2]  
1244 2 2     // int-to-string: memory[2] = memory[2].toString()  
1243 2       // log memory[2] (console.log)  
1245          // end of program
``` 

Here, each `123X` number is a custom opcode (explained below), and the numbers following them are operands like memory indices or literal values. This example shows how the AST of assignments and a `console.log` call are transformed into a linear sequence of VM instructions.

Before bytecode generation, the obfuscator might also **encrypt or encode constants**. In this project, string literals are not embedded in plain form; instead, they are stored as sequences of character codes in the bytecode and reconstructed at runtime. For instance, the string `"A is bigger than B!"` appears in bytecode as its char codes followed by a terminator `0` ([Update · ajsdev/VM-obfuscation@e1321b3 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/e1321b3c8224672d04d449b672ef86f75a84a0c5#:~:text=%6020%60%60%60%60)). This likely happens in a utility (perhaps `lib/toints.js`) that converts strings to integer lists and numbers to a normalized form for insertion into the `CODE` array.

## 2. AST to Custom Bytecode Compilation

After or during AST traversal, the tool produces a **custom bytecode** – essentially an array of integers (`CODE`) that encode the program logic. The repository’s `lib/vmcompiler.js` handles assembling this bytecode and the VM source. Notably, it constructs the big `switch` statement for the VM with randomized opcode values. In the code, we see it generating snippet strings like: 

```js
var ssc = getRandom();
var set_string = sprintf("case %1: %2[%3[%4++]] = decryptString(); break;", ssc, MEMORY, CODE, COUNTER);
``` 

This uses a `getRandom()` to choose a unique opcode number and `sprintf` to fill a template with that opcode and the placeholders `MEMORY`, `CODE`, `COUNTER` ([Update · ajsdev/VM-obfuscation@e1321b3 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/e1321b3c8224672d04d449b672ef86f75a84a0c5#:~:text=)). In effect, each run can assign a different numeric ID to an instruction (e.g., the “set string” operation might be opcode 1233 one time and 871 another time), making the bytecode **non-deterministic** across obfuscations. All such opcodes are collected into the VM’s switch-case. A partial list of instructions implemented in the project includes: 

- **Allocate value**: e.g., `case 1233` for allocating a string, `1234` for an integer, etc. These take a memory slot operand and a value. In the VM, they store the given value into the `MEMORY` array at that index. For example, opcode `1234` (allocate INT) is implemented as: 

  ```js
  case 1234: // allocate memory INT
      MEMORY[CODE[COUNTER++]] = CODE[COUNTER++];
      break;
  ``` 
   ([Update · ajsdev/VM-obfuscation@71cd582 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/71cd58268d81d3d743a52ee4da9753377cd443b3#:~:text=)) 

  This reads the next byte as the target memory index, and the following byte as the integer value, then stores the value. Similarly, `1233` uses a helper `decryptString()` to read subsequent bytes into a string for storage ([Update · ajsdev/VM-obfuscation@71cd582 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/71cd58268d81d3d743a52ee4da9753377cd443b3#:~:text=)).

- **Arithmetic**: e.g., `1237` for addition, `1238` subtraction, `1239` multiplication, `1240` division. These typically take three operands: a destination index and two source indices. The VM will perform the operation on `MEMORY[src1]` and `MEMORY[src2]` and put the result in `MEMORY[dest]`. For instance, an addition might be compiled to bytecode `[1237, dest, op1, op2]`, and the VM executes it as `MEMORY[dest] = MEMORY[op1] + MEMORY[op2]`. (In an earlier commit, the code used an immediate value for one operand ([Update · ajsdev/VM-obfuscation@71cd582 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/71cd58268d81d3d743a52ee4da9753377cd443b3#:~:text=case%201237%3A%20%2F%2F%20Addition)), but it was later adjusted to use memory references for both, matching a register-like design.)

- **Array and String operations**: The project adds opcodes for common operations on containers. For example, `1246` performs concatenation: 

  ```js
  case 1246: // concat string/array
      MEMORY[CODE[COUNTER++]] = 
          MEMORY[CODE[COUNTER++]].concat( MEMORY[CODE[COUNTER++]] );
      break;
  ``` 
   ([Update · ajsdev/VM-obfuscation@ae08e30 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/ae08e30c43cfe862bbae3c6dc0464bbc9f1b5c73#:~:text=case%201246%3A%20%2F%2F%20concat%20string%2Farray))

  This pops three operands from `CODE`: a destination index and two source indices, and sets `MEMORY[dest] = MEMORY[src1].concat(MEMORY[src2])`. Likewise, `1247` gets a length (`MEMORY[dest] = MEMORY[src].length`), `1248` slices a string/array (`.slice()` with two indices), `1249` pushes an element onto an array, etc. ([Update · ajsdev/VM-obfuscation@ae08e30 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/ae08e30c43cfe862bbae3c6dc0464bbc9f1b5c73#:~:text=)) ([Update · ajsdev/VM-obfuscation@ae08e30 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/ae08e30c43cfe862bbae3c6dc0464bbc9f1b5c73#:~:text=case%201249%3A%20%2F%2F%20push)). These correspond to higher-level AST nodes (like property accesses or method calls) being converted into low-level bytecode.

- **Control flow**: The VM supports unconditional jumps via opcode `1242` (GOTO). In bytecode, `1242 X` means set the instruction pointer (`COUNTER`) to X, effectively jumping to a new position in the `CODE` array ([Update · ajsdev/VM-obfuscation@71cd582 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/71cd58268d81d3d743a52ee4da9753377cd443b3#:~:text=)). Conditional logic (if/else) is handled by a compare opcode (`1241`) combined with conditional or unconditional jumps. For example, the pseudo-bytecode `1241, op1, op2, L` might compare `MEMORY[op1] > MEMORY[op2]` and if false, jump to label `L` (the start of the else-block) by setting `COUNTER`. The exact implementation in the repo is incomplete, but we see the intention in comments: `compare (a > b)` followed by an `else` label and a GOTO for skipping the else block ([Update · ajsdev/VM-obfuscation@e1321b3 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/e1321b3c8224672d04d449b672ef86f75a84a0c5#:~:text=%6014%60%60%60%60)) ([Update · ajsdev/VM-obfuscation@e1321b3 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/e1321b3c8224672d04d449b672ef86f75a84a0c5#:~:text=)). (In the final code, `1241` likely stores a boolean or directly manipulates `COUNTER` to achieve the conditional jump. `1245` is used as an **END** instruction to break out of the VM loop.)

- **External calls**: Since the VM cannot natively execute real API calls, such calls are either simulated by custom opcodes or left in clear. The example above uses `1243` as a “log” operation. In one commit, `case 1243` is labeled `// external func` ([Update · ajsdev/VM-obfuscation@71cd582 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/71cd58268d81d3d743a52ee4da9753377cd443b3#:~:text=)), and later they use it specifically for `console.log` (logging a value). This suggests a general mechanism where certain opcodes trigger real JavaScript functions. The VM might handle `1243 X` by doing `console.log(MEMORY[X])` or calling a user-provided function. (Other projects handle function calls by storing actual function references in `MEMORY` and invoking them when an opcode is encountered.)

**Bytecode structure:** The bytecode is stored as a plain array of numbers in the generated output code (in a variable often still named `CODE`). The interpreter uses an index `COUNTER` to fetch the next opcode and increment as it reads operands. Memory for variables is an array `MEMORY`. The design here is **register-like** (with `MEMORY` indices serving as registers). This is similar to other VM obfuscators like Rusty-JSYC, which represent operations as sequences of opcodes and operands (some denoting registers) ([The Secret Guide To Virtualization Obfuscation In JavaScript | Johannes Willbold](https://jwillbold.com/posts/obfuscation/2019-06-16-The-Secret-Guide-To-Virtualization-Obfuscation-In-JavaScript/#:~:text=LoadNum%20Reg,c%20%3D%20a%20%2B%20b)).

Before output, the `vmcompiler.js` replaces placeholder names with randomly generated ones for extra confusion. The code picks random identifiers for `MEMORY`, `CODE`, `COUNTER` using `generateVar()` ([Update · ajsdev/VM-obfuscation@8f492e3 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/8f492e3afe02e420d8feb2bbb99daa119820994d#:~:text=var%20MEMORY%20%3D%20generateVar)). For example, in one run it might choose `%1="qMz"`, `%2="X9_"`, etc., and then produce the VM code with those names instead of obvious ones. This makes the final obfuscated code less recognizable.

## 3. The `vm.js` Virtual Machine Execution

The final obfuscated code consists of the **virtual machine function** (an IIFE in `machine.js`) and the **embedded bytecode array**. When this code runs, it instantiates the VM and executes the bytecode, reproducing the original program’s behavior. 

The **VM loop** is a classic interpreter: 

- Initialize `MEMORY` (empty array) and `COUNTER = 0`.  
- Enter a `while(true)` loop and read the next instruction code: `switch(CODE[COUNTER++]) { ... }`.  
- For each `case <opcode>:`, perform the defined operation, which may read/write `MEMORY` and the `COUNTER`. Most cases end with `break` to continue the loop.  
- The `END` opcode (`1245`) triggers a termination. In the VM code, this is implemented by breaking out of the loop or simply calling `return` from the IIFE ([Update · ajsdev/VM-obfuscation@ae08e30 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/ae08e30c43cfe862bbae3c6dc0464bbc9f1b5c73#:~:text=)) ([Update · ajsdev/VM-obfuscation@71cd582 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/71cd58268d81d3d743a52ee4da9753377cd443b3#:~:text=)). Once the VM function returns, the obfuscated code’s job is done.

At runtime, each high-level construct causes a series of VM operations. For example, a single line `c = a + b;` became a sequence of three VM instructions (load `a`, load `b`, add) executed step by step. The VM’s switch dispatch for an addition looks like: 

```js
case 1237: // Addition
    MEMORY[ CODE[COUNTER++] ] = MEMORY[ CODE[COUNTER++] ] + MEMORY[ CODE[COUNTER++] ];
    break;
``` 

This pops three operands from the `CODE` array and performs the add ([Update · ajsdev/VM-obfuscation@e1321b3 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/e1321b3c8224672d04d449b672ef86f75a84a0c5#:~:text=)) ([Update · ajsdev/VM-obfuscation@e1321b3 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/e1321b3c8224672d04d449b672ef86f75a84a0c5#:~:text=)). Every possible operation defined in the bytecode compiler has a corresponding handler here. If the original code had loops or complex expressions, they would be unrolled into many low-level VM ops.

**Reproducing control flow:** If an `if` statement was present, the VM would use the compare and goto opcodes to achieve the conditional jump. For example, after comparing two values via `1241`, the VM might set `COUNTER` to skip a block. Similarly, a high-level loop could be implemented by explicit backward `goto` instructions in bytecode forming a loop.

**Memory semantics:** The `MEMORY` array holds all variables and intermediate values. Because JavaScript is dynamically typed, `MEMORY` can store numbers, strings, objects, etc. The VM opcodes handle them appropriately (e.g., concatenation calls `.concat`, which works on arrays or strings). This design is akin to a **stack machine with a single global stack/heap** (the `MEMORY` array) and a program counter (`COUNTER`). It’s a simple model, but effective for interpreting arbitrary code.

One interesting aspect is how strings are handled: The `decryptString()` function in the VM reads sequential bytes until a `0` terminator and builds a JS string from those char codes ([Update · ajsdev/VM-obfuscation@71cd582 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/71cd58268d81d3d743a52ee4da9753377cd443b3#:~:text=)) ([Update · ajsdev/VM-obfuscation@71cd582 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/71cd58268d81d3d743a52ee4da9753377cd443b3#:~:text=)). This is invoked by the “allocate string” opcode. Thus, any string literal in the original program is stored as numbers in `CODE` and reconstructed at runtime, foiling straightforward static analysis of the final code.

## 4. Design Choices, Comparisons, and Security Implications

**Instruction set design:** The instruction set chosen here is relatively *high-level* (e.g., separate opcodes for array `push`, `slice`, etc., rather than combining everything into very primitive operations). This makes the bytecode a bit more verbose but easier to generate from source AST. Other JavaScript VM obfuscators use similar designs. For example, Johannes Willbold’s Rusty-JSYC uses a register-based VM with opcodes like LOAD_NUM, ADD, etc. ([The Secret Guide To Virtualization Obfuscation In JavaScript | Johannes Willbold](https://jwillbold.com/posts/obfuscation/2019-06-16-The-Secret-Guide-To-Virtualization-Obfuscation-In-JavaScript/#:~:text=LoadNum%20Reg,c%20%3D%20a%20%2B%20b)), and Jscrambler’s VM-based protection (used in some malware or protection scripts) also features a large switch in JS interpreting arrays of bytecodes. 

**Use of randomization:** A notable innovation in `VM-obfuscation` is the use of **random opcode values and variable names** for each obfuscation run. The project’s compiler picks random integers for each instruction (`getRandom()` in `vmcompiler.js`) and builds the VM’s switch-case accordingly ([Update · ajsdev/VM-obfuscation@e1321b3 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/e1321b3c8224672d04d449b672ef86f75a84a0c5#:~:text=var%20getRandom%20%3D%20function%20,)) ([Update · ajsdev/VM-obfuscation@e1321b3 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/e1321b3c8224672d04d449b672ef86f75a84a0c5#:~:text=)). For instance, one run may assign `case 235: // addition` and another run choose `case 834:` for the same operation. This means the numeric bytecode is unique per instance, thwarting pattern-based deobfuscation. Similarly, it gives `MEMORY`, `CODE`, and `COUNTER` random names (like `_$a1`), which makes the VM code harder to recognize. These tactics increase the **entropy** of the obfuscated output, forcing an attacker to reverse-engineer the instruction set anew for each variant ([The Secret Guide To Virtualization Obfuscation In JavaScript | Johannes Willbold](https://jwillbold.com/posts/obfuscation/2019-06-16-The-Secret-Guide-To-Virtualization-Obfuscation-In-JavaScript/#:~:text=Since%20the%20bytecode%20is%20executed,to%20analyze%20the%20actual%20bytecode)).

**Comparison to other tools:** Other open-source projects like **aesthetic0001/js-virtualizer** follow a similar pipeline. They parse code with Babel, identify functions marked for virtualization, compile them to a custom bytecode, and inject a JS VM to run it ([GitHub - aesthetic0001/js-virtualizer: Virtualization-based obfuscation for javascript](https://github.com/aesthetic0001/js-virtualizer#:~:text=js,would%20have%20to%20run%20synchronously)) ([GitHub - aesthetic0001/js-virtualizer: Virtualization-based obfuscation for javascript](https://github.com/aesthetic0001/js-virtualizer#:~:text=const%20%7Btranspile%7D%20%3D%20require%28%22js)). The main differences are in implementation details: e.g., js-virtualizer uses a stack-based VM and focuses on selected functions (for performance reasons), whereas `VM-obfuscation` appears to aim at whole-program virtualization (with many opcodes to cover JS features). Commercial obfuscators (like Jscrambler or Babel Enterprise) implement even more elaborate VMs or multiple virtualization layers. 

**Innovative aspects:** The strength of VM-based obfuscation is that the original code’s control flow and data flow are hidden behind a layer of interpretation ([The Secret Guide To Virtualization Obfuscation In JavaScript | Johannes Willbold](https://jwillbold.com/posts/obfuscation/2019-06-16-The-Secret-Guide-To-Virtualization-Obfuscation-In-JavaScript/#:~:text=Virtualization%20obfuscation%20is%20a%20state,thereby%20executing%20the%20actual%20code)). This project demonstrates that by turning variables and literals into abstract memory indices and opcodes. Even if an attacker views the final code, they see only a tangle of numbers and a big switch – the logic is non-obvious. Additionally, the use of a **unique, custom VM per run** (thanks to opcode randomization) means automated deobfuscators struggle, since “any two virtualization obfuscations are potentially different” ([The Secret Guide To Virtualization Obfuscation In JavaScript | Johannes Willbold](https://jwillbold.com/posts/obfuscation/2019-06-16-The-Secret-Guide-To-Virtualization-Obfuscation-In-JavaScript/#:~:text=Since%20the%20bytecode%20is%20executed,to%20analyze%20the%20actual%20bytecode)).

**Limitations:** The trade-off for this strong obfuscation is **performance and complexity**. Running code via a JS interpreter incurs a significant speed penalty – every original operation might take dozens of JS operations under the hood. Thus, obfuscating an entire large program can make it run orders of magnitude slower. In practice, VM obfuscation is often applied only to sensitive routines (e.g., license checks, cryptographic functions) rather than everything. Another limitation is that supporting the full JavaScript language is hard – features like closures, `this` context, `async/await`, prototypes, etc., would require many additional opcodes and careful handling. The given project is labeled **experimental/not-done**, and indeed some parts (like full `if/else` handling or function calls) appear incomplete. 

**Security implications:** While VM obfuscation greatly raises the reverse-engineering bar, it’s not unbreakable. Attackers can still analyze the VM. For example, one could run the obfuscated code in a debugger or instrument it to trace `MEMORY` and `CODE` usage, thereby **disassembling** the bytecode. In fact, researchers have built generic devirtualizers by symbolically executing the VM dispatcher to recover higher-level semantics ([Writing Disassemblers for VM-based Obfuscators - Tim Blazytko](https://synthesis.to/2021/10/21/vm_based_obfuscation.html#:~:text=Writing%20Disassemblers%20for%20VM,to%20build%20disassemblers%20for)) ([Virtual Machine based obfuscation: An Overview - Hackcyom](https://www.hackcyom.com/2024/09/vm-obfuscation-overview/#:~:text=Virtual%20Machine%20based%20obfuscation%3A%20An,design%20philosophy%20and%20future%20research)). There are publicly documented efforts to reverse engineer VM-protected code (e.g., analyses of TikTok’s VM obfuscation on Reddit) which involve understanding the custom bytecode and writing a decompiler for it. The randomization in `VM-obfuscation` means such a reverse-engineer must do that analysis per sample, but given enough motivation, the VM can be understood. Once the opcode meanings are deduced, the bytecode can be translated back to readable code (or at least pseudo-code). 

In summary, `ajsdev/VM-obfuscation` showcases a powerful obfuscation pipeline: using an AST parser to capture the original program structure, compiling it into a bespoke bytecode (with a defined instruction set and stored data), and deploying a JavaScript virtual machine (`vm.js`) that executes this bytecode to mimic the original functionality. This approach, similar to other JS virtualization tools, significantly complicates static analysis of the code ([The Secret Guide To Virtualization Obfuscation In JavaScript | Johannes Willbold](https://jwillbold.com/posts/obfuscation/2019-06-16-The-Secret-Guide-To-Virtualization-Obfuscation-In-JavaScript/#:~:text=Virtualization%20obfuscation%20is%20a%20state,thereby%20executing%20the%20actual%20code)). However, it comes with high runtime cost and complexity. It’s an **innovative yet heavy** protection – ideal for small but critical code portions where one is willing to trade performance for confidentiality. With the groundwork this project lays (AST-to-bytecode compiler and a JS interpreter), one can see how more features or even multiple layers of VMs could be added to further enhance the obfuscation against determined reverse engineers. 

**Sources:** The analysis references the VM-obfuscation repository’s code snippets and comments to illustrate how high-level code is transformed into bytecode ([Update · ajsdev/VM-obfuscation@9ff05ab · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/9ff05ab0d9c37416b62f816568f824eb07ad4c58#:~:text=1234%200%2010%20%2F%2F%20allocate,0%20as%2010)) ([Update · ajsdev/VM-obfuscation@9ff05ab · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/9ff05ab0d9c37416b62f816568f824eb07ad4c58#:~:text=1244%202%202%20%2F%2F%20inttostring,2%20store%20in%202)) and how the virtual machine executes these instructions (e.g., handling of concatenation ([Update · ajsdev/VM-obfuscation@ae08e30 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/ae08e30c43cfe862bbae3c6dc0464bbc9f1b5c73#:~:text=case%201246%3A%20%2F%2F%20concat%20string%2Farray)) and integer allocation ([Update · ajsdev/VM-obfuscation@71cd582 · GitHub](https://github.com/ajsdev/VM-obfuscation/commit/71cd58268d81d3d743a52ee4da9753377cd443b3#:~:text=))). We also include conceptual context from a blog on JS virtualization obfuscation ([The Secret Guide To Virtualization Obfuscation In JavaScript | Johannes Willbold](https://jwillbold.com/posts/obfuscation/2019-06-16-The-Secret-Guide-To-Virtualization-Obfuscation-In-JavaScript/#:~:text=Virtualization%20obfuscation%20is%20a%20state,thereby%20executing%20the%20actual%20code)) ([The Secret Guide To Virtualization Obfuscation In JavaScript | Johannes Willbold](https://jwillbold.com/posts/obfuscation/2019-06-16-The-Secret-Guide-To-Virtualization-Obfuscation-In-JavaScript/#:~:text=Since%20the%20bytecode%20is%20executed,to%20analyze%20the%20actual%20bytecode)) to emphasize the strategy and challenges of this approach.

