
import time
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.console import Console
from rich import box
from sensor_core import SensorManager

# Configuración de rangos para las barras visuales (ajusta según tu proceso)
MAX_TEMP = 100.0
MAX_HUM = 100.0
MAX_RAD = 1000.0
MAX_MASA = 5000.0 # Ejemplo: 5kg max

def make_bar(value, max_val, color="green"):
    """Crea una barra de progreso textual"""
    width = 20
    percent = min(max(value / max_val, 0), 1)
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{color}]{bar}[/{color}] {value:.2f}"

def generate_layout():
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    return layout

def create_dashboard(data):
    # Tabla de Sensores Ambientales
    table_env = Table(box=box.ROUNDED, title="Sensores Ambientales", expand=True)
    table_env.add_column("Sensor", style="cyan")
    table_env.add_column("Valor", justify="right")
    table_env.add_column("Gráfica", justify="left")

    table_env.add_row("Temp 1", f"{data['temperatura1_C']} °C", make_bar(data['temperatura1_C'], MAX_TEMP, "red"))
    table_env.add_row("Hum 1", f"{data['humedad1_RH']} %", make_bar(data['humedad1_RH'], MAX_HUM, "blue"))
    table_env.add_row("Temp 2", f"{data['temperatura2_C']} °C", make_bar(data['temperatura2_C'], MAX_TEMP, "red"))
    table_env.add_row("Hum 2", f"{data['humedad2_RH']} %", make_bar(data['humedad2_RH'], MAX_HUM, "blue"))
    table_env.add_row("Radiación", f"{data['radiacion_W_m2']} W/m²", make_bar(data['radiacion_W_m2'], MAX_RAD, "yellow"))

    # Tabla de Proceso (Termopares y Masa)
    table_proc = Table(box=box.ROUNDED, title="Variables de Proceso", expand=True)
    table_proc.add_column("Variable", style="magenta")
    table_proc.add_column("Valor", justify="right")
    
    table_proc.add_row("Termopar 1", f"{data['termopar1_C']} °C")
    table_proc.add_row("Termopar 2", f"{data['termopar2_C']} °C")
    table_proc.add_row("MASA (Balanza)", f"[bold green]{data['masa_g']:.2f} g[/]")

    # Estado de Ventiladores
    fans = data['ventiladores']
    fan_status = "  ".join([
        f"[bold white on green] ON [/]" if f else "[bold white on red] OFF [/]" 
        for f in fans
    ])
    
    panel_fans = Panel(
        Align.center(f"V1: {fans[0]}   V2: {fans[1]}   V3: {fans[2]}\n\n{fan_status}"),
        title="Estado Ventiladores",
        border_style="green"
    )

    return table_env, table_proc, panel_fans

def run_monitor():
    manager = SensorManager()
    manager.start()
    
    console = Console()
    layout = generate_layout()
    
    layout["header"].update(Panel(Align.center("[bold gold1]SISTEMA DE MONITOREO SECADOR IOT[/]"), style="bold white"))
    layout["footer"].update(Panel(Align.center("Presiona [bold red]Ctrl+C[/] para salir"), style="dim"))

    try:
        with Live(layout, refresh_per_second=4, screen=True):
            while True:
                data = manager.get_data()
                
                t_env, t_proc, p_fans = create_dashboard(data)
                
                layout["left"].update(Panel(t_env))
                layout["right"].split(
                    Layout(Panel(t_proc), ratio=2),
                    Layout(p_fans, ratio=1)
                )
                time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop()
        print("Monitor cerrado.")

if __name__ == "__main__":
    run_monitor()
