from Utils import *

class Client:
    def __init__(self, Trace, CSize, AProb=0.5):
        self.Trace = Trace
        self.CSys = LHR.CacheSys(CSize, AProb)

    def main(self):
        HITs = []
        DoneReqs = 0
        K = 10000

        for i in range(len(self.Trace)):
            Req = self.Trace[i]
            hit = self.CSys.admit(Req)
            DoneReqs += 1
            HITs.append(hit)

            if DoneReqs == K:
                DoneReqs = 0
                self.CSys.reset()

        MHits = np.mean(HITs)

        return MHits, HITs


if __name__ == '__main__':
    Trace = None
    CacheSize = None
    AdmitProb = 0.5
    
    BCache = Client(Trace, CacheSize, AdmitProb)
    BCache.main()
