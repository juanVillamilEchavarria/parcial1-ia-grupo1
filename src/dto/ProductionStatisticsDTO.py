class ProductionStatisticsDTO:
    def __init__(self, average, median, std, min, max, count, sum):
        self.average = average
        self.median = median
        self.std = std
        self.min = min
        self.max = max
        self.count = count
        self.sum = sum