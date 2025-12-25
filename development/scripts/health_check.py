import requests
import sys
from rich.console import Console
from rich.table import Table

console = Console()

def check_server(name, url):
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return True, response.json(), response.elapsed.total_seconds()
        return False, f"Status {response.status_code}", 0
    except Exception as e:
        return False, str(e), 0

def main():
    console.print("[bold cyan]TG-SYSTEM Connectivity Test[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Service Name")
    table.add_column("Port")
    table.add_column("Status")
    table.add_column("Latency")
    table.add_column("Response Payload")

    # 1. Core Kernel Check
    ok_core, data_core, lat_core = check_server("Core Kernel", "http://127.0.0.1:8000/")
    status_core = "[green]ONLINE[/green]" if ok_core else "[red]OFFLINE[/red]"
    
    table.add_row(
        "TG-CORE", 
        "8000", 
        status_core, 
        f"{lat_core:.3f}s", 
        str(data_core)[:50] + "..."
    )

    # 2. Commerce Engine Check
    ok_comm, data_comm, lat_comm = check_server("Commerce Engine", "http://127.0.0.1:8001/")
    status_comm = "[green]ONLINE[/green]" if ok_comm else "[red]OFFLINE[/red]"
    
    table.add_row(
        "TG-COMMERCE", 
        "8001", 
        status_comm, 
        f"{lat_comm:.3f}s", 
        str(data_comm)[:50] + "..."
    )

    console.print(table)
    
    if ok_core and ok_comm:
        console.print("\n[bold green]✅ All Systems Operational![/bold green]")
        console.print("You can now proceed with Frontend(POS) or External Integration.")
    else:
        console.print("\n[bold red]❌ System Partial Failure detected.[/bold red]")
        console.print("Please check the console windows for error logs.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass