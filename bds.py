# n = int(input())
# if n < 1:
#     exit(1)
#
# arr = list(map(int, input().split()))
#
# if not arr:
#     print(0)
#     exit(1)
#
# transformed = ['#']
# for num in arr:
#     transformed.append(num)
#     transformed.append('#')
#
# length = len(transformed)
# palRad = [0] * length
# center = right = 0
#
# for i in range(length):
#     mirror = 2 * center - i
#
#     if i < right:
#         palRad[i] = min(right - i, palRad[mirror])
#
#     while (i - palRad[i] - 1 >= 0 and i + palRad[i] + 1 < length  and transformed[palRad[i] + i + 1] == transformed[i - palRad[i] - 1]):
#         palRad[i] += 1
#
#     if i + palRad[i] > right:
#         center = i
#         right = i + palRad[i]
#
# maxLen = max(palRad)
#
# if maxLen > 1:
#     print(maxLen)
# else:
#     print(0)


# def calculate(s: str) -> int:
#     stack = []
#     num = 0
#     sign = 1
#     result = 0
#
#     for char in s:
#         if char.isdigit():
#             num = num * 10 + int(char)
#         elif char == '+':
#             result += sign * num
#             num = 0
#             sign = 1
#         elif char == '-':
#             result += sign * num
#             num = 0
#             sign = -1
#         elif char == '(':
#             stack.append(result)
#             stack.append(sign)
#             result = 0
#             sign = 1
#         elif char == ')':
#             result += sign * num
#             num = 0
#             result *= stack.pop()  # знак перед скобкой
#             result += stack.pop()  # предыдущий результат
#
#     return result + sign * num


# def calculate(s: str) -> int:
#     stack = []
#     i = 0
#     num = 0
#     result = 0
#     sign = 1
#
#     last_token_was_op = True
#
#     while i < len(s):
#         ch = s[i]
#
#         if ch == ' ':
#             i += 1
#             continue
#
#         elif ch in '+-':
#             current_sign = 1 if ch == '+' else -1
#             i += 1
#
#             while i < len(s):
#                 if s[i] == ' ':
#                     i += 1
#                     continue
#                 if s[i] == '+':
#                     i += 1
#                 elif s[i] == '-':
#                     current_sign *= -1
#                     i += 1
#                 else:
#                     break
#
#             if last_token_was_op:
#                 sign *= current_sign
#             else:
#                 result += sign * num
#                 num = 0
#                 sign = current_sign
#                 last_token_was_op = True
#
#         elif ch.isdigit():
#             num = 0
#             while i < len(s) and s[i].isdigit():
#                 num = num * 10 + int(s[i])
#                 i += 1
#             last_token_was_op = False
#
#         elif ch == '(':
#             stack.append(result)
#             stack.append(sign)
#             result = 0
#             sign = 1
#             i += 1
#             last_token_was_op = True
#
#         elif ch == ')':
#             result += sign * num
#             num = 0
#             result *= stack.pop()  # знак перед скобкой
#             result += stack.pop()  # предыдущий результат
#             i += 1
#             last_token_was_op = False
#
#     result += sign * num
#     return result

# def calculate(expression: str) -> int:
#
# expression = input()
#
# index = 0
# total = 0
# operator = 1
# contextStack = []
# expect = True
#
# while index < len(expression):
#     current = expression[index]
#
#     if current == ' ':
#         index += 1
#         continue
#
#     elif current.isdigit():
#         value = 0
#         while index < len(expression) and expression[index].isdigit():
#             value = value * 10 + int(expression[index])
#             index += 1
#         total += operator * value
#         expect = False
#         continue
#
#     elif current in '+-':
#         signFlip = 1 if current == '+' else -1
#         index += 1
#         while index < len(expression):
#             if expression[index] == ' ':
#                 index += 1
#                 continue
#             elif expression[index] == '+':
#                 index += 1
#             elif expression[index] == '-':
#                 signFlip *= -1
#                 index += 1
#             else:
#                 break
#
#         if expect:
#             operator *= signFlip
#         else:
#             operator = signFlip
#             expect = True
#
#     elif current == ')':
#         total *= contextStack.pop()
#         total += contextStack.pop()
#         index += 1
#         expect = False
#
#     elif current == '(':
#         contextStack.append(total)
#         contextStack.append(operator)
#         expect = True
#         operator = 1
#         index += 1
#         total = 0
#
# print(total)


