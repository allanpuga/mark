from gestor_de_ganhos_motoristas.db_env import normalize_db_env, normalize_db_envs

normalize_db_env()
normalize_db_envs()

import reflex as rx
import requests
import logging
from sqlalchemy import text
from gestor_de_ganhos_motoristas.utils import _request_with_retry


class ProfileState(rx.State):
    nome: str = ""
    email: str = ""
    estado: str = ""
    cidade: str = ""
    whatsapp: str = ""
    dias_semana: int = 6
    horas_dia: int = 8
    km_dia: float = 150.0
    veiculo_ativo_id: str = ""
    estados: list[dict[str, str]] = []
    cidades: list[str] = []
    is_loading: bool = False

    @rx.event
    async def load_profile(self):
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState

        auth = await self.get_state(AuthState)
        if not auth.user_id:
            return
        try:
            async with rx.asession() as session:
                result = await session.execute(
                    text(
                        "SELECT nome, email, estado, cidade, whatsapp, dias_semana, horas_dia, km_dia, veiculo_ativo_id FROM profiles WHERE user_id = :user_id"
                    ),
                    {"user_id": auth.user_id},
                )
                row = result.first()
                if row:
                    self.nome = row[0] or auth.username
                    self.email = row[1] or auth.email
                    self.estado = row[2] or ""
                    self.cidade = row[3] or ""
                    self.whatsapp = row[4] or ""
                    self.dias_semana = row[5] if row[5] is not None else 6
                    self.horas_dia = row[6] if row[6] is not None else 8
                    self.km_dia = float(row[7]) if row[7] is not None else 150.0
                    self.veiculo_ativo_id = row[8] or ""
        except Exception as e:
            logging.exception(f"Error loading profile: {e}")
            yield rx.toast("Erro ao carregar dados do perfil.")
        if not self.estados:
            yield ProfileState.fetch_estados
        if self.estado:
            yield ProfileState.fetch_cidades

    @rx.event(background=True)
    async def fetch_estados(self):
        async with self:
            self.is_loading = True
        try:
            res = _request_with_retry(
                "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome",
                timeout=10,
            )
            estados_data = res.json()
            async with self:
                self.estados = [
                    {"sigla": s["sigla"], "nome": s["nome"]}
                    for s in estados_data
                ]
        except Exception as e:
            logging.exception(f"Error fetching estados: {e}")
            async with self:
                yield rx.toast("Erro ao carregar estados. Tente novamente.")
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_estado_cidade(self, form_data: dict):
        self.estado = form_data.get("estado", "")
        self.cidade = form_data.get("cidade", "")
        if self.estado:
            yield ProfileState.fetch_cidades

    @rx.event
    def set_estado(self, estado: str):
        self.estado = estado
        self.cidade = ""
        yield ProfileState.fetch_cidades

    @rx.event
    def set_cidade(self, cidade: str):
        self.cidade = cidade

    @rx.event(background=True)
    async def fetch_cidades(self):
        async with self:
            if not self.estado:
                self.cidades = []
                return
            self.is_loading = True
            estado = self.estado
        try:
            res = _request_with_retry(
                f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado}/municipios",
                timeout=10,
            )
            cidades_data = res.json()
            async with self:
                self.cidades = [c["nome"] for c in cidades_data]
        except Exception as e:
            logging.exception(f"Error fetching cidades: {e}")
            async with self:
                yield rx.toast("Erro ao carregar cidades. Tente novamente.")
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    async def update_active_vehicle(self, vehicle_id: str):
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState

        auth = await self.get_state(AuthState)
        if not auth.user_id:
            return
        self.veiculo_ativo_id = vehicle_id
        try:
            async with rx.asession() as session:
                await session.execute(
                    text(
                        "UPDATE profiles SET veiculo_ativo_id = :v_id WHERE user_id = :uid"
                    ),
                    {"v_id": vehicle_id, "uid": auth.user_id},
                )
                await session.commit()
        except Exception as e:
            logging.exception(f"Error updating active vehicle in profile: {e}")

    @rx.event
    async def save_profile(self, form_data: dict):
        nome = form_data.get("nome", "").strip()
        email = form_data.get("email", "").strip()
        if not nome or not email:
            yield rx.toast("Nome e E-mail são obrigatórios.")
            return
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState

        auth = await self.get_state(AuthState)
        self.nome = nome
        self.email = email
        self.whatsapp = form_data.get("whatsapp", "")
        try:
            self.dias_semana = int(form_data.get("dias_semana", 6))
            self.horas_dia = int(form_data.get("horas_dia", 8))
            self.km_dia = float(form_data.get("km_dia", 150.0))
        except ValueError:
            yield rx.toast("Valores numéricos inválidos.")
            return
        try:
            async with rx.asession() as session:
                await session.execute(
                    text("""
                    INSERT INTO profiles (user_id, nome, email, estado, cidade, whatsapp, dias_semana, horas_dia, km_dia, veiculo_ativo_id) 
                    VALUES (:uid, :nome, :email, :estado, :cidade, :whatsapp, :dias, :horas, :km, :veiculo)
                    ON DUPLICATE KEY UPDATE 
                        nome = VALUES(nome), email = VALUES(email), estado = VALUES(estado), cidade = VALUES(cidade),
                        whatsapp = VALUES(whatsapp), dias_semana = VALUES(dias_semana), horas_dia = VALUES(horas_dia), km_dia = VALUES(km_dia)
                    """),
                    {
                        "uid": auth.user_id,
                        "nome": self.nome,
                        "email": self.email,
                        "estado": self.estado,
                        "cidade": self.cidade,
                        "whatsapp": self.whatsapp,
                        "dias": self.dias_semana,
                        "horas": self.horas_dia,
                        "km": self.km_dia,
                        "veiculo": self.veiculo_ativo_id,
                    },
                )
                await session.commit()
            yield rx.toast("Perfil salvo com sucesso!")
            yield rx.redirect("/app/veiculos")
        except Exception as e:
            logging.exception(f"Error saving profile: {e}")
            yield rx.toast("Erro ao salvar perfil. Tente novamente.")