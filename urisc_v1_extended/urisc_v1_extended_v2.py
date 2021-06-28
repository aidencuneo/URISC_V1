import string
import sys


class Variable:

    def __init__(self, name, bits):
        # Bit size is ALMOST ALWAYS 8
        self.bit_size = len(bits)
        self.name = name
        self.names = [name + '_BIT_' + str(i) for i in range(self.bit_size)]
        # Bit values (variable names)
        self.bits = bits

    '''

    The majority of these methods will return compiled code

    '''

    def get_code(self):
        # Result code
        out = []

        # Iterate over each bit in this variable
        for bit_index in range(self.bit_size):
            bit_name = self.names[bit_index]
            bit_value = self.bits[bit_index]

            # Set this bit to its correct value
            out.append(bit_name + ' = ' + bit_value + '\n')

        # Return the result code
        return ''.join(out)

    def add(self, other, result_var, compiler):
        out = []

        c_in = compiler.get_temp()

        for bit_index in range(self.bit_size - 1, -1, -1):
            bit = result_var.names[bit_index]

            a = self.names[bit_index]
            b = other.names[bit_index]

            out.append(f'''
{bit} = (({a} ^ {b}) ^ {c_in})
{c_in} = (({a} ^ {b} & {c_in}) | ({a} & {b}))
            '''.strip() + '\n')

        # Append compiled code to the compiled output
        compiler.output.append(''.join(out))

    def logical_not(self, result_var, compiler):
        out = []

        result_value = compiler.get_temp()

        # Remember whether or not the result should be true
        b0, b1, b2, b3, b4, b5, b6, b7 = self.names
        out.append(f'{result_value} = (:! ({b0} | {b1} | {b2} | {b3} | {b4} | {b5} | {b6} | {b7}))\n')

        # Set new variable to 0
        for bit in result_var.names:
            out.append(f'{bit} = 0\n')

        # Recall whether or not the result should be true
        last_bit = result_var.names[-1]
        out.append(f'{last_bit} = {result_value}\n')

        # Append compiled code to the compiled output
        compiler.output.append(''.join(out))

    def invert(self, result_var, compiler):
        out = []

        # Invert new variable
        for bit_index in range(self.bit_size):
            bit = result_var.names[bit_index]
            a = self.names[bit_index]

            out.append(f'{bit} = (:! {a})\n')

        # Append compiled code to the compiled output
        compiler.output.append(''.join(out))


