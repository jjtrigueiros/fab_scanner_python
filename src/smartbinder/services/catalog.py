from sqlalchemy.orm import Session


class CatalogService:
    """
    A catalog for cards and printings.
    """

    def __init__(self, session: Session) -> None:
        self.session: Session = session

    def get_cards(self):
        pass
