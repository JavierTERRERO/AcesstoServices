from typing import Optional, Iterator, List
from bs4 import BeautifulSoup
from operator import attrgetter
from operator import methodcaller
from dataclasses import dataclass
import json
import dataclasses


class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)


@dataclass
class RootFullResult:
	agences: List[str]


class Root:
	def __init__(self, html: BeautifulSoup):
		self.html = html

	def to_json(self) -> str:
		return json.dumps(self.get_full_result(), cls=EnhancedJSONEncoder)

	def agences(self) -> Iterator[str]:
		return map(itemgetter("href", self.html.select("a.block-item-link")))

	def get_full_result(self) -> 'RootFullResult':
		return RootFullResult(list(self.agences()))


@dataclass
class AgencesFullResult:
	name_txt: Optional[str]
	type_txt: Optional[str]
	address_txt: Optional[str]
	gps_txt: Optional[str]
	candidat_txt: Optional[str]
	employeur_txt: Optional[str]


class Agences:
	def __init__(self, html: BeautifulSoup):
		self.html = html

	def to_json(self) -> str:
		return json.dumps(self.get_full_result(), cls=EnhancedJSONEncoder)

	def name_txt(self) -> Optional[str]:
		return None if (element := self.html.select_one("div.col-xs-6:nth-of-type(1) strong")) is None else element.text

	def type_txt(self) -> Optional[str]:
		return None if (element := self.html.select_one("p.text-center")) is None else element.text

	def address_txt(self) -> Optional[str]:
		return None if (element := self.html.select_one("div:nth-of-type(3) dd")) is None else element.text

	def gps_txt(self) -> Optional[str]:
		return None if (element := self.html.select_one("dd:nth-of-type(4)")) is None else element.text

	def candidat_txt(self) -> Optional[str]:
		return None if (element := self.html.select_one("dd:nth-of-type(1) a")) is None else element.text

	def employeur_txt(self) -> Optional[str]:
		return None if (element := self.html.select_one("dd:nth-of-type(2) a")) is None else element.text

	def get_full_result(self) -> 'AgencesFullResult':
		return AgencesFullResult(self.name_txt(), self.type_txt(), self.address_txt(), self.gps_txt(), self.candidat_txt(), self.employeur_txt())

# Site:
base_url = 'https://www.pole-emploi.fr/annuaire/votre-pole-emploi.html'

base_data = Root(base_url)
print(base_data)

data = AgencesFullResult('base_url')
