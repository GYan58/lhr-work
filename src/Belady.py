from Utils import *

class Belady:
    def __init__(self,Trace,CacheSize):
        self.Trace = cp.deepcopy(Trace)
        self.CSize = CacheSize
        self.UsedSpace = 0
        self.Caches = {}
        self.Timer = 0
        self.hit = 0
        self.miss = 0
        self.ReqTimes = {}
        self.Counters = {}
        self.process()

    def process(self):
        self.ReqTimes, self.Counters = get_req_time(self.Trace)

    def reset(self):
        self.hit = 0
        self.miss = 0

    def evict(self):
        Dises = {}
        for ky in self.Caches.keys():
            CNow = self.Counters[ky]
            NRT = self.ReqTimes[ky][CNow]
            Dis = (NRT - self.Timer) * self.Caches[ky]
            Dises[ky] = Dis

        SDis = sorted(Dises.items(), key=lambda item: item[1])
        for i in range(len(SDis)):
            Id = SDis[-1-i][0]
            Size = self.Caches[Id]
            self.UsedSpace -= Size
            self.Caches.pop(Id)
            if self.UsedSpace <= self.CSize:
                break

    def admit(self,req):
        Id = req[1]
        Time = req[0]
        Size = req[2]
        self.Timer = Time
        self.Counters[Id] += 1
        Hit = 0
        Cache = False
        if Id not in self.Caches.keys():
            Cache = True
            self.miss += 1
        else:
            self.hit += 1
            Hit = 1
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
    BCache = Belady(Trace, CacheSize)
    BCache.main()
