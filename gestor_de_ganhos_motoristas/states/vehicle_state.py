from gestor_de_ganhos_motoristas.db_env import normalize_db_env, normalize_db_envs

normalize_db_env()
normalize_db_envs()

import reflex as rx
import requests
import logging
import uuid
from sqlalchemy import text
from typing import TypedDict
from gestor_de_ganhos_motoristas.utils import _request_with_retry
from gestor_de_ganhos_motoristas.cache import fipe_cache


class Vehicle(TypedDict):
    id: str
    marca: str
    modelo: str
    ano: str
    valor_fipe: str
    tipo_posse: str
    valor_aluguel_semana: float
    valor_parcela: float
    parcelas_restantes: int
    categorias: list[str]


class VehicleState(rx.State):
    vehicles: list[Vehicle] = []
    marca_code: str = ""
    marca_name: str = ""
    modelo_code: str = ""
    modelo_name: str = ""
    ano_code: str = ""
    ano_name: str = ""
    valor_fipe: str = ""
    tipo_posse: str = "Próprio"
    valor_aluguel_semana: float = 0.0
    valor_parcela: float = 0.0
    parcelas_restantes: int = 0
    available_categories: list[str] = [
        "Uber X/ 99Pop",
        "Comfort / Plus",
        "Black",
        "Eletric",
        "99 e-Pro",
        "Pet",
        "Uber bag",
        "UberXL",
        "Uber Black SUV",
    ]
    selected_categories: list[str] = []
    brands: list[dict[str, str]] = []
    models: list[dict[str, str]] = []
    years: list[dict[str, str]] = []
    is_loading: bool = False

    @rx.event
    def toggle_category(self, cat: str):
        if cat in self.selected_categories:
            self.selected_categories.remove(cat)
        else:
            self.selected_categories.append(cat)

    @rx.event
    async def load_vehicles(self):
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState

        auth = await self.get_state(AuthState)
        if not auth.user_id:
            return
        try:
            async with rx.asession() as session:
                result = await session.execute(
                    text(
                        "SELECT id, marca, modelo, ano, valor_fipe, tipo_posse, valor_aluguel_semana, valor_parcela, parcelas_restantes, categorias FROM vehicles WHERE user_id = :user_id"
                    ),
                    {"user_id": auth.user_id},
                )
                rows = result.all()
                self.vehicles = [
                    {
                        "id": row[0],
                        "marca": row[1],
                        "modelo": row[2],
                        "ano": row[3],
                        "valor_fipe": row[4],
                        "tipo_posse": row[5],
                        "valor_aluguel_semana": float(row[6]),
                        "valor_parcela": float(row[7]),
                        "parcelas_restantes": int(row[8]),
                        "categorias": row[9].split("| ") if row[9] else [],
                    }
                    for row in rows
                ]
        except Exception as e:
            logging.exception(f"Error loading vehicles: {e}")
            yield rx.toast("Erro ao carregar veículos.")
        if not self.brands:
            yield VehicleState.fetch_brands

    @rx.event(background=True)
    async def fetch_brands(self):
        async with self:
            self.is_loading = True
        cached_data = fipe_cache.get("fipe_brands")
        if cached_data:
            async with self:
                self.brands = cached_data
                self.is_loading = False
            return
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = _request_with_retry(
                "https://fipe.parallelum.com.br/api/v2/cars/brands",
                headers=headers,
                timeout=10,
            )
            data = res.json()
            formatted_brands = [
                {"code": str(b["code"]), "name": b["name"]} for b in data
            ]
            fipe_cache.set("fipe_brands", formatted_brands, 86400)
            async with self:
                self.brands = formatted_brands
        except Exception as e:
            logging.exception(f"Error fetching FIPE brands: {e}")
            async with self:
                yield rx.toast(
                    "Erro ao carregar marcas/modelos/anos/valor FIPE. Tente novamente."
                )
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_marca(self, code: str):
        self.marca_code = code
        self.marca_name = next(
            (b["name"] for b in self.brands if b["code"] == code), ""
        )
        self.modelo_code = ""
        self.modelo_name = ""
        self.ano_code = ""
        self.ano_name = ""
        self.valor_fipe = ""
        self.models = []
        self.years = []
        if code:
            yield VehicleState.fetch_models

    @rx.event(background=True)
    async def fetch_models(self):
        async with self:
            if not self.marca_code:
                return
            self.is_loading = True
            code = self.marca_code
        cache_key = f"fipe_models_{code}"
        cached_data = fipe_cache.get(cache_key)
        if cached_data:
            async with self:
                self.models = cached_data
                self.is_loading = False
            return
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = _request_with_retry(
                f"https://fipe.parallelum.com.br/api/v2/cars/brands/{code}/models",
                headers=headers,
                timeout=10,
            )
            data = res.json()
            formatted_models = [
                {"code": str(m["code"]), "name": m["name"]} for m in data
            ]
            fipe_cache.set(cache_key, formatted_models, 43200)
            async with self:
                self.models = formatted_models
        except Exception as e:
            logging.exception(f"Error fetching FIPE models: {e}")
            async with self:
                yield rx.toast(
                    "Erro ao carregar marcas/modelos/anos/valor FIPE. Tente novamente."
                )
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_modelo(self, code: str):
        self.modelo_code = code
        self.modelo_name = next(
            (m["name"] for m in self.models if m["code"] == code), ""
        )
        self.ano_code = ""
        self.ano_name = ""
        self.valor_fipe = ""
        self.years = []
        if code:
            yield VehicleState.fetch_years

    @rx.event(background=True)
    async def fetch_years(self):
        async with self:
            if not self.modelo_code:
                return
            self.is_loading = True
            b_code = self.marca_code
            m_code = self.modelo_code
        cache_key = f"fipe_years_{b_code}_{m_code}"
        cached_data = fipe_cache.get(cache_key)
        if cached_data:
            async with self:
                self.years = cached_data
                self.is_loading = False
            return
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = _request_with_retry(
                f"https://fipe.parallelum.com.br/api/v2/cars/brands/{b_code}/models/{m_code}/years",
                headers=headers,
                timeout=10,
            )
            data = res.json()
            formatted_years = [
                {"code": str(y["code"]), "name": y["name"]} for y in data
            ]
            fipe_cache.set(cache_key, formatted_years, 43200)
            async with self:
                self.years = formatted_years
        except Exception as e:
            logging.exception(f"Error fetching FIPE years: {e}")
            async with self:
                yield rx.toast(
                    "Erro ao carregar marcas/modelos/anos/valor FIPE. Tente novamente."
                )
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_ano(self, code: str):
        self.ano_code = code
        self.ano_name = next(
            (y["name"] for y in self.years if y["code"] == code), ""
        )
        self.valor_fipe = ""
        if code:
            yield VehicleState.fetch_value

    @rx.event(background=True)
    async def fetch_value(self):
        async with self:
            if not self.ano_code:
                return
            self.is_loading = True
            b_code = self.marca_code
            m_code = self.modelo_code
            y_code = self.ano_code
        cache_key = f"fipe_value_{b_code}_{m_code}_{y_code}"
        cached_data = fipe_cache.get(cache_key)
        if cached_data:
            async with self:
                self.valor_fipe = cached_data
                self.is_loading = False
            return
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = _request_with_retry(
                f"https://fipe.parallelum.com.br/api/v2/cars/brands/{b_code}/models/{m_code}/years/{y_code}",
                headers=headers,
                timeout=10,
            )
            data = res.json()
            fipe_val = data.get("price", "")
            fipe_cache.set(cache_key, fipe_val, 21600)
            async with self:
                self.valor_fipe = fipe_val
        except Exception as e:
            logging.exception(f"Error fetching FIPE value: {e}")
            async with self:
                yield rx.toast(
                    "Erro ao carregar marcas/modelos/anos/valor FIPE. Tente novamente."
                )
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_tipo_posse(self, tipo: str):
        self.tipo_posse = tipo

    @rx.event
    async def add_vehicle(self, form_data: dict):
        if not self.marca_name or not self.modelo_name or (not self.ano_name):
            yield rx.toast("Selecione marca, modelo e ano.")
            return
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState
        from gestor_de_ganhos_motoristas.states.profile_state import ProfileState

        auth = await self.get_state(AuthState)
        user_id = auth.user_id
        try:
            aluguel = float(form_data.get("valor_aluguel_semana", 0))
            parcela = float(form_data.get("valor_parcela", 0))
            restantes = int(form_data.get("parcelas_restantes", 0))
        except ValueError:
            yield rx.toast("Valores numéricos inválidos.")
            return
        new_vehicle_id = str(uuid.uuid4())
        serialized_cats = "| ".join(self.selected_categories)
        new_v = {
            "id": new_vehicle_id,
            "marca": self.marca_name,
            "modelo": self.modelo_name,
            "ano": self.ano_name,
            "valor_fipe": self.valor_fipe,
            "tipo_posse": self.tipo_posse,
            "valor_aluguel_semana": aluguel,
            "valor_parcela": parcela,
            "parcelas_restantes": restantes,
            "categorias": list(self.selected_categories),
        }
        self.vehicles.append(new_v)
        try:
            async with rx.asession() as session:
                await session.execute(
                    text("""
                    INSERT INTO vehicles (id, user_id, marca, modelo, ano, valor_fipe, tipo_posse, valor_aluguel_semana, valor_parcela, parcelas_restantes, categorias)
                    VALUES (:id, :uid, :marca, :modelo, :ano, :fipe, :posse, :aluguel, :parcela, :restantes, :cats)
                    """),
                    {
                        "id": new_vehicle_id,
                        "uid": user_id,
                        "marca": self.marca_name,
                        "modelo": self.modelo_name,
                        "ano": self.ano_name,
                        "fipe": self.valor_fipe,
                        "posse": self.tipo_posse,
                        "aluguel": aluguel,
                        "parcela": parcela,
                        "restantes": restantes,
                        "cats": serialized_cats,
                    },
                )
                await session.commit()
        except Exception as e:
            logging.exception(f"Error adding vehicle: {e}")
            yield rx.toast("Erro ao cadastrar veículo. Tente novamente.")
            return
        self.marca_code = ""
        self.marca_name = ""
        self.modelo_code = ""
        self.modelo_name = ""
        self.ano_code = ""
        self.ano_name = ""
        self.valor_fipe = ""
        self.tipo_posse = "Próprio"
        self.selected_categories = []
        yield ProfileState.update_active_vehicle(new_vehicle_id)
        yield rx.toast("Veículo cadastrado com sucesso!")
        yield rx.redirect("/app/custos")

    @rx.event
    async def remove_vehicle(self, v_id: str):
        from gestor_de_ganhos_motoristas.states.auth_state import AuthState
        from gestor_de_ganhos_motoristas.states.profile_state import ProfileState

        auth = await self.get_state(AuthState)
        self.vehicles = [v for v in self.vehicles if v["id"] != v_id]
        profile = await self.get_state(ProfileState)
        try:
            async with rx.asession() as session:
                await session.execute(
                    text(
                        "DELETE FROM vehicles WHERE id = :id AND user_id = :uid"
                    ),
                    {"id": v_id, "uid": auth.user_id},
                )
                await session.commit()
            if profile.veiculo_ativo_id == v_id:
                yield ProfileState.update_active_vehicle("")
            yield rx.toast("Veículo removido com sucesso.")
        except Exception as e:
            logging.exception(f"Error removing vehicle: {e}")
            yield rx.toast("Erro ao remover veículo.")

    @rx.event
    async def set_active_vehicle(self, v_id: str):
        from gestor_de_ganhos_motoristas.states.profile_state import ProfileState

        yield ProfileState.update_active_vehicle(v_id)
        yield rx.toast("Veículo ativo atualizado!")