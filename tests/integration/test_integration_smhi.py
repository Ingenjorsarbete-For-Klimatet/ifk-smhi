"""SMHI integration tests."""


class TestIntegrationSMHI:
    """Integration test of SMHI class."""


   @pytest.mark.parametrize(
        "parameter, station, period, parameter_data, station_data, period_data, data_title, data_df",
        [
            (
                1,
                1,
                "corrected-archive",
                MetobsVersionItem(
                    key="1",
                    title="Lufttemperatur",
                    summary="momentanvärde, 1 gång/tim",
                    unit="celsius",
                ),
                (1, "Akalla"),
                "corrected-archive",
                "Lufttemperatur - Akalla - Kvalitetskontrollerade historiska "
                + "data (utom de senaste 3 mån): Ladda ner data",
                {},
            ),
        ],
    )
    def test_integration_smhi(self):
        """Integration test of SMHI class."""
        
