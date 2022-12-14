"""SMHI Metobs v1 integration tests."""
import pytest
import datetime
from smhi.metobs import Metobs, Parameters, Stations, Periods, Data


class TestIntegrationMetobs:
    """Integration tests of Metobs."""

    @pytest.mark.parametrize(
        "parameter, station, period, init_key, init_title, parameter_data_0, "
        + "station_data_0, period_data_0, data_title, table_loc, table, header_0",
        [
            (
                1,
                1,
                "corrected-archive",
                "metobs",
                "Meteorologiska observationer från SMHI: Välj "
                + "version (sedan parameter, station och tidsutsnitt)",
                ("1", "Lufttemperatur"),
                (1, "Akalla"),
                "corrected-archive",
                "Lufttemperatur - Akalla - Kvalitetskontrollerade historiska "
                + "data (utom de senaste 3 mån): Ladda ner data",
                None,
                False,
                None,
            ),
            (
                1,
                192840,
                "corrected-archive",
                "metobs",
                "Meteorologiska observationer från SMHI: Välj "
                + "version (sedan parameter, station och tidsutsnitt)",
                ("1", "Lufttemperatur"),
                (1, "Akalla"),
                "corrected-archive",
                "Lufttemperatur - Karesuando A - Kvalitetskontrollerade "
                + "historiska data (utom de senaste 3 mån): Ladda ner data",
                16,
                "2008-11-01",
                "\ufeffStationsnamn;Stationsnummer;Stationsnät;Mäthöjd (meter "
                + "över marken)\nKaresuando A;192840;SMHIs stationsnät;2.0\n\n"
                + "Parameternamn;Beskrivning;Enhet\nLufttemperatur;momentanvärde, "
                + "1 gång/tim;degree celsius\n\nTidsperiod (fr.o.m);Tidsperiod "
                + "(t.o.m);Höjd (meter över havet);Latitud (decimalgrader);Longitud "
                + "(decimalgrader)\n2008-11-01 00:00:00;{{ date }} 08:00:00;329.68;"
                + "68.4418;22.4435\n\n",
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
            header_0
        """
        if header_0:
            header_0 = header_0.replace(
                "{{ date }}", datetime.date.today().strftime("%Y-%m") + "-01"
            )

        client = Metobs()
        client.get_parameters()
        client.get_stations(parameter)
        client.get_periods(station)
        header, data = client.get_data(period)

        assert client.parameters.data[0] == parameter_data_0
        assert client.stations.data[0] == station_data_0
        assert client.periods.data[0] == period_data_0
        assert client.data.title == data_title
        if table:
            assert data.iloc[table_loc, 0] == table
            assert header == header_0

    @pytest.mark.parametrize(
        "parameter, station, period, init_key, init_title, parameter_data_0, "
        + "station_data_0, period_data_0, data_title, table_loc, table, header_0",
        [
            (
                1,
                1,
                "corrected-archive",
                "metobs",
                "Meteorologiska observationer från SMHI: Välj "
                + "version (sedan parameter, station och tidsutsnitt)",
                ("1", "Lufttemperatur"),
                (1, "Akalla"),
                "corrected-archive",
                "Lufttemperatur - Akalla - Kvalitetskontrollerade historiska "
                + "data (utom de senaste 3 mån): Ladda ner data",
                None,
                False,
                None,
            ),
            (
                1,
                192840,
                "corrected-archive",
                "metobs",
                "Meteorologiska observationer från SMHI: Välj "
                + "version (sedan parameter, station och tidsutsnitt)",
                ("1", "Lufttemperatur"),
                (1, "Akalla"),
                "corrected-archive",
                "Lufttemperatur - Karesuando A - Kvalitetskontrollerade "
                + "historiska data (utom de senaste 3 mån): Ladda ner data",
                16,
                "2008-11-01",
                "\ufeffStationsnamn;Stationsnummer;Stationsnät;Mäthöjd (meter "
                + "över marken)\nKaresuando A;192840;SMHIs stationsnät;2.0\n\n"
                + "Parameternamn;Beskrivning;Enhet\nLufttemperatur;momentanvärde, "
                + "1 gång/tim;degree celsius\n\nTidsperiod (fr.o.m);Tidsperiod "
                + "(t.o.m);Höjd (meter över havet);Latitud (decimalgrader);Longitud "
                + "(decimalgrader)\n2008-11-01 00:00:00;{{ date }} 08:00:00;329.68;"
                + "68.4418;22.4435\n\n",
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
            header_0
        """
        if header_0:
            header_0 = header_0.replace(
                "{{ date }}", datetime.date.today().strftime("%Y-%m") + "-01"
            )

        parameters = Parameters()
        stations = Stations(parameters, parameter)
        periods = Periods(stations, station)
        data = Data(periods, period)

        assert parameters.data[0] == parameter_data_0
        assert stations.data[0] == station_data_0
        assert periods.data[0] == period_data_0
        assert data.title == data_title
        if table:
            assert data.data.iloc[table_loc, 0] == table
            assert data.data_header == header_0
