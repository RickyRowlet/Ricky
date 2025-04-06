import tkinter as tk
from tkinter import ttk, messagebox
import database

class MisaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MISA Clone - Quản lý kho")

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=True, fill="both")

        self.build_warehouse_tab()

        self.build_sales_tab()
        self.build_accounting_tab()
        self.build_statistics_tab()
        database.init_user_file()

    def build_warehouse_tab(self):
        self.warehouse_tab = tk.Frame(self.tabs)
        self.tabs.add(self.warehouse_tab, text="Kho hàng")

        # --- Form nhập ---
        form_frame = tk.Frame(self.warehouse_tab)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Tên hàng").grid(row=0, column=0)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Số lượng").grid(row=1, column=0)
        self.quantity_entry = tk.Entry(form_frame)
        self.quantity_entry.grid(row=1, column=1)

        tk.Label(form_frame, text="Đơn giá").grid(row=2, column=0)
        self.price_entry = tk.Entry(form_frame)
        self.price_entry.grid(row=2, column=1)

        tk.Label(form_frame, text="Nhà cung cấp").grid(row=3, column=0)
        self.supplier_entry = tk.Entry(form_frame)
        self.supplier_entry.grid(row=3, column=1)

        self.add_button = tk.Button(form_frame, text="Thêm", command=self.add_product)
        self.add_button.grid(row=4, column=0, pady=5)

        self.update_button = tk.Button(form_frame, text="Sửa", command=self.update_product)
        self.update_button.grid(row=4, column=1)

        # --- Thanh tìm kiếm ---
        search_frame = tk.Frame(self.warehouse_tab)
        search_frame.pack()
        tk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT)
        tk.Button(search_frame, text="Tìm", command=self.search_product).pack(side=tk.LEFT)
        tk.Button(search_frame, text="Hiện tất cả", command=self.load_products).pack(side=tk.LEFT)

        # --- Bảng danh sách ---
        self.tree = ttk.Treeview(self.warehouse_tab, columns=("ID", "Tên", "SL", "Đơn giá", "NCC"), show="headings")
        for col in ("ID", "Tên", "SL", "Đơn giá", "NCC"):
            self.tree.heading(col, text=col)
        self.tree.pack(pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

        # --- Nút xóa ---
        tk.Button(self.warehouse_tab, text="Xóa sản phẩm", command=self.delete_product).pack()

        self.load_products()

    def add_product(self):
        name = self.name_entry.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()
        supplier = self.supplier_entry.get()
        if name and quantity and price and supplier:
            database.add_product(name, quantity, price, supplier)
            messagebox.showinfo("✔", "Đã thêm sản phẩm.")
            self.load_products()
        else:
            messagebox.showwarning("Lỗi", "Vui lòng điền đầy đủ thông tin.")

    def load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for product in database.get_products():
            self.tree.insert("", "end", values=product)

    def search_product(self):
        keyword = self.search_entry.get()
        results = database.search_products(keyword)
        self.tree.delete(*self.tree.get_children())
        for row in results:
            self.tree.insert("", "end", values=row)

    def on_select_row(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            self.selected_id = values[0]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[1])
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, values[2])
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, values[3])
            self.supplier_entry.delete(0, tk.END)
            self.supplier_entry.insert(0, values[4])

    def update_product(self):
        try:
            product_id = self.selected_id
        except AttributeError:
            messagebox.showwarning("Chưa chọn", "Hãy chọn sản phẩm để sửa.")
            return

        name = self.name_entry.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()
        supplier = self.supplier_entry.get()

        if name and quantity and price and supplier:
            database.update_product(product_id, name, quantity, price, supplier)
            messagebox.showinfo("✔", "Đã cập nhật.")
            self.load_products()
        else:
            messagebox.showwarning("Lỗi", "Vui lòng điền đủ thông tin.")

    def delete_product(self):
        try:
            product_id = self.selected_id
        except AttributeError:
            messagebox.showwarning("Chưa chọn", "Hãy chọn sản phẩm để xóa.")
            return
        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa?")
        if confirm:
            database.delete_product(product_id)
            messagebox.showinfo("✔", "Đã xóa.")
            self.load_products()

    def build_sales_tab(self):
        self.sales_tab = tk.Frame(self.tabs)
        self.tabs.add(self.sales_tab, text="Bán hàng")

        form = tk.Frame(self.sales_tab)
        form.pack(pady=10)

        tk.Label(form, text="Khách hàng").grid(row=0, column=0)
        self.customer_entry = tk.Entry(form)
        self.customer_entry.grid(row=0, column=1)

        tk.Label(form, text="Tổng tiền").grid(row=1, column=0)
        self.total_entry = tk.Entry(form)
        self.total_entry.grid(row=1, column=1)

        tk.Button(form, text="Tạo hóa đơn", command=self.add_invoice).grid(row=2, columnspan=2, pady=5)

        self.invoice_tree = ttk.Treeview(self.sales_tab, columns=("ID", "Ngày", "Khách", "Tổng"), show="headings")
        for col in ("ID", "Ngày", "Khách", "Tổng"):
            self.invoice_tree.heading(col, text=col)
        self.invoice_tree.pack()

        self.load_invoices()
        search_frame = tk.Frame(self.sales_tab)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Tìm khách hàng").grid(row=0, column=0)
        self.invoice_search_entry = tk.Entry(search_frame)
        self.invoice_search_entry.grid(row=0, column=1)

        tk.Label(search_frame, text="Từ ngày (yyyy-mm-dd)").grid(row=0, column=2)
        self.invoice_start_entry = tk.Entry(search_frame, width=12)
        self.invoice_start_entry.grid(row=0, column=3)

        tk.Label(search_frame, text="Đến ngày").grid(row=0, column=4)
        self.invoice_end_entry = tk.Entry(search_frame, width=12)
        self.invoice_end_entry.grid(row=0, column=5)

        tk.Button(search_frame, text="Lọc", command=self.filter_invoices).grid(row=0, column=6, padx=5)
        
    def filter_invoices(self):
        keyword = self.invoice_search_entry.get()
        start_date = self.invoice_start_entry.get()
        end_date = self.invoice_end_entry.get()

        results = database.search_invoices(keyword, start_date, end_date)

        self.invoice_tree.delete(*self.invoice_tree.get_children())
        for row in results:
            self.invoice_tree.insert("", "end", values=row)


    def add_invoice(self):
        customer = self.customer_entry.get()
        total = self.total_entry.get()
        if customer and total:
            try:
                total = float(total)
                database.add_invoice(customer, total)
                messagebox.showinfo("✔", "Hóa đơn đã tạo.")
                self.load_invoices()
            except ValueError:
                messagebox.showerror("Lỗi", "Tổng tiền phải là số.")
        else:
            messagebox.showwarning("Thiếu", "Vui lòng nhập đủ thông tin.")

    def load_invoices(self):
        for row in self.invoice_tree.get_children():
            self.invoice_tree.delete(row)
        for invoice in database.get_invoices():
            self.invoice_tree.insert("", "end", values=invoice)

    def build_accounting_tab(self):
        self.accounting_tab = tk.Frame(self.tabs)
        self.tabs.add(self.accounting_tab, text="Kế toán")

        form = tk.Frame(self.accounting_tab)
        form.pack(pady=10)

        tk.Label(form, text="Loại giao dịch (Thu/Chi)").grid(row=0, column=0)
        self.type_entry = tk.Entry(form)
        self.type_entry.grid(row=0, column=1)

        tk.Label(form, text="Số tiền").grid(row=1, column=0)
        self.amount_entry = tk.Entry(form)
        self.amount_entry.grid(row=1, column=1)

        tk.Label(form, text="Mô tả").grid(row=2, column=0)
        self.desc_entry = tk.Entry(form)
        self.desc_entry.grid(row=2, column=1)

        tk.Button(form, text="Thêm giao dịch", command=self.add_transaction).grid(row=3, columnspan=2, pady=5)

        self.trans_tree = ttk.Treeview(self.accounting_tab, columns=("ID", "Ngày", "Loại", "Số tiền", "Mô tả"), show="headings")
        for col in ("ID", "Ngày", "Loại", "Số tiền", "Mô tả"):
            self.trans_tree.heading(col, text=col)
        self.trans_tree.pack()

        self.load_transactions()
        search_frame = tk.Frame(self.accounting_tab)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Loại (thu/chi)").grid(row=0, column=0)
        self.trans_type_filter = tk.Entry(search_frame, width=8)
        self.trans_type_filter.grid(row=0, column=1)

        tk.Label(search_frame, text="Từ ngày").grid(row=0, column=2)
        self.trans_start_entry = tk.Entry(search_frame, width=12)
        self.trans_start_entry.grid(row=0, column=3)

        tk.Label(search_frame, text="Đến ngày").grid(row=0, column=4)
        self.trans_end_entry = tk.Entry(search_frame, width=12)
        self.trans_end_entry.grid(row=0, column=5)

        tk.Label(search_frame, text="Từ khóa").grid(row=0, column=6)
        self.trans_keyword_entry = tk.Entry(search_frame)
        self.trans_keyword_entry.grid(row=0, column=7)

        tk.Button(search_frame, text="Lọc", command=self.filter_transactions).grid(row=0, column=8, padx=5)

    def filter_transactions(self):
        t_type = self.trans_type_filter.get()
        keyword = self.trans_keyword_entry.get()
        start = self.trans_start_entry.get()
        end = self.trans_end_entry.get()

        results = database.search_transactions(t_type, keyword, start, end)

        self.trans_tree.delete(*self.trans_tree.get_children())
        for row in results:
            self.trans_tree.insert("", "end", values=row)

    def add_transaction(self):
        t_type = self.type_entry.get()
        amount = self.amount_entry.get()
        desc = self.desc_entry.get()
        if t_type and amount and desc:
            try:
                amount = float(amount)
                database.add_transaction(t_type, amount, desc)
                messagebox.showinfo("✔", "Giao dịch đã lưu.")
                self.load_transactions()
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiền phải là số.")
        else:
            messagebox.showwarning("Thiếu", "Vui lòng điền đủ thông tin.")

    def load_transactions(self):
        for row in self.trans_tree.get_children():
            self.trans_tree.delete(row)
        for trans in database.get_transactions():
            self.trans_tree.insert("", "end", values=trans)
    def build_statistics_tab(self):
        self.stats_tab = tk.Frame(self.tabs)
        self.tabs.add(self.stats_tab, text="Thống kê")

        tk.Button(self.stats_tab, text="Làm mới thống kê", command=self.load_statistics).pack(pady=10)

        self.stats_text = tk.Text(self.stats_tab, height=15, width=70, font=("Consolas", 12))
        self.stats_text.pack()

        self.load_statistics()

    def load_statistics(self):
        inventory_qty, inventory_value = database.get_inventory_summary()
        sales_total = database.get_sales_summary()
        income, expense = database.get_accounting_summary()

        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, f"TỒN KHO\n")
        self.stats_text.insert(tk.END, f" - Tổng số lượng: {inventory_qty}\n")
        self.stats_text.insert(tk.END, f" - Tổng giá trị:  {inventory_value:,.0f} VND\n\n")

        self.stats_text.insert(tk.END, f"DOANH THU BÁN HÀNG\n")
        self.stats_text.insert(tk.END, f" - Tổng doanh thu: {sales_total:,.0f} VND\n\n")

        self.stats_text.insert(tk.END, f"KẾ TOÁN\n")
        self.stats_text.insert(tk.END, f" - Tổng THU:  {income:,.0f} VND\n")
        self.stats_text.insert(tk.END, f" - Tổng CHI:  {expense:,.0f} VND\n")
        self.stats_text.insert(tk.END, f" - CHÊNH LỆCH: {income - expense:,.0f} VND\n")

if __name__ == "__main__":
    database.create_files()
    root = tk.Tk()
    app = MisaApp(root)
    root.mainloop()