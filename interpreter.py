# TODO:
# Add error handling
#
#
#
#

def lexer(line, lineNum, ram, lables, reg, pnt): 

    ##########
    # This function takes an input and turns it into tokens
    ##########



    line_splt = line.split(' ')
    flag_str = 0
    flag_float = 0
    string = ''
    tokens = []

    for tok in line_splt:
        tok = tok.strip('\n,')
        tok = tok.replace('\\033[', '\033[') # Allows for \033 escape

        if tok:
            if tok[-1] == "'" or tok[-1] == "\"": # Is end of string OR string has no spaces
                if tok[0] == "'" or tok[0] == "\"":
                    string += tok.strip('\'"')

                    tokens.append(['str', string])

                else:
                    string += tok.strip('\'"')
                    tokens.append(['str', string])
                    flag_str = 0
                string = ''
                
            elif flag_str:  # Is in a string
                string += tok + ' '

            elif flag_float: # Is a float
                tokens.append(['float', float(tok)])
                flag_float = 0

            elif tok[0] == "'" or tok[0] == "\"": # Is start of string
                string = ''
                string += tok.strip('\'"') + ' '
                flag_str = 1

            elif tok[0] == '@': # Is value of reg
                if isinstance(reg[tok.strip('@')], list):
                    tokens.append(reg[tok.strip('@')])

                else:
                    tokens.append(['???', reg[tok.strip('@')]])

            elif tok[0] == '#': # Is value in stack at defined pos
                if tok[1] == '$': # Def pos is in hex
                    tokens.append(ram[int(tok.strip('#$'), base=16)])
                
                elif tok[1] == '%': # Def pos is in bin
                    tokens.append(ram[int(tok.strip('#%'), base=2)])

                else: # Def pos is in base 10
                    tokens.append(ram[int(tok.strip('#'), base=10)])

            elif tok[0] == '*': # Is pointer
                x = tok[1:].strip(']').split('[')

                for i in pnt:
                    if i[0] == x[0]:

                        if x[1] == '':
                            tokens.append(['str', ''.join(map(str, i[1]))])

                        elif x[1][0] == '$':
                            tokens.append(['???', i[1][int(x[1].strip('$'), base=16)]])

                        elif x[1][0] == '%':
                            tokens.append(['???', i[1][int(x[1].strip('%'), base=2)]])

                        elif x[1][0] == '@':
                            tokens.append(['???', i[1][reg[x[1].strip('@')][1]]])
                        
                        else:
                            tokens.append(['???', i[1][int(x[1], base=10)]]) 


            elif tok[0] == '%': #bin
                tokens.append(['bin', int(tok.strip('%'), base=2)])
                
            elif tok[0] == '$': #hex
                tokens.append(['hex', int(tok.strip('$'), base=16)])

            elif tok == '__float':
                flag_float = 1

            elif tok[-1] == ":":
                tokens.append(['label', lineNum, tok.strip(':')])
            

            elif tok in ['ax', 'bx', 'cx', 'dx', 'eax', 'ebx', 'ecx', 'edx', 'ip', 'esp', 'esi', 'io']: # Is refrincing reg
                tokens.append(['reg ref', tok])

            elif tok[0] == ';': # Is comment
                break

            else: 
                for i in lables:
                    if i[1] == tok:
                        tokens.append(['label ref', i[0]])

                try:
                    tokens.append(['int', int(tok, base=10)])

                except ValueError:
                    tokens.append(tok)
    return tokens
            
