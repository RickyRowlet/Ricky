import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
import database
from datetime import datetime

class MisaApp:
    def __init__(self, root, role):
        self.root = root
        self.role = role  # Lưu quyền của tài khoản
        self.root.title("Phần mềm quản lý bán hàng Misa")
        self.root.geometry("1000x700")

        self.configure_styles()

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=True, fill="both", padx=10, pady=10)

        self.build_inventory_tab()
        self.build_sales_tab()
        self.build_accounting_tab()
        self.build_statistics_tab()

        if self.role == "admin":
            self.build_user_management_tab()  # Chỉ admin mới có tab quản lý tài khoản

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('Treeview', font=('Helvetica', 10), rowheight=25)
        style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))

    # Tab "Kho"
    def build_inventory_tab(self):
        self.inventory_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.inventory_tab, text="Kho")

        self.tree = ttk.Treeview(self.inventory_tab, columns=("ID", "Name", "Quantity", "Price"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Tên sản phẩm")
        self.tree.heading("Quantity", text="Số lượng")
        self.tree.heading("Price", text="Đơn giá")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.inventory_tab)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Thêm sản phẩm", command=self.add_product_window).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Xóa sản phẩm", command=self.delete_product).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Sửa sản phẩm", command=self.edit_product_window).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Sắp xếp theo tên", command=self.sort_products_by_name).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Làm mới", command=self.load_inventory).pack(side="left", padx=5)

        self.load_inventory()

    def add_product_window(self):
        def save_product():
            name = entry_name.get()
            quantity = entry_quantity.get()
            price = entry_price.get()
            if name and quantity and price:
                try:
                    database.add_product(name, int(quantity), float(price), "Nhà cung cấp")
                    self.load_inventory()
                    add_window.destroy()
                except ValueError:
                    messagebox.showerror("Lỗi", "Số lượng và đơn giá phải là số hợp lệ!")
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin sản phẩm!")

        add_window = tk.Toplevel(self.root)
        add_window.title("Thêm sản phẩm")

        ttk.Label(add_window, text="Tên sản phẩm").grid(row=0, column=0, padx=10, pady=5)
        entry_name = ttk.Entry(add_window)
        entry_name.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(add_window, text="Số lượng").grid(row=1, column=0, padx=10, pady=5)
        entry_quantity = ttk.Entry(add_window)
        entry_quantity.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(add_window, text="Đơn giá").grid(row=2, column=0, padx=10, pady=5)
        entry_price = ttk.Entry(add_window)
        entry_price.grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(add_window, text="Lưu", command=save_product).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm để xóa!")
            return

        product_id = self.tree.item(selected_item, "values")[0]
        database.delete_product(int(product_id))
        self.load_inventory()

    def edit_product_window(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm để sửa!")
            return

        product = self.tree.item(selected_item, "values")

        def save_changes():
            new_name = entry_name.get()
            new_quantity = entry_quantity.get()
            new_price = entry_price.get()
            if new_name and new_quantity and new_price:
                database.update_product(int(product[0]), new_name, int(new_quantity), float(new_price), "Nhà cung cấp")
                self.load_inventory()
                edit_window.destroy()

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Sửa sản phẩm")

        ttk.Label(edit_window, text="Tên sản phẩm").grid(row=0, column=0, padx=10, pady=5)
        entry_name = ttk.Entry(edit_window)
        entry_name.insert(0, product[1])
        entry_name.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(edit_window, text="Số lượng").grid(row=1, column=0, padx=10, pady=5)
        entry_quantity = ttk.Entry(edit_window)
        entry_quantity.insert(0, product[2])
        entry_quantity.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(edit_window, text="Đơn giá").grid(row=2, column=0, padx=10, pady=5)
        entry_price = ttk.Entry(edit_window)
        entry_price.insert(0, product[3])
        entry_price.grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(edit_window, text="Lưu", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    def sort_products_by_name(self):
        products = database.get_products()
        sorted_products = sorted(products, key=lambda x: x[1].lower())
        self.tree.delete(*self.tree.get_children())
        for product in sorted_products:
            self.tree.insert("", "end", values=product)

    def load_inventory(self):
        self.tree.delete(*self.tree.get_children())
        for product in database.get_products():
            self.tree.insert("", "end", values=product)

    # Tab "Bán hàng"
    def build_sales_tab(self):
        self.sales_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.sales_tab, text="Bán hàng")

        ttk.Label(self.sales_tab, text="Danh sách hóa đơn").pack()
        self.sales_tree = ttk.Treeview(self.sales_tab, columns=("ID", "Date", "Customer", "Total"), show="headings")
        self.sales_tree.heading("ID", text="ID")
        self.sales_tree.heading("Date", text="Ngày")
        self.sales_tree.heading("Customer", text="Khách hàng")
        self.sales_tree.heading("Total", text="Tổng tiền")
        self.sales_tree.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(self.sales_tab, text="Thêm hóa đơn", command=self.add_invoice_window).pack(side="left", padx=5, pady=5)
        ttk.Button(self.sales_tab, text="Làm mới", command=self.load_sales).pack(side="left", padx=5, pady=5)

    def add_invoice_window(self):
        def save_invoice():
            customer = entry_customer.get()
            total = entry_total.get()
            if customer and total:
                try:
                    database.add_invoice(customer, float(total))
                    self.load_sales()
                    add_window.destroy()
                except ValueError:
                    messagebox.showerror("Lỗi", "Tổng tiền phải là số hợp lệ!")
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin hóa đơn!")

        add_window = tk.Toplevel(self.root)
        add_window.title("Thêm hóa đơn")

        ttk.Label(add_window, text="Khách hàng").grid(row=0, column=0, padx=10, pady=5)
        entry_customer = ttk.Entry(add_window)
        entry_customer.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(add_window, text="Tổng tiền").grid(row=1, column=0, padx=10, pady=5)
        entry_total = ttk.Entry(add_window)
        entry_total.grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(add_window, text="Lưu", command=save_invoice).grid(row=2, column=0, columnspan=2, pady=10)

    def load_sales(self):
        self.sales_tree.delete(*self.sales_tree.get_children())
        for invoice in database.get_invoices():
            self.sales_tree.insert("", "end", values=invoice)

    # Tab "Kế toán"
    def build_accounting_tab(self):
        self.accounting_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.accounting_tab, text="Kế toán")

        ttk.Label(self.accounting_tab, text="Danh sách giao dịch").pack()
        self.accounting_tree = ttk.Treeview(self.accounting_tab, columns=("ID", "Date", "Type", "Amount", "Description"), show="headings")
        self.accounting_tree.heading("ID", text="ID")
        self.accounting_tree.heading("Date", text="Ngày")
        self.accounting_tree.heading("Type", text="Loại")
        self.accounting_tree.heading("Amount", text="Số tiền")
        self.accounting_tree.heading("Description", text="Mô tả")
        self.accounting_tree.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(self.accounting_tab, text="Thêm giao dịch", command=self.add_transaction_window).pack(side="left", padx=5, pady=5)
        ttk.Button(self.accounting_tab, text="Làm mới", command=self.load_accounting).pack(side="left", padx=5, pady=5)

    def add_transaction_window(self):
        def save_transaction():
            trans_type = combo_type.get()
            amount = entry_amount.get()
            description = entry_description.get()
            if trans_type and amount and description:
                try:
                    database.add_transaction(trans_type, float(amount), description)
                    self.load_accounting()
                    add_window.destroy()
                except ValueError:
                    messagebox.showerror("Lỗi", "Số tiền phải là số hợp lệ!")
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin giao dịch!")

        add_window = tk.Toplevel(self.root)
        add_window.title("Thêm giao dịch")

        ttk.Label(add_window, text="Loại").grid(row=0, column=0, padx=10, pady=5)
        combo_type = ttk.Combobox(add_window, values=["Thu", "Chi"], state="readonly")
        combo_type.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(add_window, text="Số tiền").grid(row=1, column=0, padx=10, pady=5)
        entry_amount = ttk.Entry(add_window)
        entry_amount.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(add_window, text="Mô tả").grid(row=2, column=0, padx=10, pady=5)
        entry_description = ttk.Entry(add_window)
        entry_description.grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(add_window, text="Lưu", command=save_transaction).grid(row=3, column=0, columnspan=2, pady=10)

    def load_accounting(self):
        self.accounting_tree.delete(*self.accounting_tree.get_children())
        for transaction in database.get_transactions():
            self.accounting_tree.insert("", "end", values=transaction)

    # Tab "Thống kê"
    def build_statistics_tab(self):
        self.stats_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.stats_tab, text="Thống kê")

        ttk.Label(self.stats_tab, text="Tổng kết cuối ngày").pack()
        self.stats_text = tk.Text(self.stats_tab, height=15, wrap="word")
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(self.stats_tab, text="Tải thống kê", command=self.load_statistics).pack(pady=5)

    def load_statistics(self):
        # Lấy ngày hiện tại
        today = datetime.now().strftime("%Y-%m-%d")

        # Lọc dữ liệu tồn kho (không cần lọc theo ngày vì tồn kho là trạng thái hiện tại)
        inventory_qty, inventory_value = database.get_inventory_summary()

        # Lọc doanh thu theo ngày hiện tại
        sales_total = 0
        for invoice in database.get_invoices():
            invoice_date = invoice[1].split(" ")[0]  # Lấy phần ngày từ chuỗi datetime
            if invoice_date == today:
                sales_total += invoice[3]

        # Lọc thu nhập và chi phí theo ngày hiện tại
        income = 0
        expense = 0
        for transaction in database.get_transactions():
            transaction_date = transaction[1].split(" ")[0]  # Lấy phần ngày từ chuỗi datetime
            if transaction_date == today:
                if transaction[2].lower() == "thu":
                    income += transaction[3]
                elif transaction[2].lower() == "chi":
                    expense += transaction[3]

        # Hiển thị kết quả trong tab "Thống kê"
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "═"*50 + " TỔNG KẾT CUỐI NGÀY " + "═"*50 + "\n\n")
        self.stats_text.insert(tk.END, f" • Tổng số lượng tồn kho: {inventory_qty}\n")
        self.stats_text.insert(tk.END, f" • Tổng giá trị tồn kho:  {inventory_value:,.0f} VND\n")
        self.stats_text.insert(tk.END, f" • Tổng doanh thu hôm nay: {sales_total:,.0f} VND\n")
        self.stats_text.insert(tk.END, f" • Tổng thu nhập hôm nay:  {income:,.0f} VND\n")
        self.stats_text.insert(tk.END, f" • Tổng chi phí hôm nay:   {expense:,.0f} VND\n")
        self.stats_text.insert(tk.END, f" • Lợi nhuận hôm nay:      {income - expense:,.0f} VND\n")

    def build_user_management_tab(self):
        self.user_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.user_tab, text="Quản lý tài khoản")

        self.user_tree = ttk.Treeview(self.user_tab, columns=("Username", "Role"), show="headings")
        self.user_tree.heading("Username", text="Tên đăng nhập")
        self.user_tree.heading("Role", text="Quyền")
        self.user_tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = ttk.Frame(self.user_tab)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Thêm tài khoản", command=self.add_user_window).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Làm mới", command=self.load_users).pack(side="left", padx=5)

        self.load_users()

    def add_user_window(self):
        def save_user():
            username = entry_username.get()
            password = entry_password.get()
            role = combo_role.get()
            if username and password and role:
                try:
                    database.add_user(username, password, role)
                    self.load_users()
                    add_window.destroy()
                except ValueError as e:
                    messagebox.showerror("Lỗi", str(e))
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")

        add_window = tk.Toplevel(self.root)
        add_window.title("Thêm tài khoản")

        ttk.Label(add_window, text="Tên đăng nhập").grid(row=0, column=0, padx=10, pady=5)
        entry_username = ttk.Entry(add_window)
        entry_username.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(add_window, text="Mật khẩu").grid(row=1, column=0, padx=10, pady=5)
        entry_password = ttk.Entry(add_window, show="*")
        entry_password.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(add_window, text="Quyền").grid(row=2, column=0, padx=10, pady=5)
        combo_role = ttk.Combobox(add_window, values=["admin", "user"], state="readonly")
        combo_role.grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(add_window, text="Lưu", command=save_user).grid(row=3, column=0, columnspan=2, pady=10)

    def load_users(self):
        self.user_tree.delete(*self.user_tree.get_children())
        for user in database.get_users():
            self.user_tree.insert("", "end", values=(user[0], user[2]))

if __name__ == "__main__":
    root = tk.Tk()
    app = MisaApp(root, "admin")  # Thay "admin" bằng "user" để kiểm tra quyền hạn
    root.mainloop()
