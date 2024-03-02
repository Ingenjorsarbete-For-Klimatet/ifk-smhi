"""SMHI Metobs v1 integration tests."""
import json
import time
import pytest
import datetime
from smhi.metobs import Metobs, Parameters, Stations, Periods, Data

METOBS_INTEGRATION = {}
for i in [1, 2, 22]:
    with open(f"tests/fixtures/metobs_integration_{i}.json", encoding="utf-8") as f:
        METOBS_INTEGRATION[i] = json.load(f)

        if i == 1:
            METOBS_INTEGRATION[i]["Tidsperiod (t.o.m)"] = (
                datetime.date.today().strftime("%Y-%m") + "-01 07:20:09"
            )

        if i == 2:
            METOBS_INTEGRATION[i]["Tidsperiod (t.o.m)"] = (
                datetime.date.today().strftime("%Y-%m") + "-01 08:20:12"
            )

        if i == 22:
            METOBS_INTEGRATION[i]["Tidsperiod (t.o.m)"] = (
                datetime.date.today().strftime("%Y-%m") + "-01 18:21:06"
            )


class TestIntegrationMetobs:
    """Integration tests of Metobs."""

    @pytest.mark.parametrize(
        "parameter, station, period, init_key, init_title, parameter_data_0, "
        + "station_data_0, period_data_0, data_title, table_locr, table_locc, "
        + "table, raw_header_0, header_0",
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
                None,
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
                "\ufeffStationsnamn;Stationsnummer;Stationsnät;Mäthöjd (meter "
                + "över marken)\nKaresuando A;192840;SMHIs stationsnät;2.0\n\n"
                + "Parameternamn;Beskrivning;Enhet\nLufttemperatur;momentanvärde, "
                + "1 gång/tim;celsius\n\nTidsperiod (fr.o.m);Tidsperiod "
                + "(t.o.m);Höjd (meter över havet);Latitud (decimalgrader);Longitud "
                + "(decimalgrader)\n2008-11-01 00:00:00;{{ date }} 07:20:09;329.68;"
                + "68.4418;22.4435\n\n",
                METOBS_INTEGRATION[1],
            ),
        ],
    )
    def test_integration_metobs_first(
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
        raw_header_0,
        header_0,
    ):
        """Integration test of the Metobs API used through the Metobs client.

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
            table_locr
            table_locc
            table
            raw_header_0
            header_0
        """
        if raw_header_0:
            raw_header_0 = raw_header_0.replace(
                "{{ date }}", datetime.date.today().strftime("%Y-%m") + "-01"
            )

        client = Metobs()
        client.get_parameters()
        client.get_stations(parameter)
        client.get_periods(station)
        data, data_header = client.get_data(period)

        station_index = [
            i for i, x in enumerate(client.stations.data) if x[0] == station
        ][0]

        assert client.parameters.data[parameter - 1] == parameter_data_0
        assert client.stations.data[station_index] == station_data_0
        assert client.periods.data[0] == period_data_0
        assert client.data.title == data_title
        if table:
            assert data.iloc[table_locr, table_locc] == table
            assert data_header == header_0

        time.sleep(1)

    @pytest.mark.parametrize(
        "parameter, station, period, init_key, init_title, parameter_data_0, "
        + "station_data_0, period_data_0, data_title, table_locr, table_locc, "
        + "table, raw_header_0, header_0",
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
                None,
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
                "\ufeffStationsnamn;Stationsnummer;Stationsnät;Mäthöjd (meter "
                + "över marken)\nKaresuando A;192840;SMHIs stationsnät;2.0\n\n"
                + "Parameternamn;Beskrivning;Enhet\nLufttemperatur;momentanvärde, "
                + "1 gång/tim;celsius\n\nTidsperiod (fr.o.m);Tidsperiod "
                + "(t.o.m);Höjd (meter över havet);Latitud (decimalgrader);Longitud "
                + "(decimalgrader)\n2008-11-01 00:00:00;{{ date }} 07:20:09;329.68;"
                + "68.4418;22.4435\n\n",
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
                "\ufeffStationsnamn;Stationsnummer;Stationsnät;Mäthöjd (meter "
                + "över marken)\nKaresuando A;192840;SMHIs stationsnät;2.0\n\n"
                + "Parameternamn;Beskrivning;Enhet\nLufttemperatur;medelvärde 1 "
                + "dygn, 1 gång/dygn, kl 00;celsius\n\nTidsperiod (fr.o.m);Tidsperiod "
                + "(t.o.m);Höjd (meter över havet);Latitud (decimalgrader);Longitud "
                + "(decimalgrader)\n2008-11-01 00:00:00;2024-01-01 08:20:12;329.68;"
                + "68.4418;22.4435\n\nFrån ",
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
                "\ufeffStationsnamn;Stationsnummer;Stationsnät;Mäthöjd "
                + "(meter över marken)\nKaresuando A;192840;SMHIs stationsnät;2.0\n\n"
                + "Parameternamn;Beskrivning;Enhet\nLufttemperatur;medel, 1 gång per "
                + "månad;celsius\n\nTidsperiod (fr.o.m);Tidsperiod (t.o.m);Höjd (meter "
                + "över havet);Latitud (decimalgrader);Longitud (decimalgrader)\n"
                + "2008-12-01 00:00:00;2024-01-01 18:21:06;329.68;68.4418;22.4435\n\nFrån ",
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
        raw_header_0,
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
            raw_header_0
            header_0
        """
        if raw_header_0:
            raw_header_0 = raw_header_0.replace(
                "{{ date }}", datetime.date.today().strftime("%Y-%m") + "-01"
            )

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
            assert data.raw_data_header == raw_header_0
            assert data.data_header == header_0

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
        except BaseException:
            assert False

        time.sleep(1)
