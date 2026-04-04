class FundAllocator:
    def __init__(self, fund_allocation: dict[str, float]) -> None:
        self.fund_allocation = fund_allocation

    def funds_for(self, index: str) -> float:
        return float(self.fund_allocation.get(index, 0))
