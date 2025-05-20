Understood — I’ll search for actual live or archived JavaScript samples that implement custom virtual machine (VM)-based obfuscation. Once I identify a viable sample, I’ll walk through its code step by step with detailed annotations, focusing on how the VM dispatcher works, how opcodes are parsed, and how the logic can be emulated or cracked.

I’ll get back to you shortly with a real code target and annotated dissection.

# TikTok Web Telemetry VM-Obfuscated Script

## Overview 
One notable real-world example of **VM-based JavaScript obfuscation** comes from TikTok’s web application. TikTok employs a **custom virtual machine (VM)** in its front-end code to hide sensitive logic (like telemetry and anti-bot fingerprinting) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=)) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=_0x4c03ae,0x487dd5%29)). Instead of using readable JavaScript functions, the logic is compiled into a **bytecode string**, and a **JavaScript VM interpreter** executes this bytecode at runtime. This makes reverse-engineering much harder, since an analyst must decipher the VM’s instruction set and behavior rather than just de-minifying some JS.

The **bytecode** appears as a long, encoded string of seemingly random characters (often hex or base64-like). For example, TikTok’s script contains calls such as: 

```js
_0x4c03ae(
  "484e4f4a403f524300252a08db14af68000004f...",  // Encoded bytecode string (abridged)
  {
    get 0x0() { return window; },              // Environment object with getters/setters
    // ... (other properties omitted for brevity)
    set 0xd(val) { _0xc2c82d = val; },
  },
  undefined
);
``` 

In the above snippet (with the string truncated for brevity), the function `_0x4c03ae` is being invoked with an **encoded bytecode string** and an environment object. Inside `_0x4c03ae`, the string is decoded into a list of bytecode **instructions** and associated data (using a key embedded at the start of the string) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=)) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=order,and%20a%20list%20of%20instructions)). This prepares the instruction array for the VM to execute. After decoding, the VM is launched by calling an inner function (here `_0x7f5f97`) with initial parameters including an **instruction pointer**, an empty args array, argument count, the environment object, and `undefined` (context data) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=Once%20this%20is%20done%2C%20the,launched%20with%20a%20few%20parameters)). 

## Bytecode Interpreter Loop and Opcode Handlers 
Once the VM starts, it enters a **dispatcher loop** that reads and executes one bytecode **opcode** at a time. In TikTok’s case, this is implemented with a continuous `for (;;)` loop and a series of nested `if/else` statements acting as a **switch** on the opcode value ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=for%20%28var%20_0x28b3ac%20%3D%20,else)) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=%2F%2F%20you%20get%20the%20idea,else%20statements%20%7D)). Below is an excerpt of the VM’s interpreter loop (variable names as in the deobfuscated TikTok code):

```js
for (var _0x28b3ac = []; ; ) {               // _0x28b3ac not used here (could be for try/catch)
  try {
    var _0xd2004 = _0x146ed2[_0x3178c9++];   // fetch next opcode from bytecode array
    if (_0xd2004 < 37) {
      if (_0xd2004 < 18) {
        if (_0xd2004 < 7) {
          if (_0xd2004 < 3) {
            // Handler for opcodes 0, 1, 2:
            _0x4f176d[++_0x53c743] = _0xd2004 === 0 || null;
          } else {
            if (_0xd2004 < 4) {
              // Handler for opcode 3:
              _0xb14b3d = _0x146ed2[_0x3178c9++];
              _0x4f176d[++_0x53c743] = (_0xb14b3d << 24) >> 24;
            } else {
              if (_0xd2004 === 4) {
                // Handler for opcode 4:
                _0xb14b3d = (_0x146ed2[_0x3178c9] << 8) + _0x146ed2[_0x3178c9 + 1];
                _0x3178c9 += 2;
                _0x4f176d[++_0x53c743] = (_0xb14b3d << 16) >> 16;
              } else {
                // ...additional handlers for opcodes 5,6,...
              }
            }
          }
        } else {
          // ...handlers for opcodes 7 through 17...
        }
      } else {
        // ...handlers for opcodes 18 through 36...
      }
    }
  } catch (_0x9843fc) {
    // ...VM exit or exception handling (omitted for brevity)...
  }
}
``` 

In this interpreter:

