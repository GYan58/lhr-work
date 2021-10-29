import numpy as np

def get_traffic(Trace, Real):
    BWidth = None
    NetDelay = None
    Thrs = []
    Lats = []
    Tfcs = []
    DLats = []
    TransBytes = 0
    TransTime = 0
    UpTime = 0
    UpSize = 0
    CleanTime = 0

    for i in range(len(Trace)):
        Req = Trace[i]
        Size = Req[2]
        Hit = Real[i]
        TDelay = Size / BWidth
        Latency = TDelay
        Laty = 0
        if Hit == 0:
            Latency += NetDelay
            Laty = Latency
            UpSize += Size
        DLats.append(Latency)
        TransBytes += Size
        TransTime += Latency
        CleanTime += Laty
        UpTime += Size / BWidth + NetDelay

        if len(DLats) == 100:
            Thr = TransBytes / TransTime / 1024 / 1024
            Thrs.append(Thr)
            Tfcs.append(CleanTime / UpTime * BWidth / 1024 / 1024)
            Lats.append(np.mean(DLats))
            DLats = []
            TransBytes = 0
            TransTime = 0
            UpTime = 0
            UpSize = 0
            CleanTime = 0

if __name__ == '__main__':
    Trace = None
    RealHits = None
    get_traffic(Trace, RealHits)




























