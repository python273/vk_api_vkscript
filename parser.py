import functools
import ast
import inspect
import string


API = object()
parseInt = object()


SAFE_KEY_LETTERS = string.ascii_letters + '_'

def escape_quotes(s):
    # TODO
    return s

def check_safe_key(k):
    return all(i in SAFE_KEY_LETTERS for i in k)

def force_safe_key(k):
    return k if check_safe_key(k) else f'"{escape_quotes(k)}"'


class VkScriptNodeVisitor(ast.NodeVisitor):
    def __init__(self, *args, **kwargs):
        self.vkscript = []
        self.vars = set()
        return super().__init__(*args, **kwargs)

    def e(self, node):
        visitor = VkScriptNodeVisitor()
        visitor.visit(node)
        return ''.join(visitor.vkscript)

    def a(self, x):
        self.vkscript.append(x)

    def parse_fn(self, source):
        func_node = ast.parse(source).body[0]

        for st in func_node.body:
            self.visit(st)
            self.a(';\n')

        return ''.join(self.vkscript)

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise Exception('assign should be simple')

        # TODO: should not add `var` in case already defined
        var_name = self.e(node.targets[0])
        value = self.e(node.value)

        kw = 'var ' if var_name not in self.vars else ''
        self.vars.add(var_name)

        self.a(f'{kw}{var_name} = {value}')

    def visit_Return(self, node):
        self.a(f'return {self.e(node.value)}')

    def visit_Call(self, node):
        if node.args and node.keywords:
            raise Exception('cant have args and kwargs')

        func_name = self.e(node.func)

        if not node.args and not node.keywords:
            self.a(
                f'{func_name}()'
            )

        if node.args:
            args = ','.join([self.e(a) for a in node.args])
            self.a(f'{func_name}({args})')

        if node.keywords:
            # kwargs get converted into object
            # fn(a=1) => fn({"a": 1})

            kwargs = ','.join([
                f'{force_safe_key(k.arg)}:{self.e(k.value)}'
                for k in node.keywords
            ])
            self.a(f'{func_name}({{{kwargs}}})')

    def visit_Attribute(self, node):
        self.a(f'{self.e(node.value)}.{node.attr}')

    def visit_Name(self, node):
        self.a(node.id)

    def visit_Num(self, node):
        self.a(str(node.n))

    def visit_Str(self, node):
        self.a(f'"{escape_quotes(node.s)}"')

    def visit_Subscript(self, node):
        self.a(f'{self.e(node.value)}[{self.e(node.slice)}]')

    def visit_Index(self, node):
        self.a(self.e(node.value))

    def visit_BinOp(self, node):
        op_str = None

        if isinstance(node.op, ast.Add):
            op_str = '+'
        elif isinstance(node.op, ast.Mult):
            op_str = '*'

        if not op_str:
            raise Exception(f'{type(node.op)} op is not supported')

        self.a(f'{self.e(node.left)} {op_str} {self.e(node.right)}')


def get_fn_vkscript(fn):
    source = inspect.getsource(fn)

    # removing function indent (e.g. if nested)
    lines = source.split('\n')

    for l in lines:
        if l.strip().startswith('@'):
            # skip decorators
            continue

        indent = l.index('def')
        break
    else:
        raise Exception('def?')

    source = '\n'.join(l[indent:] for l in source.split('\n'))
    vkscript_code = VkScriptNodeVisitor().parse_fn(source)
    return vkscript_code


def vkscript(fn):
    vkscript_code = get_fn_vkscript(fn)

    @functools.wraps(fn)
    def wrapped(vk):
        return vk.execute(code=vkscript_code)

    return wrapped


def main():
    def some_magic():
        x = parseInt(API.status.get()['text'])
        x = x + 1
        return API.status.set(text=x)

    print(get_fn_vkscript(some_magic))


if __name__ == "__main__":
    main()
