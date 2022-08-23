"""Application class for ponyexpress"""

from functools import partial, singledispatchmethod
from importlib.metadata import entry_points
from pathlib import Path
from typing import Optional, Union

import yaml
from loguru import logger as log

from ponyexpress.types import Configuration, Connector, PlugInSpec, Strategy

CONNECTOR_GROUP = "ponyexpress.connectors"
STRATEGY_GROUP = "ponyexpress.strategies"


class Spider:
    """This is ponyexpress' Spider

    With this animal we traverse the desert of social media networks.
    """

    def __init__(self) -> None:
        """This is the intializer


        Params
        ------

        Returns
        -------

        None : Nothing. Nada.
        """
        # set the loaded configuration to None, as it is not loaded yet
        self.configuration: Optional[Configuration] = None

    @classmethod
    def available_configurations(cls) -> list[dict[str, Union[str, Path]]]:
        """returns the names of available configuration files in the working directory

        Returns
        -------
        list[str] : names of the configurations, [] if no present

        """
        return [
            {"name": _.name.removesuffix(".pe.yml"), "path": _}
            for _ in Path().glob("*.pe.yml")
        ]

    def start(self, config: str):
        """start a collection

        Params
        -----

        config : str : the configuration's name which we want to load-
        """
        self.load_config(config)
        self.spider()

    # def restart(self):
    #     pass

    def load_config(self, config_name: str) -> None:
        """loads a named configuration

        Params
        ------
        config_name : str : the name of the configuration to load
        """
        log.debug(
            f"Choosing form these configurations: {Spider.available_configurations()}"
        )

        config = [
            _ for _ in Spider.available_configurations() if _["name"] == config_name
        ]

        if len(config) == 1:
            with config[0]["path"].open("r", encoding="utf8") as file:
                self.configuration = yaml.full_load(file)
        else:
            log.warning(
                f"A project named {config_name} is not present in current folder"
            )

    def spider(self) -> None:
        """runs the collections loop

        Returns:
        None : Nothing. Nada.
        """
        if not self.configuration:
            log.error("No configuration loaded. Aborting.")
        else:
            # start with seed list
            seeds = self.configuration.seeds
            connector = self.get_connector(self.configuration.connector)
            strategy = self.get_strategy(self.configuration.strategy)

            if seeds is not None:
                for _ in range(self.configuration.max_iteration):
                    edges, nodes = connector(seeds)
                    seeds = strategy(edges, nodes)

    # section: plugin loading

    def get_strategy(self, strategy_name: PlugInSpec) -> Strategy:
        """lazy load a Strategy

        Params
        ------
        strategy_name : str : name of the strategy

        Returns
        -------
        Strategy : the wished for strategy

        Raises
        ------
        IndexError : if the strategy does not exist
        """

        return self._get_plugin_from_spec_(strategy_name, STRATEGY_GROUP)

    def get_connector(self, connector_name: PlugInSpec) -> Connector:
        """lazy load a Connector

        Params
        ------
        connector_name : str : name of the connector

        Returns
        -------
        Connector : the wished for connector

        Raises
        ------
        IndexError : if the connector does not exist
        """
        return self._get_plugin_from_spec_(connector_name, CONNECTOR_GROUP)

    # section: private methods

    @singledispatchmethod
    def _get_plugin_from_spec_(self, spec: PlugInSpec, group: str):
        raise NotImplementedError()

    @_get_plugin_from_spec_.register
    def _(self, spec: str, group: str):
        entry_point = [_ for _ in entry_points()[group] if _.name == spec]
        return entry_point[0].load()

    @_get_plugin_from_spec_.register
    def _(self, spec: dict, group: str):
        for key, values in spec.items():
            entry_point = [_ for _ in entry_points()[group] if _.name == key]
            return partial(entry_point[0].load(), **values)
