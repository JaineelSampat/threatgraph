class EntityNotFoundError(Exception):
    """Raised when a requested entity id doesn't exist in the graph."""

    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        super().__init__(f"No entity found with id '{entity_id}'")
