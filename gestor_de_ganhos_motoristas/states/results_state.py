from gestor_de_ganhos_motoristas.db_env import normalize_db_env, normalize_db_envs

normalize_db_env()
normalize_db_envs()

import reflex as rx


class ResultsState(rx.State):
    custo_operacional_mensal: float = 0.0
    custo_mensal_total: float = 0.0
    custo_por_km: float = 0.0
    custo_por_hora: float = 0.0
    valor_ideal_km: float = 0.0
    valor_ideal_hora: float = 0.0
    salario_base_dieese: float = 7200.0
    markup_sugerido: float = 0.0
    custo_diario: float = 0.0
    custo_semanal: float = 0.0
    faturamento_bruto: float = 0.0
    bar_chart_data: list[dict[str, str | float]] = []
    pie_chart_data: list[dict[str, str | float]] = []
    total_cf: float = 0.0
    total_cv: float = 0.0
    total_cp_iss: float = 0.0
    total_cp_icms: float = 0.0
    markup_iss: float = 0.0
    markup_icms: float = 0.0
    saved_results: list[dict] = []
    is_saving: bool = False

    @rx.event
    async def recalculate(self):
        from gestor_de_ganhos_motoristas.states.profile_state import ProfileState
        from gestor_de_ganhos_motoristas.states.vehicle_state import VehicleState
        from gestor_de_ganhos_motoristas.states.costs_state import CostsState
        from gestor_de_ganhos_motoristas.utils import compute_markup_math

        profile = await self.get_state(ProfileState)
        vehicle_state = await self.get_state(VehicleState)
        costs = await self.get_state(CostsState)
        if not costs.has_active_vehicle:
            return
        active_vehicle = next(
            (
                v
                for v in vehicle_state.vehicles
                if v["id"] == profile.veiculo_ativo_id
            ),
            None,
        )
        if not active_vehicle:
            return

        fipe_val = costs._parse_fipe(active_vehicle["valor_fipe"])

        math_results = compute_markup_math(
            km_dia=profile.km_dia,
            dias_semana=profile.dias_semana,
            horas_dia=profile.horas_dia,
            tipo_posse=active_vehicle["tipo_posse"],
            valor_aluguel_semana=float(
                active_vehicle.get("valor_aluguel_semana", 0.0)
            ),
            valor_parcela=float(active_vehicle.get("valor_parcela", 0.0)),
            fipe_val=fipe_val,
            cf_ipva=costs.cf_ipva,
            cf_licenciamento=costs.cf_licenciamento,
            cf_seguro_obrig=costs.cf_seguro_obrig,
            cf_seguro_carro=costs.cf_seguro_carro,
            cf_inss=costs.cf_inss,
            cf_internet=costs.cf_internet,
            cv_alim_dia=costs.cv_alim_dia,
            preco_comb=costs.preco_comb,
            consumo_comb=costs.consumo_comb,
            cv_manut_mensal=costs.cv_manut_mensal,
            cv_oleo=costs.cv_oleo,
            cv_pneu=costs.cv_pneu,
            cv_lavagem=costs.cv_lavagem,
            cv_alinhamento=costs.cv_alinhamento,
            cp_ipca=costs.cp_ipca,
            cp_iss=costs.cp_iss,
            cp_icms=costs.cp_icms,
            margem_iss=costs.margem_iss,
            margem_icms=costs.margem_icms,
            remuneracao_semanal=costs.remuneracao_semanal,
        )

        self.custo_por_km = math_results["custo_por_km"]
        self.custo_por_hora = math_results["custo_por_hora"]
        self.custo_operacional_mensal = math_results["custo_mensal_total"]
        self.valor_ideal_km = math_results["valor_ideal_km"]
        self.valor_ideal_hora = math_results["valor_ideal_hora"]
        self.total_cf = math_results["total_cf"]
        self.total_cv = math_results["total_cv"]
        self.total_cp_iss = math_results["total_cp_iss"]
        self.total_cp_icms = math_results["total_cp_icms"]
        self.custo_mensal_total = math_results["custo_mensal_total"]
        self.markup_iss = math_results["markup_iss"]
        self.markup_icms = math_results["markup_icms"]
        self.markup_sugerido = math_results["markup_sugerido"]
        self.faturamento_bruto = math_results["faturamento_bruto"]
        self.custo_diario = math_results["custo_diario"]
        self.custo_semanal = math_results["custo_semanal"]

        self.bar_chart_data = [
            {"name": "Fixos", "valor": round(self.total_cf, 2)},
            {"name": "Variáveis", "valor": round(self.total_cv, 2)},
            {
                "name": "Impostos",
                "valor": round(math_results["total_cp_iss_anual"] / 144, 2),
            },
        ]
        combustivel_mensal = math_results["cv_combustivel_anual"] / 12
        oleo_mensal = math_results["cv_oleo_anual"] / 12
        pneu_mensal = math_results["cv_pneu_anual"] / 12
        vehicle_monthly = math_results["cf_financiamento_anual"] / 12
        self.pie_chart_data = [
            {"name": "Veículo", "value": round(vehicle_monthly, 2)},
            {"name": "Combustível", "value": round(combustivel_mensal, 2)},
            {
                "name": "Manutenção",
                "value": round(
                    (
                        math_results["cv_manut_anual"]
                        + math_results["cv_oleo_anual"]
                        + math_results["cv_pneu_anual"]
                        + math_results["cv_alinhamento_anual"]
                    )
                    / 12,
                    2,
                ),
            },
            {
                "name": "Outros Fixos",
                "value": round(
                    (
                        math_results["total_cf_anual"]
                        - math_results["cf_financiamento_anual"]
                    )
                    / 12,
                    2,
                ),
            },
            {
                "name": "Outros Vars",
                "value": round(
                    (
                        math_results["total_cv_anual"]
                        - math_results["cv_combustivel_anual"]
                        - math_results["cv_oleo_anual"]
                        - math_results["cv_pneu_anual"]
                        - math_results["cv_manut_anual"]
                        - math_results["cv_alinhamento_anual"]
                    )
                    / 12,
                    2,
                ),
            },
        ]

    @rx.event
    async def save_result(self):
        """Save the current calculation result to the database."""
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState
        from gestor_de_ganhos_motoristas.states.profile_state import ProfileState
        from gestor_de_ganhos_motoristas.states.vehicle_state import VehicleState
        from gestor_de_ganhos_motoristas.states.costs_state import CostsState
        from sqlalchemy import text
        import uuid

        auth = await self.get_state(AuthState)
        profile = await self.get_state(ProfileState)
        vehicle_state = await self.get_state(VehicleState)
        costs = await self.get_state(CostsState)
        if not auth.user_id or not profile.veiculo_ativo_id:
            yield rx.toast("Nenhum veículo ativo selecionado.")
            return
        active_vehicle = next(
            (
                v
                for v in vehicle_state.vehicles
                if v["id"] == profile.veiculo_ativo_id
            ),
            None,
        )
        if not active_vehicle:
            yield rx.toast("Veículo não encontrado.")
            return
        self.is_saving = True
        result_id = str(uuid.uuid4())
        veiculo_nome = f"{active_vehicle['marca']} {active_vehicle['modelo']} {active_vehicle['ano']}"
        try:
            async with rx.asession() as session:
                await session.execute(
                    text("""
                    INSERT INTO saved_results (
                        id, user_id, vehicle_id, veiculo_nome, valor_fipe, tipo_posse,
                        dias_semana, horas_dia, km_dia, remuneracao_semanal,
                        margem_iss, margem_icms, cp_iss, cp_icms, cp_ipca,
                        custo_por_km, custo_por_hora, valor_ideal_km, valor_ideal_hora,
                        custo_mensal_total, custo_diario, custo_semanal,
                        markup_sugerido, faturamento_bruto, total_cf, total_cv
                    ) VALUES (
                        :id, :uid, :vid, :vname, :fipe, :posse,
                        :dias, :horas, :km, :remun,
                        :miss, :micms, :iss, :icms, :ipca,
                        :ckm, :chora, :vikm, :vihora,
                        :cmensal, :cdiario, :csemanal,
                        :markup, :fat, :tcf, :tcv
                    )
                """),
                    {
                        "id": result_id,
                        "uid": auth.user_id,
                        "vid": profile.veiculo_ativo_id,
                        "vname": veiculo_nome,
                        "fipe": active_vehicle["valor_fipe"],
                        "posse": active_vehicle["tipo_posse"],
                        "dias": profile.dias_semana,
                        "horas": profile.horas_dia,
                        "km": profile.km_dia,
                        "remun": costs.remuneracao_semanal,
                        "miss": costs.margem_iss,
                        "micms": costs.margem_icms,
                        "iss": costs.cp_iss,
                        "icms": costs.cp_icms,
                        "ipca": costs.cp_ipca,
                        "ckm": self.custo_por_km,
                        "chora": self.custo_por_hora,
                        "vikm": self.valor_ideal_km,
                        "vihora": self.valor_ideal_hora,
                        "cmensal": self.custo_mensal_total,
                        "cdiario": self.custo_diario,
                        "csemanal": self.custo_semanal,
                        "markup": self.markup_sugerido,
                        "fat": self.faturamento_bruto,
                        "tcf": self.total_cf,
                        "tcv": self.total_cv,
                    },
                )
                await session.commit()
            yield rx.toast("Resultado salvo com sucesso!")
            yield ResultsState.load_saved_results
        except Exception as e:
            import logging

            logging.exception(f"Error saving result: {e}")
            yield rx.toast("Erro ao salvar resultado.")
        finally:
            self.is_saving = False

    @rx.event
    async def auto_save_result(self):
        """Auto-save result on page load. Only saves if values changed from last saved."""
        if self.custo_por_km <= 0:
            return
        if self.saved_results:
            last = self.saved_results[0]
            if (
                abs(float(last.get("custo_por_km", 0)) - self.custo_por_km)
                < 0.01
                and abs(
                    float(last.get("valor_ideal_km", 0)) - self.valor_ideal_km
                )
                < 0.01
            ):
                return
        yield ResultsState.save_result

    @rx.event
    async def load_saved_results(self):
        """Load all previously saved results for this user."""
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState
        from sqlalchemy import text

        auth = await self.get_state(AuthState)
        if not auth.user_id:
            return
        try:
            async with rx.asession() as session:
                result = await session.execute(
                    text("""
                    SELECT id, veiculo_nome, valor_fipe, tipo_posse,
                        dias_semana, horas_dia, km_dia, remuneracao_semanal,
                        margem_iss, cp_iss, cp_ipca,
                        custo_por_km, custo_por_hora, valor_ideal_km, valor_ideal_hora,
                        custo_mensal_total, markup_sugerido, created_at
                    FROM saved_results
                    WHERE user_id = :uid
                    ORDER BY created_at DESC
                    LIMIT 20
                """),
                    {"uid": auth.user_id},
                )
                rows = result.all()
                self.saved_results = [
                    {
                        "id": row[0],
                        "veiculo_nome": row[1] or "",
                        "valor_fipe": row[2] or "",
                        "tipo_posse": row[3] or "",
                        "dias_semana": int(row[4] or 6),
                        "horas_dia": int(row[5] or 8),
                        "km_dia": float(row[6] or 150),
                        "remuneracao_semanal": float(row[7] or 1551),
                        "margem_iss": float(row[8] or 20),
                        "cp_iss": float(row[9] or 5),
                        "cp_ipca": float(row[10] or 4.62),
                        "custo_por_km": float(row[11] or 0),
                        "custo_por_hora": float(row[12] or 0),
                        "valor_ideal_km": float(row[13] or 0),
                        "valor_ideal_hora": float(row[14] or 0),
                        "custo_mensal_total": float(row[15] or 0),
                        "markup_sugerido": float(row[16] or 0),
                        "created_at": str(row[17].strftime("%d/%m/%Y %H:%M"))
                        if row[17]
                        else "",
                    }
                    for row in rows
                ]
        except Exception as e:
            import logging

            logging.exception(f"Error loading saved results: {e}")

    @rx.event
    async def delete_saved_result(self, result_id: str):
        """Delete a saved result by ID."""
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState
        from sqlalchemy import text

        auth = await self.get_state(AuthState)
        try:
            async with rx.asession() as session:
                await session.execute(
                    text(
                        "DELETE FROM saved_results WHERE id = :id AND user_id = :uid"
                    ),
                    {"id": result_id, "uid": auth.user_id},
                )
                await session.commit()
            self.saved_results = [
                r for r in self.saved_results if r["id"] != result_id
            ]
            yield rx.toast("Resultado removido.")
        except Exception as e:
            import logging

            logging.exception(f"Error deleting result: {e}")
            yield rx.toast("Erro ao remover resultado.")