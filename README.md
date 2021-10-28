# LHR Simulator
Here provides the basic realization of LHR on Python3. The simulator here contains all functions described in our submitted paper "Learning from Optimal Caching for Content Delivery".


# Usage
1. Requirement: Python >= 3.6, Xgboost and Lightgbm

2. The script "LHR.py" is the realization of LHR algorithm, parameters can be changed according to user's needs

3. The code named "Utils.py" contains the functions used in LHR


# Experiment
Here only use the Wikipedia dataset as a test, the dataset can be found in the link https://github.com/sunnyszy/lrb. The real hits could be seen:
![image](https://github.com/GYan58/lhr-work/blob/main/Experiments/wiki.jpeg)


# Prototype
The prototype is implemented on ATS, the original prototype can be found in Zhenyu's work (https://github.com/sunnyszy/lrb). Based on the modified framework, we put LHR on ATS. 


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





