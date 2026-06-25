import tkinter as tk
import ast
import operator


class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧮 Calculator")
        self.geometry("360x500")
        self.resizable(False, False)
        self.configure(bg="#1f1f1f")

        self.expression = ""
        self.display_var = tk.StringVar(value="0")

        self.create_ui()

    def create_ui(self):
        display = tk.Entry(
            self,
            textvariable=self.display_var,
            justify="right",
            font=("Segoe UI", 28, "bold"),
            bd=0,
            bg="#2b2b2b",
            fg="white",
            relief="flat",
        )
        display.pack(fill="x", padx=10, pady=(10, 8), ipady=18)
        display.bind("<KeyPress>", self.on_keypress)

        button_frame = tk.Frame(self, bg="#1f1f1f")
        button_frame.pack(fill="both", expand=True, padx=10, pady=8)

        buttons = [
            ("C", "clear"),
            ("⌫", "back"),
            ("%", "operator"),
            ("÷", "operator"),
            ("7", "digit"),
            ("8", "digit"),
            ("9", "digit"),
            ("×", "operator"),
            ("4", "digit"),
            ("5", "digit"),
            ("6", "digit"),
            ("−", "operator"),
            ("1", "digit"),
            ("2", "digit"),
            ("3", "digit"),
            ("+", "operator"),
            ("±", "toggle"),
            ("0", "digit"),
            (".", "dot"),
            ("=", "equals"),
        ]

        for index, (text, kind) in enumerate(buttons):
            row, col = divmod(index, 4)
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Segoe UI", 18, "bold"),
                bg="#2f2f2f" if kind != "operator" and text not in {"=", "C", "⌫"} else "#ff9f0a",
                fg="white",
                relief="flat",
                bd=0,
                width=6,
                height=2,
                command=lambda t=text, k=kind: self.handle_button(t, k),
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

        for i in range(4):
            button_frame.columnconfigure(i, weight=1)
        for i in range(5):
            button_frame.rowconfigure(i, weight=1)

    def on_keypress(self, event):
        key = event.char
        if key in "0123456789.+-*/%":
            self.handle_button(key, "digit" if key.isdigit() or key in "." else "operator")
        elif key == "\r":
            self.handle_button("=", "equals")
        elif key == "\b":
            self.handle_button("⌫", "back")

    def handle_button(self, text, kind):
        if kind == "clear":
            self.expression = ""
            self.display_var.set("0")
        elif kind == "back":
            self.expression = self.expression[:-1]
            self.display_var.set(self.expression if self.expression else "0")
        elif kind == "toggle":
            if self.expression and self.expression[0] != "-":
                self.expression = "-" + self.expression
            elif self.expression.startswith("-"):
                self.expression = self.expression[1:]
            self.display_var.set(self.expression if self.expression else "0")
        elif kind == "digit" or kind == "dot":
            if text == "." and "." in self.expression.split(".")[-1]:
                return
            self.expression += text
            self.display_var.set(self.expression)
        elif kind == "operator":
            if not self.expression:
                return
            last_char = self.expression[-1]
            if last_char in "+-*/%":
                self.expression = self.expression[:-1] + self.map_operator(text)
            else:
                self.expression += self.map_operator(text)
            self.display_var.set(self.expression)
        elif kind == "equals":
            self.evaluate()

    def map_operator(self, symbol):
        mapping = {"÷": "/", "×": "*", "−": "-", "+": "+", "%": "%"}
        return mapping.get(symbol, symbol)

    def evaluate(self):
        try:
            expression = self.expression.replace("×", "*").replace("÷", "/").replace("−", "-")
            safe_expression = self._safe_eval(expression)
            result = str(safe_expression)
            self.expression = result
            self.display_var.set(result)
        except Exception:
            self.expression = ""
            self.display_var.set("Error")

    def _safe_eval(self, expression):
        allowed_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
                return allowed_ops[type(node.op)](_eval(node.left), _eval(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops:
                return allowed_ops[type(node.op)](_eval(node.operand))
            raise ValueError("Invalid expression")

        return _eval(ast.parse(expression, mode="eval"))


if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()
