# LibRecommender

## Overview

**LibRecommender** is an easy-to-use recommender system focused on end-to-end recommendation. The main features are:

+ Implemented a number of popular recommendation algorithms such as SVD++, DeepFM, BPR etc.

+ A hybrid recommender system, which allows user to use either collaborative-filtering or content-based features or both.

+ Ease of memory usage, automatically convert categorical features to sparse representation.

+ Support training for both explicit and implicit datasets, and negative sampling can be used for implicit dataset.

+ Making use of Cython or Tensorflow for high-speed model training.

+ Provide end-to-end workflow, i.e. data handling / preprocessing -> model training -> evaluate -> serving.

+ Provide unified and friendly API for all algorithms.



## Usage

#### _pure collaborative-filtering example_ : 

```python
import numpy as np
import pandas as pd
from libreco.data import random_split, DatasetPure
from libreco.algorithms import SVDpp  # pure data, algorithm SVD++

data = pd.read_csv("examples/sample_data/sample_movielens_rating.dat", sep="::", 
                   names=["user", "item", "label", "time"])

# split whole data into three folds for training, evaluating and testing
train_data, eval_data, test_data = random_split(data, multi_ratios=[0.8, 0.1, 0.1])

train_data, data_info = DatasetPure.build_trainset(train_data)
eval_data = DatasetPure.build_testset(eval_data)
test_data = DatasetPure.build_testset(test_data)
print(data_info)   # n_users: 5894, n_items: 3253, data sparsity: 0.4172 %

svdpp = SVDpp(task="rating", data_info=data_info, embed_size=16, n_epochs=3, lr=0.001, 
              reg=None, batch_size=256)
# monitor metrics on eval_data during training
svdpp.fit(train_data, verbose=2, eval_data=eval_data, metrics=["rmse", "mae", "r2"])

# do final evaluation on test data
svdpp.evaluate(test_data, metrics=["rmse", "mae"])  
# predict preference of user 1 to item 2333
print("prediction: ", svdpp.predict(user=1, item=2333))
# recommend 7 items for user 1
print("recommendation(id, probability): ", svdpp.recommend_user(user=1, n_rec=7))  
```

#### _include features example_ : 

```python
import numpy as np
import pandas as pd
from libreco.data import split_by_ratio_chrono, DatasetFeat
from libreco.algorithms import YouTubeRanking  # feat data, algorithm YouTubeRanking

data = pd.read_csv("examples/sample_data/sample_movielens_merged.csv", sep=",", header=0)
data["label"] = 1  # convert to implicit data and do negative sampling afterwards

# split into train and test data based on time
train_data, test_data = split_by_ratio_chrono(data, test_size=0.2)

# specify complete columns information
sparse_col = ["sex", "occupation", "genre1", "genre2", "genre3"]
dense_col = ["age"]
user_col = ["sex", "age", "occupation"]
item_col = ["genre1", "genre2", "genre3"]

train_data, data_info = DatasetFeat.build_trainset(
    train_data, user_col, item_col, sparse_col, dense_col)
test_data = DatasetFeat.build_testset(test_data, sparse_col, dense_col)
train_data.build_negative_samples(data_info)  # sample negative items for each record
test_data.build_negative_samples(data_info)
print(data_info)  # n_users: 5962, n_items: 3226, data sparsity: 0.4185 %

ytb_ranking = YouTubeRanking(task="ranking", data_info=data_info, embed_size=16, 
                             n_epochs=3, lr=1e-4, batch_size=512, use_bn=True, 
                             hidden_units="128,64,32")
ytb_ranking.fit(train_data, verbose=2, shuffle=True, eval_data=test_data,
                metrics=["loss", "roc_auc", "precision", "recall", "map", "ndcg"])

# predict preference of user 1 to item 2333
print("prediction: ", ytb_ranking.predict(user=1, item=2333))  
# recommend 7 items for user 1
print("recommendation(id, probability): ", ytb_ranking.recommend_user(user=1, n_rec=7))  
```


## Data Format
JUST normal data format, each line represents a sample. One thing is important, the model assumes that `user`, `item`, and `label` column index are 0, 1, and 2, respectively. You may wish to change the column order if that's not the case. Take for Example, the `movielens-1m` dataset:

