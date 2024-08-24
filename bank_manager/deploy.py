import subprocess
import sys


def run_command(command, check=True):
    """Ejecuta un comando y muestra la salida en tiempo real."""
    print(f"Ejecutando: {command}")
    result = subprocess.run(command, shell=True, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)


def main():
    try:
        # Actualizar el repositorio
        run_command("git pull origin main")

        # Definir el directorio del entorno virtual y el directorio del proyecto
        venv_bin = '/home/ubuntu/back/bank_manager_back/venv/bin'
        manage_py = '/home/ubuntu/back/bank_manager_back/bank_manager'

        # Activar el entorno virtual y ejecutar comandos dentro de él
        pip_install = f"{venv_bin}/pip install -r {manage_py}/requirements.txt"
        run_command(pip_install)

        makemigrations = f"{venv_bin}/python {manage_py}/manage.py makemigrations"
        migrate = f"{venv_bin}/python {manage_py}/manage.py migrate"
        collectstatic = f"{venv_bin}/python {manage_py}/manage.py collectstatic --noinput"

        # Aplicar migraciones y recolectar archivos estáticos
        run_command(makemigrations)
        run_command(migrate)
        run_command(collectstatic)

        # Reiniciar Gunicorn
        run_command("sudo systemctl restart gunicorn_bank")

        # Reiniciar Nginx (si es necesario)
        run_command("sudo systemctl restart nginx")

        print("Despliegue completado exitosamente.")

    except subprocess.CalledProcessError as e:
        print(f"Error durante el despliegue: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
