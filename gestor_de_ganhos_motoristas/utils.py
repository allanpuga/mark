import requests
import time
import logging


def _request_with_retry(url, headers=None, timeout=10, retries=2):
    """Helper to fetch an URL with exponential backoff on failure."""
    for attempt in range(retries + 1):
        try:
            res = requests.get(url, headers=headers, timeout=timeout)
            if res.status_code == 200:
                return res
            logging.warning(
                f"Request failed with status {res.status_code} for {url}"
            )
        except Exception as e:
            logging.exception("Unexpected error")
            logging.warning(
                f"Request exception on attempt {attempt + 1}/{retries + 1} for {url}: {e}"
            )
        if attempt < retries:
            time.sleep(1 * 2**attempt)
    raise Exception(f"Failed to fetch {url} after {retries + 1} attempts")


def compute_markup_math(
    km_dia: float,
    dias_semana: int,
    horas_dia: int,
    tipo_posse: str,
    valor_aluguel_semana: float,
    valor_parcela: float,
    fipe_val: float,
    cf_ipva: float,
    cf_licenciamento: float,
    cf_seguro_obrig: float,
    cf_seguro_carro: float,
    cf_inss: float,
    cf_internet: float,
    cv_alim_dia: float,
    preco_comb: float,
    consumo_comb: float,
    cv_manut_mensal: float,
    cv_oleo: float,
    cv_pneu: float,
    cv_lavagem: float,
    cv_alinhamento: float,
    cp_ipca: float,
    cp_iss: float,
    cp_icms: float,
    margem_iss: float,
    margem_icms: float,
    remuneracao_semanal: float,
) -> dict:
    annual_km = km_dia * dias_semana * 52
    monthly_km = annual_km / 12
    monthly_hours = horas_dia * dias_semana * 4.33
    vehicle_monthly_cost = 0.0
    if tipo_posse == "Aluguel":
        vehicle_monthly_cost = valor_aluguel_semana * 4.33
    elif tipo_posse == "Financiamento":
        vehicle_monthly_cost = valor_parcela

    cf_depreciacao_anual = fipe_val * 0.24
    cf_ipva_anual = cf_ipva
    cf_licenciamento_anual = cf_licenciamento
    cf_seguro_obrig_anual = cf_seguro_obrig
    cf_seguro_carro_anual = cf_seguro_carro
    cf_financiamento_anual = vehicle_monthly_cost * 12
    cf_inss_anual = cf_inss * 12
    cf_internet_anual = cf_internet * 12
    total_cf_anual = (
        cf_depreciacao_anual
        + cf_ipva_anual
        + cf_licenciamento_anual
        + cf_seguro_obrig_anual
        + cf_seguro_carro_anual
        + cf_financiamento_anual
        + cf_inss_anual
        + cf_internet_anual
    )
    cv_alimentacao_anual = cv_alim_dia * dias_semana * 52
    daily_fuel = km_dia / max(consumo_comb, 0.1) * preco_comb
    cv_combustivel_anual = daily_fuel * dias_semana * 52
    cv_oleo_anual = annual_km / 10000 * cv_oleo
    cv_pneu_anual = annual_km / 60000 * cv_pneu
    cv_manut_anual = cv_manut_mensal * 12
    cv_lavagem_anual = cv_lavagem * 12
    cv_alinhamento_anual = (
        annual_km / 10000 * cv_alinhamento if cv_alinhamento > 0 else 0.0
    )
    total_cv_anual = (
        cv_alimentacao_anual
        + cv_combustivel_anual
        + cv_oleo_anual
        + cv_pneu_anual
        + cv_manut_anual
        + cv_lavagem_anual
        + cv_alinhamento_anual
    )
    custo_operacional_anual = total_cf_anual + total_cv_anual
    cp_ipca_anual = custo_operacional_anual * (cp_ipca / 100)
    cp_iss_anual = remuneracao_semanal * (cp_iss / 100) * 52
    cp_icms_anual = remuneracao_semanal * (cp_icms / 100) * 52
    total_costs_with_taxes_iss = (
        custo_operacional_anual + cp_ipca_anual + cp_iss_anual
    )
    profit_margin_iss = total_costs_with_taxes_iss * (margem_iss / 100)
    markup_iss_anual = total_costs_with_taxes_iss + profit_margin_iss
    total_costs_with_taxes_icms = (
        custo_operacional_anual + cp_ipca_anual + cp_icms_anual
    )
    profit_margin_icms = total_costs_with_taxes_icms * (margem_icms / 100)
    markup_icms_anual = total_costs_with_taxes_icms + profit_margin_icms
    total_cp_iss_anual = cp_iss_anual + cp_ipca_anual
    total_cp_icms_anual = cp_icms_anual + cp_ipca_anual
    custo_operacional_mensal = custo_operacional_anual / 12

    custo_por_km = (
        custo_operacional_mensal / monthly_km if monthly_km > 0 else 0.0
    )
    custo_por_hora = (
        custo_operacional_mensal / monthly_hours if monthly_hours > 0 else 0.0
    )

    markup_iss_mensal = markup_iss_anual / 12
    valor_ideal_km = markup_iss_mensal / monthly_km if monthly_km > 0 else 0.0
    valor_ideal_hora = (
        markup_iss_mensal / monthly_hours if monthly_hours > 0 else 0.0
    )

    total_cf = total_cf_anual / 12
    total_cv = total_cv_anual / 12
    total_cp_iss = total_cp_iss_anual / 12
    total_cp_icms = total_cp_icms_anual / 12

    markup_iss = (
        (markup_iss_anual / custo_operacional_anual - 1) * 100
        if custo_operacional_anual > 0
        else 0.0
    )
    markup_icms = (
        (markup_icms_anual / custo_operacional_anual - 1) * 100
        if custo_operacional_anual > 0
        else 0.0
    )

    faturamento_bruto = markup_iss_mensal
    days_per_month = dias_semana * 4.33
    custo_diario = (
        custo_operacional_mensal / days_per_month if days_per_month > 0 else 0.0
    )
    custo_semanal = custo_diario * dias_semana

    combustivel_mensal = cv_combustivel_anual / 12
    oleo_mensal = cv_oleo_anual / 12
    pneu_mensal = cv_pneu_anual / 12
    vehicle_monthly = cf_financiamento_anual / 12

    return {
        "custo_por_km": custo_por_km,
        "custo_por_hora": custo_por_hora,
        "valor_ideal_km": valor_ideal_km,
        "valor_ideal_hora": valor_ideal_hora,
        "total_cf": total_cf,
        "total_cv": total_cv,
        "total_cp_iss": total_cp_iss,
        "total_cp_icms": total_cp_icms,
        "custo_mensal_total": custo_operacional_mensal,
        "markup_iss": markup_iss,
        "markup_icms": markup_icms,
        "markup_sugerido": markup_iss,
        "faturamento_bruto": faturamento_bruto,
        "custo_diario": custo_diario,
        "custo_semanal": custo_semanal,
        "cv_combustivel_anual": cv_combustivel_anual,
        "cv_oleo_anual": cv_oleo_anual,
        "cv_pneu_anual": cv_pneu_anual,
        "cv_manut_anual": cv_manut_anual,
        "cv_alinhamento_anual": cv_alinhamento_anual,
        "cf_financiamento_anual": cf_financiamento_anual,
        "total_cf_anual": total_cf_anual,
        "total_cv_anual": total_cv_anual,
        "total_cp_iss_anual": total_cp_iss_anual,
    }