> 1::1193::5::978300760<br>
> 1::661::3::978302109<br>
> 1::914::3::978301968<br>
> 1::3408::4::978300275

Besides, if you want to use some other meta features (e.g., age, sex, category etc.),  you need to tell the model which columns are [`sparse_col, dense_col, user_col, item_col`], which means all features must be in a same table. See above `YouTubeRanking` for example.



## Serving

For how to serve a trained model in LibRecommender, see [serving README](<https://github.com/massquantity/LibRecommender/tree/master/serving>) .



## Installation & Dependencies 

From pypi : &nbsp;  

```
$ pip install LibRecommender==0.1.0
```

To build from source, you 'll first need [Cython](<https://cython.org/>) and [Numpy](<https://numpy.org/>):

```
$ # pip install numpy cython
$ git clone https://github.com/massquantity/LibRecommender.git
$ cd LibRecommender
$ python setup.py install
```


#### Basic Dependencies in `libreco`:
- Python >= 3.6
- tensorflow >= 1.14
- numpy >= 1.15.4
- pandas >= 0.23.4
- scipy >= 1.2.1
- scikit-learn >= 0.20.0
- tqdm >= 4.46.0

`LibRecommender` is tested under tensorflow 1.14 and 2.3. If you encounter any problem during running, feel free to open an issue.

#### Optional Serving Dependencies:

+ flask >= 1.0.0
+ requests >= 2.22.0
+ [redis](<https://redis.io/>) == 3.0.6
+ [redis-py](https://github.com/andymccurdy/redis-py) >= 3.3.5
+ [faiss](https://github.com/facebookresearch/faiss) == 1.5.2
+ [Tensorflow Serving](<https://github.com/tensorflow/serving>)



## References

|     Algorithm     | Category | Paper                                                        |
| :---------------: | :------: | :----------------------------------------------------------- |
| userCF / itemCF |   pure   | [Item-Based Collaborative Filtering Recommendation Algorithms](http://www.ra.ethz.ch/cdstore/www10/papers/pdf/p519.pdf) |
|        SVD        |   pure   | [Matrix Factorization Techniques for Recommender Systems](https://datajobs.com/data-science-repo/Recommender-Systems-[Netflix].pdf) |
|      SVD ++       |   pure   | [Factorization Meets the Neighborhood: a Multifaceted Collaborative Filtering Model](https://dl.acm.org/citation.cfm?id=1401944) |
|        ALS        |   pure   | 1. [Matrix Completion via Alternating Least Square(ALS)](https://stanford.edu/~rezab/classes/cme323/S15/notes/lec14.pdf) / <br>2. [Collaborative Filtering for Implicit Feedback Datasets](http://yifanhu.net/PUB/cf.pdf) / <br>3. [Applications of the Conjugate Gradient Method for Implicit Feedback Collaborative Filtering](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.379.6473&rep=rep1&type=pdf) |
|        NCF        |   pure   | [Neural Collaborative Filtering](https://arxiv.org/pdf/1708.05031.pdf) |
|        BPR        |   pure   | [BPR: Bayesian Personalized Ranking from Implicit Feedback](https://arxiv.org/ftp/arxiv/papers/1205/1205.2618.pdf) |
|    Wide & Deep    |   feat   | [Wide & Deep Learning for Recommender Systems](https://arxiv.org/pdf/1606.07792.pdf) |
|        FM         |   feat   | [Factorization Machines](https://www.csie.ntu.edu.tw/~b97053/paper/Rendle2010FM.pdf) |
|      DeepFM       |   feat   | [DeepFM: A Factorization-Machine based Neural Network for CTR Prediction](https://arxiv.org/pdf/1703.04247.pdf) |
|   YouTubeMatch  YouTubeRanking |   feat   | [Deep Neural Networks for YouTube Recommendations](<https://static.googleusercontent.com/media/research.google.com/zh-CN//pubs/archive/45530.pdf>) |
| AutoInt | feat | [AutoInt: Automatic Feature Interaction Learning via Self-Attentive Neural Networks](https://arxiv.org/pdf/1810.11921.pdf) |
|        DIN        |   feat   | [Deep Interest Network for Click-Through Rate Prediction](https://arxiv.org/pdf/1706.06978.pdf) |

> `pure` means collaborative-filtering algorithms which only use behavior data, whereas `feat` means other features can be included.

## License

#### MIT

<br>

