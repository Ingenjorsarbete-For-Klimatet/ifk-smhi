"""SMHI Metobs v1 integration tests."""
import json
import pytest
import datetime
from smhi.metobs import Metobs, Parameters, Stations, Periods, Data


with open("tests/fixtures/metobs_integration_1.json") as f:
    metobs_integration_1 = json.load(f)
    metobs_integration_1["Tidsperiod (t.o.m)"] = (
        datetime.date.today().strftime("%Y-%m") + "-01 07:20:09"
    )

with open("tests/fixtures/metobs_integration_2.json") as f:
    metobs_integration_2 = json.load(f)
    metobs_integration_2["Tidsperiod (t.o.m)"] = (
        datetime.date.today().strftime("%Y-%m") + "-01 07:20:09"
    )


class TestIntegrationMetobs:
    """Integration tests of Metobs."""

    @pytest.mark.parametrize(
        "parameter, station, period, init_key, init_title, parameter_data_0, "
        + "station_data_0, period_data_0, data_title, table_loc, table, "
        + "raw_header_0, header_0",
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
                -15.2,
                "\ufeffStationsnamn;Stationsnummer;Stationsnät;Mäthöjd (meter "
                + "över marken)\nKaresuando A;192840;SMHIs stationsnät;2.0\n\n"
                + "Parameternamn;Beskrivning;Enhet\nLufttemperatur;momentanvärde, "
                + "1 gång/tim;celsius\n\nTidsperiod (fr.o.m);Tidsperiod "
                + "(t.o.m);Höjd (meter över havet);Latitud (decimalgrader);Longitud "
                + "(decimalgrader)\n2008-11-01 00:00:00;{{ date }} 07:20:09;329.68;"
                + "68.4418;22.4435\n\n",
                metobs_integration_2,
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
        table_loc,
        table,
        raw_header_0,
        header_0,
    ):
        """Integration test of Metobs.

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
            table_loc
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

        assert client.parameters.data[0] == parameter_data_0
        assert client.stations.data[station_index] == station_data_0
        assert client.periods.data[0] == period_data_0
        assert client.data.title == data_title
        if table:
            assert data.iloc[table_loc, 0] == table
            assert data_header == header_0

    @pytest.mark.parametrize(
        "parameter, station, period, init_key, init_title, parameter_data_0, "
        + "station_data_0, period_data_0, data_title, table_loc, table, "
        + "raw_header_0, header_0",
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
                -15.2,
                "\ufeffStationsnamn;Stationsnummer;Stationsnät;Mäthöjd (meter "
                + "över marken)\nKaresuando A;192840;SMHIs stationsnät;2.0\n\n"
                + "Parameternamn;Beskrivning;Enhet\nLufttemperatur;momentanvärde, "
                + "1 gång/tim;celsius\n\nTidsperiod (fr.o.m);Tidsperiod "
                + "(t.o.m);Höjd (meter över havet);Latitud (decimalgrader);Longitud "
                + "(decimalgrader)\n2008-11-01 00:00:00;{{ date }} 07:20:09;329.68;"
                + "68.4418;22.4435\n\n",
                metobs_integration_2,
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
        table_loc,
        table,
        raw_header_0,
        header_0,
    ):
        """Integration test of Metobs.

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
            table_loc
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

        assert parameters.data[0] == parameter_data_0
        assert stations.data[station_index] == station_data_0
        assert periods.data[0] == period_data_0
        assert periods_from_name.data[0] == period_data_0
        assert data.title == data_title
        if table:
            assert data.data.iloc[table_loc, 0] == table
            assert data.raw_data_header == raw_header_0
            assert data.data_header == header_0
