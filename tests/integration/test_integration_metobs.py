"""SMHI Metobs v1 integration tests."""

import json
import time

import pandas as pd
import pytest
from smhi.metobs import Data, Parameters, Periods, Stations
from smhi.models.metobs_model import MetobsVersionItem

METOBS_INTEGRATION_DF = {}
for i in [1, 2, 22]:
    with open(
        f"tests/fixtures/metobs/metobs_integration_{i}.json", encoding="utf-8"
    ) as f:
        METOBS_INTEGRATION_DF[i] = []
        all_dfs = json.load(f)
        for j, header in enumerate(all_dfs):
            METOBS_INTEGRATION_DF[i].append(pd.DataFrame(header, index=[0]))

            if j == 3:
                METOBS_INTEGRATION_DF[i][j].set_index("Index", drop=True, inplace=True)
                METOBS_INTEGRATION_DF[i][j].index.name = None
                METOBS_INTEGRATION_DF[i][j].index = pd.to_datetime(
                    METOBS_INTEGRATION_DF[i][j].index, utc=True
                )


class TestIntegrationMetobs:
    """Integration tests of Metobs."""

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
            (
                1,
                192840,
                "corrected-archive",
                MetobsVersionItem(
                    key="1",
                    title="Lufttemperatur",
                    summary="momentanvärde, 1 gång/tim",
                    unit="celsius",
                ),
                (192840, "Karesuando A"),
                "corrected-archive",
                "Lufttemperatur - Karesuando A - Kvalitetskontrollerade "
                + "historiska data (utom de senaste 3 mån): Ladda ner data",
                METOBS_INTEGRATION_DF[1],
            ),
            (
                2,
                192840,
                "corrected-archive",
                MetobsVersionItem(
                    key="2",
                    title="Lufttemperatur",
                    summary="medelvärde 1 dygn, 1 gång/dygn, kl 00",
                    unit="celsius",
                ),
                (192840, "Karesuando A"),
                "corrected-archive",
                "Lufttemperatur - Karesuando A - Kvalitetskontrollerade "
                + "historiska data (utom de senaste 3 mån): Ladda ner data",
                METOBS_INTEGRATION_DF[2],
            ),
            (
                22,
                192840,
                "corrected-archive",
                MetobsVersionItem(
                    key="22",
                    title="Lufttemperatur",
                    summary="medel, 1 gång per månad",
                    unit="celsius",
                ),
                (192840, "Karesuando A"),
                "corrected-archive",
                "Lufttemperatur - Karesuando A - Kvalitetskontrollerade "
                + "historiska data (utom de senaste 3 mån): Ladda ner data",
                METOBS_INTEGRATION_DF[22],
            ),
        ],
    )
    def test_integration_metobs_second(
        self,
        parameter,
        station,
        period,
        parameter_data,
        station_data,
        period_data,
        data_title,
        data_df,
    ):
        """Integration test of the Metobs API through the object clients."""
        parameters = Parameters()
        stations = Stations(parameters, parameter)
        periods = Periods(stations, station)
        periods_from_name = Periods(stations, station_name=station_data[1])
        data = Data(periods, period)

        station_index = [i for i, x in enumerate(stations.data) if x[0] == station][0]

        assert parameters.data[parameter - 1] == parameter_data
        assert stations.data[station_index] == station_data
        assert periods.data[0] == period_data
        assert periods_from_name.data[0] == period_data
        assert data.title == data_title

        if len(data_df) > 0:
            pd.testing.assert_frame_equal(data.station, data_df[0])
            pd.testing.assert_frame_equal(data.parameter, data_df[1])
            pd.testing.assert_frame_equal(
                data.period.iloc[:, 2:],
                data_df[2].iloc[:, 2:],  # skip columns Tidsperiod
            )
            pd.testing.assert_frame_equal(data.df.iloc[:1, :], data_df[3])

        time.sleep(1)

    @pytest.mark.parametrize(
        "parameter", [parameter.key for parameter in Parameters().data]
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
