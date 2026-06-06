import reflex as rx
import os

port = int(os.environ.get("PORT", "3000"))

config = rx.Config(
    app_name="gestor_de_ganhos_motoristas",
    db_url=os.environ.get("DATABASE_URL"),
    plugins=[rx.plugins.TailwindV3Plugin()],
    frontend_port=port,
    backend_port=port + 1,
)
