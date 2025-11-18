from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        self.tour_per_regione = {}

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
        Interroga il database per ottenere tutte le relazioni fra tour e attrazioni
        """
        relazioni = TourDAO.get_tour_attrazioni()

        for tour in self.tour_map.values():
            tour.attrazioni = set()

        for relazione in relazioni:

            id_tour = relazione["id_tour"]
            id_attrazione = relazione["id_attrazione"]

            tour = self.tour_map.get(id_tour)
            attrazione = self.attrazioni_map.get(id_attrazione)



    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        tour_della_regione = []
        for tour in self.tour_map.values():
            if tour.id_regione == id_regione:
                tour_della_regione.append(tour)

        if not tour_della_regione:
            return self._pacchetto_ottimo, self._costo, self._valore_ottimo

        self._ricorsione(
            start_index=0,
            pacchetto_parziale = [],
            durata_corrente=0,
            costo_corrente=0,
            valore_corrente=0,
            attrazioni_usate=set(),
            tour_disponibili=tour_della_regione,
            max_giorni=max_giorni,
            max_budget=max_budget
        )

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int,
                    costo_corrente: float, valore_corrente: int, attrazioni_usate: set,
                    tour_disponibili: list, max_giorni: int, max_budget: float):
        """
        Algoritmo ricorsivo con backtracking per trovare il pacchetto ottimale
        """
        # 🟤 A - Aggiorna soluzione ottima se migliore
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._costo = costo_corrente

        # 🔴 E - Ricorsione
        for i in range(start_index, len(tour_disponibili)):
            tour = tour_disponibili[i]

            # 🟡 C - Verifica vincoli prima di procedere
            # Vincolo giorni
            if max_giorni is not None and durata_corrente + tour.durata_giorni > max_giorni:
                continue

            # Vincolo budget
            if max_budget is not None and costo_corrente + tour.costo > max_budget:
                continue

            # Vincolo attrazioni duplicate
            if not hasattr(tour, 'attrazioni'):
                continue

            nuove_attrazioni = tour.attrazioni - attrazioni_usate
            if not nuove_attrazioni:
                continue  # Tour non aggiunge nuove attrazioni

            # 🟢 B - Calcola il valore aggiuntivo
            valore_aggiuntivo = sum(attr.valore_culturale for attr in nuove_attrazioni)

            # 🔵 D - Aggiorna stato corrente
            pacchetto_parziale.append(tour)
            nuovo_valore = valore_corrente + valore_aggiuntivo
            nuova_durata = durata_corrente + tour.durata_giorni
            nuovo_costo = costo_corrente + tour.costo
            nuove_attrazioni_usate = attrazioni_usate.union(nuove_attrazioni)

            # Ricorsione
            self._ricorsione(i + 1, pacchetto_parziale, nuova_durata, nuovo_costo,
                             nuovo_valore, nuove_attrazioni_usate, tour_disponibili,
                             max_giorni, max_budget)

            # 🟣 F - Backtracking
            pacchetto_parziale.pop()


