import flet as ft
from datetime import datetime, timedelta
import calendar
import re

class Tenant:
    def __init__(self, name, rent_amount, floor, apartment_type, phone_number, starting_date):
        self.name = name
        self.rent_amount = rent_amount
        self.floor = floor
        self.apartment_type = apartment_type
        self.phone_number = phone_number
        self.starting_date = starting_date
        self.rent_paid = False
        self.advance_paid = False
        self.payment_method = None
        self.payment_date = None
        self.rent_period = None
        self.balance = 0
        self.last_payment_amount = 0

class RentManagementApp:
    def __init__(self):
        self.tenants = []

    def add_tenant(self, tenant):
        self.tenants.append(tenant)

    def mark_rent_paid(self, tenant_name, payment_method, rent_period, amount_paid):
        for tenant in self.tenants:
            if tenant.name == tenant_name:
                tenant.rent_paid = amount_paid >= tenant.rent_amount
                tenant.balance += amount_paid - tenant.rent_amount
                tenant.payment_method = payment_method
                tenant.payment_date = datetime.now()
                tenant.rent_period = rent_period
                tenant.advance_paid = rent_period == "Advance"
                tenant.last_payment_amount = amount_paid
                return True
        return False

    def get_unpaid_tenants(self):
        return [tenant for tenant in self.tenants if not tenant.rent_paid]

