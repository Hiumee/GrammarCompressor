import string
from grammar import Grammar, Symbol, Literal, Composition
from brotli import decompress, compress
from math import ceil
import os

g = Grammar()

### JSON Grammar ###
json = Symbol("json")
value = Symbol("value")
obj = Symbol("obj")
members = Symbol("members")
member = Symbol("member")
array = Symbol("array")
elements = Symbol("elements")
element = Symbol("element")
sstring = Symbol("sstring")
characters = Symbol("characters")
character = Symbol("character")
escape = Symbol("escape")
hexx = Symbol("hexx")
number = Symbol("number")
integer = Symbol("integer")
digits = Symbol("digits")
digit = Symbol("digit")
onenine = Symbol("onenine")
fraction = Symbol("fraction")
exponent = Symbol("exponent")
sign = Symbol("sign")
ws = Symbol("ws")

g.add_rule(json, element)

g.add_rule(value, obj)
g.add_rule(value, array)
g.add_rule(value, sstring)
g.add_rule(value, number)
g.add_rule(value, Literal("true"))
g.add_rule(value, Literal("false"))
g.add_rule(value, Literal("null"))

g.add_rule(obj, Composition(Literal("{"), ws, Literal("}")))
g.add_rule(obj, Composition(Literal("{"), members, Literal("}")))

g.add_rule(members, Composition(member, Literal(","), members))
g.add_rule(members, member)

g.add_rule(member, Composition(ws, sstring, ws, Literal(":"), element))

g.add_rule(array, Composition(Literal("["), ws, Literal("]")))
g.add_rule(array, Composition(Literal("["), elements, Literal("]")))

g.add_rule(elements, Composition(element, Literal(","), elements))
g.add_rule(elements, element)

g.add_rule(element, Composition(ws, value, ws))

g.add_rule(sstring, Composition(Literal('"'), characters, Literal('"')))

g.add_rule(characters, Composition(character, characters))
g.add_rule(characters, Literal(""))

for char in string.ascii_letters + string.digits + string.punctuation + string.whitespace:
    if char in '"\\':
        continue
    g.add_rule(character, Literal(char)) # TODO: Not all valid characters are included here
g.add_rule(character, Composition(Literal("\\"), escape))

g.add_rule(escape, Literal('"'))
g.add_rule(escape, Literal('\\'))
g.add_rule(escape, Literal('/'))
g.add_rule(escape, Literal('b'))
g.add_rule(escape, Literal('f'))
g.add_rule(escape, Literal('n'))
g.add_rule(escape, Literal('r'))
g.add_rule(escape, Literal('t'))
g.add_rule(escape, Composition(Literal('u'), hexx, hexx, hexx, hexx))

g.add_rule(hexx, digit)
g.add_rule(hexx, Literal('a'))
g.add_rule(hexx, Literal('b'))
g.add_rule(hexx, Literal('c'))
g.add_rule(hexx, Literal('d'))
g.add_rule(hexx, Literal('e'))
g.add_rule(hexx, Literal('f'))
g.add_rule(hexx, Literal('A'))
g.add_rule(hexx, Literal('B'))
g.add_rule(hexx, Literal('C'))
g.add_rule(hexx, Literal('D'))
g.add_rule(hexx, Literal('E'))
g.add_rule(hexx, Literal('F'))

g.add_rule(number, Composition(integer, fraction, exponent))

g.add_rule(integer, Composition(onenine, digits))
g.add_rule(integer, Composition(Literal("-"), digit))
g.add_rule(integer, Composition(Literal("-"), onenine, digits))
g.add_rule(integer, digit)

g.add_rule(digits, Composition(digit, digits))
g.add_rule(digits, digit)

g.add_rule(digit, Literal("0"))
g.add_rule(digit, onenine)

g.add_rule(onenine, Literal("1"))
g.add_rule(onenine, Literal("2"))
g.add_rule(onenine, Literal("3"))
g.add_rule(onenine, Literal("4"))
g.add_rule(onenine, Literal("5"))
g.add_rule(onenine, Literal("6"))
g.add_rule(onenine, Literal("7"))
g.add_rule(onenine, Literal("8"))
g.add_rule(onenine, Literal("9"))

g.add_rule(fraction, Composition(Literal("."), digits))
g.add_rule(fraction, Literal(""))

g.add_rule(exponent, Composition(Literal("e"), sign, digits))
g.add_rule(exponent, Composition(Literal("E"), sign, digits))
g.add_rule(exponent, Literal(""))

g.add_rule(sign, Literal("+"))
g.add_rule(sign, Literal("-"))
g.add_rule(sign, Literal(""))

g.add_rule(ws, Composition(Literal(" "), ws))
g.add_rule(ws, Composition(Literal("\n"), ws))
g.add_rule(ws, Composition(Literal("\t"), ws))
g.add_rule(ws, Composition(Literal("\r"), ws))
g.add_rule(ws, Literal(""))

g.set_starting_symbol(json)
### End JSON Grammar ###


def compress_tree(tree):
    if len(tree) == 0:
        return []
    
    output = []
    _, index, total = tree[0]
    if total > 1:
        bit_lenght = total.bit_length()
        output.append(f"{index:0{bit_lenght}b}")
        
    next_steps = tree[1]
    for step in next_steps:
        output += compress_tree(step)
        
    return output

def decompress_tree(compressed, grammar):
    return grammar.expand(compressed)

files = os.listdir("examples")

for file in files:
    if file.endswith(".json"):
        with open(f"examples/{file}", "r") as f:
            input_string = f.read()
            print()
            print(f"===Input: {file}===")
            success, tree = g.parse(input_string)
            print(f"    Original size: {len(input_string)} bytes")
            assert(success)

            compressed = compress_tree(tree)
            compressed = "".join(compressed)
            compressed_bin = bytearray()
            for i in range(0, len(compressed), 8):
                byte = compressed[i:i+8]
                if len(byte) < 8:
                    byte = byte.ljust(8, '0')
                compressed_bin.append(int(byte, 2))
            brotli_compressed_compressed_data = compress(compressed_bin)
            expanded = decompress_tree(compressed, g)[0]
            assert(expanded == input_string)
            
            print("  ===Compressed===")
            print(f"    Compressed size: {ceil(len(compressed) / 8)} bytes")
            print(f"    Compressed size (Brotli): {len(brotli_compressed_compressed_data)} bytes")
            print(f"    Compression ratio: {len(compressed) / (len(input_string) * 8):.2f}")
            print(f"    Compression ratio (Brotli): {len(brotli_compressed_compressed_data) / len(input_string):.2f}")

            print()
            print("  ===Brotli===")
            input_string = input_string.encode('utf-8')
            compressed_data = compress(input_string)

            print(f"    Original size: {len(input_string)} bytes")
            print(f"    Compressed size: {len(compressed_data)} bytes")
            print(f"    Compression ratio: {len(compressed_data) / len(input_string):.2f}")
            
            print("  ===Comparing===")
            print(f"    Brotly is better by {ceil(len(compressed) / 8) - len(compressed_data)} bytes")

            decompressed_data = decompress(compressed_data)
            assert(decompressed_data == input_string)

