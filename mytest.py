#!/usr/bin/env python3
import csv
import io
import json
import os
import re
import subprocess

# /Users/ymy/CS846/sourcecode/gcc/gcc/testsuite
# clang -fmodules -fsyntax-only -Xclang -ast-dump=json pr105148.c


class AnalyzeContext:
    full_name: str
    file_name: str
    id: str
    struct: int = 0

    def __init__(self, full_name: str, file_name: str, id: str) -> None:
        self.full_name = full_name
        self.file_name = file_name
        self.id = id
        self.lines = 0
        self.max_ast_depth = 0
        self.characteristicDict = {}

        self.struct = 0
        self.union = 0
        self.loop = 0
        self.register_op = 0
        self.subscript = 0
        self.ifstmt = 0
        self.pointer_deref = 0
        self.func_invoke = 0
        self.enum_declear = 0
        self.goto = 0
        self.volatile = 0
        self.explicit_type_conversion = 0
        self.asm = 0
        self.func_template = 0
        self.class_template = 0
        self.cpp_new = 0
        self.cpp_inherit = 0

    def analyzePatterns(self):
        proc = subprocess.run(
            ["clang", "-fmodules", "-fsyntax-only",
                "-Xclang", "-ast-dump=json", self.full_name],
            capture_output=True)
        # if proc.returncode != 0:
        #     print("Error")
        #     return
        with open(self.full_name, "rb") as file:
            self.lines = len(file.readlines())
        ast = None
        try:
            ast = json.load(io.BytesIO(proc.stdout))
        except:
            # if clang did not exit properly, json will be broken.
            print("Json parse error.")
            return
        if not isinstance(ast, dict):
            return
        # inFile = False
        if not isinstance(ast.get("inner", None), list):
            return
        self.traverse(ast["inner"])

    def traverse(self, inner: list, inFile: bool = False, depth: int = 1, line_num=None):
        if self.max_ast_depth < depth:
            self.max_ast_depth = depth
        for n in inner:
            if n.get("loc", {}).get("file", None) == self.full_name:
                inFile = True
            if inFile:
                if n.get("loc", {}).get("file", self.full_name) != self.full_name:
                    inFile = False
                    # print("Switched to other file")
                else:
                    self.handleElement(n, depth=depth, line_num=line_num)

    def handleElement(self, n: dict, depth: int, line_num=None):
        line_num = n.get("range", {}).get("begin", {}).get("line", line_num)
        line_num = n.get("loc", {}).get("line", line_num)
        if n.get("kind") == "RecordDecl":  # struct
            print("Find record")
            if n.get("tagUsed") == "union":
                self.union += 1
                self.addCharacteristic(line_num, "union")
            else:
                self.struct += 1
                self.addCharacteristic(line_num, "struct")
        elif n.get("kind") == "WhileStmt":
            print("Find while")
            self.loop += 1
            self.addCharacteristic(line_num, "loop")
        elif n.get("kind") == "ForStmt":
            print("Find for")
            self.loop += 1
            self.addCharacteristic(line_num, "loop")
        elif n.get("kind") == "DoStmt":
            print("Find do-while")
            self.loop += 1
            self.addCharacteristic(line_num, "loop")
        elif n.get("kind") == "ArraySubscriptExpr":
            print("Find subscript")
            self.subscript += 1
            self.addCharacteristic(line_num, "subscript")
        elif n.get("kind") == "IfStmt":
            print("Find ifstmt")
            self.ifstmt += 1
            self.addCharacteristic(line_num, "ifstmt")
        elif n.get("kind") == "UnaryOperator" and n.get("opcode") == "*":
            self.pointer_deref += 1
            self.addCharacteristic(line_num, "pointer_deref")
        # CallExpr -> ImplicitCastExpr -> DeclRefExpr
        # .referencedDecl.kind == "FunctionDecl"
        # .referencedDecl.name == func_name
        elif n.get("kind") == "DeclRefExpr" and n.get("referencedDecl", {}).get("kind") == "FunctionDecl":
            self.func_invoke += 1
            self.addCharacteristic(line_num, "func_invoke")
        elif n.get("kind") == "EnumDecl" or (n.get("kind") == "TypedefDecl" and n.get("ownedTagDecl", {}).get("kind") == "EnumDecl"):
            # include both enum some_enum{}; and typedef enum{} some_enum;
            # TypedefDecl -> ElaboratedType[ownedTagDecl.kind = EnumDecl] -> EnumType
            self.enum_declear += 1
            self.addCharacteristic(line_num, "enum_declear")
        elif n.get("kind") == "GotoStmt":
            self.goto += 1
            self.addCharacteristic(line_num, "goto")
        elif n.get("kind") == "FieldDecl" and "volatile" in n.get("type", {}).get("qualType", ""):
            self.volatile += 1
            self.addCharacteristic(line_num, "volatile")
        elif n.get("kind") == "CStyleCastExpr":
            self.explicit_type_conversion += 1
            self.addCharacteristic(line_num, "explicit_type_conversion")
        elif n.get("kind") == "GCCAsmStmt":
            self.asm += 1
            self.addCharacteristic(line_num, "asm")
        elif n.get("kind") == "FunctionTemplateDecl":
            self.func_template += 1
            self.addCharacteristic(line_num, "func_template")
        elif n.get("kind") == "ClassTemplateDecl":
            self.class_template += 1
            self.addCharacteristic(line_num, "class_template")
        elif n.get("kind") == "CXXNewExpr":
            self.cpp_new += 1
            self.addCharacteristic(line_num, "cpp_new")
        elif n.get("kind") == "CXXRecordDecl" and len(n.get("bases", [])) > 0:
            self.cpp_inherit += 1
            self.addCharacteristic(line_num, "cpp_inherit")
        elif n.get("storageClass") == "register":
            self.register_op += 1
            self.addCharacteristic(line_num, "register_op")
        if isinstance(n.get("inner"), list):
            self.traverse(n["inner"], True, depth=depth+1, line_num=line_num)

    def addCharacteristic(self, line: int | None, ch: str):
        if line == None:
            return
        featureSet = self.characteristicDict.get(line)
        if featureSet == None:
            featureSet = set()
            self.characteristicDict[line] = featureSet
        featureSet.add(ch)

    def __iter__(self):
        return iter([self.full_name, self.file_name, self.id, self.struct, self.union, self.loop, self.register_op, self.subscript, self.ifstmt, self.pointer_deref, self.func_invoke, self.enum_declear, self.goto, self.volatile, self.explicit_type_conversion, self.asm, self.func_template, self.class_template, self.cpp_new, self.cpp_inherit, self.lines, self.max_ast_depth, self.max_features_in_line()])

    def max_features_in_line(self) -> int:
        result = 0
        for k in self.characteristicDict:
            currLen = len(self.characteristicDict[k])
            if currLen > result:
                result = currLen
        return result

