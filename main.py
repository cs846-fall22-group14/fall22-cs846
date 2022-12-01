# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import xlsxwriter
import os

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

def program_extractor(worksheet, file, line_no):

    c_file = False
    array_def = False
    use_struct = False
    use_macro = False
    use_loop = False
    use_cond = False
    use_pointer = False
    use_memalloc = False
    use_func = False
    use_goto = False
    use_volatile = False
    use_union = False
    use_asm = False

    file1 = open(file, 'r')
    Lines = file1.readlines()
    count = 0
    if (file.endswith('.c')):
        c_file = True
    for line in Lines:
        if '[]' in line:
            array_def = True
        if 'struct' in line:
            use_struct = True
        if '#define' in line:
            use_macro = True
        if 'for' in line:
            use_loop = True
        if 'if' in line:
            use_cond = True
        if '*' or '&' in line:
            use_pointer = True
        if 'malloc' in line:
            use_memalloc = True
        if '()' in line:
            use_func = True
        if 'goto' in line:
            use_goto = True
        if 'volatile' in line:
            use_volatile = True
        if 'union' in line:
            use_union = True
        if 'asm' in line:
            use_asm = True


    worksheet.write('A' + line_no, file)
    if c_file:
        worksheet.write('B'+line_no, 'y')
    if array_def:
        worksheet.write('C'+line_no, 'y')
    if use_struct:
        worksheet.write('D'+line_no, 'y')
    if use_macro:
        worksheet.write('E'+line_no, 'y')
    if use_loop:
        worksheet.write('F'+line_no, 'y')
    if use_cond:
        worksheet.write('G'+line_no, 'y')
    if use_pointer:
        worksheet.write('H'+line_no, 'y')
    if use_memalloc:
        worksheet.write('I'+line_no, 'y')
    if use_func:
        worksheet.write('J'+line_no, 'y')
    if use_goto:
        worksheet.write('K'+line_no, 'y')
    if use_volatile:
        worksheet.write('L'+line_no, 'y')
    if use_union:
        worksheet.write('M'+line_no, 'y')
    if use_asm:
        worksheet.write('N'+line_no, 'y')



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    workbook = xlsxwriter.Workbook('analysis.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'id')
    worksheet.write('B1', 'Language')
    worksheet.write('C1', 'Array_def')
    worksheet.write('D1', 'Structure')
    worksheet.write('E1', 'Macro')
    worksheet.write('F1', 'Loop')
    worksheet.write('G1', 'Condition')
    worksheet.write('H1', 'Pointer')
    worksheet.write('I1', 'Memory allocation')
    worksheet.write('J1', 'Function')
    worksheet.write('K1', 'Goto')
    worksheet.write('L1', 'Volatile')
    worksheet.write('M1', 'Union')
    worksheet.write('N1', 'Asm')
    i = 1

    for file in os.listdir(os.getcwd()):
        program_extractor(worksheet, file, i)
        i += 1
    workbook.close()

