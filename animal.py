from typing import Any, Optional

class Animal:
    def __init__(self,
                animal_id: int,
                species: str,
                environment_type: str,
                health_status: Optional[str] = None,
                age: Optional[int]= None,
                ) -> None:
        self.age = age
        self.species = species
        self.animal_id = animal_id
        self.environment_type: str
        self.health_status = health_status

    

def get_animal_details(self) -> dict[str, Any]:
        pass

def update_animal_details(self, **kwargs: Any) -> None:
        pass


