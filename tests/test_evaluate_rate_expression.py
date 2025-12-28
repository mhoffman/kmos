#!/usr/bin/env python
"""Unit tests for kmos.evaluate_rate_expression function."""

import pytest
from kmos import evaluate_rate_expression, species


class TestEvaluateRateExpression:
    """Test suite for evaluate_rate_expression function."""

    def test_simple_constant(self):
        """Test evaluation of a simple numeric constant."""
        result = evaluate_rate_expression(rate_expr="1.5e-3")
        assert result == pytest.approx(1.5e-3)

    def test_math_expression(self):
        """Test evaluation with math operations."""
        result = evaluate_rate_expression(rate_expr="2 * 3 + 4")
        assert result == pytest.approx(10.0)

    def test_exp_function(self):
        """Test evaluation with exp function."""
        result = evaluate_rate_expression(rate_expr="exp(1)")
        assert result == pytest.approx(2.718281828, rel=1e-6)

    def test_with_parameters(self):
        """Test evaluation with parameters."""
        parameters = {"T": {"value": 600}, "p_CO": {"value": 1.0}}
        result = evaluate_rate_expression(rate_expr="T * 2", parameters=parameters)
        assert result == pytest.approx(1200.0)

    def test_with_physical_constants(self):
        """Test evaluation with physical constants (kboltzmann, h, eV)."""
        result = evaluate_rate_expression(rate_expr="kboltzmann * 600")
        expected = 1.3806488e-23 * 600
        assert result == pytest.approx(expected, rel=1e-6)

    def test_arrhenius_expression(self):
        """Test a typical Arrhenius rate expression."""
        parameters = {"T": {"value": 600}}
        rate_expr = "1/(beta*h)*exp(-beta*0.9*eV)"
        result = evaluate_rate_expression(rate_expr=rate_expr, parameters=parameters)
        assert result > 0  # Should be positive
        assert result < 1e20  # Should be a reasonable value

    def test_with_species_module_no_mu(self):
        """Test that species module can be passed even when not needed."""
        result = evaluate_rate_expression(rate_expr="1.5e-3", species=species)
        assert result == pytest.approx(1.5e-3)

    def test_species_namespace_available(self):
        """
        Regression test for species namespace issue.

        This test ensures that the species module is properly available
        in the eval namespace when needed, preventing UnboundLocalError.
        """
        # This should not raise UnboundLocalError even though
        # species is only conditionally imported
        result = evaluate_rate_expression(rate_expr="2 + 3", species=species)
        assert result == pytest.approx(5.0)

    def test_invalid_expression(self):
        """Test that invalid expressions raise appropriate errors."""
        with pytest.raises(UserWarning, match="Could not evaluate rate expression"):
            evaluate_rate_expression(rate_expr="undefined_variable")

    def test_empty_expression(self):
        """Test handling of empty expression."""
        result = evaluate_rate_expression(rate_expr="")
        assert result == pytest.approx(0.0)

    def test_parameters_as_list(self):
        """Test that parameters can be passed as a list of Parameter objects."""
        from kmos.types import Parameter

        params = [Parameter(name="T", value=600), Parameter(name="p_CO", value=1.0)]
        result = evaluate_rate_expression(rate_expr="T * 2", parameters=params)
        assert result == pytest.approx(1200.0)

    def test_complex_rate_expression_with_species(self):
        """
        Test a complex rate expression that would trigger species import.

        This is the type of expression that caused the original bug where
        species was not available in the eval namespace.
        """
        parameters = {"T": {"value": 600}, "E_react": {"value": 0.9}}
        # Expression similar to what's in AB_model.xml
        rate_expr = "1/(beta*h)*exp(-beta*E_react*eV)"

        result = evaluate_rate_expression(
            rate_expr=rate_expr, parameters=parameters, species=species
        )

        # Verify it's a reasonable rate constant
        assert result > 0
        assert result < 1e20

    def test_beta_alias_expansion(self):
        """Test that beta alias expands correctly to 1/(kboltzmann*T)."""
        parameters = {"T": {"value": 600}}

        # Using beta directly
        result_with_beta = evaluate_rate_expression(
            rate_expr="beta", parameters=parameters
        )

        # Manual expansion
        expected = 1.0 / (1.3806488e-23 * 600)

        assert result_with_beta == pytest.approx(expected, rel=1e-6)

    def test_regression_species_unbound_error(self):
        """
        Regression test for UnboundLocalError with species variable.

        This test reproduces the exact bug that occurred when exporting
        AB_model.xml. The bug happened because:
        1. evaluate_rate_expression tried to pass 'species' to eval()
        2. But 'species' was only imported conditionally (when mu_ tokens exist)
        3. This caused UnboundLocalError when species wasn't imported
        4. Even though species was imported at module level in io.py,
           a local 'species' variable in a for loop shadowed it

        The fix was to:
        - Make species an optional parameter to evaluate_rate_expression
        - Import species as species_module in io.py to avoid shadowing
        - Only include species in eval namespace if it's provided
        """
        from kmos import species as species_mod

        parameters = {"T": {"value": 600}, "E_react": {"value": 0.9}}

        # This is similar to the expression from AB_model.xml that triggered the bug
        # Using the symbolic form that gets expanded
        rate_expr = "1/(beta*h)*exp(-beta*E_react*eV)"

        # This should NOT raise UnboundLocalError
        result = evaluate_rate_expression(
            rate_expr=rate_expr, parameters=parameters, species=species_mod
        )

        assert result > 0
        assert result < 1e20

    def test_evaluate_without_species_param(self):
        """
        Test that expressions without mu_ tokens work without species parameter.

        This ensures backward compatibility - calls without species parameter
        should still work for expressions that don't need it.
        """
        parameters = {"T": {"value": 600}}
        rate_expr = "1/(beta*h)*exp(-beta*0.9*eV)"

        # Should work without species parameter
        result = evaluate_rate_expression(rate_expr=rate_expr, parameters=parameters)

        assert result > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
