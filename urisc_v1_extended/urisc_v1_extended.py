import string
import sys


class URISC_V1_Extended:

    def __init__(self, code):
        self.code = code
        self.output = ['_ONE ?\n']
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
            out = '? ' + line[1] + '\n'

        elif line[0] == 'label':
            out = line[1] + '\n'

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
                temp_1 = self.get_temp()

                # Add literal code to the output
                self.output.append(
                    a + ' ?\n' +
                    a + ' ' + label_1 + '\n' +
                    temp_1 + ' ?\n' +
                    label_1 + '\n'
                )

                # Return the result of this code
                out = temp_1

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
            a = exp[0]
            op = exp[1]
            b = exp[2]

            # Expression expansion
            if a.startswith('(') and a.endswith(')'):
                a = self.compexp(a)
            if b.startswith('(') and b.endswith(')'):
                b = self.compexp(b)

            # Perform operations
            if op == '&':
                label_1 = self.get_label()
                label_2 = self.get_label()

                # Return the result of this code
                out = self.get_temp()

                # Add literal code to the output
                self.output.append(
                    a + ' ' + label_1 + '\n' +
                    b + ' ' + label_2 + '\n' +
                    out + ' ?\n' +
                    label_2 + '\n' +
                    b + ' ?\n' +
                    label_1 + '\n' +
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

                # Return the result of this code
                out = self.get_temp()

                # Add literal code to the output
                self.output.append(
                    a + ' ?\n' +
                    a + ' ' + label_1 + '\n' +
                    b + ' ?\n' +
                    b + ' ' + label_2 + '\n' +
                    out + ' ?\n' +
                    label_2 + '\n' +
                    label_1 + '\n' +
                    out + ' ?\n'
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

                # Return the result of this code
                out = self.get_temp()

                # Add literal code to the output
                self.output.append(
                    a + ' ' + label_1 + '\n' +
                    out + ' ?\n' +
                    label_1 + '\n' +
                    a + ' ?\n' +

                    b + ' ' + label_2 + '\n' +
                    out + ' ?\n' +
                    label_2 + '\n' +
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
                raise Exception('That\'s not a logic gate')

        # Function calling
        elif line[0].startswith('!(') and line[0].endswith(')'):
            # Retrieve function info
            line = self.tokln(line[0][2:-1])

            name = line[0]
            args = line[1:]

            function = self.functions[name]
            func_args = function[0]
            exp = function[1]
            print('Calling', function, 'with', args)

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
            return '_ZERO'
        elif line[0] == '1':
            return '_ONE'

        # Keywords
        elif line[0] == 'in':
            label_1 = self.get_label()

            # Return the result of this code
            out = self.get_temp()

            self.output.append(
                # Invert temp var if input bit is 1
                'in ' + label_1 + '\n' +
                out + ' ?\n' +
                label_1 + '\n' +
                out + ' ?\n'
            )

        else:
            return expression

        return out

    def get_label(self):
        label = 'LABEL_' + str(self.label_num)
        self.label_num += 1
        return label

    def get_temp(self):
        temp = 'TEMP_' + str(self.temp_num)
        self.temp_num += 1
        return temp


with open(sys.argv[1]) as f:
    code = f.read()

compiler = URISC_V1_Extended(code)
compiler.comp()

print('\n\nResult code:\n\n')
print(compiler.output)

with open(sys.argv[1] + '.out', 'w') as f:
    f.write(compiler.output)
