import reflex as rx
import os

config = rx.Config(
    app_name="gestor_de_ganhos_motoristas",
    db_url=os.environ.get("DATABASE_URL"),
    plugins=[rx.plugins.TailwindV3Plugin()],
)