class URISC_V1_Extended:

    def __init__(self, code):
        self.code = code
        self.output = ['_ONE = 1\n']

        self.protected_vars = []
        self.var = {}
        self.functions = {}

        # Initialise number variables (inclusively 0 to 255)
        for num in range(256):
            self.protected_vars.append(str(num))
            self.var[str(num)] = Variable('0', list(format(num, '08b')))

        self.label_num = 0
        self.temp_num = 0

    def comp(self):
        for line in self.code.split('\n'):
            # print(line)
            self.output.append(self.compln(line))

        self.output = ''.join(self.output)

    def tokln(self, line):
        if not line:
            return

        out = []
        current = ''

        # Char type stuff
        chartype = ''
        last_chartype = ''

        rb = 0 # Regular-bracket = 0

        # Set initial char type
        if line[0].isalnum():
            chartype = 'A'
        # elif line[0].isdigit():
        #     chartype = 'D'
        elif line[0] in string.punctuation:
            chartype = 'S'
        # elif line[0] == '\n':
        #     chartype = 'L'
        elif line[0].isspace():
            chartype = 'W'

        for c in line:
            last_chartype = chartype

            # Set char type for each character
            if c.isalnum():
                chartype = 'A'
            # elif c.isdigit():
            #     chartype = 'D'
            elif c in string.punctuation:
                chartype = 'S'
            # elif c == '\n':
            #     chartype = 'L'
            elif c.isspace():
                chartype = 'W'

            if chartype == 'W' and rb <= 0:
                out.append(current)
                current = ''
            else:
                current += c

            # Concatenation stuff
            if c == '(':
                rb += 1
            elif c == ')':
                rb -= 1

        # Final token
        out.append(current)

        # Filter
        out = [a for a in out if a]

        print(out)

        return out

    def compln(self, line):
        line = self.tokln(line)
        out = ''

        if not line or line[0].startswith('#'):
            return ''

        if line[0] == 'invert':
            out = line[1] + ' ?\n'

        elif line[0] == 'set':
            # Set variable to 0
            label = self.get_label()
            out = (
                label + '\n' +
                line[1] + ' ' + label + '\n'
            )

            # Invert variable if desired
            if line[2] != '0' and line[2] != 'false':
                out += line[1] + ' ?\n'

        elif line[0] == 'jump':
            out = (
                '? ' + line[1] + '\n' +
                '? ' + line[1] + '\n'
            )

        elif line[0] == 'if':
            exp = self.compexp(line[1])
            label = line[2]

            # Jump to label if expression result is 1
            out = (
                exp + ' ?\n' +
                exp + ' ' + label + '\n'
            )

        elif line[0] == 'ifn':
            exp = self.compexp(line[1])
            label = line[2]

            # Jump to label if expression result is 0
            out = exp + ' ' + label + '\n'

        elif line[0] == 'label':
            out = line[1] + '\n'

        elif line[0] == 'print':
            exp = self.compexp(line[1])
            out = 'print ' + ' '.join(exp.names) + '\n'

        elif '=' in line:
            # name = exp
            name = line[0]
            exp = self.compexp(line[2])

            # Variable stuff
            if name not in self.protected_vars and name in self.var:
                # If this is already a variable, add code to change it
                self.var[name].bits = exp.names
                out = self.var[name].get_code()
            else:
                # If this isn't a variable yet, create it
                self.var[name] = Variable(name, exp.names)
                out = self.var[name].get_code()

            # var = self.var[name]

            # Move expression result into name
            # label_1 = self.get_label()
            # label_2 = self.get_label()

        elif '=>' in line:
            # func => arg1,arg2,arg2 ((arg1 & arg2) | arg3)
            name = line[0]
            args = line[2].split(',')
            exp = line[3]

            self.functions[name] = [args, exp]

        return out

    def compexp(self, expression):
        line = self.tokln(expression)
        out = self.var['0'] # Return 0 by default

        if not expression:
            return out

        # Unary operators
        if line[0].startswith('(:') and line[0].endswith(')'):
            # Tokenise this bracket expression
            exp = self.tokln(line[0][2:-1])

            # Get result of (op a) and store in a temporary variable
            op = exp[0]
            a = self.compexp(exp[1])

            # Perform operations
            if op == '!':
                out = Variable(self.get_temp(), list('0' * 8))
                a.logical_not(out, compiler)

            elif op == '~':
                temp = Variable(self.get_temp(), list('0' * 8))
                out = Variable(self.get_temp(), list('0' * 8))

                # Invert a and save in temp
                a.invert(temp, compiler)

                # Add 1 to temp and save in out
                temp.add(
                    self.compexp('1'),
                    out,
                    compiler)

            else:
                raise Exception('invalid unary operation: "' + op + '"')

        # Logic gates (Binary operators)
        elif line[0].startswith('(') and line[0].endswith(')'):
            # Tokenise this bracket expression
            exp = self.tokln(line[0][1:-1])

            # Get result of (a op b op n...) and store in a temporary variable
            while len(exp) > 1:
                a = self.compexp(exp[0])
                op = exp[1]
                b = self.compexp(exp[2])
                result = ''

                # Perform operations
                if op == '+':
                    result = Variable(self.get_temp(), list('0' * 8))
                    a.add(b, result, compiler)

                elif op == '-':
                    temp_1 = Variable(self.get_temp(), list('0' * 8))
                    temp_2 = Variable(self.get_temp(), list('0' * 8))
                    result = Variable(self.get_temp(), list('0' * 8))

                    # Invert b and save in temp_1
                    b.invert(temp_1, compiler)

                    # Add 1 to temp_1 and save in temp_2
                    temp_1.add(
                        self.compexp('1'),
                        temp_2,
                        compiler)

                    # Add a to temp_2 ((a - b) == (a + ~b)) and save in result
                    a.add(temp_2, result, compiler)

                elif op == 'pp2|':
                    label_1 = self.get_label()
                    label_2 = self.get_label()
                    label_3 = self.get_label()

                    # Return the result of this code
                    result = self.get_temp()

                    # Add literal code to the output
                    self.output.append(
                        # Set result to 0
                        label_1 + '\n' +
                        result + ' ' + label_1 + '\n' +

                        # Perform logical xor
                        a + ' ' + label_2 + '\n' +
                        result + ' ?\n' +
                        label_2 + '\n' +
                        a + ' ?\n' +

                        b + ' ' + label_3 + '\n' +
                        result + ' ?\n' +
                        label_3 + '\n' +
                        b + ' ?\n'
                    )

                    '''
                    a end_1
                    output ?
                    end_1
                    a ?

                    b end_2
                    output ?
                    end_2
                    b ?

                    '''

                else:
                    raise Exception('invalid binary operation: "' + op + '"')

                exp[:3] = [result]

            # Return the final result
            out = exp[0]

        # Function calling
        # elif line[0].startswith('!(') and line[0].endswith(')'):
        #     # Retrieve function info
        #     line = self.tokln(line[0][2:-1])

        #     name = line[0]
        #     args = line[1:]

        #     function = self.functions[name]
        #     func_args = function[0]
        #     exp = function[1]
        #     print('Calling', function, 'with', args)

        #     # Check arg lengths
        #     if len(args) != len(func_args):
        #         raise Exception('invalid number of arguments for function')

        #     # Save local variables to be retrieved later
        #     for arg_index in range(len(args)):
        #         local_arg = args[arg_index]
        #         temp_var = 'FUNCTION_ARG_' + local_arg

        #         # Move local variables to function argument variables
        #         label_1 = self.get_label()
        #         label_2 = self.get_label()

        #         self.output.append(
        #             # Set temporary variable to 0
        #             label_1 + '\n' +
        #             temp_var + ' ' + label_1 + '\n' +

        #             # Invert temporary variable if local arg is 1
        #             local_arg + ' ' + label_2 + '\n' +
        #             temp_var + ' ?\n' +
        #             label_2 + '\n' +
        #             local_arg + ' ?\n'
        #         )

        #     # Move temp variables into function argument variables
        #     for arg_index in range(len(func_args)):
        #         func_arg = func_args[arg_index]
        #         local_arg = args[arg_index]
        #         temp_var = 'FUNCTION_ARG_' + local_arg

        #         # Move local variables to function argument variables
        #         label_1 = self.get_label()
        #         label_2 = self.get_label()

        #         self.output.append(
        #             # Set function arg to 0
        #             label_1 + '\n' +
        #             func_arg + ' ' + label_1 + '\n' +

        #             # Invert function arg if temp var is 1
        #             temp_var + ' ' + label_2 + '\n' +
        #             func_arg + ' ?\n' +
        #             label_2 + '\n' +
        #             temp_var + ' ?\n'
        #         )

        #     # Compute and return expression
        #     out = self.compexp(exp)

        # Numbers
        elif line[0].isdigit():
            num = int(line[0])
            if 0 <= num <= 255:
                num_var = Variable(self.get_temp(), list(format(num, '08b')))
                # Append variable code
                self.output.append(num_var.get_code())
                return num_var

        # Variables
        elif line[0] in self.var:
            return self.var[line[0]]

        # Keywords
        elif line[0] == 'in':
            label_1 = self.get_label()
            label_2 = self.get_label()

            # Return the result of this code
            out = self.get_temp()

            self.output.append(
                # Set out to 0
                label_1 + '\n' +
                out + ' ' + label_1 + '\n' +

                # Invert out if input bit is 1
                'in ' + label_2 + '\n' +
                out + ' ?\n' +
                label_2 + '\n' +
                out + ' ?\n'
            )

        return out

    def get_label(self):
        label = 'L_' + str(self.label_num)
        self.label_num += 1
        return label

    def get_temp(self):
        temp = 'T_' + str(self.temp_num)
        self.temp_num += 1
        return temp


with open(sys.argv[1]) as f:
    code = f.read()

compiler = URISC_V1_Extended(code)
compiler.comp()

print('\n\nResult code:\n\n')
print(compiler.output)

with open(sys.argv[1] + '.xv1', 'w') as f:
    f.write(compiler.output)
