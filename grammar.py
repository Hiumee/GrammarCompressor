debug_print = print
debug_print = lambda *args, **kwargs: None  # Disable debug printing

class Grammar:
    def __init__(self, starting_symbol=None):
        self.rules = {}
        self.level = 0
        
    def set_starting_symbol(self, starting_symbol):
        self.starting_symbol = starting_symbol

    def add_rule(self, non_terminal, production):
        if non_terminal not in self.rules:
            self.rules[non_terminal] = []
        self.rules[non_terminal].append(production)

    def get_rules(self, non_terminal):
        return self.rules.get(non_terminal, [])

    def __str__(self):
        result = []
        for non_terminal, productions in self.rules.items():
            result.append(f"{non_terminal} -> {' | '.join([str(x) for x in productions])}")
        return "\n".join(result)
    
    def parse(self, input_string):
        debug_print(f"{'  '*self.level}Starting parse with input: {input_string}")
        success, remaining, steps = self.starting_symbol.parse(self, input_string)
        if success and not remaining:
            return True, steps
        return False, steps
    
    def expand(self, compressed):
        return self.starting_symbol.expand(self, compressed)
    
class Symbol:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Symbol({self.name})"

    def __repr__(self):
        return f"Symbol({self.name})"
    
    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def parse(self, g, input_string):
        g.level += 1
        debug_print(f"{'  '*g.level}Parsing Symbol: {self.name} in {input_string}")
        rules = g.get_rules(self)
        for index, rule in enumerate(rules):
            debug_print(f"{'  '*g.level}Trying rule: {rule}")
            success, remaining, steps = rule.parse(g, input_string)
            if success:
                g.level -= 1
                return True, remaining, [(self, index, len(rules)), [steps]]
        g.level -= 1
        return False, input_string, []
    
    def expand(self, g, compressed):
        number_of_choices = len(g.get_rules(self))
        if number_of_choices == 0:
            raise ValueError(f"No rules found for symbol {self.name}")
        if number_of_choices == 1:
            return g.get_rules(self)[0].expand(g, compressed)
        
        bit_length = number_of_choices.bit_length()
        index = int(compressed[:bit_length], 2)
        compressed = compressed[bit_length:]
        
        return g.get_rules(self)[index].expand(g, compressed)
    
class Composition:
    def __init__(self, *symbols):
        self.symbols = symbols

    def __str__(self):
        return f"Composition({', '.join(map(str, self.symbols))})"

    def __repr__(self):
        return f"Composition({', '.join(map(repr, self.symbols))})"
    
    def __eq__(self, other):
        return isinstance(other, Composition) and self.symbols == other.symbols
    
    def __hash__(self):
        return hash(tuple(self.symbols))
    
    def parse(self, g, input_string):
        g.level += 1
        debug_print(f"{'  '*g.level}Parsing Composition: {self} in {input_string}")
        remaining = input_string
        all_steps = []
        for index, symbol in enumerate(self.symbols):
            debug_print(f"{'  '*g.level}Parsing symbol: {symbol}")
            success, remaining, steps = symbol.parse(g, remaining)
            if not success:
                g.level -= 1
                return False, input_string, []
            all_steps.append(steps)
        g.level -= 1
        return True, remaining, [(self, 0, 1), all_steps]
    
    def expand(self, g, compressed):
        full_result = ""
        for symbol in self.symbols:
            result, compressed = symbol.expand(g, compressed)
            full_result += result
        return full_result, compressed
    
class Literal:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Literal({self.value})"

    def __repr__(self):
        return f"Literal({self.value})"
    
    def __eq__(self, other):
        return isinstance(other, Literal) and self.value == other.value
    
    def __hash__(self):
        return hash(self.value)
    
    def parse(self, g, input_string):
        g.level += 1
        debug_print(f"{'  '*g.level}Parsing Literal: {self.value} in {input_string}")
        if input_string.startswith(self.value):
            g.level -= 1
            return True, input_string[len(self.value):], [(self, 0, 1), []]
        g.level -= 1
        return False, input_string, []
    
    def expand(self, g, compressed):
        return self.value, compressed
