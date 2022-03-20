import pprint
from multipledispatch import dispatch

class Automaton:
    def __init__(self, *args):
        if not len(args):
            self.__automaton = {} 
            self.__ini = set() #initial states
            self.__fin = set() #final states 
        else: #copy constructor
            self.__automaton = args[0].automaton
            self.__ini = args[0].initial_states
            self.__fin = args[0].final_states
        self.__current_label = 0 #label of the new state
        self.__sigma = set() #alphabet
        

    @dispatch(bool,bool)
    def new_state(self, ini, fin):
        if ini: self.__ini.add(self.__current_label)
        if fin: self.__fin.add(self.__current_label)
        self.__automaton[self.__current_label] = {}
        self.__current_label += 1
    

    @dispatch(int,list,int)
    def set_transition(self, state1, links, state2):
        if state1 not in self.__automaton:
            raise noState("state1 not exists")
        if state2 not in self.__automaton:
            raise noState("state2 not exists")
        if not all(type(link)==str for link in links):
            raise invalidList("Only string list")
        if not all(len(link)==1 for link in links):
            raise invalidString("String length must be one")
        temp = self.__automaton[state1]
        for link in links:
            if link not in temp:
                self.__sigma.add(link)
                s = set()
                s.add(state2)
                temp[link] = s
            else: temp[link].add(state2)
    

    @dispatch(int,str,int)
    def set_transition(self, state1, link, state2):
        if state1 not in self.__automaton:
            raise noState("state1 not exists")
        if state2 not in self.__automaton:
            raise noState("state2 not exists")
        if  not len(link)==1:
            raise invalidString("String length must be one")
        temp = self.__automaton[state1]
        if link not in temp:
            self.__sigma.add(link)
            s = set()
            s.add(state2)
            temp[link] = s
        else: temp[link].add(state2)


    @dispatch(str)
    def check_string(self, s): 
        def check(self, s, states, index): #DFS
            if index >= len(s):
                for state in states:
                    if state in self.__fin: return True
                return False
            for state in states:
                if s[index] in self.__automaton[state]:
                    if check(self, s, self.__automaton[state][s[index]], index+1): return True
            return False
  
        return check(self, s, self.__ini, 0)    


    def reverse(self):
        reverse = {}
        for state in self.__automaton:
            temp = self.__automaton[state]
            for link in temp:
                temp2 = temp[link] #set
                for state2 in temp2:
                    if state2 not in reverse:
                        reverse[state2] = {} #new state of reverse automaton
                    if link not in reverse[state2]:
                        s = set()
                        s.add(state)
                        reverse[state2][link]=s
                    else: reverse[state2][link].add(state)

        self.__ini,self.__fin = self.__fin,self.__ini #the initial states become final states and vice versa
        self.__automaton = reverse
        

    def subset_construction(self):
        if not self.__automaton: return

        self.__current_label = 0
        fin = set() #set of new final states
        dfa = {}
        processed_states = [] #states already processed
        queue = [self.__ini] #queue of states to process (each state is a set of states of nfa)
        while queue:
            dfa[self.__current_label] = {} #new state of DFA
            for link in self.__sigma:
                s = set()
                for state in queue[0]:
                    if state in self.__automaton:
                        temp = self.__automaton[state] ##
                        if link in temp: s |= temp[link]
                    if state in self.__fin: fin.add(self.__current_label) #if at least one state in the set is final for NFA --> the new state is final for DFA
                if s:
                    if (s not in processed_states) and (s not in queue): queue.append(s)
                    dfa[self.__current_label][link] = s
            processed_states.append(queue.pop(0))
            self.__current_label += 1
    
        for state in dfa: #renaming states
            for link in dfa[state]:
                s = set()
                s.add(processed_states.index(dfa[state][link]))
                dfa[state][link] =  s

        self.__ini = set([0]) #only one initial state (state 0)
        self.__fin = fin
        self.__automaton = dfa


    def minimization(self): #brzozowski algorithm
        self.reverse()
        self.subset_construction()
        self.reverse()
        self.subset_construction()
    
    
    def print(self):
        print("\nAutomaton")
        pprint.pprint(self.__automaton)
        if self.__ini:
            print("\nInitial states: ",self.__ini)
        if self.__fin:
            print("Final states: ",self.__fin)


    @property
    def automaton(self):
        return self.__automaton.copy() #defensive copying


    @property
    def initial_states(self):
        return self.__ini.copy() #defensive copying


    @property
    def final_states(self):
        return self.__fin.copy() #defensive copying


    def __str__(self):
        return str(self.__automaton)