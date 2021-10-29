from Utils import *

def get_inters(Trace):
    Counters = {}
    Inters = {}
    Sizes = {}

    Times = {}
    for i in range(len(Trace)):
        Req = Trace[i]
        I = Req[1]
        T = Req[0]
        S = Req[2]
        if I not in Times.keys():
            Times[I] = [T]
        else:
            Times[I].append(T)

        Sizes[I] = S

    for ky in Times.keys():
        Counters[ky] = 0
        inter = [1000000]
        GTs = Times[ky]
        if len(GTs) > 1:
            inter = []
            for i in range(len(GTs)-1):
                inter.append(GTs[i+1] - GTs[i])
        Inters[ky] = inter
    return Inters, Counters, Sizes


class Hazard:
    def __init__(self, Trace, CacheSize):
        self.Trace = cp.deepcopy(Trace)
        self.CSize = CacheSize
        self.UsedSpace = 0
        self.Caches = {}
        self.Timer = 0
        self.hit = 0
        self.miss = 0
        self.C = 0
        self.Rates = {}
        self.Inters = {}
        self.Counters = {}
        self.process()
        self.initrates()
        self.HisIDs = []
        self.Sizes = {}

    def process(self):
        self.Inters, self.Counters, self.Sizes = get_inters(self.Trace)

    def initrates(self):
        for ky in self.Inters.keys():
            GIs = self.Inters[ky][self.Counters[ky]:]
            if len(GIs) > 0:
                self.Rates[ky] = 1 / np.mean(GIs) / self.Sizes[ky]

    def reset(self):
        self.hit = 0
        self.miss = 0

    def evict(self):
        GRates = {}
        for ky in self.Caches.keys():
            GRates[ky] = self.Rates[ky]

        SRates = sorted(GRates.items(), key=lambda item: item[1])
        for i in range(len(SRates)):
            Id = SRates[i][0]
            Size = self.Caches[Id]
            self.UsedSpace -= Size
            self.Caches.pop(Id)
            if self.UsedSpace <= self.CSize:
                break

    def admit(self, req):
        Id = req[1]
        Time = req[0]
        Size = req[2]

        self.Timer = Time
        self.C += 1
        self.Counters[Id] += 1

        UInter = self.Inters[Id][self.Counters[Id]-1:]
        if len(UInter) == 0:
            self.Rates[Id] = 1 / 1000000 / Size
        else:
            self.Rates[Id] = 1 / np.mean(UInter) / Size

        Hit = 0
        Cache = False
        if Id not in self.Caches.keys():
            Cache = True
            self.miss += 1
        else:
            self.hit += 1
            Hit = 1

        self.HisIDs.append(Id)
        self.Sizes[Id] = Size

        if Cache == True:
            self.Caches[Id] = Size
            self.UsedSpace += Size

        if self.UsedSpace > self.CSize:
            self.evict()

        return Hit

    def main(self):
        HITs = []
        K = None
        DoneReqs = 0
        C = 0

        for i in range(len(self.Trace)):
            Req = self.Trace[i]
            self.admit(Req)
            DoneReqs += 1
            if DoneReqs == K:
                C += 1
                DoneReqs = 0
                Hit = self.hit
                self.reset()
                HITs.append(Hit)
        MHit = np.mean(HITs)

        return MHit, HITs

if __name__ == '__main__':
    Trace = None
    CacheSize = None
    HCache = Hazard(Trace, CacheSize)
    HCache.main()
