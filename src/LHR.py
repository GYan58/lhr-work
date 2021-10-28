import random as rd
import copy as cp
from Utils import *
import gc

class CacheSim:
    def __init__(self,Caches,Csize,RVals,USpace,LRTs,Timer,AdmitProb):
        self.Caches = Caches
        self.CSize = Csize
        self.RankVal = RVals
        self.UsedSpace = USpace
        self.hit = 0
        self.miss = 0
        self.LRTs = LRTs
        self.Timer = Timer
        self.AProb = AdmitProb

    def evict(self):
        SIDs = rd.sample(list(self.Caches.keys()),256)
        
        Dises = {}
        for ky in SIDs:
            Dises[ky] = self.RankVal[ky] / (self.Timer - self.LRTs[ky] + 1)

        SDis = sorted(Dises.items(), key=lambda item: item[1])
        for i in range(len(SDis)):
            Id = SDis[i][0]
            Size = self.Caches[Id]
            self.UsedSpace -= Size
            self.Caches.pop(Id)
            if self.UsedSpace <= self.CSize:
                break


    def admit(self,Req,Prob):
        Time = Req[0]
        Id = Req[1]
        Size = Req[2]

        self.RankVal[Id] = Prob / Size

        self.Timer = Time
        self.LRTs[Id] = Time

        Cache = False
        if Id not in self.Caches.keys():
            self.miss += 1
            Cache = True
        else:
            self.hit += 1
            self.Caches.pop(Id)
            self.Caches[Id] = Size

        if Cache == True and Prob >= self.AProb:
            self.Caches[Id] = Size
            self.UsedSpace += Size

        if self.UsedSpace > self.CSize:
            self.evict()