# AnalyzeContext(
#     "/Users/ymy/CS846/sourcecode/gcc/gcc/testsuite/gcc.dg/pr94600-6.c",
#     "pr94600-6.c",
#     "94600").analyzePatterns()


def analyze_codes(path: str):
    # g = os.walk("/Users/ymy/CS846/sourcecode/gcc/gcc/testsuite")
    g = os.walk(path)
    # pat = re.compile(r"pr(\d+).*\.c[c|pp]?$", re.I)
    pat = re.compile(r"\.(?:c[c|pp]?|h)$", re.I)
    result_list = []

    for path, dir_list, file_list in g:
        for file_name in file_list:
            match = pat.search(file_name)
            if match:
                print("Analyzing " + path + "/" + file_name)
                ctx = AnalyzeContext(path + "/" + file_name,
                                     file_name, "")
                ctx.analyzePatterns()
                result_list.append(ctx)
    save_path = 'stat public repos.csv'
    saveResults(result_list, save_path)


def analyze_generated():
    iterationCount = 500
    flag_list = [
        [],
        # ["--lang-cpp"],
        # ["--no-pointers"],
        # ["--no-jumps"],
    ]
    base_folder = "/home/shabivps/source/repo/clang-learning/generated-programs"

    result_list = []
    id = 0
    for flags in flag_list:
        for i in range(id, id + iterationCount):
            file_name = str(i) + ".c"
            full_name = base_folder + "/" + file_name
            proc = subprocess.run(
                ["csmith", "--output", full_name] + flags,
                capture_output=True)
            if proc.returncode != 0:
                print("Error")
                return
            ctx = AnalyzeContext(full_name,
                                 file_name, str(i))
            ctx.analyzePatterns()
            result_list.append(ctx)
        id += iterationCount
    save_path = 'stat generated.csv'
    saveResults(result_list, save_path)


def saveResults(result_list, save_path):
    with open(save_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for result in result_list:
            writer.writerow(list(result))


analyze_codes("/home/shabivps/source/repo/fall22-researched-repos")