class MAIN:

    def __init__(self, file):
        #self.INSTRUCTIONS = ['mov', 'int', 'dec', 'pop', 'push']
        self.labels = []
        self.reg = {
            'ax':['int', 0],
            'bx':['int', 0],
            'cx':['int', 0],
            'dx':['int', 0],
            'eax':['int', 0],
            'ebx':['int', 0],
            'ecx':['int', 0],
            'edx':['int', 0],

            'ip':['int', 0],
            'io':['int', 0],
            'esp':['int', 0],
            'esi':['int', 0],
            
        }
        self.ram = []
        self.pointers = []
        self.retPoint = 0
        self.file = open(file)

    def mov(self, args):
        if args[1][0] == 'reg ref':
            self.reg[args[1][1]] = args[2]

    def _int(self, args):
        if args[1][1] == 0:

            if self.reg['esi'][1] == 0:
                print(self.reg['ax'][1])
            
            elif self.reg['esi'][1] == 1:
                print(self.reg['ax'][1], end='')

            elif self.reg['esi'][1] == 2:
                print(self.reg['ax'][1], end='\r')
        
        elif args[1][1] == 1:
            if self.reg['esi'][1] == 0:
                self.reg['ax'] = ['int', int(input())]

            elif self.reg['esi'][1] == 1:
                self.reg['ax'] = ['str', str(input())]

    def inc(self, args):
        if args[1][0] == 'reg ref':
            self.reg[args[1][1]][1] = self.reg[args[1][1]][1] + 1
            
    def dec(self, args):
        if args[1][0] == 'reg ref':
            self.reg[args[1][1]][1] = self.reg[args[1][1]][1] - 1

    def set(self, args):
        if args[1] == 'stack':
            if args[2] == 'size':
                if self.reg['esi'][1]:
                    self.ram = []

                for i in range(args[3][1]):
                    self.ram.append('')

    def push(self, args):
        if self.reg['esp'][1] > len(self.ram) - 1:
            print(f'Stack index error. Tried to index pos {self.reg["esp"][1]} stack index range is 0 to {len(self.ram)-1} with a lenth of {len(self.ram)}')

        else:
            self.ram[self.reg['esp'][1]] = self.reg[args[1][1]]

    def pop(self, args):
        if self.reg['esp'][1] > len(self.ram) - 1:
            print(f'Stack index error. Tried to index pos {self.reg["esp"][1]} stack index range is 0 to {len(self.ram)-1} with a lenth of {len(self.ram)}')

        else:
            self.reg[args[1][1]] = self.ram[self.reg['esp'][1]]

    def _if(self, args):
        out = True
        passed = False

        if self.reg['esi'][1] == 0:
            if args[1][1] == args[2][1]:
                out = False

        elif self.reg['esi'][1] == 1:
            if args[1][1] != args[2][1]:
                out = False

        elif self.reg['esi'][1] == 2:
            if args[1][1] > args[2][1]:
                out = False

        elif self.reg['esi'][1] == 3:
            if args[1][1] < args[2][1]:
                out = False

        elif self.reg['esi'][1] == 4:
            if args[1][1] >= args[2][1]:
                out = False

        elif self.reg['esi'][1] == 1:
            if args[1][1] <= args[2][1]:
                out = False

        if not out:
            passed = True

        return out, passed

    def db(self, args):
        out = []
        for k,i in enumerate(args[2:]):

            if i[0] == 'str':
                for j in i[1]:
                    out.append(j)
                if k != len(args[2:]) - 1:
                    out.append(' ')
                    
            else:
                out.append(i[1])
                if k != len(args[2:]) - 1:
                    out.append(' ')

        self.pointers.append([args[1], out])

    def add(self, args):
        self.reg['io'] = args[1][1] + args[2][1]

    def sub(self, args):
        self.reg['io'] = args[1][1] - args[2][1]

    def mul(self, args):
        if self.reg['esi'][1] == 0:
            self.reg['io'] = args[1][1] * args[2][1]

        elif self.reg['esi'][1] == 1:
            self.reg['io'] = args[1][1] ** args[2][1]

    def div(self, args):
        if self.reg['esi'][1] == 0:
            self.reg['io'] = args[1][1] / args[2][1]

        elif self.reg['esi'][1] == 1:
            self.reg['io'] = args[1][1] // args[2][1]

        elif self.reg['esi'][1] == 2:
            self.reg['io'] = args[1][1] % args[2][1]
        
    def size(self, args):
        self.reg['io'] = ['int', len(args[1][1])]

    def call(self, args):
        if args[1][0] == 'label ref':
            self.retPoint = self.reg['ip']
            self.reg['ip'] = ['int', args[1][1]]

    def ret(self):
        self.reg['ip'] = self.retPoint
        self.retPoint = 0

    def jmp(self, args):
        if args[1][0] == 'label ref':
            self.reg['ip'] = ['int', args[1][1]]
            
        
        else:
            self.reg['ip'] = args[1]

    def syscall(self, args):
        
        args[1][1] = args[1][1].split('.')

        if args[1][1][-1] in ['py', 'py3', 'pyw']:
            import importlib

            if len(args) > 1:
                modual_name = '.'.join(args[1][1][:-1])
            modual = importlib.import_module(modual_name)
            call_args = []

            for i in args[2:]:
                call_args.append(i[1])

            self.reg['io'] = modual.main(call_args)

        elif args[1][1][1] == 'dat':
            with open(args[1][1][0]+'.dat') as file:
                for line in file.readlines():
                    line = line.strip('\n').split(': ')
                    self.pointers.append([line[0], line[1]])

        elif args[1][1][1] == 'asm':
            from interpreter import MAIN
            M = MAIN(args[1][1][0]+'.asm')
            self.reg['io'] = M.main() 

        elif args[1][1][1] == 'dll':
            pass

    def main(self):       
        lines = self.file.readlines()
        self.file.close()

        if_flag = False
        if_passed = False
        active = False
        startpoint = ''

        while True:
            output = lexer(lines[self.reg['ip'][1]], self.reg['ip'][1], self.ram, self.labels, self.reg, self.pointers)
            if not True:
                print(output, startpoint)

            if not output:
                pass

            elif not isinstance(output[0], list) and not active:
                if output[0] == '.start':
                    startpoint = output[1]

                elif output[0] == '.stack':
                    for i in range(output[1][1]):
                        self.ram.append('')


            elif not isinstance(output[0], list) and not if_flag and active:

                if output[0] == 'end':
                    return output[1:]

                elif output[0] == 'mov':
                    self.mov(output)
                
                elif output[0] == 'int':
                    self._int(output)

                elif output[0] == 'inc':
                    self.inc(output)

                elif output[0] == 'dec':
                    self.dec(output)

                elif output[0] == 'set':
                    self.set(output)

                elif output[0] == 'push':
                    self.push(output)

                elif output[0] == 'pop':
                    self.pop(output)

                elif output[0] == 'nop':
                    pass

                elif output[0] == 'db':
                    self.db(output)                    

                elif output[0] == 'add':
                    self.add(output)

                elif output[0] == 'sub':
                    self.sub(output)
                
                elif output[0] == 'mul':
                    self.mul(output)

                elif output[0] == 'div':
                    self.div(output)

                elif output[0] == 'size':
                    self.size(output)

                elif output[0] == 'call':
                    self.call(output)

                elif output[0] == 'ret':
                    self.ret()

                elif output[0] == 'jmp':
                    self.jmp(output)

                elif output[0] == 'syscall':
                    self.syscall(output)
                
                elif output[0] == 'if':
                    if_flag, if_passed = self._if(output)

                elif output[0] == 'endif':
                    if_flag, if_passed = False, False

                elif output[0] in ['else', 'elseif']:
                    if_flag = True

            else:
                if if_flag:
                    if not if_passed:
                        if output[0] == 'elseif':
                            if_flag, if_passed = self._if(output)                         

                        elif output[0] == 'else':
                            if_flag = False

                    if output[0] == 'endif':
                        if_flag, if_passed = False, False

                if output[0][0] == 'label':
                        self.labels.append([output[0][1], output[0][2]])
                        if output[0][2] == startpoint:
                            active = True

            self.reg['ip'][1] = self.reg['ip'][1] + 1



        

if __name__ == '__main__':
    M = MAIN('test.asm') # Defult file
    M.main()
