# LHR Simulator
Here provides the basic realization of LHR on Python3. The simulator here contains all functions described in our submitted paper "Learning from Optimal Caching for Content Delivery".


# Usage
1. Requirement: Python >= 3.6, Xgboost and Lightgbm

2. The script "LHR.py" is the realization of LHR algorithm, parameters can be changed under different cases

3. The code named "Utils.py" contains the functions used in LHR

4. Run the file "Main.py" to start the LHR

5. THe file "Traffic.py" is used to estimated traffic WAN

6. "HRO.py" provides the method to get the upper bound and "Belady.py" simulates the behaviour of Belady's algorithm

# Trace Format
| Time | ID | Size |
|:----:|:----:|:----:|
| 0 | 1 | 1024 |
| 1 | 23 | 1024 |
| 2 | 15 | 2048 |
| 3 | 10 | 1024 |


# Experiments
We have implemented LHR and a bunch of state-of-the-arts in simulators including but not limited to:
- LHR
- [Hawkeye](https://ieeexplore.ieee.org/document/7551384/) 
- Learning Relaxed Belady ([LRB](https://www.usenix.org/conference/nsdi20/accepted-papers))
- LRU
- B-LRU (Bloom Filter LRU)
- LRUK
- LFUDA
- AdaptSize

To get the results in figure 8 of our paper, you should do:
- Run LHR algorithm to get the real hits
- Run Simulators in [Webcachesim](https://github.com/sunnyszy/lrb) to get results for SOTAs
- By using real-hit results, run "Traffic.py" to get the estimated WAN


To get figure 2, you should do:
- Run "HRO.py" and "Belady.py" to get HRO bound and Belady bound
- Run [PFOO](https://github.com/dasebe/optimalwebcaching) to get the PFOO bound
- SOTAs could be reached by using [Webcachesim](https://github.com/sunnyszy/lrb)

To estimate overhead, put all algorithms on the same platform and add the following codes to estimate the overhead:
```
import time
TStart = time.time()
......
TEnd = time.time()
RunTime = TEnd - TStart

import psutil
CPU = psutil.cpu_percent()
Memory = psutil.virtual_memory()
```

# Citation
If you use the simulator or some results in our paper for a published project, please cite our work by using the following bibtex entry

```
@inproceedings{yan2021learning,
  title={Learning from Optimal Caching for Content Delivery},
  author={Yan, Gang and Li, Jian and Towsley, Don},
  booktitle={Proc. of ACM CoNEXT},
  year={2021}
}
```