# print(calculate("(1 + -2) + (3-4 - (5-6 - 7)) +8"))
# print(calculate("-123 + 23"))
# print(calculate("-((5 -2) - (3) +2) + 1"))
# print(calculate("--42"))  # 3
# # print(calculate("(1+(4+5+2)-3)+(6+8)"))  # 23
# # # Примеры использования
# # print(calculate("-(1 + -2) + (3-4 - (5-6 - 7)) +8"))  # 14
# # print(calculate("2-1 + 2"))  # 3
# # print(calculate("(1+(4+5+2)-3)+(6+8)"))  # 23
# print(calculate("42"))        # 42
# print(calculate("-42"))       # -42
# print(calculate("--42"))      # 42
# print(calculate("-(-42)"))    # 42
# print(calculate("1 + --2"))   # 3
# print(calculate("-(1 + 2)"))
#
#
# def calculate(s: str) -> int:
#
import sys
from collections import deque


def evaluate_expression(s: str) -> int:
    # Удаляем все пробелы
    s = s.replace(" ", "")

    # Преобразуем выражение в токены с учетом унарных операторов
    tokens = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isdigit():
            num = 0
            while i < n and s[i].isdigit():
                num = num * 10 + int(s[i])
                i += 1
            tokens.append(num)
        else:
            # Обработка унарных минусов
            if c == '-' and (i == 0 or s[i - 1] == '(' or s[i - 1] in '+-'):
                tokens.append('neg')  # Специальный маркер для унарного минуса
            else:
                tokens.append(c)
            i += 1

    # Преобразование в обратную польскую нотацию
    output = []
    operators = []

    for token in tokens:
        if isinstance(token, int):
            output.append(token)
        elif token == 'neg':
            operators.append(token)
        elif token in '+-':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            operators.append(token)
        elif token == '(':
            operators.append(token)
        elif token == ')':
            while operators[-1] != '(':
                output.append(operators.pop())
            operators.pop()  # Удаляем '('

    while operators:
        output.append(operators.pop())

    # Вычисление ОПН
    stack = []
    for token in output:
        if isinstance(token, int):
            stack.append(token)
        elif token == 'neg':
            stack.append(-stack.pop())
        else:
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)

    return stack[0] if stack else 0


# Чтение ввода и вывод результата
s = sys.stdin.read().strip()
print(evaluate_expression(s))
#
# def calculate(math_str: str) -> int:
#     # Удаляем все пробелы из строки
#     clean_str = math_str.translate(str.maketrans('', '', ' '))
#
#     # Конвертируем инфиксную запись в обратную польскую нотацию
#     def convert_to_rpn(math_expr: str) -> list:
#         rpn_output = []
#         op_stack = []
#         pos = 0
#         length = len(math_expr)
#
#         while pos < length:
#             current_char = math_expr[pos]
#
#             if current_char.isdigit():
#                 value = 0
#                 while pos < length and math_expr[pos].isdigit():
#                     value = value * 10 + int(math_expr[pos])
#                     pos += 1
#                 rpn_output.append(value)
#                 continue
#
#             elif current_char in '+-':
#                 # Обрабатываем унарные операторы
#                 if (current_char == '-' and
#                         (pos == 0 or math_expr[pos - 1] == '(' or math_expr[pos - 1] in '+-')):
#                     rpn_output.append(0)
#                     op_stack.append('~')  # Используем ~ для унарного минуса
#                 else:
#                     # Обрабатываем бинарные операторы
#                     while op_stack and op_stack[-1] != '(':
#                         rpn_output.append(op_stack.pop())
#                     op_stack.append(current_char)
#                 pos += 1
#
#             elif current_char == '(':
#                 op_stack.append(current_char)
#                 pos += 1
#
#             elif current_char == ')':
#                 while op_stack and op_stack[-1] != '(':
#                     rpn_output.append(op_stack.pop())
#                 op_stack.pop()  # Удаляем '('
#                 pos += 1
#
#         # Добавляем оставшиеся операторы
#         rpn_output.extend(reversed(op_stack))
#         return rpn_output
#
#     # Вычисляем выражение в RPN-формате
#     def evaluate_rpn(rpn_tokens: list) -> int:
#         calc_stack = []
#
#         for element in rpn_tokens:
#             if isinstance(element, int):
#                 calc_stack.append(element)
#             else:
#                 if element == '~':  # Унарный минус
#                     calc_stack.append(-calc_stack.pop())
#                 else:
#                     right = calc_stack.pop()
#                     left = calc_stack.pop()
#                     if element == '+':
#                         calc_stack.append(left + right)
#                     elif element == '-':
#                         calc_stack.append(left - right)
#
#         return calc_stack[0] if calc_stack else 0
#
#     # Основной поток выполнения
#     rpn_expression = convert_to_rpn(clean_str)
#     return evaluate_rpn(rpn_expression)


