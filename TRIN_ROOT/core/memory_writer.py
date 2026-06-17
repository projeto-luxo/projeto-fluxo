from pathlib import Path
from datetime import datetime
import csv


class MemoryWriter:

    def __init__(self):

        self.pasta = Path("memoria")
        self.pasta.mkdir(exist_ok=True)

        hoje = datetime.now().strftime("%Y_%m_%d")

        self.arquivo = self.pasta / f"TRIN_MEMORIA_{hoje}.csv"

        self.cabecalho_escrito = self.arquivo.exists()

    def write(self, tick):

        campos = list(tick.keys())

        with open(
            self.arquivo,
            "a",
            newline="",
            encoding="utf-8-sig"
        ) as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=campos,
                delimiter=";"
            )

            if not self.cabecalho_escrito:
                writer.writeheader()
                self.cabecalho_escrito = True

            writer.writerow(tick)