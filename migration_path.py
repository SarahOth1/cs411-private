from typing import Optional
from typing import Any
from wildlife_tracker.habitat_management.habitat import Habitat


class MigrationPath:

    def __init__(self,path_id: int,
                 species: str,
                 start_location: Habitat,
                 destination: Habitat,
                 duration: Optional[int] = None) -> None:
        self.path_id: int = path_id,
        self.destination: Habitat = destination
        self.duration: Optional[int] = duration
        self.species: str = species
        self.start_location: Habitat = start_location


        def get_migration_path_details(self) -> dict:
            pass
        def update_migration_path_details(self, **kwargs: Any) -> None:
            pass