# # Тестовые случаи
# print(compute_expression("--42"))  # 42
# print(compute_expression("- (3 + 4)"))  # -7
# print(compute_expression("1 - (-2)"))  # 3
# print(compute_expression("+-42"))  # -42
# print(compute_expression("(-5)"))  # -5
#
#
# def calculate(math_str: str) -> int:
#     # Удаляем все пробелы из строки
#     clean_str = math_str.translate(str.maketrans('', '', ' '))
#
#     # Конвертируем инфиксную запись в обратную польскую нотацию
#     def convert_to_rpn(math_expr: str) -> list:
#         rpn_output = []
#         op_stack = []
#         pos = 0
#         length = len(math_expr)
#
#         while pos < length:
#             current_char = math_expr[pos]
#
#             if current_char.isdigit():
#                 value = 0
#                 while pos < length and math_expr[pos].isdigit():
#                     value = value * 10 + int(math_expr[pos])
#                     pos += 1
#                 rpn_output.append(value)
#                 continue
#
#             elif current_char in '+-':
#                 # Обрабатываем унарные операторы
#                 if (current_char == '-' and
#                         (pos == 0 or math_expr[pos - 1] == '(' or math_expr[pos - 1] in '+-')):
#                     rpn_output.append(0)
#                     op_stack.append('~')  # Используем ~ для унарного минуса
#                 else:
#                     # Обрабатываем бинарные операторы
#                     while op_stack and op_stack[-1] != '(':
#                         rpn_output.append(op_stack.pop())
#                     op_stack.append(current_char)
#                 pos += 1
#
#             elif current_char == '(':
#                 op_stack.append(current_char)
#                 pos += 1
#
#             elif current_char == ')':
#                 while op_stack and op_stack[-1] != '(':
#                     rpn_output.append(op_stack.pop())
#                 op_stack.pop()  # Удаляем '('
#                 pos += 1
#
#         # Добавляем оставшиеся операторы
#         rpn_output.extend(reversed(op_stack))
#         return rpn_output
#
#     # Вычисляем выражение в RPN-формате
#     def evaluate_rpn(rpn_tokens: list) -> int:
#         calc_stack = []
#
#         for element in rpn_tokens:
#             if isinstance(element, int):
#                 calc_stack.append(element)
#             else:
#                 if element == '~':  # Унарный минус
#                     calc_stack.append(-calc_stack.pop())
#                 else:
#                     right = calc_stack.pop()
#                     left = calc_stack.pop()
#                     if element == '+':
#                         calc_stack.append(left + right)
#                     elif element == '-':
#                         calc_stack.append(left - right)
#
#         return calc_stack[0] if calc_stack else 0
#
#     # Основной поток выполнения
#     rpn_expression = convert_to_rpn(clean_str)
#     return evaluate_rpn(rpn_expression)
#
# # Тесты
# print(calculate("--42"))  # 42 (теперь правильно)
# print(calculate("- (3 + 4)"))  # -7
# print(calculate("1 - (-2)"))  # 3
# print(calculate("+-42"))  # -42
# print(calculate("(-5)"))  # -5
#
#
# # Тесты
# print(calculate("1 + 1"))  # 2
# print(calculate("2-1 + 2"))  # 3
# print(calculate("(1+(4+5+2)-3)+(6+8)"))  # 23
# print(calculate("- (3 + 4)"))  # -7
# print(calculate("1 - (-2)"))  # 3
# print(calculate("2147483647 + 1"))  # 2147483648
#
# print(calculate("(1 + -2) + (3-4 - (5-6 - 7)) +8"))
# print(calculate("-123 + 23"))
# print(calculate("-((5 -2) - (3) +2) + 1"))
# print(calculate("--42"))  # 3
# print(calculate("(1+(4+5+2)-3)+(6+8)"))  # 23
# # Примеры использования
# print(calculate("-(1 + -2) + (3-4 - (5-6 - 7)) +8"))  # 14
# print(calculate("2-1 + 2"))  # 3
# print(calculate("(1+(4+5+2)-3)+(6+8)"))  # 23
# print(calculate("42"))        # 42
# print(calculate("-42"))       # -42
# print(calculate("--42"))      # 42
# print(calculate("-(-42)"))    # 42
# print(calculate("1 + --2"))   # 3
# print(calculate("-(1 + 2)"))