import string
import sys


class URISC_V1_Extended:

    def __init__(self, code):
        self.code = code
        self.output = ''
        self.label_num = 0
        self.temp_num = 0

    def comp(self):
        for line in self.code.split('\n'):
            # print(line)
            self.output += self.compln(line)

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

        if not line:
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
            if line[2] != '0':
                out += line[1] + ' ?\n'

        elif line[0] == 'jump':
            out = '? ' + line[1] + '\n'

        elif '=' in line:
            # var = exp
            var = line[0]
            exp = line[2]

            # Expression expansion
            exp = self.compexp(exp)

            print('RESULT!!!', exp)

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

        return out


    def compexp(self, expression):
        line = self.tokln(expression)
        out = ''

        if not expression:
            return ''

        # Logic gates
        if line[0].startswith('(') and line[0].endswith(')'):
            # Tokenise this bracket expression
            exp = self.tokln(line[0][1:-1])

            # Get result of (a op b) and store in _temp
            c = '_temp'
            a = exp[0]
            op = exp[1]
            b = exp[2]

            # Expression expansion
            if a.startswith('(') and a.endswith(')'):
                a = self.compexp(a)
            if b.startswith('(') and b.endswith(')'):
                b = self.compexp(b)

            print('YO!', a, op, b)

            # Perform logic
            if op == '&':
                label_1 = self.get_label()
                label_2 = self.get_label()
                temp_1 = self.get_temp()

                print('BEFORE!!!', self.output)

                # Add literal code to the output
                self.output += (
                    a + ' ' + label_1 + '\n' +
                    b + ' ' + label_2 + '\n' +
                    temp_1 + ' ?\n' +
                    label_2 + '\n' +
                    b + ' ?\n' +
                    label_1 + '\n' +
                    a + ' ?\n'
                )

                print('AFTER!!!', self.output)

                # Return the result of this code
                out = temp_1

                '''
                a end_1
                b end_2
                temp ?
                end_2
                b ?
                end_1
                a ?
                '''

            elif op == '|':
                label_1 = self.get_label()
                label_2 = self.get_label()
                temp_1 = self.get_temp()

                # Add literal code to the output
                self.output += (
                    a + ' ?\n' +
                    a + ' ' + label_1 + '\n' +
                    b + ' ?\n' +
                    b + ' ' + label_2 + '\n' +
                    temp_1 + ' ?\n' +
                    label_2 + '\n' +
                    label_1 + '\n' +
                    temp_1 + ' ?\n'
                )

                # Return the result of this code
                out = temp_1

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

            else:
                raise Exception('That\'s not a logic gate')

        else:
            out = expression

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

print(compiler.output)

with open(sys.argv[1] + '.out', 'w') as f:
    f.write(compiler.output)
