import numpy as np
import random as rd
import copy as cp
import lightgbm as gbm
import xgboost as xgb
from scipy.stats import linregress

BaseRoot = ""
Symbol = ""

class DModel:
    def __init__(self,X,Y):
        self.X = X
        self.Y = Y

    def model(self):
        params = {
            'boosting_type': 'gbdt',
            'objective': 'regression',
            'learning_rate': 0.1,
            'num_leaves': 32,
            'max_depth': 50,
            "min_data_in_leaf": 0,

            'verbose': -1
        }

        data_train = gbm.Dataset(self.X, self.Y)
        model = gbm.train(params, data_train, num_boost_round=100)

        #model = xgb.XGBRegressor(max_depth=10, learning_rate=0.1, n_estimators=50, objective='reg:squarederror')
        #model.fit(self.X_train,self.Y_train)

        return model

class Zipf:
    def __init__(self,trace):
        self.trace = trace

    def estimate(self):
        Data = self.trace
        data = {}
        num_data = 0
        for req in Data:
            Id = req[1]
            if Id not in data.keys():
                data[Id] = 1
            else:
                data[Id] += 1
            num_data += 1

        Data = {}
        Sort_Data = sorted(data.items(), key=lambda item: item[1])
        for i in range(len(Sort_Data)):
            id_now = i + 1
            freq_now = Sort_Data[-1-i][1]
            Data[id_now] = freq_now

        X = []
        Y = []
        for ky in Data.keys():
            X.append(np.log(ky))
            Y.append(np.log(Data[ky] / num_data))

        alpha, intercept, r_value, p_value, std_err = linregress(X,Y)

        return -alpha

def get_req_time(Trace):
    GTimes = {}
    Counters = {}
    for i in range(len(Trace)):
        Req = Trace[i]
        I = Req[1]
        T = Req[0]
        if I not in GTimes.keys():
            GTimes[I] = [T]
            Counters[I] = 0
        else:
            GTimes[I].append(T)

    for ky in GTimes.keys():
        GTimes[ky].append(pow(10,8))

    return GTimes, Counters

def get_arriv_rates(Trace):
    GTimes = {}
    Sizes = {}
    for i in range(len(Trace)):
        Req = Trace[i]
        I = Req[1]
        T = Req[0]
        S = Req[2]
        if I not in GTimes.keys():
            GTimes[I] = [T]
        else:
            GTimes[I].append(T)

        Sizes[I] = S

    Rates = {}
    for ky in GTimes.keys():
        GTs = GTimes[ky]
        inter = [100000000]
        if len(GTs) > 3:
            inter = []
            for i in range(len(GTs)-1):
                First = GTs[i+1]
                Second = GTs[i]
                inter.append(First - Second)

        minter = np.mean(inter)
        Rates[ky] = 1 / minter / Sizes[ky]

    return Rates, Sizes

class Extractor:
    def __init__(self,L=32):
        self.LRTs = {}
        self.Deltas = {}
        self.L = L

    def main(self,Req):
        L = self.L

        Id = Req[1]
        Size = Req[2]
        Time = Req[0]

        Feas = [Size]
        delta = []

        if Id not in self.Deltas.keys():
            for i in range(L):
                delta.append(pow(10, 8))
        else:
            last_delta = self.Deltas[Id]
            d0 = Time - self.LRTs[Id]
            last_delta.append(d0)
            delta = last_delta[-L:]

        self.Deltas[Id] = delta
        self.LRTs[Id] = Time
        Feas += delta

        return Feas


class HazardOPT:
    def __init__(self, Trace, CacheSize):
        self.Trace = cp.deepcopy(Trace)
        self.CSize = CacheSize

        self.UsedSpace = 0
        self.Caches = {}
        self.RankVals = {}
        self.Timer = 0
        self.hit = 0
        self.miss = 0
        self.C = 0

        self.Rates = {}
        self.process()
        self.HisIDs = []
        self.Sizes = {}

        self.Full = False

    def process(self):
        self.Rates, self.Sizes = get_arriv_rates(self.Trace)

    def reset(self):
        self.hit = 0
        self.miss = 0

    def recency_check(self):
        UIDs = list(np.unique(self.HisIDs))
        DelIds = list(set(list(self.Caches.keys()))-set(UIDs))
        if len(DelIds) > 0:
            DelNum = min(len(DelIds),8)
            DIds = rd.sample(DelIds,DelNum)
            for ky in DIds:
                self.UsedSpace -= self.Caches[ky]
                self.Caches.pop(ky)
                self.RankVals.pop(ky)

    def evict(self):
        SRates = sorted(self.RankVals.items(), key=lambda item: item[1])
        for i in range(len(SRates)):
            Id = SRates[i][0]
            Size = self.Caches[Id]
            self.UsedSpace -= Size
            self.Caches.pop(Id)
            self.RankVals.pop(Id)
            if self.UsedSpace <= self.CSize:
                break

    def admit(self, req):
        Id = req[1]
        Time = req[0]
        Size = req[2]
        Rt = self.Rates[Id]

        self.Timer = Time
        self.C += 1

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
            self.RankVals[Id] = Rt
            self.UsedSpace += Size

        if self.UsedSpace > self.CSize:
            self.evict()
            self.Full = True

        if self.C % 1000 == 0:
            if self.Full == True:
                CheckRange = 20000
                if len(self.HisIDs) > CheckRange:
                    self.HisIDs = self.HisIDs[-CheckRange:]
                self.recency_check()

        return Hit

    def main(self, Caches, USpace, K=10000):
        OPTs = []
        self.Caches = cp.deepcopy(Caches)
        for ky in self.Caches.keys():
            if ky in self.Rates.keys():
                self.RankVals[ky] = self.Rates[ky]
            else:
                self.RankVals[ky] = 1 / pow(10,6)
        self.UsedSpace = USpace
        L = len(self.Trace) - K

        self.HisIDs = []
        for i in range(L):
            Req = self.Trace[i]
            ID = Req[1]
            self.HisIDs.append(ID)

        for i in range(K):
            Req = self.Trace[L + i]
            Id = Req[1]
            self.admit(Req)
            if Id in self.Caches.keys():
                OPTs.append(1)
            else:
                OPTs.append(0)

        return OPTs
