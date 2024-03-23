"""SMHI Metobs v1 integration tests."""

import json
import time

import pandas as pd
import pytest
from smhi.metobs import Data, Parameters, Periods, Stations

METOBS_INTEGRATION = {}
for i in [1, 2, 22]:
    with open(f"tests/fixtures/metobs_integration_{i}.json", encoding="utf-8") as f:
        METOBS_INTEGRATION[i] = []
        all_headers = json.load(f)
        for header in all_headers:
            METOBS_INTEGRATION[i].append(pd.DataFrame(header, index=[0]))


class TestIntegrationMetobs:
    """Integration tests of Metobs."""

    @pytest.mark.parametrize(
        "parameter, station, period, init_key, init_title, parameter_data_0, "
        + "station_data_0, period_data_0, data_title, table_locr, table_locc, "
        + "table, header_0",
        [
            (
                1,
                1,
                "corrected-archive",
                "metobs",
                "Meteorologiska observationer från SMHI: Välj "
                + "version (sedan parameter, station och tidsutsnitt)",
                ("1", "Lufttemperatur", "momentanvärde, 1 gång/tim"),
                (1, "Akalla"),
                "corrected-archive",
                "Lufttemperatur - Akalla - Kvalitetskontrollerade historiska "
                + "data (utom de senaste 3 mån): Ladda ner data",
                None,
                None,
                False,
                {},
            ),
            (
                1,
                192840,
                "corrected-archive",
                "metobs",
                "Meteorologiska observationer från SMHI: Välj "
                + "version (sedan parameter, station och tidsutsnitt)",
                ("1", "Lufttemperatur", "momentanvärde, 1 gång/tim"),
                (192840, "Karesuando A"),
                "corrected-archive",
                "Lufttemperatur - Karesuando A - Kvalitetskontrollerade "
                + "historiska data (utom de senaste 3 mån): Ladda ner data",
                0,
                0,
                -15.2,
                METOBS_INTEGRATION[1],
            ),
            (
                2,
                192840,
                "corrected-archive",
                "metobs",
                "Meteorologiska observationer från SMHI: Välj "
                + "version (sedan parameter, station och tidsutsnitt)",
                ("2", "Lufttemperatur", "medelvärde 1 dygn, 1 gång/dygn, kl 00"),
                (192840, "Karesuando A"),
                "corrected-archive",
                "Lufttemperatur - Karesuando A - Kvalitetskontrollerade "
                + "historiska data (utom de senaste 3 mån): Ladda ner data",
                0,
                2,
                -16.1,
                METOBS_INTEGRATION[2],
            ),
            (
                22,
                192840,
                "corrected-archive",
                "metobs",
                "Meteorologiska observationer från SMHI: Välj "
                + "version (sedan parameter, station och tidsutsnitt)",
                ("22", "Lufttemperatur", "medel, 1 gång per månad"),
                (192840, "Karesuando A"),
                "corrected-archive",
                "Lufttemperatur - Karesuando A - Kvalitetskontrollerade "
                + "historiska data (utom de senaste 3 mån): Ladda ner data",
                0,
                2,
                -8.7,
                METOBS_INTEGRATION[22],
            ),
        ],
    )
    def test_integration_metobs_second(
        self,
        parameter,
        station,
        period,
        init_key,
        init_title,
        parameter_data_0,
        station_data_0,
        period_data_0,
        data_title,
        table_locr,
        table_locc,
        table,
        header_0,
    ):
        """Integration test of the Metobs API through the object clients.

        Args:
            parameter
            station
            period
            init_key
            init_title
            parameter_data_0
            station_data_0
            period_data_0
            data_title
            table_locr,
            table_locc
            table
            header_0
        """
        parameters = Parameters()
        stations = Stations(parameters, parameter)
        periods = Periods(stations, station)
        periods_from_name = Periods(stations, station_name=station_data_0[1])
        data = Data(periods, period)

        station_index = [i for i, x in enumerate(stations.data) if x[0] == station][0]

        assert parameters.data[parameter - 1] == parameter_data_0
        assert stations.data[station_index] == station_data_0
        assert periods.data[0] == period_data_0
        assert periods_from_name.data[0] == period_data_0
        assert data.title == data_title
        if table:
            assert data.data.iloc[table_locr, table_locc] == table
            pd.testing.assert_frame_equal(data.station, header_0[0])
            pd.testing.assert_frame_equal(data.parameter, header_0[1])
            pd.testing.assert_frame_equal(
                data.period[
                    data.period.columns.drop(
                        list(data.period.filter(regex="Tidsperiod"))
                    )
                ],
                header_0[2][
                    header_0[2].columns.drop(
                        list(header_0[2].filter(regex="Tidsperiod"))
                    )
                ],
            )

        time.sleep(1)

    @pytest.mark.parametrize(
        "parameter", [parameter for parameter, _, _ in Parameters().data]
    )
    def test_integration_metobs_passing(self, parameter):
        """Test that all parameters available return data without error.

        This does not check that the returned data is correct, only that the client
        does fetch data without error.

        Args:
            parameter: parameter to test
        """
        parameters = Parameters()
        stations = Stations(parameters, parameter)
        periods = Periods(stations, stations.data[1][0])

        try:
            _ = Data(periods)
            assert True
        except TypeError:
            assert True
        except Exception:
            assert False

        time.sleep(1)