- `_0x146ed2` is the **bytecode instruction array** (filled by decoding the input string) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=We%20can%20see%20that%20this,is)). `_0x3178c9` serves as the **instruction pointer**, incrementing as each byte is read ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=suggests%20that%20,is)).  
- `_0xd2004` holds the current opcode. The code uses a chain of range checks (`< 3`, `< 4`, etc.) to determine which operation to perform, effectively acting like opcode **dispatch** logic ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=if%20%28_0xd2004%20,0xd2004%20%3D%3D%3D%204%29)). (This nested style is likely an optimization to minimize comparisons, equivalent to a large switch-case or lookup table.)
- `_0x4f176d` is an array acting as the VM’s **operand stack**. `_0x53c743` is the stack pointer (index) for the top of this stack ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=if%20%28_0xd2004%20,else)). Many opcode handlers push results onto this stack. For example, opcodes 0–2 push a boolean value (`true` for opcode 0, `false` for 1, and `null` for 2) by the expression `_0xd2004 === 0 || null` ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=if%20%28_0xd2004%20,else)). Opcode 3 reads the next byte from the bytecode (`_0x146ed2[_0x3178c9++]`) and pushes it as a signed 8-bit value ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=%7D%20else%20,0xd2004%20%3D%3D%3D%204%29)). Opcode 4 combines the next two bytes into a 16-bit number and pushes that ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=_0xb14b3d%20%3D%20_0x146ed2,else)). Each group of opcodes would have its own handler logic inside these conditionals.
- The `try/catch` suggests the loop relies on an exception to break out – likely an out-of-range opcode or a special opcode triggers a throw to exit the VM (common in such obfuscations to avoid an explicit `break` out of the infinite loop).

This TikTok VM snippet clearly showcases a **custom bytecode (the encoded string)**, a **dispatcher loop** stepping through the bytecode, and multiple **opcode handlers** (via nested if/else). It maintains a **virtual stack** (`_0x4f176d`) and uses a program counter (`_0x3178c9`) and other temp variables (like `_0xb14b3d` for intermediate values) – all hallmarks of a virtual machine execution model.

## Why this Sample? 
The TikTok `webmssdk.js` VM is an ideal candidate for deep analysis because it’s not a toy example – it’s a **deployed, real-world obfuscation** protecting a popular web service’s code. It contains all the aspects of a true JS-based VM obfuscator:

- **Custom bytecode format** – the logic is embedded in a data string, not in visible source code ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=)).
- **Decoder and initialization** – the VM function `_0x4c03ae` extracts a bytecode instruction array and setup values from the input string before execution ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=order,and%20a%20list%20of%20instructions)).
- **Interpreter loop** – a `for(;;)` loop reads and processes each opcode in sequence ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=for%20%28var%20_0x28b3ac%20%3D%20,else)).
- **Opcode dispatch handlers** – different opcodes (identified by numeric values) trigger different actions, as seen with the range checks and stack operations ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=if%20%28_0xd2004%20,0xd2004%20%3D%3D%3D%204%29)).
- **Virtual execution context** – uses its own stack and instruction pointer, operating on an isolated state (only interacting with the outside via the provided environment object) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=Once%20this%20is%20done%2C%20the,launched%20with%20a%20few%20parameters)) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=if%20%28_0xd2004%20,else)).

Because this VM was engineered to deter reverse-engineering, studying it will provide insights into control flow, data handling, and anti-debug tricks used by modern obfuscators. In a follow-up, we can systematically **walk through this code line-by-line**, decipher the opcode meanings, and even attempt to reconstruct the original logic that the bytecode represents ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=We%20can%20see%20that%20this,is)) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=We%20can%20see%20that%20this,is%20our%20instruction%20pointer)). This makes it highly suitable for a deep dive into VM-based obfuscation techniques. 

**Sources:** The above code and analysis are based on TikTok’s `webmssdk.js` script as deobfuscated and described by researchers ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=)) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=for%20%28var%20_0x28b3ac%20%3D%20,else)). This script is publicly accessible (e.g., via TikTok’s web interface and in research blogs) and has been archived/analyzed in articles like *“Reverse Engineering TikTok's VM Obfuscation”* ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=One%20day%2C%20I%20stumbled%20across,up%20where%20they%20left%20off)) ([Reverse Engineering TikTok's VM Obfuscation | Ibiyemi Abiodun](https://ibiyemiabiodun.com/projects/reversing-tiktok-pt2/#:~:text=Once%20this%20is%20done%2C%20the,launched%20with%20a%20few%20parameters)), which confirm the presence of a custom JS VM in TikTok’s front-end. The sample illustrates a genuine VM-based obfuscation in the wild, rather than a contrived example, meeting all the criteria for deep VM analysis. 

