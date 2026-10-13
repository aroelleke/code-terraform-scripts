from base_controller import BaseController
from dataclasses import dataclass
from machine_store import MachineStore


@dataclass
class BioCollectorConfig:
    auto_fullfill_order: bool = True


class BioCollectorController(BaseController):
    def __init__(self, ref: BioCollector):
        super().__init__(ref)
        self.ref: BioCollector

        self.store: MachineStore[BioCollectorConfig] = MachineStore(f"bio_collector.{ref.id}", BioCollectorConfig)

        self.journal: Journal = get_component("journal")

    def iteration(self):
        # When cargo is already filled, wait until it is emptied by bio lab
        if self.ref.cargo:
            return

        target = self.get_next_uncataloged()

        # No target? Get from comms
        if not target:
            target = self.get_next_task()

        # Still no target? Nothing to do
        if not target:
            return

        self.collect(target)

    def get_next_uncataloged(self) -> FragmentLocation:
        locations = self.get_uncataloged()
        if len(locations) > 0:
            return locations[0]

    def get_uncataloged(self) -> List[FragmentLocation]:
        return [location for location in self.ref.scan() if not location.cataloged]

    def get_next_task(self) -> FragmentLocation:
        task = self.comms.next()

        if not task:
            return None

        if task.value["type"] == "collect":
            return self.find_location(task.value["data"]["fragment_id"])

    def find_location(self, fragment_id: str) -> CatalogedFragment:
        # TODO: Read planet_id dynamically
        fragments = self.journal.cataloged_fragments("nocturna")

        sites = [item for item in fragments if item.fragment_id == fragment_id]
        if len(sites) > 0:
            return sites[0]

    def collect(self, location: FragmentLocation) -> ActionResult:
        return self.ref.collect(location.coords)
