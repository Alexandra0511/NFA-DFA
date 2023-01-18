from __future__ import annotations
from builtins import print
from typing import Type
from src.Regex import Character, Operator


class Parser:
    # This function should:
    # -> Classify input as either character(or string) or operator
    # -> Convert special inputs like [0-9] to their correct form
    # -> Convert escaped characters
    # You can use Character and Operator defined in Regex.py

    def intervalReplace(self, a: str) -> str:
        newstr = "("
        for i in range(ord(a[1]), ord(a[3])):
            newstr += chr(i)
            newstr += "|"
        newstr += chr(ord(a[3]))
        return newstr + ")"

    def isTerminal(self, a: str) -> bool:
        if a.isalpha() or a.isdigit():
            return True
        return False

    @staticmethod
    def preprocess(regex: str) -> str:
        parser = Parser()
        # Convert special inputs like [0-9] to their correct form
        if regex == "eps":
            return regex
        s = [pos for pos, char in enumerate(regex) if char == '[']
        newstr = regex
        for i in s:
            newstr = newstr.replace(regex[i:i + 5], parser.intervalReplace(regex[i:i + 5]))
        indices = [i for i, c in enumerate(newstr) if c == '?']
        if len(indices) != 0:
            app = indices[0]
        i = 0

        while i < len(indices):
            if newstr[app - 1] != ')':
                ch = newstr[app - 1]
                newch = "(" + ch + '|' + '?' + ")"
                newstr = newstr.replace(newstr[app - 1:app + 1], newch)
            else:
                found = newstr[:app].rfind('(')
                newch = "(" + newstr[found:app] + '|' + '?' + ")"
                newstr = newstr.replace(newstr[found:app + 1], newch)
            x = app + 3
            app = newstr.find('?', x)
            i = i + 1

        i = 0
        while i < len(newstr):
            if newstr[i] == '+':
                if newstr[i - 1] != ')':
                    ch = newstr[i - 1]
                    newch = "(" + ch + ch + '*' + ")"
                    newstr = newstr.replace(newstr[i - 1:i + 1], newch)
                else:
                    found = newstr[:i].rfind('(')
                    newch = "(" + newstr[found:i] + newstr[found:i] + '*' + ")"
                    newstr = newstr.replace(newstr[found:i + 1], newch)
            i = i + 1
        i = 0
        ns = ""
        while i < len(newstr) - 1:
            if newstr[i] == '\'':
                if i + 3 < len(newstr):
                    if newstr[i + 3] != '.' and newstr[i + 3] != '|' and newstr[i + 3] != '*' and newstr[i + 3] != ')':
                        ns += '\'' + newstr[i + 1] + '\''
                        ns += "."
                    else:
                        ns += '\'' + newstr[i + 1] + '\''
                else:
                    ns += '\'' + newstr[i + 1]
                i = i + 3

            else:
                ns += newstr[i]

                if (parser.isTerminal(newstr[i]) and parser.isTerminal(newstr[i + 1])) or (
                        parser.isTerminal(newstr[i]) and newstr[i + 1] == '(') or (
                        newstr[i] == ')' and parser.isTerminal(newstr[i + 1])) or (
                        newstr[i] == ')' and newstr[i + 1] == '(') or (
                        newstr[i] == '*' and newstr[i + 1] == '(') or (
                        newstr[i] == '*' and parser.isTerminal(newstr[i + 1]) or (
                        newstr[i] == '\'' and newstr[i + 1] == '\'') or (
                                newstr[i] == '\'' and newstr[i + 1] == '(') or (
                                parser.isTerminal(newstr[i]) and newstr[i + 1] == '\'') or (
                                newstr[i] == '?' and parser.isTerminal(newstr[i + 1]))):
                    ns += "."

                i = i + 1
        ns += newstr[len(newstr) - 1]
        return ns

    def prior(self, oper: str) -> int:
        if oper == "|":
            return 1
        elif oper == ".":
            return 2
        elif oper == "*":
            return 3
        else:
            return 0

    def convertOp(self, op: str) -> str:
        if op == "*":
            return "STAR"
        elif op == "|":
            return "UNION"
        elif op == ".":
            return "CONCAT"
        else:
            return "CEVA"

    def rex(self, regex: str) -> []:
        res = list()
        stack = list()
        if regex == "eps":
            l = ["eps"]
            return l

        l = list(regex[:: -1])

        for i in range(0, len(l)):
            if l[i] == ')':
                l[i] = '('
            elif l[i] == '(':
                l[i] = ')'

        reversed = "".join(l)

        reversed = "(" + reversed + ")"

        i = 0
        while i < len(reversed):
            c = reversed[i]

            if c == '\'':
                res.append('\'' + reversed[i + 1] + '\'')
                found = reversed.find('\'', i + 1)
                reversed = reversed.replace(reversed[i:found + 1], "")
                continue
            if c.isalpha() or c.isdigit() or c == '?':
                res.append(c)
            elif c == '(':
                stack.append(c)
            elif c == ')':
                while stack[-1] != '(':
                    res.append(self.convertOp(stack[-1]))
                    stack.pop()
                stack.pop()
            else:
                if len(stack) != 0:
                    while ((self.prior(c) < self.prior(stack[-1]))
                           or (self.prior(c) <= self.prior(stack[-1]) and c == '*')):
                        res.append(self.convertOp(stack[-1]))
                        stack.pop()
                    stack.append(c)
            i = i + 1
        while len(stack) != 0:
            res.append(self.convertOp(stack.pop()))
        return res

    # This function should construct a prenex expression out of a normal one.
    @staticmethod
    def toPrenex(s: str) -> str:
        parser = Parser()

        string = parser.preprocess(s)
        l = parser.rex(string)
        final = ""

        for i in range(0, len(l)):
            final += l[len(l) - 1 - i]
            final += " "
        questfound = final.find('?')
        if questfound != -1:
            final = final.replace(final[questfound], "eps")
        print(final)
        return final
