from gestor_de_ganhos_motoristas.db_env import normalize_db_env, normalize_db_envs

normalize_db_env()
normalize_db_envs()

import reflex as rx
from sqlalchemy import text
from gestor_de_ganhos_motoristas.utils import _request_with_retry


class CostsState(rx.State):
    is_costs_loaded: bool = False
    has_active_vehicle: bool = False
    cf_ipva: float = 0.0
    cf_licenciamento: float = 0.0
    cf_seguro_obrig: float = 0.0
    cf_seguro_carro: float = 0.0
    cf_inss: float = 155.32
    cf_internet: float = 60.0
    cf_depreciacao: float = 0.0
    cv_alim_dia: float = 30.0
    cv_lavagem: float = 120.0
    preco_comb: float = 5.8
    consumo_comb: float = 10.0
    tipo_comb: str = "Gasolina"
    cv_manut_mensal: float = 150.0
    cv_oleo: float = 250.0
    cv_alinhamento: float = 0.0
    cv_pneu: float = 1600.0
    cp_iss: float = 5.0
    cp_icms: float = 0.0
    cp_irpf: float = 0.0
    cp_ipca: float = 4.62
    margem_iss: float = 20.0
    margem_icms: float = 20.0
    remuneracao_semanal: float = 1551.0
    salario_minimo: float = 1412.0
    is_auto_filled: bool = False
    vehicle_is_rental: bool = False
    info_ipva: str = ""
    info_licenciamento: str = ""
    info_combustivel: str = ""
    info_consumo: str = ""

    def _get_ipva_rate(self, estado: str) -> float:
        rates = {
            "AC": 2.0,
            "AL": 3.0,
            "AP": 3.0,
            "AM": 3.0,
            "BA": 2.5,
            "CE": 3.0,
            "DF": 3.5,
            "ES": 2.0,
            "GO": 3.75,
            "MA": 2.5,
            "MT": 3.0,
            "MS": 3.0,
            "MG": 4.0,
            "PA": 2.5,
            "PB": 2.5,
            "PR": 3.5,
            "PE": 3.0,
            "PI": 2.5,
            "RJ": 4.0,
            "RN": 3.0,
            "RS": 3.0,
            "RO": 3.0,
            "RR": 3.0,
            "SC": 2.0,
            "SP": 4.0,
            "SE": 2.5,
            "TO": 2.0,
        }
        return rates.get(estado, 0.0)

    def _get_licenciamento_fee(self, estado: str) -> float:
        fees = {
            "AC": 120.0,
            "AL": 140.0,
            "AP": 130.0,
            "AM": 140.0,
            "BA": 165.35,
            "CE": 201.23,
            "DF": 180.0,
            "ES": 110.0,
            "GO": 160.0,
            "MA": 120.0,
            "MT": 160.0,
            "MS": 150.0,
            "MG": 39.36,
            "PA": 140.0,
            "PB": 130.0,
            "PR": 90.94,
            "PE": 140.0,
            "PI": 120.0,
            "RJ": 268.65,
            "RN": 130.0,
            "RS": 160.0,
            "RO": 130.0,
            "RR": 120.0,
            "SC": 120.0,
            "SP": 160.22,
            "SE": 130.0,
            "TO": 120.0,
        }
        return fees.get(estado, 0.0)

    def _get_avg_fuel_price(self, estado: str) -> float:
        prices = {
            "AC": 6.8,
            "AL": 6.3,
            "AP": 6.7,
            "AM": 6.5,
            "BA": 6.2,
            "CE": 6.4,
            "DF": 6.1,
            "ES": 5.9,
            "GO": 5.8,
            "MA": 6.5,
            "MT": 5.9,
            "MS": 5.85,
            "MG": 5.95,
            "PA": 6.6,
            "PB": 6.3,
            "PR": 5.8,
            "PE": 6.3,
            "PI": 6.4,
            "RJ": 6.5,
            "RN": 6.35,
            "RS": 6.0,
            "RO": 6.4,
            "RR": 6.8,
            "SC": 5.85,
            "SP": 5.8,
            "SE": 6.2,
            "TO": 6.3,
        }
        return prices.get(estado, 5.8)

    def _estimate_consumption(self, model: str) -> float:
        model_up = model.upper()
        segments = {
            "Hatch": [
                "UNO",
                "MOBI",
                "HB20",
                "ONIX",
                "GOL",
                "POLO",
                "ARGO",
                "SANDERO",
                "KA",
            ],
            "Sedan": ["CRONOS", "VIRTUS", "VOYAGE", "VERSA", "YARIS", "CITY"],
            "SUV Compact": [
                "T-CROSS",
                "CRETA",
                "TRACKER",
                "RENEGADE",
                "KICKS",
                "HR-V",
                "PULSE",
            ],
            "SUV Med": [
                "COMPASS",
                "TUCSON",
                "SPORTAGE",
                "RAV4",
                "COROLLA CROSS",
                "TIGGO",
            ],
            "Pickup": [
                "HILUX",
                "S10",
                "RANGER",
                "AMAROK",
                "STRADA",
                "TORO",
                "SAVEIRO",
            ],
            "Luxury": ["COROLLA", "CIVIC", "CRUZE", "SENTRA", "JETTA"],
        }
        for seg, keywords in segments.items():
            if any((k in model_up for k in keywords)):
                if seg == "Hatch":
                    return 12.0
                if seg == "Sedan":
                    return 11.5
                if seg == "SUV Compact":
                    return 10.5
                if seg == "SUV Med":
                    return 9.5
                if seg == "Pickup":
                    return 8.5
                if seg == "Luxury":
                    return 11.0
        return 10.0

    def _parse_fipe(self, val_str: str) -> float:
        if not val_str:
            return 0.0
        clean = (
            val_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
        )
        try:
            return float(clean)
        except ValueError:
            return 0.0

    @rx.event(background=True)
    async def fetch_ipca(self):
        try:
            url = "https://servicodados.ibge.gov.br/api/v3/agregados/1737/periodos/-1/variaveis/2265?localidades=N1[all]"
            res = _request_with_retry(url, timeout=10)
            data = res.json()
            resultados = data[0]["resultados"][0]["series"][0]["serie"]
            last_key = list(resultados.keys())[-1]
            ipca_value = float(resultados[last_key])
            async with self:
                self.cp_ipca = ipca_value
        except Exception as e:
            import logging

            logging.exception(f"Error fetching IPCA: {e}")
            async with self:
                yield rx.toast("Erro ao carregar o IPCA. Tente novamente.")

    @rx.event
    async def load_costs(self):
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState
        from gestor_de_ganhos_motoristas.states.profile_state import ProfileState
        from gestor_de_ganhos_motoristas.states.vehicle_state import VehicleState

        self.is_costs_loaded = False
        auth = await self.get_state(AuthState)
        profile = await self.get_state(ProfileState)
        vehicle_state = await self.get_state(VehicleState)
        if not auth.user_id or not profile.veiculo_ativo_id:
            self.has_active_vehicle = False
            self.is_costs_loaded = True
            return
        self.has_active_vehicle = True
        key = (auth.user_id, profile.veiculo_ativo_id)
        v_data = next(
            (
                v
                for v in vehicle_state.vehicles
                if v["id"] == profile.veiculo_ativo_id
            ),
            None,
        )
        self.vehicle_is_rental = (
            v_data["tipo_posse"] == "Aluguel" if v_data else False
        )
        self.cf_inss = self.salario_minimo * 0.11
        fipe_val = self._parse_fipe(v_data["valor_fipe"]) if v_data else 0.0
        self.cf_depreciacao = fipe_val * 0.24 / 12
        try:
            async with rx.asession() as session:
                result = await session.execute(
                    text(
                        "SELECT cf_ipva, cf_licenciamento, cf_seguro_obrig, cf_seguro_carro, cf_inss, cf_internet, cv_alim_dia, cv_lavagem, preco_comb, consumo_comb, tipo_comb, cv_manut_mensal, cv_oleo, cv_alinhamento, cv_pneu, cp_iss, cp_icms, margem_iss, cf_depreciacao, cp_irpf, cp_ipca, margem_icms, remuneracao_semanal FROM costs WHERE user_id = :uid AND vehicle_id = :vid"
                    ),
                    {"uid": auth.user_id, "vid": profile.veiculo_ativo_id},
                )
                row = result.first()
                if row:
                    self.cf_ipva = float(row[0] or 0)
                    self.cf_licenciamento = float(row[1] or 0)
                    self.cf_seguro_obrig = float(row[2] or 0)
                    self.cf_seguro_carro = float(row[3] or 0)
                    self.cf_internet = float(row[5] or 0)
                    self.cv_alim_dia = float(row[6] or 0)
                    self.cv_lavagem = float(row[7] or 0)
                    self.preco_comb = float(row[8] or 0)
                    self.consumo_comb = float(row[9] or 10.0)
                    self.tipo_comb = row[10] or "Gasolina"
                    self.cv_manut_mensal = float(row[11] or 0)
                    self.cv_oleo = float(row[12] or 0)
                    self.cv_alinhamento = float(row[13] or 0)
                    self.cv_pneu = float(row[14] or 0)
                    self.cp_iss = float(row[15] or 0)
                    self.cp_icms = float(row[16] or 0)
                    self.margem_iss = float(row[17] or 20.0)
                    if len(row) > 18:
                        self.cp_irpf = float(
                            row[19] if row[19] is not None else 0.0
                        )
                        self.cp_ipca = float(
                            row[20] if row[20] is not None else 4.62
                        )
                        self.margem_icms = float(
                            row[21] if row[21] is not None else 20.0
                        )
                    if len(row) > 22:
                        self.remuneracao_semanal = float(
                            row[22] if row[22] is not None else 1551.0
                        )
                    else:
                        self.remuneracao_semanal = 1551.0
                    self.is_auto_filled = False
                else:
                    self.remuneracao_semanal = 1551.0
                    self.is_auto_filled = True
                    estado = profile.estado or "SP"
                    if self.vehicle_is_rental:
                        self.cf_ipva = 0.0
                        self.cf_licenciamento = 0.0
                    else:
                        rate = self._get_ipva_rate(estado)
                        self.cf_ipva = fipe_val * rate / 100
                        self.cf_licenciamento = self._get_licenciamento_fee(
                            estado
                        )
                    self.preco_comb = self._get_avg_fuel_price(estado)
                    self.consumo_comb = (
                        self._estimate_consumption(v_data["modelo"])
                        if v_data
                        else 10.0
                    )
        except Exception as e:
            import logging

            logging.exception(f"Error loading costs: {e}")
            yield rx.toast("Erro ao carregar custos do veículo.")
        yield CostsState.fetch_ipca
        if self.vehicle_is_rental:
            self.info_ipva = "Incluído no aluguel"
            self.info_licenciamento = "Incluído no aluguel"
        else:
            self.info_ipva = (
                "Calculado automaticamente com base no valor FIPE e estado"
            )
            self.info_licenciamento = (
                "Calculado automaticamente com base no estado"
            )
        self.info_combustivel = f"Média do estado ({profile.estado}): R$ {self._get_avg_fuel_price(profile.estado or 'SP'):.2f}"
        model_name = v_data["modelo"] if v_data else "veículo"
        self.info_consumo = f"Estimativa para {model_name}: {self._estimate_consumption(model_name):.1f} km/l"
        self.is_costs_loaded = True

    @rx.event
    async def save_costs(self, form_data: dict):
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState
        from gestor_de_ganhos_motoristas.states.profile_state import ProfileState

        auth = await self.get_state(AuthState)
        profile = await self.get_state(ProfileState)
        if not auth.user_id or not profile.veiculo_ativo_id:
            yield rx.toast("Nenhum veículo ativo selecionado.")
            return
        try:
            self.cf_ipva = float(form_data.get("cf_ipva", 0))
            self.cf_licenciamento = float(form_data.get("cf_licenciamento", 0))
            self.cf_seguro_obrig = float(form_data.get("cf_seguro_obrig", 0))
            self.cf_seguro_carro = float(form_data.get("cf_seguro_carro", 0))
            self.cf_inss = float(form_data.get("cf_inss", 0))
            self.cf_internet = float(form_data.get("cf_internet", 0))
            self.cv_alim_dia = float(form_data.get("cv_alim_dia", 0))
            self.cv_lavagem = float(form_data.get("cv_lavagem", 0))
            self.preco_comb = float(form_data.get("preco_comb", 0))
            self.consumo_comb = float(form_data.get("consumo_comb", 1))
            if self.consumo_comb <= 0:
                self.consumo_comb = 1
            self.tipo_comb = form_data.get("tipo_comb", "Gasolina")
            self.cv_manut_mensal = float(form_data.get("cv_manut_mensal", 0))
            self.cv_oleo = float(form_data.get("cv_oleo", 0))
            self.cv_alinhamento = float(form_data.get("cv_alinhamento", 0))
            self.cv_pneu = float(form_data.get("cv_pneu", 0))
            self.cp_iss = float(form_data.get("cp_iss", 0))
            self.cp_icms = float(form_data.get("cp_icms", 0))
            self.margem_iss = float(form_data.get("margem_iss", 0))
            self.cp_ipca = float(form_data.get("cp_ipca", 4.62))
            self.margem_icms = float(form_data.get("margem_icms", 20.0))
            self.remuneracao_semanal = float(
                form_data.get("remuneracao_semanal", 1551.0)
            )
            try:
                async with rx.asession() as session:
                    await session.execute(
                        text("""
                        INSERT INTO costs (user_id, vehicle_id, cf_ipva, cf_licenciamento, cf_seguro_obrig, cf_seguro_carro, cf_inss, cf_internet, cv_alim_dia, cv_lavagem, preco_comb, consumo_comb, tipo_comb, cv_manut_mensal, cv_oleo, cv_alinhamento, cv_pneu, cp_iss, cp_icms, margem_iss, cf_depreciacao, cp_irpf, cp_ipca, margem_icms, remuneracao_semanal)
                        VALUES (:uid, :vid, :ipva, :lic, :sob, :scarro, :inss, :int, :alim, :lav, :pcomb, :ccomb, :tcomb, :manut, :oleo, :alin, :pneu, :iss, :icms, :miss, :deprec, :irpf, :ipca, :micms, :remun)
                        ON DUPLICATE KEY UPDATE
                            cf_ipva = VALUES(cf_ipva), cf_licenciamento = VALUES(cf_licenciamento), cf_seguro_obrig = VALUES(cf_seguro_obrig), cf_seguro_carro = VALUES(cf_seguro_carro),
                            cf_inss = VALUES(cf_inss), cf_internet = VALUES(cf_internet), cv_alim_dia = VALUES(cv_alim_dia), cv_lavagem = VALUES(cv_lavagem),
                            preco_comb = VALUES(preco_comb), consumo_comb = VALUES(consumo_comb), tipo_comb = VALUES(tipo_comb), cv_manut_mensal = VALUES(cv_manut_mensal),
                            cv_oleo = VALUES(cv_oleo), cv_alinhamento = VALUES(cv_alinhamento), cv_pneu = VALUES(cv_pneu), cp_iss = VALUES(cp_iss), cp_icms = VALUES(cp_icms), margem_iss = VALUES(margem_iss),
                            cf_depreciacao = VALUES(cf_depreciacao), cp_irpf = VALUES(cp_irpf), cp_ipca = VALUES(cp_ipca), margem_icms = VALUES(margem_icms), remuneracao_semanal = VALUES(remuneracao_semanal)
                        """),
                        {
                            "uid": auth.user_id,
                            "vid": profile.veiculo_ativo_id,
                            "ipva": self.cf_ipva,
                            "lic": self.cf_licenciamento,
                            "sob": self.cf_seguro_obrig,
                            "scarro": self.cf_seguro_carro,
                            "inss": self.cf_inss,
                            "int": self.cf_internet,
                            "alim": self.cv_alim_dia,
                            "lav": self.cv_lavagem,
                            "pcomb": self.preco_comb,
                            "ccomb": self.consumo_comb,
                            "tcomb": self.tipo_comb,
                            "manut": self.cv_manut_mensal,
                            "oleo": self.cv_oleo,
                            "alin": self.cv_alinhamento,
                            "pneu": self.cv_pneu,
                            "iss": self.cp_iss,
                            "icms": self.cp_icms,
                            "miss": self.margem_iss,
                            "deprec": self.cf_depreciacao,
                            "irpf": self.cp_irpf,
                            "ipca": self.cp_ipca,
                            "micms": self.margem_icms,
                            "remun": self.remuneracao_semanal,
                        },
                    )
                    await session.commit()
                yield rx.toast("Custos salvos com sucesso!")
                yield rx.redirect("/app/resultados")
            except Exception as e:
                import logging

                logging.exception(f"Error saving costs: {e}")
                yield rx.toast("Erro ao salvar custos. Tente novamente.")
        except ValueError:
            yield rx.toast("Por favor, insira valores numéricos válidos.")