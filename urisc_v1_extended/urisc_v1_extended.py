import string
import sys


class URISC_V1_Extended:

    def __init__(self, code):
        self.code = code
        self.output = ['1 ?\n']
        self.functions = {}
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

        # print(out)

        return out

    def compln(self, line):
        line = self.tokln(line)
        out = ''

        if not line or line[0].startswith('#'):
            return ''

        if line[0] == '```':
            out = ' '.join(line[1:])

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
            # Iterate over each expression in the line and print it as a bit
            for bit in line[1:]:
                exp = self.compexp(bit)

                # Print bit to output buffer
                label_1 = self.get_label()
                label_2 = self.get_label()

                out += (
                    # Set out to 0
                    label_1 + '\n' +
                    'out ' + label_1 + '\n' +

                    # Invert out if expression result
                    exp + ' ' + label_2 + '\n' +
                    'out ?\n' +
                    label_2 + '\n' +
                    exp + ' ?\n' +

                    # Print bit to output buffer
                    'print ?\n'
                )

        elif '=' in line:
            # var = exp
            var = line[0]
            exp = line[2]

            # Expression expansion
            exp = self.compexp(exp)

            # Move expression result into var
            label_1 = self.get_label()
            label_2 = self.get_label()

            out = (
                # Set var to 0
                label_1 + '\n' +
                var + ' ' + label_1 + '\n' +

                # Invert var if expression result
                exp + ' ' + label_2 + '\n' +
                var + ' ?\n' +
                label_2 + '\n' +
                exp + ' ?\n'
            )

        elif '=>' in line:
            # func => arg1,arg2,arg2 ((arg1 & arg2) | arg3)
            name = line[0]
            args = line[2].split(',')
            exp = line[3]

            self.functions[name] = [args, exp]

        return out

    def compexp(self, expression):
        line = self.tokln(expression)
        out = ''

        if not expression:
            return ''

        # Unary operators
        if line[0].startswith('(:') and line[0].endswith(')'):
            # Tokenise this bracket expression
            exp = self.tokln(line[0][2:-1])

            # Get result of (op a) and store in a temporary variable
            op = exp[0]
            a = exp[1]

            # Expression expansion
            if a.startswith('(') and a.endswith(')'):
                a = self.compexp(a)

            # Perform operations
            if op == '!':
                label_1 = self.get_label()
                label_2 = self.get_label()

                # Return the result of this code
                out = self.get_temp()

                # Add literal code to the output
                self.output.append(
                    # Set out to 0
                    label_1 + '\n' +
                    out + ' ' + label_1 + '\n' +

                    # Invert out if not a
                    a + ' ?\n' +
                    a + ' ' + label_2 + '\n' +
                    out + ' ?\n' +
                    label_2 + '\n'
                )

                '''
                a ?
                a label_1
                temp_1 ?
                label_1
                '''

        # Logic gates (Binary operators)
        elif line[0].startswith('(') and line[0].endswith(')'):
            # Tokenise this bracket expression
            exp = self.tokln(line[0][1:-1])

            # Get result of (a op b) and store in a temporary variable
            while len(exp) > 1:
                a = exp[0]
                op = exp[1]
                b = exp[2]

                result = ''

                # Expression expansion
                if a.startswith('(') and a.endswith(')'):
                    a = self.compexp(a)
                if b.startswith('(') and b.endswith(')'):
                    b = self.compexp(b)

                # Perform operations
                if op == '&':
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

                        # Perform logical and
                        a + ' ' + label_2 + '\n' +
                        b + ' ' + label_3 + '\n' +
                        result + ' ?\n' +
                        label_3 + '\n' +
                        b + ' ?\n' +
                        label_2 + '\n' +
                        a + ' ?\n'
                    )

                    '''
                    a end_1
                    b end_2
                    output ?
                    end_2
                    b ?
                    end_1
                    a ?
                    '''

                elif op == '|':
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

                        # Perform logical or
                        a + ' ?\n' +
                        a + ' ' + label_2 + '\n' +
                        b + ' ?\n' +
                        b + ' ' + label_3 + '\n' +
                        result + ' ?\n' +
                        label_3 + '\n' +
                        label_2 + '\n' +
                        result + ' ?\n'
                    )

                    '''
                    a ?
                    a end_1
                    b ?
                    b end_2
                    output ?
                    end_2
                    end_1

                    output ?
                    '''

                elif op == '^':
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
        elif line[0].startswith('!(') and line[0].endswith(')'):
            # Retrieve function info
            line = self.tokln(line[0][2:-1])

            name = line[0]
            args = line[1:]

            function = self.functions[name]
            func_args = function[0]
            exp = function[1]
            # print('Calling', function, 'with', args)

            # Check arg lengths
            if len(args) != len(func_args):
                raise Exception('invalid number of arguments for function')

            # Save local variables to be retrieved later
            for arg_index in range(len(args)):
                local_arg = args[arg_index]
                temp_var = 'FUNCTION_ARG_' + local_arg

                # Move local variables to function argument variables
                label_1 = self.get_label()
                label_2 = self.get_label()

                self.output.append(
                    # Set temporary variable to 0
                    label_1 + '\n' +
                    temp_var + ' ' + label_1 + '\n' +

                    # Invert temporary variable if local arg is 1
                    local_arg + ' ' + label_2 + '\n' +
                    temp_var + ' ?\n' +
                    label_2 + '\n' +
                    local_arg + ' ?\n'
                )

            # Move temp variables into function argument variables
            for arg_index in range(len(func_args)):
                func_arg = func_args[arg_index]
                local_arg = args[arg_index]
                temp_var = 'FUNCTION_ARG_' + local_arg

                # Move local variables to function argument variables
                label_1 = self.get_label()
                label_2 = self.get_label()

                self.output.append(
                    # Set function arg to 0
                    label_1 + '\n' +
                    func_arg + ' ' + label_1 + '\n' +

                    # Invert function arg if temp var is 1
                    temp_var + ' ' + label_2 + '\n' +
                    func_arg + ' ?\n' +
                    label_2 + '\n' +
                    temp_var + ' ?\n'
                )

            # Compute and return expression
            out = self.compexp(exp)

        # Digits
        elif line[0] == '0':
            return '0'
        elif line[0] == '1':
            return '1'

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

        else:
            return expression

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

# print('\n\nResult code:\n\n')
# print(compiler.output)

with open(sys.argv[1] + '.urisc_v1', 'w') as f:
    f.write(compiler.output)
