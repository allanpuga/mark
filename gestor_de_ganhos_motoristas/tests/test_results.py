import unittest
from gestor_de_ganhos_motoristas.utils import compute_markup_math


class TestResultsMarkup(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the markup calculation logic."""

    async def test_recalculate_markup(self):
        """Verify the math logic of recalculate function using pure python math helper."""
        math_results = compute_markup_math(
            km_dia=150.0,
            dias_semana=6,
            horas_dia=8,
            tipo_posse="Próprio",
            valor_aluguel_semana=0.0,
            valor_parcela=0.0,
            fipe_val=50000.0,
            cf_ipva=2000.0,
            cf_licenciamento=160.0,
            cf_seguro_obrig=0.0,
            cf_seguro_carro=2500.0,
            cf_inss=155.32,
            cf_internet=60.0,
            cv_alim_dia=30.0,
            preco_comb=5.8,
            consumo_comb=10.0,
            cv_manut_mensal=150.0,
            cv_oleo=250.0,
            cv_pneu=1600.0,
            cv_lavagem=120.0,
            cv_alinhamento=100.0,
            cp_ipca=4.62,
            cp_iss=5.0,
            cp_icms=0.0,
            margem_iss=20.0,
            margem_icms=20.0,
            remuneracao_semanal=1551.0,
        )

        expected_monthly_km = 150 * 6 * 52 / 12
        self.assertEqual(expected_monthly_km, 3900.0)
        self.assertGreater(math_results["custo_por_km"], 0)
        self.assertGreater(
            math_results["valor_ideal_km"], math_results["custo_por_km"]
        )
        self.assertGreater(math_results["markup_sugerido"], 0)
        self.assertGreater(math_results["markup_sugerido"], 20.0)
        self.assertLess(math_results["markup_sugerido"], 40.0)
        self.assertAlmostEqual(
            math_results["faturamento_bruto"],
            math_results["valor_ideal_km"] * expected_monthly_km,
            places=0,
        )
        print(
            f"\n✓ Math Verified: Custo/km = R$ {math_results['custo_por_km']:.2f}, Ideal/km = R$ {math_results['valor_ideal_km']:.2f}, Markup = {math_results['markup_sugerido']:.1f}%"
        )


if __name__ == "__main__":
    unittest.main()