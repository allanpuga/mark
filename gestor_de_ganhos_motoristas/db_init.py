from gestor_de_ganhos_motoristas.db_env import normalize_db_env, normalize_db_envs

normalize_db_env()
normalize_db_envs()

from gestor_de_ganhos_motoristas.db_compat import apply_aiomysql_ping_patch

apply_aiomysql_ping_patch()

import reflex as rx
import asyncio
from sqlalchemy import text
import bcrypt
import logging

logging.basicConfig(level=logging.INFO)
_initialized = False


async def init_db():
    """Initialize database tables. Optimized to prevent blocking the health check."""
    global _initialized
    if _initialized:
        return
    try:
        async with asyncio.timeout(10):
            async with rx.asession() as session:
                try:
                    check = await session.execute(
                        text("SELECT 1 FROM users LIMIT 1")
                    )
                    check.first()
                    _initialized = True
                    return
                except Exception:
                    logging.exception("Unexpected error")
                    logging.info(
                        "Database tables not found. Initializing schema..."
                    )
                await session.execute(
                    text("SET SESSION innodb_lock_wait_timeout = 5")
                )
                await session.execute(text("SET SESSION wait_timeout = 60"))
                await session.execute(
                    text("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_admin TINYINT(1) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                )
                await session.execute(
                    text("""
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id VARCHAR(36) PRIMARY KEY,
                    nome VARCHAR(255) DEFAULT '',
                    email VARCHAR(255) DEFAULT '',
                    whatsapp VARCHAR(50) DEFAULT '',
                    estado VARCHAR(2) DEFAULT '',
                    cidade VARCHAR(255) DEFAULT '',
                    dias_semana INT DEFAULT 6,
                    horas_dia INT DEFAULT 8,
                    km_dia FLOAT DEFAULT 150.0,
                    veiculo_ativo_id VARCHAR(36) DEFAULT '',
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                """)
                )
                await session.execute(
                    text("""
                CREATE TABLE IF NOT EXISTS vehicles (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    marca VARCHAR(255) DEFAULT '',
                    modelo VARCHAR(255) DEFAULT '',
                    ano VARCHAR(50) DEFAULT '',
                    valor_fipe VARCHAR(100) DEFAULT '',
                    tipo_posse VARCHAR(50) DEFAULT 'Próprio',
                    valor_aluguel_semana FLOAT DEFAULT 0,
                    valor_parcela FLOAT DEFAULT 0,
                    parcelas_restantes INT DEFAULT 0,
                    categorias TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                """)
                )
                await session.execute(
                    text("""
                CREATE TABLE IF NOT EXISTS costs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    vehicle_id VARCHAR(36) NOT NULL,
                    cf_ipva FLOAT DEFAULT 0,
                    cf_licenciamento FLOAT DEFAULT 0,
                    cf_seguro_obrig FLOAT DEFAULT 0,
                    cf_seguro_carro FLOAT DEFAULT 0,
                    cf_inss FLOAT DEFAULT 155.32,
                    cf_internet FLOAT DEFAULT 60.0,
                    cf_depreciacao FLOAT DEFAULT 0,
                    cv_alim_dia FLOAT DEFAULT 30.0,
                    cv_lavagem FLOAT DEFAULT 120.0,
                    preco_comb FLOAT DEFAULT 5.8,
                    consumo_comb FLOAT DEFAULT 10.0,
                    tipo_comb VARCHAR(50) DEFAULT 'Gasolina',
                    cv_manut_mensal FLOAT DEFAULT 150.0,
                    cv_oleo FLOAT DEFAULT 250.0,
                    cv_alinhamento FLOAT DEFAULT 0,
                    cv_pneu FLOAT DEFAULT 1600.0,
                    cp_iss FLOAT DEFAULT 5.0,
                    cp_icms FLOAT DEFAULT 0,
                    cp_irpf FLOAT DEFAULT 0,
                    cp_ipca FLOAT DEFAULT 4.62,
                    margem_iss FLOAT DEFAULT 20.0,
                    margem_icms FLOAT DEFAULT 20.0,
                    remuneracao_semanal FLOAT DEFAULT 1551.0,
                    UNIQUE KEY unique_user_vehicle (user_id, vehicle_id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                """)
                )
                await session.execute(
                    text("""
                CREATE TABLE IF NOT EXISTS saved_results (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    vehicle_id VARCHAR(36) NOT NULL,
                    veiculo_nome VARCHAR(255) DEFAULT '',
                    valor_fipe VARCHAR(100) DEFAULT '',
                    tipo_posse VARCHAR(50) DEFAULT '',
                    dias_semana INT DEFAULT 6,
                    horas_dia INT DEFAULT 8,
                    km_dia FLOAT DEFAULT 150.0,
                    remuneracao_semanal FLOAT DEFAULT 1551.0,
                    margem_iss FLOAT DEFAULT 20.0,
                    margem_icms FLOAT DEFAULT 20.0,
                    cp_iss FLOAT DEFAULT 5.0,
                    cp_icms FLOAT DEFAULT 0.0,
                    cp_ipca FLOAT DEFAULT 4.62,
                    custo_por_km FLOAT DEFAULT 0,
                    custo_por_hora FLOAT DEFAULT 0,
                    valor_ideal_km FLOAT DEFAULT 0,
                    valor_ideal_hora FLOAT DEFAULT 0,
                    custo_mensal_total FLOAT DEFAULT 0,
                    custo_diario FLOAT DEFAULT 0,
                    custo_semanal FLOAT DEFAULT 0,
                    markup_sugerido FLOAT DEFAULT 0,
                    faturamento_bruto FLOAT DEFAULT 0,
                    total_cf FLOAT DEFAULT 0,
                    total_cv FLOAT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                """)
                )
                hashed_password = bcrypt.hashpw(
                    "123456".encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
                await session.execute(
                    text("""
                    INSERT IGNORE INTO users (id, username, email, password_hash, is_admin) 
                    VALUES ('default-user-001', 'admin', 'admin@gestao.com', :hashed_password, 1);
                """),
                    {"hashed_password": hashed_password},
                )
                await session.execute(
                    text("""
                    INSERT IGNORE INTO profiles (user_id, nome, email, dias_semana, horas_dia, km_dia)
                    VALUES ('default-user-001', 'Motorista', 'admin@gestao.com', 6, 8, 150.0);
                """)
                )
                await session.commit()
        _initialized = True
    except Exception as e:
        logging.exception("Non-fatal error during database initialization")
        _initialized = True