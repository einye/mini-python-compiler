# x86_generator.py

def generate_x86(tac, variables=None):
    registers = ['eax', 'ebx', 'ecx', 'edx']
    reg_map = {}
    mem_map = {}
    
    # FIX: Start with the known variables from semantic analysis (if provided)
    data_section = set(variables) if variables else set()
    asm = []

    def get_operand(op):
        if isinstance(op, int):
            return f"{op}"
        if op in reg_map:
            return reg_map[op]
        elif op in mem_map:
            return f"[{mem_map[op]}]"
        else:
            return f"[{op}]"

    def allocate(op):
        if op is None or isinstance(op, int):
            return
        if op.startswith('t'):
            for r in registers:
                if r not in reg_map.values():
                    reg_map[op] = r
                    return
        if not (isinstance(op, str) and op.startswith('L')):
            mem_map[op] = op
            data_section.add(op) # Ensure it's in the data section

    for quad in tac:
        op, a1, a2, res = quad
        if op not in ('label', 'goto'):
            allocate(a1)
            allocate(a2)
        if op not in ('label', 'goto', 'ifnz'):
            allocate(res)

    asm.append("section .data")
    asm.append("    newline db 10")
    asm.append("    buf times 12 db 0")
    asm.append("    true_str db 'True', 10, 0")
    asm.append("    false_str db 'False', 10, 0")
    
    # Declare all variables, sorted for consistency
    for var in sorted(data_section):
        # Make sure we don't declare temporary registers or labels as memory
        if not var.startswith('t') and not var.startswith('L'):
            asm.append(f"    {var} dd 0")

    asm.append("\nsection .text")
    asm.append("    global _start")
    asm.append("_start:")

    for quad in tac:
        op, a1, a2, res = quad

        if op == '=':
            src = '1' if a1 == 'True' else '0' if a1 == 'False' else get_operand(a1)
            dst = get_operand(res)
            asm.append(f"    mov eax, {src}")
            if dst != 'eax':
                asm.append(f"    mov {dst}, eax")

        elif op in ('+', '-', '*', '//'):
            left = get_operand(a1)
            right = get_operand(a2)
            dst = get_operand(res)
            asm.append(f"    mov eax, {left}")
            if op == '+':
                asm.append(f"    add eax, {right}")
            elif op == '-':
                asm.append(f"    sub eax, {right}")
            elif op == '*':
                asm.append(f"    imul eax, {right}")
            elif op == '//':
                asm.append("    cdq")
                asm.append(f"    mov ebx, {right}")
                asm.append("    idiv ebx")
            if dst != 'eax':
                asm.append(f"    mov {dst}, eax")

        elif op in ('==', '!=', '>', '<', '>=', '<='):
            left = get_operand(a1)
            right = get_operand(a2)
            dst = get_operand(res)
            asm.append(f"    mov eax, {left}")
            asm.append(f"    cmp eax, {right}")
            set_instr = {
                '==': 'sete', '!=': 'setne', '>': 'setg', '<': 'setl', '>=': 'setge', '<=': 'setle'
            }[op]
            asm.append(f"    {set_instr} al")
            asm.append(f"    movzx eax, al")
            if dst != 'eax':
                asm.append(f"    mov {dst}, eax")

        elif op == 'and':
            left = get_operand(a1)
            right = get_operand(a2)
            dst = get_operand(res)
            asm.append(f"    mov eax, {left}")
            asm.append(f"    and eax, {right}")
            if dst != 'eax':
                asm.append(f"    mov {dst}, eax")

        elif op == 'or':
            left = get_operand(a1)
            right = get_operand(a2)
            dst = get_operand(res)
            asm.append(f"    mov eax, {left}")
            asm.append(f"    or eax, {right}")
            if dst != 'eax':
                asm.append(f"    mov {dst}, eax")

        elif op == 'not':
            src = get_operand(a1)
            dst = get_operand(res)
            asm.append(f"    mov eax, {src}")
            # Bitwise NOT on 0 gives -1 (true), on 1 gives -2 (still truthy).
            # Since Python's `not` yields True/False (1/0), normalize:
            asm.append("    cmp eax, 0")
            asm.append("    sete al")
            asm.append("    movzx eax, al")
            if dst != 'eax':
                asm.append(f"    mov {dst}, eax")
                
        elif op == 'ifnz':
            cond = get_operand(a1)
            label = res
            asm.append(f"    cmp {cond}, 0")
            asm.append(f"    jne {label}")

        elif op == 'goto':
            asm.append(f"    jmp {res}")

        elif op == 'label':
            asm.append(f"{res}:")

        elif op == 'print':
            if a1 == 'True':
                asm += [
                    "    mov eax, 4",
                    "    mov ebx, 1",
                    "    mov ecx, true_str",
                    "    mov edx, 5",
                    "    int 0x80"
                ]
            elif a1 == 'False':
                asm += [
                    "    mov eax, 4",
                    "    mov ebx, 1",
                    "    mov ecx, false_str",
                    "    mov edx, 6",
                    "    int 0x80"
                ]
            else:
                val = get_operand(a1)
                asm.append(f"    mov eax, {val}")
                asm.append(f"    call print_int")

    asm += [
        "    mov eax, 1",
        "    xor ebx, ebx",
        "    int 0x80"
    ]

    asm += [
        "\nprint_int:",
        "    mov ecx, buf + 11",
        "    mov byte [ecx], 0",
        "    dec ecx",
        "    cmp eax, 0",
        "    jge .convert",
        "    neg eax",
        "    mov bl, '-'",
        "    mov [ecx], bl",
        "    dec ecx",
        ".convert:",
        "    xor edx, edx",
        "    mov ebx, 10",
        ".next_digit:",
        "    xor edx, edx",
        "    div ebx",
        "    add dl, '0'",
        "    mov [ecx], dl",
        "    dec ecx",
        "    test eax, eax",
        "    jnz .next_digit",
        "    inc ecx",
        "    mov eax, 4",
        "    mov ebx, 1",
        "    mov edx, buf + 12",
        "    sub edx, ecx",
        "    int 0x80",
        "    mov eax, 4",
        "    mov ebx, 1",
        "    mov ecx, newline",
        "    mov edx, 1",
        "    int 0x80",
        "    ret"
    ]

    return '\n'.join(asm)


def save_asm(filename, asm_code):
    with open(filename, 'w') as f:
        f.write(asm_code)