from typing import Callable, Generic, TypeVar

from src.NFA import NFA

S = TypeVar("S")
T = TypeVar("T")


class DFA(Generic[S]):
    def __init__(self):
        self.numberOfStates = 0
        self.arce = {}
        self.epsilonClosure = {}
        self.states = []
        self.final = 0
        self.initial = []
        self.newstates = {}
        self.contor = 0

    def DFSUtil(self, v, visited, nfa: NFA[S]):
        visited.add(v)

        if nfa.transitions.get((v, "eps")) is None:
            return
        for neighbour in nfa.transitions.get((v, "eps")):
            if neighbour not in visited:
                self.DFSUtil(neighbour, visited, nfa)
            values = self.epsilonClosure.get(v)
            values.update(self.epsilonClosure.get(neighbour))
            self.epsilonClosure.update({v: values})

    def DFS(self, nfa: NFA[S]):
        visited = set()
        for i in range(1, nfa.numberOfStates + 1):
            hei = set()
            hei.add(i)
            self.epsilonClosure.update({i: hei})
        for i in range(1, nfa.numberOfStates + 1):
            self.DFSUtil(i, visited, nfa)

    def nfaToDfa(self, nfa: NFA[S]):
        self.DFS(nfa)
        if nfa.numberOfStates == 1:
            initial = nfa.numberOfStates
        else:
            initial = nfa.numberOfStates - 1
        self.final = nfa.numberOfStates
        allTransition = set()
        for i in nfa.transitions.keys():
            if i[1] != "eps":
                allTransition.add(i[1])

        queue = list()
        queue.append(self.epsilonClosure.get(initial))

        while queue:
            state = queue.pop(0)
            # iau toate tranzitiile care pleaca din starea state
            for i in allTransition:
                s = set()
                for iter in state:
                    if nfa.transitions.get((iter, i)) is None:
                        continue
                    for j in nfa.transitions.get((iter, i)):
                        s.update(self.epsilonClosure.get(j))
                if s not in self.states:
                    queue.append(s)
                    self.states.append(s)

                begin = 0
                end = 0
                for key, value in self.newstates.items():
                    if value == state:
                        begin = key
                if begin == 0:
                    self.contor = self.contor + 1
                    begin = self.contor
                    self.newstates.update({self.contor: state})
                for key, value in self.newstates.items():
                    if value == s:
                        end = key
                if end == 0 and len(s) != 0:
                    self.contor = self.contor + 1
                    end = self.contor
                    self.newstates.update({self.contor: s})

                if len(s) != 0:
                    self.arce.update({(begin, i): end})

    def map(self, f: Callable[[S], T]) -> 'DFA[T]':
        pass

    def next(self, from_state: S, on_chr: str) -> S:
        return self.arce.get(from_state, on_chr)

    def getStates(self) -> 'set[S]':
        pass

    def rec_accepts(self, current: S, word: str) -> bool:
        if (len(word) == 0 or word == "eps") and (self.isFinal(current)):
            return True
        else:

            tupl = [item for item in self.arce.keys() if item[0] == current]
            for iter in tupl:
                nextt = self.arce.get(iter)
                ok = False
                if iter[1] == word[:1]:
                    ok = self.rec_accepts(nextt, word[1:])
                if ok == True:
                    return True
            return False

    def accepts(self, str: str) -> bool:
        initial = 1
        return self.rec_accepts(initial, str)

    def isFinal(self, state: S) -> bool:
        if self.newstates.get(state) is None:
            if self.final == state:
                return True
            else:
                return False
        if self.final in self.newstates.get(state):
            return True
        return False

    @staticmethod
    def fromPrenex(str: str) -> 'DFA[int]':
        nfa = NFA.fromPrenex(str)
        dfa = DFA[int]()

        dfa.nfaToDfa(nfa)
        return dfa
