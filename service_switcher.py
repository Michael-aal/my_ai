import subprocess
import tkinter as tk
from tkinter import ttk, messagebox


def run_powershell(command):
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)


def get_services():
    out, err = run_powershell(
        "Get-Service | Sort-Object DisplayName | "
        "ForEach-Object { '{0}|{1}|{2}' -f $_.Name, $_.DisplayName, $_.Status }"
    )
    services = []
    for line in out.splitlines():
        parts = line.split("|")
        if len(parts) == 3:
            services.append({
                "name": parts[0].strip(),
                "display": parts[1].strip(),
                "status": parts[2].strip(),
            })
    return services


def is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


class ServiceSwitcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Service Switcher")
        self.root.geometry("760x540")
        self.services = []
        self.admin = is_admin()

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=10, pady=8)

        tk.Label(top, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.filter_services())
        tk.Entry(top, textvariable=self.search_var, width=30).pack(side="left", padx=6)

        tk.Button(top, text="Refresh", command=self.refresh).pack(side="right")

        self.status_var = tk.StringVar(
            value="Admin mode: ON" if self.admin else "Admin mode: OFF (Start/Stop may fail)"
        )
        tk.Label(self.root, textvariable=self.status_var, anchor="w",
                 fg="green" if self.admin else "red").pack(fill="x", padx=10)

        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=6)

        self.tree = ttk.Treeview(frame, columns=("name", "display", "status"), show="headings", height=16)
        self.tree.heading("name", text="Service Name")
        self.tree.heading("display", text="Display Name")
        self.tree.heading("status", text="Status")
        self.tree.column("name", width=200)
        self.tree.column("display", width=380)
        self.tree.column("status", width=90)
        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        btns = tk.Frame(self.root)
        btns.pack(fill="x", padx=10, pady=8)

        self.start_btn = tk.Button(btns, text="▶  Switch ON (Start)", width=18,
                                   command=lambda: self.change_state("start"))
        self.start_btn.pack(side="left", padx=4)

        self.stop_btn = tk.Button(btns, text="■  Switch OFF (Stop)", width=18,
                                  command=lambda: self.change_state("stop"))
        self.stop_btn.pack(side="left", padx=4)

        self.restart_btn = tk.Button(btns, text="↻  Restart", width=14,
                                     command=lambda: self.change_state("restart"))
        self.restart_btn.pack(side="left", padx=4)

        self.selected_status = tk.StringVar()
        tk.Label(btns, textvariable=self.selected_status).pack(side="right", padx=6)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh(self):
        self.status_var.set("Loading services...")
        self.root.update_idletasks()
        self.services = get_services()
        self.filter_services()
        self.status_var.set(
            f"Loaded {len(self.services)} services | "
            + ("Admin mode: ON" if self.admin else "Admin mode: OFF (Start/Stop may fail)")
        )

    def filter_services(self):
        query = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        for s in self.services:
            if (query in s["name"].lower() or query in s["display"].lower()):
                tag = "running" if s["status"] == "Running" else "stopped"
                self.tree.insert("", "end", iid=s["name"],
                                 values=(s["name"], s["display"], s["status"]),
                                 tags=(tag,))

    def on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            self.selected_status.set("")
            return
        name = sel[0]
        svc = next((s for s in self.services if s["name"] == name), None)
        if svc:
            self.selected_status.set(f"{svc['name']}: {svc['status']}")

    def change_state(self, action):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a service first.")
            return

        name = sel[0]
        if not self.admin:
            if messagebox.askyesno(
                "Admin required",
                "Controlling services needs Administrator rights.\n"
                "Restart the app as administrator?"
            ):
                self.elevate_and_exit()
            return

        confirm = messagebox.askyesno(
            "Confirm",
            f"Are you sure you want to {action.upper()} the service\n'{name}'?"
        )
        if not confirm:
            return

        if action == "start":
            cmd = f"Start-Service -Name '{name}' -ErrorAction Stop"
        elif action == "stop":
            cmd = f"Stop-Service -Name '{name}' -Force -ErrorAction Stop"
        else:
            cmd = f"Restart-Service -Name '{name}' -Force -ErrorAction Stop"

        _, err = run_powershell(cmd)
        if err:
            messagebox.showerror("Error", f"Failed to {action} '{name}':\n{err}")
        else:
            messagebox.showinfo("Done", f"Service '{name}' {action} command sent.")
        self.refresh()

    def elevate_and_exit(self):
        import ctypes, sys
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Elevation failed", str(e))


def main():
    root = tk.Tk()
    root.configure(bg="#f5f5f5")
    style = ttk.Style(root)
    try:
        style.theme_use("vista")
    except Exception:
        pass
    style.configure("Treeview", rowheight=24)
    ServiceSwitcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
