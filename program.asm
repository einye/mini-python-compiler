section .data
    newline db 10
    buf resb 12
    true_str db 'True', 10, 0
    false_str db 'False', 10, 0
    x dd 0

section .text
    global _start
_start:
    mov eax, 0
    mov [x], eax
    jmp L1
L0:
    mov eax, [x]
    call print_int
    mov eax, [x]
    add eax, 1
    mov ebx, eax
    mov eax, ebx
    mov [x], eax
L1:
    mov eax, [x]
    cmp eax, 3
    setl al
    movzx eax, al
    mov ecx, eax
    cmp ecx, 0
    jne L0
    mov eax, 1
    xor ebx, ebx
    int 0x80

print_int:
    mov ecx, buf + 11
    mov byte [ecx], 0
    dec ecx
    cmp eax, 0
    jge .convert
    neg eax
    mov bl, '-'
    mov [ecx], bl
    dec ecx
.convert:
    xor edx, edx
    mov ebx, 10
.next_digit:
    xor edx, edx
    div ebx
    add dl, '0'
    mov [ecx], dl
    dec ecx
    test eax, eax
    jnz .next_digit
    inc ecx
    mov eax, 4
    mov ebx, 1
    mov edx, buf + 12
    sub edx, ecx
    int 0x80
    mov eax, 4
    mov ebx, 1
    mov ecx, newline
    mov edx, 1
    int 0x80
    ret