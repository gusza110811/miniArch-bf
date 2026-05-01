class Compiler:
    def __init__(self, source:str):
        self.bracketc = 0
        self.bracketids = []
        self.index = 0
        self.source = source
        self.length = len(self.source)
    def get(self):
        if self.length == self.index:
            return False

        val = self.source[self.index]
        self.index += 1
        return val

    def main(self):
        output:list[str] = [
            ".offset 0x7c00",
            "func main {",
            " mov cx, 0x2000",
            " mov ds, cx",
            " mov dx, 1",
            " mov bx, 0",
        ]

        # main gen
        while 1:
            char = self.get()
            if not char: break

            match char:
                case "-":
                    output.append(" sub ax, 1")
                case "+":
                    output.append(" add ax, 1")

                case "[":
                    id = self.bracketc
                    self.bracketc += 1
                    self.bracketids.append(id)
                    output.append(f"o{id}:")
                    output.append(" mov ah, 0")
                    output.append(f" cmp ax, 0")
                    output.append(f" jz c{id}")
                case "]":
                    id = self.bracketids.pop()
                    output.append(f" jmp o{id}")
                    output.append(f"c{id}:")
                
                case "<":
                    output.append(" mov [b bx], ax")
                    output.append(" sub bx, 1")
                    output.append(" mov ax, [b bx]")
                case ">":
                    output.append(" mov [b bx], ax")
                    output.append(" add bx, 1")
                    output.append(" mov ax, [b bx]")
                
                case ".":
                    output.append(" int 0x14")

        output.extend([
            " hlt",
            "}"
        ])

        def next_line(idx):
            if idx+1 < len(output):
                return output[idx+1]
            else:
                return ""

        optimized = []
        # optimize pointer
        for idx, line in enumerate(output):
            next = next_line(idx)
            if line == " mov ax, [b bx]" and next == " mov [b bx], ax":
                continue
            else:
                optimized.append(line)
        output = optimized

        optimized = []
        # optimize addition and subtraction
        idx = 0
        while idx < len(output):
            line = output[idx]
            next = next_line(idx)

            if line == " add ax, 1":
                count = 1
                while next == line:
                    count += 1
                    idx += 1
                    next = next_line(idx)
                optimized.append(f" add ax, {count}")
                idx += 1
            elif line == " add bx, 1":
                count = 1
                while next == line:
                    count += 1
                    idx += 1
                    next = next_line(idx)
                optimized.append(f" add bx, {count}")
                idx += 1
            elif line == " sub ax, 1":
                count = 1
                while next == line:
                    count += 1
                    idx += 1
                    next = next_line(idx)
                optimized.append(f" sub ax, {count}")
                idx += 1
            elif line == " sub bx, 1":
                count = 1
                while next == line:
                    count += 1
                    idx += 1
                    next = next_line(idx)
                optimized.append(f" sub bx, {count}")
                idx += 1
            else:
                idx += 1
                optimized.append(line)
        output = optimized

        return "\n".join(output)

if __name__ == "__main__":
    test = "-[------->+<]>-.-[->+++++<]>++.+++++++..+++.[->+++++<]>+.------------.---[->+++<]>.-[--->+<]>---.+++.------.--------.-[--->+<]>."

    compiler = Compiler(test)

    output = compiler.main()

    with open("out.asm","w") as out:
        out.write(output)
