import tkinter as tk

class CalculatorWindow(tk.Toplevel):
    FEE_RATE = 0.001  # 0.1%

    def __init__(self, master, usdt_balance, btc_balance):
        super().__init__(master)
        self.title("🖩 Calculadora de Órdenes")
        self.config(bg="DarkGoldenrod")
        self.usdt_balance = usdt_balance
        self.btc_balance = btc_balance

        # BUY side
        buy_f = tk.LabelFrame(self, text="Buy BTC", bg="DarkGoldenrod", fg="white", font=("CrushYourEnemies",12))
        buy_f.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self._build_side(buy_f, is_buy=True)

        # SELL side
        sell_f = tk.LabelFrame(self, text="Sell BTC", bg="DarkGoldenrod", fg="white", font=("CrushYourEnemies",12))
        sell_f.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self._build_side(sell_f, is_buy=False)

    def _build_side(self, parent, is_buy):
        # Variables
        price_var  = tk.DoubleVar(value=0.0)
        amt_var    = tk.DoubleVar(value=0.0)
        total_var  = tk.DoubleVar(value=0.0)
        fee_var    = tk.DoubleVar(value=0.0)

        # Available
        avail = self.usdt_balance if is_buy else self.btc_balance
        tk.Label(parent, text=f"Available: {avail:.6f} {'USDT' if is_buy else 'BTC'}",
                 bg="DarkGoldenrod", fg="white").grid(row=0, column=0, columnspan=2, sticky="w")

        # Price
        tk.Label(parent, text="Price:", bg="DarkGoldenrod", fg="white").grid(row=1, column=0, sticky="e")
        e_price = tk.Entry(parent, textvariable=price_var); e_price.grid(row=1, column=1, sticky="ew")

        # Amount
        tk.Label(parent, text="Amount:", bg="DarkGoldenrod", fg="white").grid(row=2, column=0, sticky="e")
        e_amt = tk.Entry(parent, textvariable=amt_var); e_amt.grid(row=2, column=1, sticky="ew")

        # Total (readonly)
        tk.Label(parent, text="Total:", bg="DarkGoldenrod", fg="white").grid(row=3, column=0, sticky="e")
        e_tot = tk.Entry(parent, textvariable=total_var, state="readonly"); e_tot.grid(row=3, column=1, sticky="ew")

        # Est. Fee
        lbl_fee = tk.Label(parent, text="Fee:", bg="DarkGoldenrod", fg="white")
        lbl_fee.grid(row=4, column=0, sticky="e")
        val_fee = tk.Label(parent, textvariable=fee_var, bg="Gold"); val_fee.grid(row=4, column=1, sticky="ew")

        # make columns expand
        parent.grid_columnconfigure(1, weight=1)

        def recalc(*_):
            try:
                p = price_var.get()
            except tk.TclError:
                p = 0.0
            try:
                a = amt_var.get()
            except tk.TclError:
                a = 0.0
            # Total = precio * cantidad
            t = p * a
            total_var.set(t)
            fee_var.set(t * self.FEE_RATE)
 
         # trace changes
        price_var.trace_add("write", recalc)
        amt_var.trace_add("write", recalc)