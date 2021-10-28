# LHR Simulator
Here provides the basic realization of LHR on Python3. The simulator here contains all functions described in our submitted paper "Learning from Optimal Caching for Content Delivery".


# Usage
1. Requirement: Python >= 3.6, Xgboost and Lightgbm

2. The script "LHR.py" is the realization of LHR algorithm, parameters can be changed under different cases

3. The code named "Utils.py" contains the functions used in LHR

4. Run the file "Main.py" to start the LHR

5. THe file "Traffic.py" is used to estimated traffic WAN


# Experiments
We have implemented LHR and a bunch of state-of-the-arts in simulators including but not limited to:
- Learning Relaxed Belady (LRB)
- LRU
- B-LRU (Bloom Filter LRU)
- LRUK
- LFUDA
- AdaptSize
- Hawkeye

To get the results in figure 8 of our paper, 



# Prototype


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