def main(page: ft.Page):
    page.title = "Landlord Rent Management"
    
    app = RentManagementApp()

    def update_tenant_list():
        tenant_list.controls.clear()
        for tenant in app.tenants:
            rent_status = "Paid" if tenant.rent_paid else f"Unpaid (Balance: ${tenant.balance:.2f})"
            advance_status = "Advance Paid" if tenant.advance_paid else "No Advance"
            tenant_list.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{tenant.name} - {tenant.apartment_type}"),
                    subtitle=ft.Column([
                        ft.Text(f"Floor: {tenant.floor}, Rent: ${tenant.rent_amount:.2f}"),
                        ft.Text(f"Phone: {tenant.phone_number}, Start Date: {tenant.starting_date}")
                    ]),
                    trailing=ft.Column([
                        ft.Text(rent_status),
                        ft.Text(advance_status)
                    ])
                )
            )
        page.update()

    def view_tenants(e):
        main_content.visible = True
        payments_list.visible = False
        page.update()

    def view_payments(e):
        main_content.visible = False
        payments_list.visible = True
        update_payments_list()
        page.update()

    def update_payments_list():
        payments_list.controls.clear()
        for tenant in app.tenants:
            if tenant.payment_date:
                payments_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{tenant.name} - ${tenant.last_payment_amount:.2f}"),
                        subtitle=ft.Text(f"Paid on: {tenant.payment_date.strftime('%d-%B-%Y')}"),
                        trailing=ft.Column([
                            ft.Text(f"Method: {tenant.payment_method}"),
                            ft.Text(f"Tag: {tenant.rent_period}"),
                            ft.Text(f"Balance: ${tenant.balance:.2f}")
                        ])
                    )
                )
        page.update()

    def open_add_tenant_dialog(e):
        page.overlay.append(add_tenant_dialog)
        add_tenant_dialog.open = True
        page.update()

    def open_add_payment_dialog(e):
        tenant_name_dropdown.options = [ft.dropdown.Option(tenant.name) for tenant in app.tenants]
        tenant_name_dropdown.value = None
        payment_method_dropdown.value = None
        payment_tag_dropdown.value = None
        custom_tag_input.value = ""
        amount_input.value = ""
        page.overlay.append(add_payment_dialog)
        add_payment_dialog.open = True
        page.update()

    def close_dialog(e):
        if add_tenant_dialog in page.overlay:
            add_tenant_dialog.open = False
            page.overlay.remove(add_tenant_dialog)
        if add_payment_dialog in page.overlay:
            add_payment_dialog.open = False
            page.overlay.remove(add_payment_dialog)
        page.update()

    def add_tenant_clicked(e):
        name = tenant_name_input.value
        rent = float(rent_input.value) if rent_input.value else 0
        floor = floor_input.value
        apartment_type = apartment_type_dropdown.value
        phone_number = phone_input.value
        starting_date = starting_date_input.value

        if not name or not rent or not floor or not apartment_type or not phone_number:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Please fill in all fields.")))
            return

        valid_date = validate_date(starting_date)
        if not valid_date:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Invalid date format. Please use dd-month-yyyy.")))
            return

        app.add_tenant(Tenant(name, rent, floor, apartment_type, phone_number, starting_date))
        update_tenant_list()
        close_dialog(e)
        view_tenants(e)

    def mark_paid_clicked(e):
        tenant_name = tenant_name_dropdown.value
        payment_method = payment_method_dropdown.value
        payment_tag = payment_tag_dropdown.value
        amount_paid = float(amount_input.value) if amount_input.value else 0

        if not tenant_name or not payment_method or not payment_tag or amount_paid <= 0:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Please fill in all fields with valid values.")))
            return

        if payment_tag == "Custom":
            payment_tag = custom_tag_input.value
            if not payment_tag:
                page.show_snack_bar(ft.SnackBar(content=ft.Text("Please enter a custom tag.")))
                return

        if app.mark_rent_paid(tenant_name, payment_method, payment_tag, amount_paid):
            update_tenant_list()
            close_dialog(e)
            view_payments(e)
        else:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Failed to mark payment. Please try again.")))

    def toggle_custom_tag(e):
        custom_tag_input.visible = payment_tag_dropdown.value == "Custom"
        page.update()

    def validate_date(date_str):
        try:
            return datetime.strptime(date_str, "%d-%B-%Y")
        except ValueError:
            return None

    def validate_input(e):
        if e.control == tenant_name_input:
            e.control.value = re.sub(r'[^a-zA-Z\s]', '', e.control.value)
        elif e.control == rent_input or e.control == phone_input or e.control == amount_input:
            e.control.value = re.sub(r'[^0-9.]', '', e.control.value)
        e.control.update()

    def update_amount_input(e):
        selected_tenant = next((tenant for tenant in app.tenants if tenant.name == tenant_name_dropdown.value), None)
        if selected_tenant:
            amount_input.value = str(selected_tenant.rent_amount)
        else:
            amount_input.value = ""
        page.update()

    tenant_name_input = ft.TextField(
        label="Tenant Name",
        on_change=validate_input
    )
    rent_input = ft.TextField(
        label="Rent Amount",
        on_change=validate_input
    )
    floor_input = ft.TextField(label="Floor")
    apartment_type_dropdown = ft.Dropdown(
        label="Apartment Type",
        options=[
            ft.dropdown.Option("1BK"),
            ft.dropdown.Option("1BHK"),
            ft.dropdown.Option("2BHK"),
        ],
    )
    phone_input = ft.TextField(
        label="Phone Number",
        on_change=validate_input
    )
    starting_date_input = ft.TextField(
        label="Starting Date (dd-month-yyyy)",
        value=datetime.now().strftime("%d-%B-%Y")
    )

    add_tenant_dialog = ft.AlertDialog(
        title=ft.Text("Add New Tenant"),
        content=ft.Column([
            tenant_name_input,
            rent_input,
            floor_input,
            apartment_type_dropdown,
            phone_input,
            starting_date_input,
        ], tight=True),
        actions=[
            ft.ElevatedButton("Add", on_click=add_tenant_clicked),
            ft.ElevatedButton("Cancel", on_click=close_dialog),
        ],
    )

    tenant_name_dropdown = ft.Dropdown(
        label="Tenant Name",
        on_change=update_amount_input
    )
    payment_method_dropdown = ft.Dropdown(
        label="Payment Method",
        options=[
            ft.dropdown.Option("Cash"),
            ft.dropdown.Option("Online Transaction"),
        ],
    )
    payment_tag_dropdown = ft.Dropdown(
        label="Payment Tag",
        options=[
            ft.dropdown.Option("Rent"),
            ft.dropdown.Option("Advance"),
            ft.dropdown.Option("Maintenance"),
            ft.dropdown.Option("Custom"),
        ],
        on_change=toggle_custom_tag
    )
    custom_tag_input = ft.TextField(
        label="Custom Tag",
        visible=False
    )
    amount_input = ft.TextField(
        label="Amount Paid",
        on_change=validate_input
    )

    add_payment_dialog = ft.AlertDialog(
        title=ft.Text("Add Payment"),
        content=ft.Column([
            tenant_name_dropdown,
            payment_method_dropdown,
            payment_tag_dropdown,
            custom_tag_input,
            amount_input,
        ], tight=True),
        actions=[
            ft.ElevatedButton("Add Payment", on_click=mark_paid_clicked),
            ft.ElevatedButton("Cancel", on_click=close_dialog),
        ],
    )

    tenant_list = ft.ListView(expand=True, spacing=10, padding=20)
    payments_list = ft.ListView(expand=True, spacing=10, padding=20, visible=False)

    def show_action_dialog(e):
        action_dialog = ft.AlertDialog(
            title=ft.Text("Choose an action"),
            actions=[
                ft.ElevatedButton("Add Tenant", on_click=open_add_tenant_dialog),
                ft.ElevatedButton("Add Payment", on_click=open_add_payment_dialog),
            ],
        )
        page.dialog = action_dialog
        page.dialog.open = True
        page.update()

    fab = ft.FloatingActionButton(
        icon=ft.icons.ADD,
        on_click=show_action_dialog
    )

    main_content = ft.Column([
        ft.Text("Tenant List", size=20, weight=ft.FontWeight.BOLD),
        tenant_list,
    ], expand=True)

    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.HOME_OUTLINED,
                selected_icon=ft.icons.HOME,
                label="Tenants"
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.MONEY_OUTLINED,
                selected_icon=ft.icons.MONEY,
                label="Payments"
            ),
        ],
        on_change=lambda e: view_tenants(e) if e.control.selected_index == 0 else view_payments(e)
    )

    page.add(
        ft.Row(
            [
                nav_rail,
                ft.VerticalDivider(width=1),
                ft.Column([main_content, payments_list], expand=True),
            ],
            expand=True,
        )
    )
    page.floating_action_button = fab
    page.update()

ft.app(target=main)