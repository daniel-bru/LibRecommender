import numpy as np
import tensorflow as tf
from sklearn.metrics import precision_score


def rmse_knn(model, dataset, mode="train"):
    if mode == "train":
        user_indices = dataset.train_user_indices
        item_indices = dataset.train_item_indices
        ratings = dataset.train_labels
    elif mode == "test":
        user_indices = dataset.test_user_indices
        item_indices = dataset.test_item_indices
        ratings = dataset.test_labels

    pred = []
    for j, (u, i) in enumerate(zip(user_indices, item_indices)):
        p = model.predict(u, i)
        pred.append(p)
    score = np.sqrt(np.mean(np.power(pred - ratings, 2)))
    return score


def rmse_svd(model, dataset, baseline=False, mode="train"):
    if mode == "train":
        user_indices = dataset.train_user_indices
        item_indices = dataset.train_item_indices
        ratings = dataset.train_ratings
    elif mode == "test":
        user_indices = dataset.test_user_indices
        item_indices = dataset.test_item_indices
        ratings = dataset.test_ratings

    pred = []
    for u, i in zip(user_indices, item_indices):
        p = model.predict(u, i)
        pred.append(p)
    score = np.sqrt(np.mean(np.power(pred - ratings, 2)))
    return score


def rmse_tf(model, dataset, mode="train"):
    if mode == "train":
        user_indices = dataset.train_user_indices
        item_indices = dataset.train_item_indices
        ratings = dataset.train_ratings
    elif mode == "test":
        user_indices = dataset.test_user_indices
        item_indices = dataset.test_item_indices
        ratings = dataset.test_ratings

    rmse = model.sess.run(model.metrics, feed_dict={model.user_indices: user_indices,
                                                    model.item_indices: item_indices,
                                                    model.ratings: ratings})
    return rmse


def precision_tf(pred, y):
    one = tf.constant(1, dtype=tf.float32)
    mask = tf.equal(pred, one)
    y_chosen = tf.boolean_mask(y, mask)
    precision = tf.reduce_sum(y_chosen) / tf.cast(tf.shape(y_chosen), tf.float32)
    return precision[0]


def AP_at_k(model, dataset, u, k):
    ranklist = model.predict_user(u)
    top_k = np.argsort(ranklist)[::-1][:k]
    precision_k = 0
    count_relevant_k = 0
    for i in range(1, k + 1):
        precision_i = 0
        if top_k[i-1] in dataset.train_user[u]:
            count_relevant_k += 1
            for pred in top_k[:i]:
                if pred in dataset.train_user[u]:
                    precision_i += 1
            precision_k += precision_i / i
        else:
            continue
    try:
        average_precision_at_k = precision_k / count_relevant_k
    except ZeroDivisionError:
        average_precision_at_k = 0.0
    return average_precision_at_k


def MAP_at_k(model, dataset, k):
    average_precision_at_k = 0
    for u in dataset.train_user:
        average_precision_at_k += AP_at_k(model, dataset, u, k)
    mean_average_precision_at_k = average_precision_at_k / dataset.n_users
    return mean_average_precision_at_k


def HitRatio_at_k(model, dataset, k):
    HitRatio = []
    for u in dataset.train_user:
        user_HitRatio = 0
        ranklist = model.predict_user(u)
        top_k = np.argsort(ranklist)[::-1][:k]
        for i in top_k:
            if i in dataset.train_user[u]:
                user_HitRatio += 1
        HitRatio.append(user_HitRatio / k)
    return np.mean(HitRatio)


def NDCG_at_k(model, dataset, k):
    NDCG = 0
    for u in dataset.train_user:
        DCG = 0
        IDCG = 0
        ranklist = model.predict_user(u)
        top_k = np.argsort(ranklist)[::-1][:k]
        for n, item in enumerate(top_k):
            if item in dataset.train_user[u]:
                DCG += np.reciprocal(np.log2(n + 2))
        for n in range(k):
            IDCG += np.reciprocal(np.log2(n + 2))
        NDCG += DCG / IDCG
    return NDCG / dataset.n_users


def NDCG_at_k_tf(labels, predictions, k):
    _, indices = tf.nn.top_k(predictions, k, sorted=True)
    n = tf.cast(tf.range(1, k + 1), tf.float32)
    top_k = tf.gather(labels, indices)
    denominator = tf.log(n + 1) / tf.log(2.0) # logarithm base 2
    dcg_numerator = tf.pow(2.0, top_k) - 1.0
    DCG = tf.reduce_sum(dcg_numerator / denominator, axis=1, keep_dims=True)
    IDCG = tf.reduce_sum(1.0 / denominator, axis=1, keep_dims=True)
    NDCG = DCG / IDCG
    return tf.metrics.mean(NDCG)


def binary_cross_entropy(model, user, item, label, method="mf"):
    ce = []
    probs = []
    for u, i, l in zip(user, item, label):
        prob, _ = model.predict(u, i, method)
        probs.append(prob)
        if l == 1.0:
            ce.append(-np.log(prob))
        elif l == 0.0:
            ce.append(-np.log(1.0 - prob))
    return np.mean(ce), probs


# TODO
# def recall

# def f1


# def evaluate in fit