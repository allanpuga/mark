from gestor_de_ganhos_motoristas.db_env import normalize_db_env, normalize_db_envs

normalize_db_env()
normalize_db_envs()

import reflex as rx
from sqlalchemy import text


class AdminState(rx.State):
    total_users: int = 0
    total_results: int = 0
    active_users_week: int = 0
    users_list: list[dict] = []
    users_search: str = ""
    all_results: list[dict] = []
    results_search: str = ""

    @rx.event
    async def load_admin_data(self):
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState

        auth = await self.get_state(AuthState)
        if not auth.is_admin:
            return
        try:
            async with rx.asession() as session:
                r = await session.execute(text("SELECT COUNT(*) FROM users"))
                self.total_users = r.scalar() or 0
                r = await session.execute(
                    text("SELECT COUNT(*) FROM saved_results")
                )
                self.total_results = r.scalar() or 0
                r = await session.execute(
                    text("""
                    SELECT COUNT(DISTINCT user_id) FROM saved_results 
                    WHERE created_at >= NOW() - INTERVAL 7 DAY
                """)
                )
                self.active_users_week = r.scalar() or 0
                r = await session.execute(
                    text("""
                    SELECT u.id, u.username, u.email, u.created_at,
                        (SELECT COUNT(*) FROM vehicles WHERE user_id = u.id) as vehicle_count,
                        (SELECT COUNT(*) FROM saved_results WHERE user_id = u.id) as results_count
                    FROM users u
                    ORDER BY u.created_at DESC
                    LIMIT 100
                """)
                )
                rows = r.all()
                self.users_list = [
                    {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "created_at": str(row[3].strftime("%d/%m/%Y %H:%M"))
                        if row[3]
                        else "",
                        "vehicle_count": int(row[4] or 0),
                        "results_count": int(row[5] or 0),
                    }
                    for row in rows
                ]
                r = await session.execute(
                    text("""
                    SELECT sr.id, u.username, sr.veiculo_nome, sr.dias_semana, sr.horas_dia,
                        sr.km_dia, sr.cp_iss, sr.margem_iss, sr.custo_por_km,
                        sr.valor_ideal_km, sr.markup_sugerido, sr.created_at
                    FROM saved_results sr
                    JOIN users u ON sr.user_id = u.id
                    ORDER BY sr.created_at DESC
                    LIMIT 200
                """)
                )
                rows = r.all()
                self.all_results = [
                    {
                        "id": row[0],
                        "username": row[1],
                        "veiculo_nome": row[2] or "",
                        "dias_semana": int(row[3] or 6),
                        "horas_dia": int(row[4] or 8),
                        "km_dia": float(row[5] or 150),
                        "cp_iss": float(row[6] or 5),
                        "margem_iss": float(row[7] or 20),
                        "custo_por_km": float(row[8] or 0),
                        "valor_ideal_km": float(row[9] or 0),
                        "markup_sugerido": float(row[10] or 0),
                        "created_at": str(row[11].strftime("%d/%m/%Y %H:%M"))
                        if row[11]
                        else "",
                    }
                    for row in rows
                ]
        except Exception as e:
            import logging

            logging.exception(f"Error loading admin data: {e}")

    @rx.event
    def set_users_search(self, value: str):
        self.users_search = value

    @rx.event
    def set_results_search(self, value: str):
        self.results_search = value

    @rx.var
    def filtered_users(self) -> list[dict]:
        if not self.users_search:
            return self.users_list
        search = self.users_search.lower()
        return [
            u
            for u in self.users_list
            if search in u["username"].lower() or search in u["email"].lower()
        ]

    @rx.var
    def filtered_results(self) -> list[dict]:
        if not self.results_search:
            return self.all_results
        search = self.results_search.lower()
        return [
            r
            for r in self.all_results
            if search in r["username"].lower()
            or search in r["veiculo_nome"].lower()
        ]