class CSys:
    def __init__(self,Csize, AProb=0.0, Pert = 5):
        self.CSize = Csize
        self.UsedSpace = 0
        self.Caches = {}
        self.Timer = 0
        self.hit = 0
        self.miss = 0
        self.AProb = AProb
        self.Pert = Pert

        self.LRTs = {}
        self.ProcNum = 0
        self.WinSize = 10000
        self.PastReqs = []
        self.PastFeas = []
        self.TrainSize = 5 * 10000
        self.Admit = None
        self.RankVal = {}
        self.extractor = Extractor(20)

        self.WinCache_Back = []
        self.Warmup = False
        self.RefillSize = 0
        self.LenCount = 0
        self.NewIDs = []
        self.PCount = 0
        self.TX = []
        self.TY = []

        self.Alphas = []
        self.CutVal = 0
        self.LastVal = 0
        self.LastTrained = False

        self.Decisions = []
        self.CollectHits = []
        self.CollectReqs = []
        self.CacheReplay = None
        self.GCaches = None
        self.GRankVal = None
        self.GSpace = None
        self.GLRTs = None
        self.GTimer = None

    def reset(self):
        self.hit = 0
        self.miss = 0

    def evict(self):
        SIDs = rd.sample(list(self.Caches.keys()),256)

        Dises = {}
        for ky in SIDs:
            Dises[ky] = self.RankVal[ky] / (self.Timer - self.LRTs[ky] + 1)

        SDis = sorted(Dises.items(), key=lambda item: item[1])
        for i in range(len(SDis)):
            Id = SDis[i][0]
            Size = self.Caches[Id]
            self.UsedSpace -= Size
            self.Caches.pop(Id)
            if self.UsedSpace <= self.CSize:
                break

    def admit(self,Req):
        Id = Req[0]
        Size = Req[1]

        Feas = self.extractor.main(Req)

        if self.GCaches == None and self.Admit != None:
            self.GCaches = cp.deepcopy(self.Caches)
            self.GRankVal = cp.deepcopy(self.RankVal)
            self.GSpace = cp.deepcopy(self.UsedSpace)
            self.GLRTs = cp.deepcopy(self.LRTs)
            self.GTimer = cp.deepcopy(self.Timer)

        self.PastReqs.append(Req)
        self.PastFeas.append(Feas)

        Prob = 1
        if self.Admit != None:
            Prob = self.Admit.predict([Feas])[0]

        self.RankVal[Id] = Prob / Size

        self.LRTs[Id] = self.Timer
        self.Timer += 1

        Hit = 0
        Cache = False
        if Id not in self.Caches.keys():
            self.miss += 1
            Cache = True
        else:
            self.hit += 1
            Hit = 1
            self.Caches.pop(Id)
            self.Caches[Id] = Size

        if Cache == True and Prob >= self.AProb:
            self.Caches[Id] = Size
            self.UsedSpace += Size

        if self.UsedSpace > self.CSize:
            self.evict()

        if self.Warmup == False:
            self.PCount += 1

        Train = False

        if self.PCount == self.TrainSize:
            self.Warmup = True
            self.PCount = 0
            self.PastFeas = []
            self.WinCache_Back = [self.Caches,self.UsedSpace]

        if self.Warmup == True:
            self.LenCount += 1
            if Id not in self.NewIDs:
                self.NewIDs.append(Id)
                self.RefillSize += Size

            if self.RefillSize >= self.CSize * 4 and self.LenCount >= 10000:
                Train = True
                self.WinSize = self.LenCount
                self.RefillSize = 0
                self.LenCount = 0
                self.NewIDs = []
                CReqs = self.PastReqs[-len(self.PastFeas):]
                Alp = Zipf(CReqs).estimate()

                if len(self.Alphas) >= 5:
                    P1 = np.percentile(self.Alphas, self.Pert)
                    ValNow = abs(Alp - self.LastVal)
                    print(ValNow,P1)
                    if ValNow <= P1 and self.LastTrained == True:
                        Train = False

                if self.LastVal == 0:
                    self.Alphas.append(0.01)
                else:
                    self.Alphas.append(abs(Alp-self.LastVal))
                self.LastVal = Alp
                if len(self.Alphas) > 10:
                    self.Alphas = self.Alphas[-10:]

                if Train == True:
                    self.LastTrained = True
                else:
                    self.LastTrained = False

                if Train == False:
                    if len(self.PastReqs) > self.TrainSize:
                        self.PastReqs = self.PastReqs[-self.TrainSize:]

        if self.Admit != None:
            self.CollectHits.append(Hit)
            self.CollectReqs.append(Req)
            self.Decisions.append(Prob)
        if Train == True and self.Admit != None:
            Candidates = []
            if self.AProb == 0.5:
                Candidates = [0]
            if self.AProb == 0:
                Candidates = [0.5]
            if self.AProb != 0 and self.AProb != 0.5:
                Candidates = [0,0.5]
            GP1 = self.AProb - 0.1
            GP2 = self.AProb + 0.1
            if GP1 > 0 and GP1 not in Candidates:
                Candidates.append(GP1)
            if GP2 > 0 and GP2 not in Candidates:
                Candidates.append(GP2)

            HitsSum = np.sum(self.CollectHits)

            self.CacheReplay = {}
            for c in Candidates:
                GCSim = CacheSim(self.GCaches,self.CSize,self.GRankVal,self.GSpace,self.GLRTs,self.GTimer,c)
                self.CacheReplay[c] = cp.deepcopy(GCSim)

            for j in range(len(self.CollectReqs)):
                Greq = self.CollectReqs[j]
                Gprob = self.Decisions[j]
                for c in Candidates:
                    self.CacheReplay[c].admit(Greq,Gprob)

            find_th = -1
            find_val = 0
            for c in Candidates:
                ghit = self.CacheReplay[c].hit
                if ghit > find_val:
                    find_val = ghit
                    find_th = c

            if find_val > HitsSum + 20:
                self.AProb = int((0.5 * self.AProb + 0.5 * find_th) * 100) / 100

            self.Decisions = []
            self.CollectHits = []
            self.CollectReqs = []
            self.CacheReplay = None
            self.GCaches = None
            self.GRankVal = None
            self.GSpace = None
            self.GLRTs = None
            self.GTimer = None

        if Train == True:
            COPT = HazardOPT(self.PastReqs,self.CSize)
            BKs = self.WinCache_Back
            OPTs = COPT.main(BKs[0],BKs[1],self.WinSize)
            VL = len(self.PastFeas)
            OPTs = OPTs[-VL:]

            self.TX = self.PastFeas
            self.TY = OPTs

            self.Admit = DModel(self.TX, self.TY).model()

            if len(self.PastReqs) > self.TrainSize:
                self.PastReqs = self.PastReqs[-self.TrainSize:]
            self.PastFeas = []

            self.WinCache_Back = [self.Caches, self.UsedSpace]

        return Hit
