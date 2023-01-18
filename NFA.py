from ctypes.wintypes import INT
from typing import Callable, Generic, TypeVar
from venv import create
import re
import shlex

S = TypeVar("S")
T = TypeVar("T")


class NFA(Generic[S]):
    def __init__(self):
        self.numberOfStates = 0
        self.transitions = {}  # dictionar tranzitii:{((stare, str):stare)}

    def createState(self) -> int:
        self.numberOfStates = self.numberOfStates + 1
        return self.numberOfStates

    def letter(self, on_chr: str) -> tuple:
        initial = self.createState()
        final = self.createState()

        values = set()
        values.add(final)
        self.transitions.update({(initial, on_chr): values})
        return (initial, final)

    def epsilon(self) -> tuple:
        initial = self.createState()
        return (initial, initial)

    def void(self) -> tuple:
        initial = self.createState()
        final = self.createState()
        return (initial, final)

    def star(self, oldInitial: int, oldFinal: int) -> tuple:
        initial = self.createState()
        final = self.createState()
        values1 = self.transitions.get((oldFinal, "eps"))
        if values1 is None:
            values1 = set()
        values1.add(oldInitial)
        self.transitions.update({(oldFinal, "eps"): values1})
        # self.transitions.update({(oldInitial, "eps"): oldFinal})

        values2 = set()
        values2.add(final)
        self.transitions.update({(initial, "eps"): values2})
        # self.transitions.update({(initial, "eps"): final})

        values3 = self.transitions.get((initial, "eps"))
        if values3 is None:
            values3 = set()
        values3.add(oldInitial)
        self.transitions.update({(initial, "eps"): values3})
        # self.transitions.update({(initial, "eps"): oldInitial})

        values4 = self.transitions.get((oldFinal, "eps"))
        if values4 is None:
            values4 = set()
        values4.add(final)
        self.transitions.update({(oldFinal, "eps"): values4})
        # self.transitions.update({(oldFinal, "eps"): final})
        return (initial, final)

    def concat(self, oldInitial1: int, oldFinal1: int, oldInitial2: int, oldFinal2: int) -> tuple:
        initial = self.createState()
        final = self.createState()

        values1 = set()
        values1.add(oldInitial1)
        self.transitions.update({(initial, "eps"): values1})

        values2 = self.transitions.get((oldFinal1, "eps"))
        if values2 is None:
            values2 = set()
        values2.add(oldInitial2)
        self.transitions.update({(oldFinal1, "eps"): values2})
        # self.transitions.update({(oldFinal1, "eps"): oldInitial2})

        values3 = set()
        values3.add(final)
        self.transitions.update({(oldFinal2, "eps"): values3})
        return (initial, final)

    def union(self, oldInitial1: int, oldFinal1: int, oldInitial2: int, oldFinal2: int) -> tuple:
        initial = self.createState()
        final = self.createState()

        values1 = self.transitions.get((initial, "eps"))
        if values1 is None:
            values1 = set()
        values1.add(oldInitial1)
        self.transitions.update({(initial, "eps"): values1})

        # self.transitions.update({(initial, "eps"): oldInitial1})
        values2 = self.transitions.get((initial, "eps"))
        if values2 is None:
            values2 = set()
        values2.add(oldInitial2)
        self.transitions.update({(initial, "eps"): values2})
        # self.transitions.update({(initial, "eps"): oldInitial2})

        values3 = self.transitions.get((oldFinal1, "eps"))
        if values3 is None:
            values3 = set()
        values3.add(final)
        self.transitions.update({(oldFinal1, "eps"): values3})
        # self.transitions.update({(oldFinal1, "eps"): final})

        values4 = self.transitions.get((oldFinal2, "eps"))
        if values4 is None:
            values4 = set()
        values4.add(final)
        self.transitions.update({(oldFinal2, "eps"): values4})
        # self.transitions.update({(oldFinal2, "eps"): final})
        return (initial, final)

    def createStack(self, prenex: str):
        stack = []
        string3 = r'(?<!("|\').{0,255}) | (?!.*\\1.*)'
        w = prenex
        if prenex.find("'") != -1:
            w = shlex.quote(prenex)
        words = shlex.split(w)

        for i in words:
            if  i[0] == '\'' and i[-1] == '\'':
                iter = i[1:-1]
            else:
                iter = i
            if iter == "UNION":
                stack.append((("UNION", 2), (0, 0), (0, 0)))
            elif iter == "STAR":
                stack.append((("STAR", 1), (0, 0)))
            elif iter == "CONCAT":
                stack.append((("CONCAT", 2), (0, 0), (0, 0)))
            elif iter == "eps":
                stack.append((("eps", 0), (0, 0), (0, 0)))
            elif iter == "void":
                stack.append((("void", 0), (0, 0), (0, 0)))
            else:
                stack.append(((iter, 0), (0, 0), (0, 0)))

            while len(stack) > 0 and stack[-1][0][1] == 0:
                top = stack.pop()
                if top[0][0] == "eps":
                    arg = self.epsilon()
                elif top[0][0] == "void":
                    arg = self.void()
                elif top[0][0] == "STAR":
                    arg = self.star(top[1][0], top[1][1])
                elif top[0][0] == "UNION":
                    arg = self.union(top[1][0], top[1][1], top[2][0], top[2][1])
                elif top[0][0] == "CONCAT":
                    arg = self.concat(top[1][0], top[1][1], top[2][0], top[2][1])
                else:
                    arg = self.letter(top[0][0])
                if len(stack) > 0:
                    snd = stack.pop()

                    if snd[0][0] == "UNION" and snd[0][1] == 2:
                        stack.append((("UNION", 1), (arg[0], arg[1]), (0, 0)))
                    if snd[0][0] == "UNION" and snd[0][1] == 1:
                        stack.append((("UNION", 0), (snd[1][0], snd[1][1]), (arg[0], arg[1])))
                    elif snd[0][0] == "STAR":
                        stack.append((("STAR", 0), (arg[0], arg[1])))
                    elif snd[0][0] == "CONCAT" and snd[0][1] == 2:
                        stack.append((("CONCAT", 1), (arg[0], arg[1]), (0, 0)))
                    elif snd[0][0] == "CONCAT" and snd[0][1] == 1:
                        stack.append((("CONCAT", 0), (snd[1][0], snd[1][1]), (arg[0], arg[1])))

    def map(self, f: Callable[[S], T]) -> 'NFA[T]':
        pass

    def next(self, from_state: S, on_chr: str) -> 'set[S]':
        return self.transitions.get((S, str))

    def getStates(self) -> 'set[S]':
        pass

    def rec_accepts(self, current: S, word: str) -> bool:
        if (len(word) == 0 or word == "eps") and self.isFinal(current):
            return True
        else:
            tupl = [item for item in self.transitions.keys() if item[0] == current]

            for iter in tupl:
                nextt = self.transitions.get(iter)
                for i in nextt:
                    ok = False
                    if iter[1] == "eps":
                        ok = self.rec_accepts(i, word)
                    elif iter[1] == word[:1]:
                        ok = self.rec_accepts(i, word[1:])
                    if ok == True:
                        return True
            return False

    def accepts(self, str: str) -> bool:

        final = self.numberOfStates
        if final == 1:  # cazul pt epsilon
            return True
        initial = self.numberOfStates - 1
        return self.rec_accepts(initial, str)

    def isFinal(self, state: S) -> bool:
        if state == self.numberOfStates:
            return True
        else:
            return False

    @staticmethod
    def fromPrenex(str: str) -> 'NFA[int]':
        nfa = NFA[int]()
        nfa.createStack(str)
        return nfa
